import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { basename, dirname, extname, relative, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

function parseArgs(argv) {
  const opts = {
    workspace: '',
    cases: '',
    output: '',
    openDocumentsRoot: '',
    htmlRoot: '',
    profile: 'precise',
    topK: 10,
    limit: 0,
    indexDir: '',
    manifest: '',
    dataDir: '',
    failuresOut: '',
    sampleQuery: '',
    sampleOut: '',
    openAiBaseUrl: process.env.OPENAI_BASE_URL || '',
    openAiApiKey: process.env.OPENAI_API_KEY || '',
    chatModel: process.env.OD_CHAT_MODEL || process.env.LLM_EP_COMPANY_MODEL || process.env.LLM_MODEL || '',
    embeddingModel: process.env.OD_EMBEDDING_MODEL || process.env.EMBEDDING_MODEL || '',
    embeddingDimensions: Number.parseInt(
      process.env.OD_EMBEDDING_DIMENSIONS || process.env.EMBEDDING_DIMENSIONS || '1024',
      10,
    ),
    retrievalOnly: false,
    resetDataDir: false,
    skipIngest: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    const next = argv[i + 1]
    if (arg === '--workspace') opts.workspace = next
    if (arg === '--cases') opts.cases = next
    if (arg === '--output') opts.output = next
    if (arg === '--opendocuments-root') opts.openDocumentsRoot = next
    if (arg === '--html-root') opts.htmlRoot = next
    if (arg === '--profile') opts.profile = next
    if (arg === '--top') opts.topK = parseInt(next, 10)
    if (arg === '--limit') opts.limit = parseInt(next, 10)
    if (arg === '--index-dir') opts.indexDir = next
    if (arg === '--manifest') opts.manifest = next
    if (arg === '--data-dir') opts.dataDir = next
    if (arg === '--failures-out') opts.failuresOut = next
    if (arg === '--sample-query') opts.sampleQuery = next
    if (arg === '--sample-out') opts.sampleOut = next
    if (arg === '--openai-base-url') opts.openAiBaseUrl = next
    if (arg === '--openai-api-key') opts.openAiApiKey = next
    if (arg === '--chat-model') opts.chatModel = next
    if (arg === '--embedding-model') opts.embeddingModel = next
    if (arg === '--embedding-dimensions') opts.embeddingDimensions = parseInt(next, 10)
    if (arg === '--retrieval-only') opts.retrievalOnly = true
    if (arg === '--reset-data-dir') opts.resetDataDir = true
    if (arg === '--skip-ingest') opts.skipIngest = true
  }

  for (const key of ['workspace', 'cases', 'output', 'openDocumentsRoot', 'htmlRoot']) {
    if (!opts[key]) {
      throw new Error(`Missing required argument: --${key}`)
    }
  }

  return opts
}

function buildConfigOverrides(opts) {
  const baseUrl = String(opts.openAiBaseUrl || '').trim()
  const chatModel = String(opts.chatModel || '').trim()
  const embeddingModel = String(opts.embeddingModel || '').trim()
  const embeddingDimensions = Number.isFinite(opts.embeddingDimensions) && opts.embeddingDimensions > 0
    ? opts.embeddingDimensions
    : 1024

  if (!baseUrl || !chatModel || !embeddingModel) {
    return null
  }

  return {
    model: {
      provider: 'openai',
      llm: chatModel,
      embedding: embeddingModel,
      apiKey: String(opts.openAiApiKey || 'stage6-local').trim() || 'stage6-local',
      baseUrl,
      embeddingDimensions,
    },
  }
}

function loadJsonLines(path) {
  return readFileSync(path, 'utf-8')
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => JSON.parse(line))
}

function loadJson(path) {
  return JSON.parse(readFileSync(path, 'utf-8'))
}

function normalizeSlashes(value) {
  return value.replace(/\\/g, '/')
}

const KNOWN_TOP_LEVEL_DIRS = new Set([
  'installing',
  'post_installation_configuration',
  'updating',
  'upgrading',
  'backup_and_restore',
  'networking',
  'security',
  'storage',
  'nodes',
  'operators',
  'observability',
  'etcd',
  'disconnected',
  'registry',
  'cli_reference',
  'support',
  'authentication',
  'architecture',
  'machine_configuration',
  'machine_management',
  'web_console',
  'applications',
  'cicd',
])

function collectHtmlFiles(rootDir) {
  const files = []

  function walk(currentDir) {
    for (const entry of readdirSync(currentDir)) {
      const entryPath = resolve(currentDir, entry)
      const stat = statSync(entryPath)
      if (stat.isDirectory()) {
        walk(entryPath)
        continue
      }
      const extension = extname(entryPath).toLowerCase()
      if (extension === '.html' || extension === '.htm') {
        files.push(entryPath)
      }
    }
  }

  walk(resolve(rootDir))
  return files.sort()
}

function loadManifestInputs(path) {
  const payload = loadJson(path)
  const documents = Array.isArray(payload.documents) ? payload.documents : []

  return documents
    .filter((item) => item.normalized_path && item.html_path)
    .map((item) => ({
      title: item.title || basename(item.html_path),
      contentPath: item.normalized_path,
      sourcePath: item.html_path,
      fileType: '.txt',
      sourceType: 'local',
      manifestPath: item.local_path || item.source_url || item.html_path,
    }))
}

function mapHtmlSourcePathToAdoc(sourcePath, htmlRoot) {
  const resolved = resolve(sourcePath)
  const resolvedRoot = resolve(htmlRoot)
  const rel = normalizeSlashes(relative(resolvedRoot, resolved))
  if (rel.startsWith('..')) {
    return normalizeSlashes(sourcePath)
  }
  return rel.replace(/\.html$/i, '.adoc')
}

function stripSourcePrefix(documentPath) {
  const normalized = normalizeSlashes(documentPath).replace(/^\/+/, '')
  const parts = normalized.split('/').filter(Boolean)
  if (parts.length >= 2 && !KNOWN_TOP_LEVEL_DIRS.has(parts[0]) && KNOWN_TOP_LEVEL_DIRS.has(parts[1])) {
    return parts.slice(1).join('/')
  }
  return parts.join('/')
}

function convertCandidate(candidate, htmlRoot, rank) {
  const documentPath = stripSourcePrefix(mapHtmlSourcePathToAdoc(candidate.sourcePath, htmlRoot))
  return {
    rank,
    source_dir: documentPath.split('/')[0] || '',
    document_path: documentPath,
    viewer_url: normalizeSlashes(candidate.sourcePath),
    score: candidate.score,
    section_title: Array.isArray(candidate.headingHierarchy) && candidate.headingHierarchy.length > 0
      ? candidate.headingHierarchy[candidate.headingHierarchy.length - 1]
      : '',
  }
}

function collectIngestInputs(opts) {
  if (opts.manifest) {
    return loadManifestInputs(opts.manifest)
  }

  if (!opts.indexDir) {
    return []
  }

  return collectHtmlFiles(opts.indexDir).map((file) => ({
    title: basename(file),
    contentPath: file,
    sourcePath: file,
    fileType: '.html',
    sourceType: 'local',
    manifestPath: file,
  }))
}

async function main() {
  const opts = parseArgs(process.argv.slice(2))
  const cases = loadJsonLines(opts.cases)
  const selectedCases = opts.limit > 0 ? cases.slice(0, opts.limit) : cases
  const ingestInputs = collectIngestInputs(opts)
  const resolvedWorkspace = resolve(opts.workspace)
  const resolvedDataDir = resolve(opts.dataDir || resolve(resolvedWorkspace, '.opendocuments-stage6'))
  const configOverrides = buildConfigOverrides(opts)

  if (opts.resetDataDir && existsSync(resolvedDataDir)) {
    rmSync(resolvedDataDir, { recursive: true, force: true })
  }

  const bootstrapModuleUrl = pathToFileURL(resolve(opts.openDocumentsRoot, 'packages/server/dist/index.js')).href
  const coreModuleUrl = pathToFileURL(resolve(opts.openDocumentsRoot, 'packages/core/dist/index.js')).href
  const { bootstrap } = await import(bootstrapModuleUrl)
  const { getProfileConfig } = await import(coreModuleUrl)

  const ctx = await bootstrap({
    projectDir: resolvedWorkspace,
    dataDir: resolvedDataDir,
    configOverrides: configOverrides || undefined,
  })

  try {
    const failures = []
    const profileConfig = getProfileConfig(opts.profile, ctx.config?.rag?.custom)

    if (!opts.skipIngest && ingestInputs.length > 0) {
      let indexedCount = 0
      let skippedCount = 0

      for (const input of ingestInputs) {
        if (!existsSync(input.contentPath)) {
          failures.push({
            title: input.title,
            source_path: normalizeSlashes(input.sourcePath),
            content_path: normalizeSlashes(input.contentPath),
            error: 'missing content path',
          })
          continue
        }

        const content = readFileSync(input.contentPath, 'utf-8')
        const result = await ctx.pipeline.ingest({
          title: input.title,
          content,
          sourceType: input.sourceType,
          sourcePath: input.sourcePath,
          fileType: input.fileType,
        })

        if (result.status === 'indexed') {
          indexedCount += 1
        } else if (result.status === 'skipped') {
          skippedCount += 1
        } else if (result.status === 'error') {
          const document = ctx.store.getDocumentBySourcePath(input.sourcePath)
          failures.push({
            title: input.title,
            source_path: normalizeSlashes(input.sourcePath),
            content_path: normalizeSlashes(input.contentPath),
            manifest_path: normalizeSlashes(input.manifestPath),
            error: document?.error_message || 'unknown ingest error',
          })
        }

        if ((indexedCount + skippedCount + failures.length) % 25 === 0) {
          console.log(
            `[progress] processed ${indexedCount + skippedCount + failures.length}/${ingestInputs.length} inputs` +
            ` (indexed=${indexedCount}, skipped=${skippedCount}, failed=${failures.length})`,
          )
        }
      }

      console.log(
        `[ok] ingest completed for ${ingestInputs.length} inputs ` +
        `(indexed=${indexedCount}, skipped=${skippedCount}, failed=${failures.length})`,
      )

      if (opts.failuresOut) {
        mkdirSync(dirname(resolve(opts.failuresOut)), { recursive: true })
        writeFileSync(resolve(opts.failuresOut), JSON.stringify(failures, null, 2), 'utf-8')
      }
    } else if (opts.failuresOut) {
      mkdirSync(dirname(resolve(opts.failuresOut)), { recursive: true })
      writeFileSync(resolve(opts.failuresOut), JSON.stringify([], null, 2), 'utf-8')
    }

    const embedder = ctx.registry.getModels().find((model) => model.capabilities.embedding && model.embed)
    if (!embedder?.embed) {
      throw new Error('No embedding model available in OpenDocuments context')
    }

    if (opts.sampleQuery) {
      let answer = ''
      let sources = []
      if (opts.retrievalOnly) {
        const retrieved = await ctx.ragEngine.retrieveWithFeatures('sample-query', opts.sampleQuery, profileConfig)
        sources = retrieved.map((item, index) => convertCandidate(item, opts.htmlRoot, index + 1))
        answer = '[retrieval-only benchmark mode]'
      } else {
        for await (const event of ctx.ragEngine.queryStream({ query: opts.sampleQuery, profile: opts.profile })) {
          if (event.type === 'chunk') answer += event.data
          if (event.type === 'sources') {
            sources = event.data.map((item, index) => convertCandidate(item, opts.htmlRoot, index + 1))
          }
        }
      }
      if (opts.sampleOut) {
        mkdirSync(dirname(resolve(opts.sampleOut)), { recursive: true })
        writeFileSync(
          resolve(opts.sampleOut),
          JSON.stringify({ query: opts.sampleQuery, answer, sources }, null, 2),
          'utf-8',
        )
      }
      console.log(`[ok] sample query executed: ${opts.sampleQuery}`)
    }

    const lines = []

    for (const testCase of selectedCases) {
      const query = testCase.question_ko
      const embedResult = await embedder.embed([query])
      const denseResults = await ctx.store.searchChunks(embedResult.dense[0], opts.topK)
      const retrieved = opts.retrievalOnly
        ? await ctx.ragEngine.retrieveWithFeatures(`bench-${testCase.id}`, query, profileConfig)
        : (await ctx.ragEngine.query({ query, profile: opts.profile })).sources

      const retrievalCandidates = denseResults.map((item, index) => convertCandidate(item, opts.htmlRoot, index + 1))
      const rerankedCandidates = retrieved.map((item, index) => convertCandidate(item, opts.htmlRoot, index + 1))
      const citations = rerankedCandidates.map((item) => ({
        document_path: item.document_path,
        viewer_url: item.viewer_url,
        section_title: item.section_title,
      }))

      const clickThroughOk = rerankedCandidates.every((item) => extname(item.viewer_url).toLowerCase() === '.html')

      lines.push(JSON.stringify({
        benchmark_case_id: testCase.id,
        retrieval_candidates: retrievalCandidates,
        reranked_candidates: rerankedCandidates,
        citations,
        grounded_answer: rerankedCandidates.length > 0,
        click_through_ok: clickThroughOk,
      }))
    }

    mkdirSync(dirname(resolve(opts.output)), { recursive: true })
    writeFileSync(resolve(opts.output), `${lines.join('\n')}\n`, 'utf-8')
    console.log(`[ok] wrote ${selectedCases.length} Stage 6 result records to ${resolve(opts.output)}`)
  } finally {
    await ctx.shutdown()
  }
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})

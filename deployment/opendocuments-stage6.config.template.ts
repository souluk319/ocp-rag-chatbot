import { defineConfig } from 'opendocuments-core'

const requireEnv = (name: string) => {
  const value = process.env[name]?.trim()
  if (!value) {
    throw new Error(`Missing required env: ${name}`)
  }
  return value
}

export default defineConfig({
  workspace: 'ocp-stage6',
  mode: 'personal',

  model: {
    provider: 'openai',
    llm: requireEnv('OD_CHAT_MODEL'),
    embedding: requireEnv('OD_EMBEDDING_MODEL'),
    apiKey: requireEnv('OPENAI_API_KEY'),
    baseUrl: requireEnv('OPENAI_BASE_URL'),
    embeddingDimensions: Number.parseInt(requireEnv('OD_EMBEDDING_DIMENSIONS'), 10),
  },

  rag: {
    profile: 'precise',
  },

  parserFallbacks: {
    '.html': ['opendocuments-parser-html'],
  },

  storage: {
    db: 'sqlite',
    vectorDb: 'lancedb',
    dataDir: './.opendocuments-stage6',
  },
})

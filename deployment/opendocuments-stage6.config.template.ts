import { defineConfig } from 'opendocuments-core'

export default defineConfig({
  workspace: 'ocp-stage6',
  mode: 'personal',

  model: {
    provider: 'openai',
    llm: process.env.OD_CHAT_MODEL || 'Qwen/Qwen3.5-9B',
    embedding: process.env.OD_EMBEDDING_MODEL || 'paraphrase-multilingual-MiniLM-L12-v2',
    apiKey: process.env.OPENAI_API_KEY || 'dummy',
    baseUrl: process.env.OPENAI_BASE_URL || 'http://127.0.0.1:18080/v1',
    embeddingDimensions: 384,
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

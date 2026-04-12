export const RUNTIME_ORIGIN = (import.meta.env.VITE_RUNTIME_ORIGIN ?? '').trim().replace(/\/$/, '');
export const RUNTIME_EXTERNAL_ORIGIN = RUNTIME_ORIGIN || 'http://127.0.0.1:8765';

export interface LibraryBook {
  book_slug: string;
  title: string;
  grade: string;
  review_status: string;
  source_type: string;
  source_lane: string;
  section_count: number;
  code_block_count: number;
  viewer_path: string;
  source_url: string;
  updated_at: string;
}

export interface LibraryBucket {
  selected_dir: string;
  books: LibraryBook[];
}

export interface DataControlRoomSummary {
  known_book_count: number;
  approved_runtime_count: number;
  gold_book_count: number;
  manualbook_count: number;
  topic_playbook_count: number;
  derived_playbook_count: number;
  playable_asset_count: number;
  answer_pass_rate: number;
}

export interface DataControlRoomResponse {
  active_pack: {
    pack_label: string;
    ocp_version: string;
    docs_language: string;
    viewer_path_prefix: string;
  };
  summary: DataControlRoomSummary;
  known_books: LibraryBook[];
  gold_books: LibraryBook[];
  manualbooks: LibraryBucket;
  topic_playbooks: LibraryBucket;
  operation_playbooks: LibraryBucket;
  troubleshooting_playbooks: LibraryBucket;
  policy_overlay_books: LibraryBucket;
  synthesized_playbooks: LibraryBucket;
  source_of_truth_drift?: {
    status_alignment?: {
      mismatches?: string[];
    };
  };
}

export interface ChatCitation {
  index: number;
  book_slug: string;
  book_title?: string;
  section: string;
  viewer_path: string;
  source_label?: string;
  source_collection?: string;
  pack_label?: string;
}

export interface ChatTraceEvent {
  step: string;
  label: string;
  status: string;
  detail?: string;
  timestamp_ms?: number;
}

export interface ChatResponse {
  answer: string;
  citations: ChatCitation[];
  warnings: string[];
  session_id: string;
  suggested_queries: string[];
  pipeline_trace?: {
    events?: ChatTraceEvent[];
  };
}

export interface DerivedAsset {
  asset_slug: string;
  asset_kind: string;
  playbook_family: string;
  family_label: string;
  title: string;
  viewer_path: string;
  section_count: number;
  source_type: string;
  family_summary: string;
}

export interface CustomerPackDraft {
  draft_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  source_type: string;
  title: string;
  book_slug: string;
  pack_label: string;
  quality_status: string;
  quality_score: number;
  quality_summary: string;
  uploaded_file_name?: string;
  uploaded_byte_size?: number;
  capture_artifact_path?: string;
  playable_asset_count: number;
  derived_asset_count: number;
  derived_assets: DerivedAsset[];
}

export interface CustomerPackDraftListResponse {
  count: number;
  drafts: CustomerPackDraft[];
}

export interface CustomerPackBookSection {
  heading: string;
  section_path_label: string;
  viewer_path: string;
  text: string;
}

export interface CustomerPackBook {
  draft_id: string;
  title: string;
  target_viewer_path: string;
  quality_status: string;
  quality_score: number;
  quality_summary: string;
  playable_asset_count: number;
  derived_asset_count: number;
  derived_assets: DerivedAsset[];
  sections: CustomerPackBookSection[];
  pack_label: string;
  source_type: string;
}

export type RepositoryCategory =
  | 'Official Docs'
  | 'Enterprise Knowledge'
  | 'Operations Demo'
  | 'Troubleshooting';

export interface RepositoryDocsSignals {
  score: number;
  inspection_status: string;
  has_readme: boolean;
  has_docs_dir: boolean;
  has_demo_assets: boolean;
  doc_keyword_hits: number;
  troubleshooting_hits: number;
  demo_hits: number;
  entry_names: string[];
  summary: string;
}

export interface RepositorySearchResult {
  id: number;
  name: string;
  full_name: string;
  owner_login: string;
  html_url: string;
  description: string;
  stargazers_count: number;
  updated_at: string;
  language: string;
  default_branch: string;
  topics: string[];
  archived: boolean;
  docs_signals: RepositoryDocsSignals;
  suggested_category: RepositoryCategory;
  is_favorite: boolean;
  favorite_category: RepositoryCategory | '';
  ranking_score: number;
}

export interface RepositorySearchResponse {
  query: string;
  rewritten_query: string;
  count: number;
  auth_mode: 'token' | 'public';
  categories: RepositoryCategory[];
  results: RepositorySearchResult[];
}

export interface RepositoryFavorite extends Omit<RepositorySearchResult, 'is_favorite' | 'favorite_category' | 'archived' | 'ranking_score'> {
  favorite_category: RepositoryCategory;
  saved_at: string;
}

export interface RepositoryFavoritesResponse {
  count: number;
  categories: RepositoryCategory[];
  updated_at: string;
  items: RepositoryFavorite[];
  groups: Record<string, RepositoryFavorite[]>;
}

export interface SourceMetaResponse {
  book_slug: string;
  book_title: string;
  anchor: string;
  section: string;
  section_path: string[];
  section_path_label: string;
  source_url: string;
  viewer_path: string;
  section_match_exact: boolean;
  source_collection?: string;
  pack_label?: string;
}

export interface SessionSummary {
  session_id: string;
  session_name: string;
  turn_count: number;
  updated_at: string;
  first_query: string;
}

export interface SessionListResponse {
  sessions: SessionSummary[];
  count: number;
}

export interface SessionSnapshot {
  session_id: string;
  session_name: string;
  turns: Array<{ query: string; answer: string; turn_id: string; created_at: string }>;
  updated_at: string;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${RUNTIME_ORIGIN}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as { error?: string };
      if (payload.error) {
        message = payload.error;
      }
    } catch {
      // Keep default HTTP message.
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export function toRuntimeUrl(path: string): string {
  if (!path) {
    return '';
  }
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  return `${RUNTIME_ORIGIN}${path}`;
}

export async function loadDataControlRoom(): Promise<DataControlRoomResponse> {
  return requestJson<DataControlRoomResponse>('/api/data-control-room');
}

export async function searchRepositories(query: string, limit = 12): Promise<RepositorySearchResponse> {
  const params = new URLSearchParams({
    query,
    limit: String(limit),
  });
  return requestJson<RepositorySearchResponse>(`/api/repositories/search?${params.toString()}`);
}

export async function loadRepositoryFavorites(): Promise<RepositoryFavoritesResponse> {
  return requestJson<RepositoryFavoritesResponse>('/api/repositories/favorites');
}

export async function saveRepositoryFavorites(
  category: RepositoryCategory,
  repositories: RepositorySearchResult[],
): Promise<RepositoryFavoritesResponse> {
  return requestJson<RepositoryFavoritesResponse>('/api/repositories/favorites', {
    method: 'POST',
    body: JSON.stringify({ category, repositories }),
  });
}

export async function removeRepositoryFavorite(fullName: string): Promise<RepositoryFavoritesResponse> {
  return requestJson<RepositoryFavoritesResponse>('/api/repositories/favorites/remove', {
    method: 'POST',
    body: JSON.stringify({ full_name: fullName }),
  });
}

export async function sendChat(payload: {
  query: string;
  sessionId: string;
  mode?: string;
  selectedDraftIds?: string[];
  restrictUploadedSources?: boolean;
}): Promise<ChatResponse> {
  return requestJson<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      query: payload.query,
      session_id: payload.sessionId,
      mode: payload.mode ?? 'ops',
      selected_draft_ids: payload.selectedDraftIds ?? [],
      restrict_uploaded_sources: payload.restrictUploadedSources ?? false,
    }),
  });
}

export async function loadSourceMeta(viewerPath: string): Promise<SourceMetaResponse> {
  return requestJson<SourceMetaResponse>(`/api/source-meta?viewer_path=${encodeURIComponent(viewerPath)}`);
}

export async function listCustomerPackDrafts(): Promise<CustomerPackDraftListResponse> {
  return requestJson<CustomerPackDraftListResponse>('/api/customer-packs/drafts');
}

export async function loadCustomerPackDraft(draftId: string): Promise<CustomerPackDraft> {
  return requestJson<CustomerPackDraft>(`/api/customer-packs/drafts?draft_id=${encodeURIComponent(draftId)}`);
}

export async function loadCustomerPackBook(draftId: string): Promise<CustomerPackBook> {
  return requestJson<CustomerPackBook>(`/api/customer-packs/book?draft_id=${encodeURIComponent(draftId)}`);
}

function inferSourceType(file: File): string {
  const extension = file.name.split('.').pop()?.toLowerCase() ?? '';
  if (['md', 'markdown'].includes(extension)) {
    return 'md';
  }
  if (['adoc', 'asciidoc'].includes(extension)) {
    return 'asciidoc';
  }
  if (['txt', 'text'].includes(extension)) {
    return 'txt';
  }
  if (['docx'].includes(extension)) {
    return 'docx';
  }
  if (['pptx'].includes(extension)) {
    return 'pptx';
  }
  if (['xlsx'].includes(extension)) {
    return 'xlsx';
  }
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'].includes(extension)) {
    return 'image';
  }
  if (['pdf'].includes(extension)) {
    return 'pdf';
  }
  return 'web';
}

async function fileToBase64(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  let binary = '';
  const chunkSize = 0x8000;
  for (let index = 0; index < bytes.length; index += chunkSize) {
    const chunk = bytes.subarray(index, index + chunkSize);
    binary += String.fromCharCode(...chunk);
  }
  return btoa(binary);
}

export async function uploadCustomerPackDraft(file: File): Promise<CustomerPackDraft> {
  const payload = {
    source_type: inferSourceType(file),
    uri: file.name,
    title: file.name.replace(/\.[^.]+$/, ''),
    language_hint: 'ko',
    file_name: file.name,
    content_base64: await fileToBase64(file),
  };
  return requestJson<CustomerPackDraft>('/api/customer-packs/upload-draft', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function captureCustomerPackDraft(draftId: string): Promise<CustomerPackDraft> {
  return requestJson<CustomerPackDraft>('/api/customer-packs/capture', {
    method: 'POST',
    body: JSON.stringify({ draft_id: draftId }),
  });
}

export async function normalizeCustomerPackDraft(draftId: string): Promise<CustomerPackDraft> {
  return requestJson<CustomerPackDraft>('/api/customer-packs/normalize', {
    method: 'POST',
    body: JSON.stringify({ draft_id: draftId }),
  });
}

export async function listSessions(limit = 50): Promise<SessionListResponse> {
  return requestJson<SessionListResponse>(`/api/sessions?limit=${limit}`);
}

export async function loadSession(sessionId: string): Promise<SessionSnapshot> {
  return requestJson<SessionSnapshot>(`/api/sessions/load?session_id=${encodeURIComponent(sessionId)}`);
}

export async function deleteSession(sessionId: string): Promise<void> {
  await requestJson<{ success: boolean; session_id: string }>('/api/sessions/delete', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function deleteAllSessions(): Promise<number> {
  const payload = await requestJson<{ success: boolean; deleted_count: number }>('/api/sessions/delete-all', {
    method: 'POST',
    body: JSON.stringify({}),
  });
  return Number(payload.deleted_count || 0);
}

export async function deleteCustomerPackDraft(draftId: string): Promise<void> {
  await requestJson<{ success: boolean }>('/api/customer-packs/delete-draft', {
    method: 'POST',
    body: JSON.stringify({ draft_id: draftId }),
  });
}

export function formatBytes(byteSize?: number): string {
  if (!byteSize || Number.isNaN(byteSize)) {
    return '';
  }
  if (byteSize < 1024) {
    return `${byteSize} B`;
  }
  if (byteSize < 1024 * 1024) {
    return `${(byteSize / 1024).toFixed(1)} KB`;
  }
  return `${(byteSize / (1024 * 1024)).toFixed(1)} MB`;
}

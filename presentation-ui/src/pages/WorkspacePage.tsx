import { useEffect, useMemo, useRef, useState, type ChangeEvent, type KeyboardEvent } from 'react';
import {
  Group,
  Panel,
  Separator,
} from 'react-resizable-panels';
import { Link } from 'react-router-dom';
import {
  Upload,
  FileText,
  ChevronDown,
  ChevronRight,
  Send,
  BookOpen,
  Cpu,
  Database,
  ArrowRight,
  Sparkles,
  Link as LinkIcon,
} from 'lucide-react';
import gsap from 'gsap';
import './WorkspacePage.css';
import {
  type ChatCitation,
  type CustomerPackBook,
  type CustomerPackDraft,
  type DerivedAsset,
  type LibraryBook,
  type SourceMetaResponse,
  RUNTIME_EXTERNAL_ORIGIN,
  captureCustomerPackDraft,
  formatBytes,
  listCustomerPackDrafts,
  loadCustomerPackBook,
  loadCustomerPackDraft,
  loadDataControlRoom,
  loadSourceMeta,
  normalizeCustomerPackDraft,
  sendChat,
  toRuntimeUrl,
  uploadCustomerPackDraft,
} from '../lib/runtimeApi';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: ChatCitation[];
}

interface SourceEntry {
  id: string;
  kind: 'manual' | 'draft';
  name: string;
  meta: string;
  viewerPath?: string;
  book?: LibraryBook;
  draft?: CustomerPackDraft;
}

type PreviewState =
  | { kind: 'empty' }
  | { kind: 'loading'; title: string }
  | {
      kind: 'viewer';
      title: string;
      subtitle: string;
      meta?: SourceMetaResponse;
      viewerUrl: string;
    }
  | {
      kind: 'draft';
      title: string;
      subtitle: string;
      draft: CustomerPackDraft;
      book?: CustomerPackBook;
      viewerUrl: string;
      derivedAssets: DerivedAsset[];
    };

function makeId(prefix: string): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function formatBookMeta(book: LibraryBook): string {
  const pieces = [book.grade, book.source_type].filter(Boolean);
  return pieces.join(' · ');
}

function formatDraftMeta(draft: CustomerPackDraft): string {
  const size = formatBytes(draft.uploaded_byte_size);
  const pieces = [draft.status, draft.source_type.toUpperCase()];
  if (size) {
    pieces.push(size);
  }
  return pieces.filter(Boolean).join(' · ');
}

function extractDraftIdFromViewerPath(viewerPath: string): string | null {
  const match = viewerPath.match(/\/playbooks\/customer-packs\/([^/]+)/);
  return match?.[1] ?? null;
}

export default function WorkspacePage() {
  const [packLabel, setPackLabel] = useState('OpenShift 4.20');
  const [manualBooks, setManualBooks] = useState<LibraryBook[]>([]);
  const [drafts, setDrafts] = useState<CustomerPackDraft[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [sessionId, setSessionId] = useState(() => makeId('workspace-session'));
  const [activeSourceId, setActiveSourceId] = useState<string | null>(null);
  const [preview, setPreview] = useState<PreviewState>({ kind: 'empty' });
  const [isUploading, setIsUploading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [isNormalizing, setIsNormalizing] = useState(false);
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>({
    manuals: true,
    drafts: true,
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.workspace-panel-item', {
        opacity: 0,
        y: 20,
        stagger: 0.1,
        duration: 0.8,
        ease: 'power3.out',
        delay: 0.2,
      });

      gsap.from('.bokeh-bg', {
        opacity: 0,
        scale: 0.8,
        duration: 2,
        ease: 'power2.out',
      });
    }, containerRef);
    return () => ctx.revert();
  }, []);

  function toggleSection(sectionId: string): void {
    setCollapsedSections((prev) => ({
      ...prev,
      [sectionId]: !prev[sectionId],
    }));
  }

  useEffect(() => {
    let cancelled = false;

    const bootstrap = async () => {
      try {
        const [room, draftPayload] = await Promise.all([
          loadDataControlRoom(),
          listCustomerPackDrafts(),
        ]);
        if (cancelled) {
          return;
        }

        const runtimeBooks = Array.isArray(room.gold_books) ? room.gold_books : [];
        const nextDrafts = draftPayload.drafts ?? [];

        setPackLabel(room.active_pack.pack_label || 'OpenShift 4.20');
        setManualBooks(runtimeBooks);
        setDrafts(nextDrafts);

        if (nextDrafts[0]) {
          void openDraftPreview(nextDrafts[0].draft_id, nextDrafts);
          return;
        }
        if (runtimeBooks[0]?.viewer_path) {
          void openManualPreview(runtimeBooks[0]);
        }
      } catch (error) {
        console.error(error);
      }
    };

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const manualSources = useMemo<SourceEntry[]>(
    () =>
      manualBooks.slice(0, 16).map((book) => ({
        id: `manual:${book.book_slug}`,
        kind: 'manual',
        name: book.title,
        meta: formatBookMeta(book),
        viewerPath: book.viewer_path,
        book,
      })),
    [manualBooks],
  );

  const draftSources = useMemo<SourceEntry[]>(
    () =>
      drafts.map((draft) => ({
        id: `draft:${draft.draft_id}`,
        kind: 'draft',
        name: draft.title,
        meta: formatDraftMeta(draft),
        draft,
      })),
    [drafts],
  );

  const activeDraft = useMemo(
    () => drafts.find((draft) => activeSourceId === `draft:${draft.draft_id}`) ?? null,
    [activeSourceId, drafts],
  );

  function mergeDraft(nextDraft: CustomerPackDraft, currentDrafts: CustomerPackDraft[] = drafts): CustomerPackDraft[] {
    return [nextDraft, ...currentDrafts.filter((draft) => draft.draft_id !== nextDraft.draft_id)];
  }

  async function openViewerPreview(viewerPath: string, title: string, sourceId?: string): Promise<void> {
    if (!viewerPath) {
      setPreview({ kind: 'empty' });
      return;
    }
    setActiveSourceId(sourceId ?? `viewer:${viewerPath}`);
    setPreview({ kind: 'loading', title });
    try {
      const meta = await loadSourceMeta(viewerPath);
      setPreview({
        kind: 'viewer',
        title: meta.book_title || title,
        subtitle: meta.section_path_label || meta.section || meta.source_url || '',
        meta,
        viewerUrl: toRuntimeUrl(meta.viewer_path || viewerPath),
      });
    } catch {
      setPreview({
        kind: 'viewer',
        title,
        subtitle: '',
        viewerUrl: toRuntimeUrl(viewerPath),
      });
    }
  }

  async function openManualPreview(book: LibraryBook): Promise<void> {
    await openViewerPreview(book.viewer_path, book.title, `manual:${book.book_slug}`);
  }

  async function openDraftPreview(
    draftId: string,
    currentDrafts: CustomerPackDraft[] = drafts,
    preferredViewerPath = '',
  ): Promise<void> {
    setActiveSourceId(`draft:${draftId}`);
    setPreview({ kind: 'loading', title: 'Customer Pack' });

    const loadedDraft = await loadCustomerPackDraft(draftId);
    const mergedDrafts = mergeDraft(loadedDraft, currentDrafts);
    setDrafts(mergedDrafts);

    let loadedBook: CustomerPackBook | undefined;
    let viewerUrl = '';

    if (loadedDraft.status === 'normalized') {
      loadedBook = await loadCustomerPackBook(draftId);
      viewerUrl = toRuntimeUrl(preferredViewerPath || loadedBook.target_viewer_path);
    } else if (loadedDraft.capture_artifact_path) {
      viewerUrl = toRuntimeUrl(`/api/customer-packs/captured?draft_id=${encodeURIComponent(draftId)}`);
    }

    setPreview({
      kind: 'draft',
      title: loadedDraft.title,
      subtitle: `${loadedDraft.pack_label} · ${loadedDraft.quality_status}`,
      draft: loadedDraft,
      book: loadedBook,
      viewerUrl,
      derivedAssets: loadedBook?.derived_assets ?? loadedDraft.derived_assets ?? [],
    });
  }

  function animatePreviewPanel(): void {
    gsap.fromTo(
      '.source-viewer-content',
      { backgroundColor: 'rgba(0, 209, 255, 0.08)' },
      { backgroundColor: 'transparent', duration: 0.8 },
    );
  }

  async function handleSourceClick(source: SourceEntry): Promise<void> {
    try {
      if (source.kind === 'manual' && source.book) {
        await openManualPreview(source.book);
      }
      if (source.kind === 'draft' && source.draft) {
        await openDraftPreview(source.draft.draft_id);
      }
      animatePreviewPanel();
    } catch (error) {
      console.error(error);
      window.alert(error instanceof Error ? error.message : '문서를 여는 중 오류가 발생했습니다.');
    }
  }

  async function handleCitationClick(citation: ChatCitation): Promise<void> {
    try {
      const draftId = extractDraftIdFromViewerPath(citation.viewer_path);
      if (draftId) {
        await openDraftPreview(draftId, drafts, citation.viewer_path);
      } else {
        await openViewerPreview(
          citation.viewer_path,
          citation.source_label || citation.book_title || citation.section,
        );
      }
      animatePreviewPanel();
    } catch (error) {
      console.error(error);
      window.alert(error instanceof Error ? error.message : '참조 원문을 여는 중 오류가 발생했습니다.');
    }
  }

  async function handleUploadSelection(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setIsUploading(true);
    try {
      const uploaded = await uploadCustomerPackDraft(file);
      setDrafts((current) => mergeDraft(uploaded, current));
      await openDraftPreview(uploaded.draft_id, mergeDraft(uploaded));
    } catch (error) {
      console.error(error);
      window.alert(error instanceof Error ? error.message : '업로드 중 오류가 발생했습니다.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }

  async function handleCapture(): Promise<void> {
    if (!activeDraft || isCapturing) {
      return;
    }
    setIsCapturing(true);
    try {
      const captured = await captureCustomerPackDraft(activeDraft.draft_id);
      setDrafts((current) => mergeDraft(captured, current));
      await openDraftPreview(captured.draft_id, mergeDraft(captured));
    } catch (error) {
      console.error(error);
      window.alert(error instanceof Error ? error.message : 'Analyze Content 중 오류가 발생했습니다.');
    } finally {
      setIsCapturing(false);
    }
  }

  async function handleNormalize(): Promise<void> {
    if (!activeDraft || isNormalizing) {
      return;
    }
    setIsNormalizing(true);
    try {
      const normalized = await normalizeCustomerPackDraft(activeDraft.draft_id);
      setDrafts((current) => mergeDraft(normalized, current));
      await openDraftPreview(normalized.draft_id, mergeDraft(normalized));
    } catch (error) {
      console.error(error);
      window.alert(error instanceof Error ? error.message : 'Create Playbook 중 오류가 발생했습니다.');
    } finally {
      setIsNormalizing(false);
    }
  }

  async function handleSend(): Promise<void> {
    const trimmed = query.trim();
    if (!trimmed || isSending) {
      return;
    }

    const nextUserMessage: Message = {
      id: makeId('user'),
      role: 'user',
      content: trimmed,
    };
    setMessages((current) => [...current, nextUserMessage]);
    setQuery('');
    setIsSending(true);

    try {
      const response = await sendChat({
        query: trimmed,
        sessionId,
        mode: 'ops',
        selectedDraftIds: activeDraft ? [activeDraft.draft_id] : [],
        restrictUploadedSources: Boolean(activeDraft),
      });

      setSessionId(response.session_id || sessionId);
      setMessages((current) => [
        ...current,
        {
          id: makeId('assistant'),
          role: 'assistant',
          content: response.answer,
          citations: response.citations ?? [],
        },
      ]);

      if (response.citations?.[0]) {
        await handleCitationClick(response.citations[0]);
      }
    } catch (error) {
      console.error(error);
      window.alert(error instanceof Error ? error.message : '질문 처리 중 오류가 발생했습니다.');
    } finally {
      setIsSending(false);
    }
  }

  function handleInputKeyDown(event: KeyboardEvent<HTMLInputElement>): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
  }

  function handleOpenDataSituationRoom(): void {
    window.open(`${RUNTIME_EXTERNAL_ORIGIN}/data-situation-room`, '_blank', 'noopener,noreferrer');
  }

  function handleDerivedAssetOpen(asset: DerivedAsset): void {
    if (preview.kind !== 'draft') {
      return;
    }
    setPreview({
      ...preview,
      subtitle: `${preview.draft.pack_label} · ${asset.family_label}`,
      viewerUrl: toRuntimeUrl(asset.viewer_path),
    });
    animatePreviewPanel();
  }

  const canCapture = Boolean(activeDraft) && !isCapturing;
  const canNormalize = Boolean(activeDraft) && !isNormalizing;

  return (
    <div className="workspace-wrapper" ref={containerRef}>
      <div className="bokeh-bg bokeh-1"></div>
      <div className="bokeh-bg bokeh-2"></div>

      <header className="workspace-nav">
        <Link to="/" className="nav-left nav-logo-link">
          <div className="logo-icon">
            <Sparkles size={20} />
          </div>
          <span className="logo-text">Playbook Studio <span className="text-dim">/ Workspace</span></span>
        </Link>
        <div className="nav-right">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>{packLabel} Active</span>
          </div>
          <button className="nav-btn" onClick={handleOpenDataSituationRoom} type="button">Export Library</button>
        </div>
      </header>

      <main className="workspace-content">
        <Group orientation="horizontal" className="main-panel-group">
          <Panel defaultSize={20} minSize={15} className="workspace-panel-item">
            <div className="panel-inner glass-panel no-border-radius-right">
              <div className="panel-header">
                <div className="header-icon"><Database size={18} /></div>
                <h3>Knowledge Source</h3>
              </div>

              <div className="source-picker-container">
                <div className="picker-label">Enterprise Pack</div>
                <div className="custom-select">
                  <span>{packLabel}</span>
                  <ChevronDown size={16} />
                </div>
              </div>

              <input
                ref={fileInputRef}
                className="file-input-hidden"
                type="file"
                onChange={(event) => {
                  void handleUploadSelection(event);
                }}
              />

              <div className="upload-zone" onClick={() => fileInputRef.current?.click()}>
                {isUploading ? (
                  <div className="loading-spinner-small"></div>
                ) : (
                  <>
                    <Upload size={24} className="upload-icon" />
                    <p>Click to add or drag file</p>
                    <span className="text-dim">PDF, Markdown, DOCX, PPTX, XLSX</span>
                  </>
                )}
              </div>

              <div className="source-list">
                <div className={`source-section ${collapsedSections.manuals ? 'collapsed' : ''}`}>
                  <button className="section-header-btn" onClick={() => toggleSection('manuals')} type="button">
                    <div className="header-label-group">
                      {collapsedSections.manuals ? <ChevronRight size={14} /> : <ChevronDown size={14} />}
                      <span className="list-title">Runtime Manual Books</span>
                    </div>
                    <span className="item-count-badge">{manualSources.length}</span>
                  </button>
                  
                  {!collapsedSections.manuals && (
                    <div className="section-items-container">
                      {manualSources.map((file) => (
                        <div
                          key={file.id}
                          className={`source-item ${activeSourceId === file.id ? 'selected' : ''}`}
                          onClick={() => { void handleSourceClick(file); }}
                        >
                          <div className="item-main">
                            <FileText size={16} className="file-icon" />
                            <span className="file-name">{file.name}</span>
                          </div>
                          <div className="item-meta">{file.meta}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className={`source-section ${collapsedSections.drafts ? 'collapsed' : ''}`}>
                  <button className="section-header-btn" onClick={() => toggleSection('drafts')} type="button">
                    <div className="header-label-group">
                      {collapsedSections.drafts ? <ChevronRight size={14} /> : <ChevronDown size={14} />}
                      <span className="list-title">Uploaded Drafts</span>
                    </div>
                    <span className="item-count-badge">{draftSources.length}</span>
                  </button>
                  
                  {!collapsedSections.drafts && (
                    <div className="section-items-container">
                      {draftSources.map((file) => (
                        <div
                          key={file.id}
                          className={`source-item ${activeSourceId === file.id ? 'selected' : ''}`}
                          onClick={() => { void handleSourceClick(file); }}
                        >
                          <div className="item-main">
                            <FileText size={16} className="file-icon" />
                            <span className="file-name">{file.name}</span>
                          </div>
                          <div className="item-meta">{file.meta}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Panel>

          <Separator className="custom-resize-handle">
            <div className="handle-visual" />
          </Separator>

          <Panel defaultSize={45} minSize={30} className="workspace-panel-item">
            <div className="panel-inner chat-area">
              <div className="chat-messages">
                {messages.map((message) => (
                  <div key={message.id} className={`message-row ${message.role}`}>
                    <div className="message-bubble glass-panel">
                      <div className="message-content">{message.content}</div>
                      {message.citations && message.citations.length > 0 && (
                        <div className="message-tags">
                          {message.citations.map((citation) => (
                            <button
                              key={`${message.id}-${citation.index}`}
                              className="citation-tag"
                              onClick={() => { void handleCitationClick(citation); }}
                              type="button"
                            >
                              <LinkIcon size={12} />
                              {citation.source_label || citation.book_title || citation.section}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="chat-input-wrapper">
                <div className="input-container glass-panel">
                  <input
                    type="text"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    onKeyDown={handleInputKeyDown}
                    placeholder="질문을 입력하거나 문서를 탐색하세요..."
                    disabled={isSending}
                  />
                  <button className="send-btn" onClick={() => { void handleSend(); }} type="button" disabled={isSending}>
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </div>
          </Panel>

          <Separator className="custom-resize-handle">
            <div className="handle-visual" />
          </Separator>

          <Panel defaultSize={35} minSize={20} className="workspace-panel-item">
            <div className="panel-inner glass-panel no-border-radius-left">
              <div className="panel-header">
                <div className="header-icon"><BookOpen size={18} /></div>
                <h3>Knowledge Studio</h3>
              </div>

              <div className="source-viewer-content">
                {preview.kind === 'empty' && (
                  <div className="empty-state">
                    <div className="empty-icon"><BookOpen size={48} className="text-dim" /></div>
                    <h4>선택된 문서가 없습니다</h4>
                    <p>왼쪽 문서를 선택하거나 채팅의 참조 태그를 눌러 원문을 확인하세요.</p>
                  </div>
                )}

                {preview.kind === 'loading' && (
                  <div className="empty-state">
                    <div className="loading-spinner-small"></div>
                    <h4>{preview.title}</h4>
                    <p>콘텐츠를 불러오는 중입니다.</p>
                  </div>
                )}

                {preview.kind === 'viewer' && (
                  <div className="document-page animate-in">
                    <div className="doc-header">
                      <span className="doc-kicker">{preview.meta?.pack_label || 'Source Viewer'}</span>
                      <h2>{preview.title}</h2>
                    </div>
                    {preview.subtitle && <p className="doc-summary">{preview.subtitle}</p>}
                    <div className="doc-metadata">
                      {preview.meta?.source_url && (
                        <a href={preview.meta.source_url} className="doc-inline-link" target="_blank" rel="noreferrer">
                          원문 열기
                        </a>
                      )}
                    </div>
                    {preview.viewerUrl && (
                      <iframe
                        title={preview.title}
                        className="source-preview-frame"
                        src={preview.viewerUrl}
                      />
                    )}
                  </div>
                )}

                {preview.kind === 'draft' && (
                  <div className="document-page animate-in">
                    <div className="doc-header">
                      <span className="doc-kicker">Customer Pack</span>
                      <h2>{preview.title}</h2>
                    </div>
                    <p className="doc-summary">{preview.subtitle}</p>
                    <div className="doc-metadata">
                      <span>Quality {preview.draft.quality_score}</span>
                      <span>{preview.draft.playable_asset_count} assets</span>
                    </div>
                    {preview.derivedAssets.length > 0 && (
                      <div className="doc-chip-row">
                        {preview.derivedAssets.map((asset) => (
                          <button
                            key={asset.asset_slug}
                            className="citation-tag"
                            onClick={() => handleDerivedAssetOpen(asset)}
                            type="button"
                          >
                            <LinkIcon size={12} />
                            {asset.family_label}
                          </button>
                        ))}
                      </div>
                    )}
                    {preview.viewerUrl ? (
                      <iframe
                        title={preview.title}
                        className="source-preview-frame"
                        src={preview.viewerUrl}
                      />
                    ) : (
                      <div className="doc-section">
                        <h4>Draft Status</h4>
                        <p>{preview.draft.status}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="panel-footer">
                <button className="outline-btn" onClick={() => { void handleCapture(); }} type="button" disabled={!canCapture}>
                  <Cpu size={14} />
                  <span>{isCapturing ? 'Analyzing...' : 'Analyze Content'}</span>
                </button>
                <button className="primary-btn" onClick={() => { void handleNormalize(); }} type="button" disabled={!canNormalize}>
                  <span>{isNormalizing ? 'Creating...' : 'Create Playbook'}</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </Panel>
        </Group>
      </main>
    </div>
  );
}

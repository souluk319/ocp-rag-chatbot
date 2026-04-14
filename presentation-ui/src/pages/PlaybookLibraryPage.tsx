import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Activity,
  Database,
  Layers,
  Globe,
  Cpu,
  ShieldCheck,
  Search,
  FileText,
  UploadCloud,
  Clock,
  Loader2,
  AlertCircle,
  HardDrive,
  BookOpen,
  Trash2,
  CheckCircle2,
  Star,
  ExternalLink,
  BookmarkPlus,
  BookmarkCheck,
  X,
} from 'lucide-react';
import gsap from 'gsap';
import './PlaybookLibraryPage.css';
import {
  type CustomerPackDraft,
  type DataControlRoomResponse,
  type LibraryBook,
  type RepositoryCategory,
  type RepositoryFavorite,
  type RepositorySearchResult,
  uploadCustomerPackDraft,
  captureCustomerPackDraft,
  normalizeCustomerPackDraft,
  loadDataControlRoom,
  listCustomerPackDrafts,
  deleteCustomerPackDraft,
  loadCustomerPackBook,
  loadRepositoryFavorites,
  removeRepositoryFavorite,
  saveRepositoryFavorites,
  searchRepositories,
  toRuntimeUrl,
  formatBytes,
} from '../lib/runtimeApi';

type PipelineStage = 'idle' | 'uploading' | 'capturing' | 'normalizing' | 'done' | 'error';

interface LogEntry {
  time: string;
  tag: 'success' | 'info' | 'error' | 'warn';
  msg: string;
}

const REPOSITORY_CATEGORIES: RepositoryCategory[] = [
  'Official Docs',
  'Enterprise Knowledge',
  'Operations Demo',
  'Troubleshooting',
];

const SUPPORTED_FORMATS = [
  { ext: 'PDF', via: 'MarkItDown' },
  { ext: 'DOCX', via: 'MarkItDown' },
  { ext: 'PPTX', via: 'MarkItDown' },
  { ext: 'XLSX', via: 'MarkItDown' },
  { ext: 'MD', via: 'Native' },
  { ext: 'TXT', via: 'Native' },
  { ext: 'AsciiDoc', via: 'Native' },
  { ext: 'HTML', via: 'Native' },
  { ext: 'Image', via: 'OCR' },
];

function nowTime(): string {
  const d = new Date();
  return [d.getHours(), d.getMinutes(), d.getSeconds()]
    .map((n) => String(n).padStart(2, '0'))
    .join(':');
}

function statusColor(status: string): string {
  switch (status) {
    case 'normalized': return 'green';
    case 'captured': return 'cyan';
    case 'planned': return 'gray';
    default: return 'red';
  }
}

const PlaybookLibraryPage: React.FC = () => {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<'monitoring' | 'repository'>('monitoring');
  const [pipelineStage, setPipelineStage] = useState<PipelineStage>('idle');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [errorMsg, setErrorMsg] = useState('');
  const [currentFile, setCurrentFile] = useState('');
  const [controlRoom, setControlRoom] = useState<DataControlRoomResponse | null>(null);
  const [drafts, setDrafts] = useState<CustomerPackDraft[]>([]);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [previewDraft, setPreviewDraft] = useState<CustomerPackDraft | null>(null);
  const [metricPopover, setMetricPopover] = useState<{ title: string; books: LibraryBook[] } | null>(null);
  const [previewViewerUrl, setPreviewViewerUrl] = useState('');
  const [previewLoading, setPreviewLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [repositoryResults, setRepositoryResults] = useState<RepositorySearchResult[]>([]);
  const [repositoryFavorites, setRepositoryFavorites] = useState<RepositoryFavorite[]>([]);
  const [activeRepositoryCategory, setActiveRepositoryCategory] = useState<RepositoryCategory>('Official Docs');
  const [selectedRepositoryNames, setSelectedRepositoryNames] = useState<string[]>([]);
  const [repositoryStage, setRepositoryStage] = useState<'idle' | 'loading' | 'done' | 'error'>('idle');
  const [repositoryError, setRepositoryError] = useState('');
  const [repositoryMeta, setRepositoryMeta] = useState<{ rewrittenQuery: string; authMode: 'token' | 'public' }>({
    rewrittenQuery: '',
    authMode: 'public',
  });
  const [savingFavorites, setSavingFavorites] = useState(false);
  const [removingFavoriteName, setRemovingFavoriteName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pipelineRef = useRef<HTMLDivElement>(null);

  const addLog = (tag: LogEntry['tag'], msg: string) => {
    setLogs((prev) => [{ time: nowTime(), tag, msg }, ...prev].slice(0, 10));
  };

  const refreshRepositoryFavorites = useCallback(() => {
    loadRepositoryFavorites()
      .then((payload) => setRepositoryFavorites(payload.items))
      .catch(() => setRepositoryFavorites([]));
  }, []);

  const refreshData = useCallback(() => {
    loadDataControlRoom().then(setControlRoom).catch(() => { });
    listCustomerPackDrafts().then((res) => setDrafts(res.drafts)).catch(() => { });
    refreshRepositoryFavorites();
  }, [refreshRepositoryFavorites]);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.header-content', { opacity: 0, y: -20, duration: 0.8, ease: 'power3.out' });
      gsap.from('.metric-card', {
        opacity: 0, y: 20, stagger: 0.1, duration: 0.8, ease: 'power3.out', delay: 0.2,
      });
    });
    return () => ctx.revert();
  }, []);

  useEffect(() => {
    if (!pipelineRef.current) return;
    const steps = pipelineRef.current.querySelectorAll('.pipeline-step');
    const connectors = pipelineRef.current.querySelectorAll('.pipeline-connector');

    const stageIndex = { idle: -1, uploading: 0, capturing: 1, normalizing: 2, done: 3, error: -1 }[pipelineStage];

    steps.forEach((step, i) => {
      step.classList.toggle('completed', i < stageIndex);
      step.classList.toggle('active', i === stageIndex);
      step.classList.toggle('final', pipelineStage === 'done' && i === 3);
    });

    connectors.forEach((conn, i) => {
      conn.classList.toggle('filled', i < stageIndex);
      conn.classList.toggle('flowing', i === stageIndex - 1 || (pipelineStage === 'done' && i === 2));
    });

    if (stageIndex >= 0 && steps[stageIndex]) {
      gsap.fromTo(
        steps[stageIndex].querySelector('.step-icon'),
        { scale: 0.8, opacity: 0.5 },
        { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(1.7)' },
      );
    }
  }, [pipelineStage]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = '';

    setErrorMsg('');
    setCurrentFile(file.name);
    let draft: CustomerPackDraft;

    try {
      setPipelineStage('uploading');
      addLog('info', `Uploading '${file.name}'...`);
      draft = await uploadCustomerPackDraft(file);
      addLog('success', `'${file.name}' uploaded → draft ${draft.draft_id}`);

      setPipelineStage('capturing');
      addLog('info', `Capturing source artifact (${draft.source_type.toUpperCase()})...`);
      draft = await captureCustomerPackDraft(draft.draft_id);
      addLog('success', `Artifact captured for '${draft.title}'`);

      setPipelineStage('normalizing');
      const backend = ['pdf', 'docx', 'pptx', 'xlsx'].includes(draft.source_type)
        ? 'MarkItDown' : 'Native parser';
      addLog('info', `Normalizing via ${backend} → canonical sections...`);
      draft = await normalizeCustomerPackDraft(draft.draft_id);

      const qualityLine = draft.quality_score > 0
        ? ` (quality: ${draft.quality_score}/100 — ${draft.quality_status})`
        : '';
      addLog('success', `Normalized: ${draft.playable_asset_count} playable assets, ${draft.derived_asset_count} derived${qualityLine}`);

      setPipelineStage('done');
      addLog('success', `'${draft.title}' ready in library.`);
      refreshData();
      setTimeout(() => { setPipelineStage('idle'); setCurrentFile(''); }, 6000);
    } catch (err: any) {
      const msg = err?.message || 'Unknown error';
      setPipelineStage('error');
      setErrorMsg(msg);
      addLog('error', `Pipeline failed: ${msg}`);
      setTimeout(() => { setPipelineStage('idle'); setCurrentFile(''); }, 5000);
    }
  };

  const handleDelete = async (draftId: string, title: string, skipConfirm = false): Promise<boolean> => {
    if (!skipConfirm && !confirm(`'${title}' 초안을 삭제하시겠습니까?`)) return false;
    setDeletingId(draftId);
    try {
      await deleteCustomerPackDraft(draftId);
      setDrafts((prev) => prev.filter((d) => d.draft_id !== draftId));
      addLog('success', `Deleted draft '${title}'`);
      refreshData();
      return true;
    } catch (err) {
      console.error('[delete-draft] error:', err);
      addLog('error', `Failed to delete '${title}'`);
      return false;
    } finally {
      setDeletingId(null);
    }
  };

  const handleRepositorySearch = async () => {
    const normalizedQuery = searchQuery.trim();
    if (!normalizedQuery) {
      setRepositoryStage('idle');
      setRepositoryError('');
      setRepositoryResults([]);
      setSelectedRepositoryNames([]);
      return;
    }
    setRepositoryStage('loading');
    setRepositoryError('');
    try {
      const payload = await searchRepositories(normalizedQuery, 12);
      setRepositoryResults(payload.results);
      setRepositoryMeta({
        rewrittenQuery: payload.rewritten_query,
        authMode: payload.auth_mode,
      });
      setSelectedRepositoryNames([]);
      setRepositoryStage('done');
      addLog('info', `Repository search '${normalizedQuery}' → ${payload.count} matches`);
    } catch (err: any) {
      const msg = err?.message || 'Repository search failed';
      setRepositoryStage('error');
      setRepositoryError(msg);
      setRepositoryResults([]);
      addLog('error', `Repository search failed: ${msg}`);
    }
  };

  const handleRepositorySubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await handleRepositorySearch();
  };

  const toggleRepositorySelection = (fullName: string) => {
    setSelectedRepositoryNames((prev) =>
      prev.includes(fullName)
        ? prev.filter((value) => value !== fullName)
        : [...prev, fullName]
    );
  };

  const handleSaveSelectedRepositories = async () => {
    const selectedRepositories = repositoryResults.filter((item) => selectedRepositoryNames.includes(item.full_name));
    if (selectedRepositories.length === 0) {
      return;
    }
    setSavingFavorites(true);
    try {
      const payload = await saveRepositoryFavorites(activeRepositoryCategory, selectedRepositories);
      setRepositoryFavorites(payload.items);
      setRepositoryResults((prev) =>
        prev.map((item) =>
          selectedRepositoryNames.includes(item.full_name)
            ? { ...item, is_favorite: true, favorite_category: activeRepositoryCategory }
            : item
        )
      );
      addLog('success', `${selectedRepositories.length} repositories saved to ${activeRepositoryCategory}`);
      setSelectedRepositoryNames([]);
    } catch (err: any) {
      const msg = err?.message || 'Favorite save failed';
      setRepositoryError(msg);
      addLog('error', `Favorite save failed: ${msg}`);
    } finally {
      setSavingFavorites(false);
    }
  };

  const handleRemoveFavorite = async (fullName: string) => {
    setRemovingFavoriteName(fullName);
    try {
      const payload = await removeRepositoryFavorite(fullName);
      setRepositoryFavorites(payload.items);
      setRepositoryResults((prev) =>
        prev.map((item) =>
          item.full_name === fullName
            ? { ...item, is_favorite: false, favorite_category: '' }
            : item
        )
      );
      addLog('info', `Removed favorite ${fullName}`);
    } catch (err: any) {
      const msg = err?.message || 'Favorite remove failed';
      setRepositoryError(msg);
      addLog('error', `Favorite remove failed: ${msg}`);
    } finally {
      setRemovingFavoriteName(null);
    }
  };

  const openPreview = async (draft: CustomerPackDraft) => {
    setPreviewDraft(draft);
    setPreviewViewerUrl('');
    setPreviewLoading(true);

    try {
      if (draft.status === 'normalized') {
        const book = await loadCustomerPackBook(draft.draft_id);
        setPreviewViewerUrl(toRuntimeUrl(book.target_viewer_path));
      } else if (draft.capture_artifact_path) {
        setPreviewViewerUrl(toRuntimeUrl(`/api/customer-packs/captured?draft_id=${encodeURIComponent(draft.draft_id)}`));
      }
    } catch {
      // viewer URL stays empty — fallback message shown
    } finally {
      setPreviewLoading(false);
    }
  };

  const closePreview = () => {
    setPreviewDraft(null);
    setPreviewViewerUrl('');
  };

  const openMetricPopover = (kind: 'known' | 'approved' | 'manual' | 'candidate' | 'derived') => {
    if (!controlRoom) return;
    const cr = controlRoom;
    let title = '';
    let books: LibraryBook[] = [];
    switch (kind) {
      case 'known':
        title = 'Known Source Books';
        books = [...(cr.known_books ?? [])];
        break;
      case 'approved':
        title = 'Approved Runtime Books';
        books = [...(cr.gold_books ?? [])];
        break;
      case 'manual':
        title = 'Materialized Manual Books';
        books = [...(cr.manualbooks?.books ?? [])];
        break;
      case 'candidate':
        title = 'Gold Candidate Books';
        books = [...(cr.gold_candidate_books?.books ?? [])];
        break;
      case 'derived':
        title = 'Derived Playbooks';
        books = [
          ...(cr.topic_playbooks?.books ?? []),
          ...(cr.operation_playbooks?.books ?? []),
          ...(cr.troubleshooting_playbooks?.books ?? []),
          ...(cr.synthesized_playbooks?.books ?? []),
          ...(cr.policy_overlay_books?.books ?? []),
        ];
        break;
    }
    setMetricPopover({ title, books });
  };

  const stageLabel = (stage: PipelineStage) => {
    switch (stage) {
      case 'uploading': return 'Uploading...';
      case 'capturing': return 'Capturing Artifact...';
      case 'normalizing': return 'Normalizing...';
      case 'done': return 'Pipeline Complete';
      case 'error': return 'Pipeline Failed';
      default: return 'Engine Idle';
    }
  };

  const isProcessing = ['uploading', 'capturing', 'normalizing'].includes(pipelineStage);

  const summary = controlRoom?.summary;
  const knownSourceBooks = summary?.known_book_count ?? controlRoom?.known_books?.length ?? 0;
  const approvedRuntimeBooks = summary?.approved_runtime_count ?? summary?.gold_book_count ?? controlRoom?.gold_books?.length ?? 0;
  const materializedManualBooks = summary?.manualbook_count ?? controlRoom?.manualbooks?.books?.length ?? 0;
  const goldCandidateBooks = summary?.gold_candidate_book_count ?? controlRoom?.gold_candidate_books?.books?.length ?? 0;
  const derivedPlaybooks = summary?.derived_playbook_count ?? 0;
  const hasMetricSourceDrift = Boolean(controlRoom?.source_of_truth_drift?.status_alignment?.mismatches?.length);
  const groupedFavorites = REPOSITORY_CATEGORIES.map((category) => ({
    category,
    items: repositoryFavorites.filter((item) => item.favorite_category === category),
  })).filter((group) => group.items.length > 0);

  return (
    <div className="library-wrapper">
      <div className="bokeh-bg bokeh-1"></div>
      <div className="bokeh-bg bokeh-2"></div>

      <header className="library-header">
        <div className="header-container">
          <div className="header-content">
            <button className="back-btn" onClick={() => navigate('/workspace')}>
              <ArrowLeft size={20} />
            </button>
            <div className="header-text">
              <h1>Playbook Library</h1>
              <p className="text-muted">Control Tower & Asset Repository</p>
            </div>
          </div>

          <div className="header-actions">
            <div className="view-toggle">
              <button
                className={viewMode === 'monitoring' ? 'active' : ''}
                onClick={() => setViewMode('monitoring')}
              >
                <Activity size={16} />
                <span>Control Tower</span>
              </button>
              <button
                className={viewMode === 'repository' ? 'active' : ''}
                onClick={() => setViewMode('repository')}
              >
                <Database size={16} />
                <span>Repository</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="library-main">
        {viewMode === 'monitoring' ? (
          <div className="monitoring-view">
            {/* Real Metrics */}
            <section className="metrics-grid">
              <div className="metric-card metric-clickable" onClick={() => openMetricPopover('known')}>
                <div className="metric-icon"><Globe size={24} /></div>
                <div className="metric-data">
                  <h3>{knownSourceBooks.toLocaleString()}</h3>
                  <p>Known Source Books</p>
                </div>
                <div className="metric-status online">Catalog</div>
              </div>
              <div className="metric-card metric-clickable" onClick={() => openMetricPopover('approved')}>
                <div className="metric-icon"><ShieldCheck size={24} /></div>
                <div className="metric-data">
                  <h3>{approvedRuntimeBooks.toLocaleString()}</h3>
                  <p>Approved Runtime Books</p>
                </div>
                <div className="metric-trend positive">
                  <BookOpen size={14} /> <span>Current</span>
                </div>
              </div>
              <div className="metric-card metric-clickable" onClick={() => openMetricPopover('manual')}>
                <div className="metric-icon"><Layers size={24} /></div>
                <div className="metric-data">
                  <h3>{materializedManualBooks.toLocaleString()}</h3>
                  <p>Materialized Manual Books</p>
                </div>
                <div className="metric-status online">Materialized</div>
              </div>
              <div className="metric-card metric-clickable" onClick={() => openMetricPopover('candidate')}>
                <div className="metric-icon"><BookOpen size={24} /></div>
                <div className="metric-data">
                  <h3>{goldCandidateBooks.toLocaleString()}</h3>
                  <p>Gold Candidate Books</p>
                </div>
                <div className="metric-status online">Candidate</div>
              </div>
              <div className="metric-card metric-clickable" onClick={() => openMetricPopover('derived')}>
                <div className="metric-icon"><Activity size={24} /></div>
                <div className="metric-data">
                  <h3>{derivedPlaybooks.toLocaleString()}</h3>
                  <p>Derived Playbooks</p>
                </div>
                <div className="metric-status optimized">Generated</div>
              </div>
            </section>

            {hasMetricSourceDrift && (
              <div className="truth-banner">
                <AlertCircle size={16} />
                <span>Stale gate snapshot was detected. This view is showing current source approval and materialized storage counts.</span>
              </div>
            )}

            {/* Pipeline Visualization */}
            <section className="pipeline-section box-container">
              <div className="section-header">
                <div className="section-header-left">
                  <h2>Knowledge Ingestion Pipeline</h2>
                  <input
                    ref={fileInputRef}
                    type="file"
                    hidden
                    accept=".pdf,.md,.docx,.pptx,.xlsx,.txt,.adoc,.html,.png,.jpg,.jpeg,.webp"
                    onChange={handleUpload}
                  />
                  <button
                    className="upload-trigger-btn"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isProcessing}
                  >
                    {isProcessing ? <Loader2 size={16} className="spin-icon" /> : <UploadCloud size={16} />}
                    <span>{isProcessing ? 'Processing...' : 'Upload File'}</span>
                  </button>
                </div>
                <div className={`pipeline-status ${pipelineStage === 'error' ? 'error' : pipelineStage === 'done' ? 'done' : ''}`}>
                  {pipelineStage === 'error' ? (
                    <AlertCircle size={14} className="status-icon-error" />
                  ) : isProcessing ? (
                    <Loader2 size={14} className="spin-icon" />
                  ) : (
                    <div className={`status-dot ${pipelineStage === 'done' ? 'done' : 'pulsing'}`}></div>
                  )}
                  <span>{stageLabel(pipelineStage)}</span>
                </div>
              </div>

              <div className="format-strip">
                <span className="format-label">Powered by MarkItDown</span>
                <div className="format-tags">
                  {SUPPORTED_FORMATS.map((f) => (
                    <span key={f.ext} className={`format-tag ${f.via === 'MarkItDown' ? 'markitdown' : f.via === 'OCR' ? 'ocr' : ''}`}>
                      {f.ext}
                    </span>
                  ))}
                </div>
              </div>

              {currentFile && isProcessing && (
                <div className="current-file-banner">
                  <FileText size={14} />
                  <span>{currentFile}</span>
                </div>
              )}

              {errorMsg && (
                <div className="pipeline-error-banner">
                  <AlertCircle size={14} />
                  <span>{errorMsg}</span>
                </div>
              )}

              <div className="pipeline-visualizer" ref={pipelineRef}>
                <div className="pipeline-step">
                  <div className="step-badge">Upload</div>
                  <div className="step-icon">
                    {pipelineStage === 'uploading' ? <Loader2 className="spin-icon" /> : <UploadCloud />}
                  </div>
                  <div className="step-info">
                    <h4>Source Intake</h4>
                    <p>File → Base64 → Draft Record</p>
                  </div>
                </div>

                <div className="pipeline-connector"><div className="flow-particle"></div></div>

                <div className="pipeline-step">
                  <div className="step-badge">Capture</div>
                  <div className="step-icon">
                    {pipelineStage === 'capturing' ? <Loader2 className="spin-icon" /> : <HardDrive />}
                  </div>
                  <div className="step-info">
                    <h4>Artifact Capture</h4>
                    <p>Source Materialization</p>
                  </div>
                </div>

                <div className="pipeline-connector"><div className="flow-particle"></div></div>

                <div className="pipeline-step">
                  <div className="step-badge">Normalize</div>
                  <div className="step-icon">
                    {pipelineStage === 'normalizing' ? <Loader2 className="spin-icon" /> : <Cpu />}
                  </div>
                  <div className="step-info">
                    <h4>MarkItDown + Normalize</h4>
                    <p>Sections · Quality · Playbooks</p>
                  </div>
                </div>

                <div className="pipeline-connector"><div className="flow-particle"></div></div>

                <div className="pipeline-step">
                  <div className="step-badge">Ready</div>
                  <div className="step-icon"><BookOpen /></div>
                  <div className="step-info">
                    <h4>Library Ready</h4>
                    <p>5 Playbook Families</p>
                  </div>
                </div>
              </div>

              <div className="pipeline-details">
                <div className="log-container">
                  <div className="log-header">Recent Processing Logs</div>
                  {logs.length === 0 && (
                    <div className="log-empty">No activity yet — upload a file to start.</div>
                  )}
                  {logs.map((log, i) => (
                    <div className="log-item" key={i}>
                      <span className="log-time">{log.time}</span>
                      <span className={`log-tag tag-${log.tag}`}>{log.tag.toUpperCase()}</span>
                      <span className="log-msg">{log.msg}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Draft Management */}
            {drafts.length > 0 && (
              <section className="draft-management box-container">
                <div className="section-header">
                  <h2>Uploaded Drafts ({drafts.length})</h2>
                </div>
                <div className="draft-grid">
                  {drafts.map((draft) => (
                    <div className="draft-card" key={draft.draft_id} onClick={() => openPreview(draft)} style={{ cursor: 'pointer' }}>
                      <div className="draft-card-top">
                        <FileText size={18} className="draft-file-icon" />
                        <span className={`draft-status-badge status-${statusColor(draft.status)}`}>
                          {draft.status}
                        </span>
                      </div>
                      <h4 className="draft-title">{draft.title}</h4>
                      <div className="draft-meta">
                        <span className="draft-type">{draft.source_type.toUpperCase()}</span>
                        {draft.uploaded_byte_size ? (
                          <span>{formatBytes(draft.uploaded_byte_size)}</span>
                        ) : null}
                        {draft.quality_score > 0 && (
                          <span className="draft-quality">Q:{draft.quality_score}</span>
                        )}
                      </div>
                      {draft.derived_asset_count > 0 && (
                        <div className="draft-assets">
                          <CheckCircle2 size={12} />
                          <span>{draft.playable_asset_count} playable · {draft.derived_asset_count} derived</span>
                        </div>
                      )}
                      <div className="draft-card-footer">
                        <span className="draft-date">
                          <Clock size={12} />
                          {new Date(draft.created_at).toLocaleDateString()}
                        </span>
                        <button
                          className="draft-delete-btn"
                          onClick={(e) => { e.stopPropagation(); handleDelete(draft.draft_id, draft.title, true); }}
                          disabled={deletingId === draft.draft_id}
                          title="Delete draft"
                        >
                          {deletingId === draft.draft_id ? <Loader2 size={14} className="spin-icon" /> : <Trash2 size={14} />}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        ) : (
          <div className="repository-view">
            <section className="repo-panel box-container">
              <div className="repo-panel-header">
                <div>
                  <h2>GitHub Repository Search</h2>
                  <p className="text-muted">
                    선택한 repo를 플레이북 소스 후보로 저장 할 수 있습니다.
                  </p>
                </div>
                <div className="repo-panel-badge">
                  <Database size={14} />
                  <span>{repositoryMeta.authMode === 'token' ? 'Authenticated Search' : 'Public Search'}</span>
                </div>
              </div>

              <form className="repo-search-form" onSubmit={handleRepositorySubmit}>
                <div className="search-bar repo-search-bar">
                  <Search size={18} />
                  <input
                    type="text"
                    placeholder="예: argocd, openshift virtualization, grafana"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  className="repo-search-btn"
                  disabled={repositoryStage === 'loading'}
                >
                  {repositoryStage === 'loading' ? <Loader2 size={16} className="spin-icon" /> : <Search size={16} />}
                  <span>{repositoryStage === 'loading' ? 'Searching...' : 'Search Repositories'}</span>
                </button>
              </form>

              <div className="repo-toolbar">
                <div className="repo-toolbar-copy">
                  <span className="repo-toolbar-label">Save To</span>
                  <span className="repo-toolbar-hint">선택한 결과를 어느 source lane으로 관리할지 고릅니다.</span>
                </div>
                <div className="filter-group repo-category-group">
                  {REPOSITORY_CATEGORIES.map((category) => (
                    <button
                      type="button"
                      key={category}
                      className={activeRepositoryCategory === category ? 'active' : ''}
                      onClick={() => setActiveRepositoryCategory(category)}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>

              {(repositoryMeta.rewrittenQuery || repositoryError) && (
                <div className="repo-meta-strip">
                  {repositoryMeta.rewrittenQuery ? (
                    <span>
                      rewritten query: <code>{repositoryMeta.rewrittenQuery}</code>
                    </span>
                  ) : null}
                  {repositoryError ? <span className="repo-error-text">{repositoryError}</span> : null}
                </div>
              )}

              <div className="repo-results-actions">
                <div className="repo-results-summary">
                  <span>{repositoryResults.length} results</span>
                  <span>·</span>
                  <span>{selectedRepositoryNames.length} selected</span>
                </div>
                <button
                  type="button"
                  className="repo-save-btn"
                  onClick={handleSaveSelectedRepositories}
                  disabled={savingFavorites || selectedRepositoryNames.length === 0}
                >
                  {savingFavorites ? <Loader2 size={16} className="spin-icon" /> : <BookmarkPlus size={16} />}
                  <span>{savingFavorites ? 'Saving...' : `Save to ${activeRepositoryCategory}`}</span>
                </button>
              </div>

              {repositoryResults.length === 0 ? (
                <div className="repo-empty">
                  <Database size={48} />
                  <p>
                    {repositoryStage === 'idle'
                      ? '검색어를 입력하면 GitHub에서 문서 가능성이 높은 repo를 재정렬해 보여줍니다.'
                      : '검색 결과가 없습니다.'}
                  </p>
                </div>
              ) : (
                <div className="repo-grid">
                  {repositoryResults.map((repository) => (
                    <div className="repo-card glass-panel" key={repository.full_name}>
                      <div className="card-header repo-card-header">
                        <label className="repo-select">
                          <input
                            type="checkbox"
                            checked={selectedRepositoryNames.includes(repository.full_name)}
                            onChange={() => toggleRepositorySelection(repository.full_name)}
                          />
                          <span>{repository.full_name}</span>
                        </label>
                        <div className="repo-card-actions">
                          {repository.is_favorite ? (
                            <span className="favorite-pill">
                              <BookmarkCheck size={12} />
                              {repository.favorite_category}
                            </span>
                          ) : (
                            <span className="status-pill" data-status="processing">
                              suggested: {repository.suggested_category}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="card-body">
                        <h4>{repository.name}</h4>
                        <p className="text-muted">{repository.description || 'No description available.'}</p>
                      </div>

                      <div className="repo-signal-row">
                        <span className="repo-signal-score">docs score {repository.docs_signals.score}</span>
                        <span>{repository.docs_signals.summary}</span>
                      </div>

                      {repository.topics.length > 0 && (
                        <div className="derived-list">
                          {repository.topics.slice(0, 4).map((topic) => (
                            <span key={topic} className="derived-tag">{topic}</span>
                          ))}
                        </div>
                      )}

                      <div className="card-footer repo-card-footer">
                        <div className="meta-info repo-meta-info">
                          <span><Star size={12} /> {repository.stargazers_count.toLocaleString()}</span>
                          {repository.language ? <span>{repository.language}</span> : null}
                          <span><Clock size={12} /> {new Date(repository.updated_at).toLocaleDateString()}</span>
                        </div>
                        <a
                          className="repo-link-btn"
                          href={repository.html_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          <ExternalLink size={14} />
                          <span>Open</span>
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="repo-favorites-section box-container">
              <div className="section-header">
                <h2>Saved Repository Sources</h2>
              </div>

              {groupedFavorites.length === 0 ? (
                <div className="repo-empty repo-favorites-empty">
                  <BookmarkPlus size={40} />
                  <p>아직 저장된 repository source가 없습니다.</p>
                </div>
              ) : (
                <div className="favorites-groups">
                  {groupedFavorites.map((group) => (
                    <div className="favorite-group" key={group.category}>
                      <div className="favorite-group-header">
                        <h3>{group.category}</h3>
                        <span>{group.items.length}</span>
                      </div>
                      <div className="favorite-group-list">
                        {group.items.map((favorite) => (
                          <div className="favorite-item" key={favorite.full_name}>
                            <div className="favorite-item-main">
                              <div className="favorite-item-title">
                                <Database size={14} />
                                <span>{favorite.full_name}</span>
                              </div>
                              <p className="text-muted">{favorite.description || 'No description available.'}</p>
                            </div>
                            <div className="favorite-item-actions">
                              <a
                                className="repo-link-btn"
                                href={favorite.html_url}
                                target="_blank"
                                rel="noreferrer"
                              >
                                <ExternalLink size={14} />
                                <span>Open</span>
                              </a>
                              <button
                                type="button"
                                className="favorite-remove-btn"
                                onClick={() => handleRemoveFavorite(favorite.full_name)}
                                disabled={removingFavoriteName === favorite.full_name}
                              >
                                {removingFavoriteName === favorite.full_name ? (
                                  <Loader2 size={14} className="spin-icon" />
                                ) : (
                                  <Trash2 size={14} />
                                )}
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}
      </main>

      {/* Preview Popover */}
      {previewDraft && (
        <div className="preview-overlay" onClick={closePreview}>
          <div className="preview-popover" onClick={(e) => e.stopPropagation()}>
            <div className="preview-header">
              <div className="preview-header-left">
                <h3>{previewDraft.title}</h3>
                <div className="preview-header-meta">
                  <span className={`draft-status-badge status-${statusColor(previewDraft.status)}`}>{previewDraft.status}</span>
                  <span>{previewDraft.source_type.toUpperCase()}</span>
                  {previewDraft.uploaded_byte_size ? <span>{formatBytes(previewDraft.uploaded_byte_size)}</span> : null}
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  className="preview-delete-btn"
                  onClick={async () => { const ok = await handleDelete(previewDraft.draft_id, previewDraft.title, true); if (ok) closePreview(); }}
                  disabled={deletingId === previewDraft.draft_id}
                  title="Delete"
                >
                  {deletingId === previewDraft.draft_id ? <Loader2 size={16} className="spin-icon" /> : <Trash2 size={16} />}
                </button>
                <button className="preview-close-btn" onClick={closePreview}><X size={18} /></button>
              </div>
            </div>
            <div className="preview-body">
              {previewLoading && (
                <div className="preview-loading"><Loader2 size={20} className="spin-icon" /> Loading viewer...</div>
              )}
              {!previewLoading && previewViewerUrl && (
                <iframe
                  title={previewDraft.title}
                  className="preview-viewer-frame"
                  src={previewViewerUrl}
                />
              )}
              {!previewLoading && !previewViewerUrl && (
                <div className="preview-no-sections">
                  {previewDraft.status === 'planned'
                    ? '아직 캡처되지 않은 초안입니다. Capture/Normalize 후 미리보기를 확인할 수 있습니다.'
                    : '뷰어를 불러올 수 없습니다.'}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Metric Detail Popover */}
      {metricPopover && (
        <div className="preview-overlay" onClick={() => setMetricPopover(null)}>
          <div className="preview-popover" onClick={(e) => e.stopPropagation()}>
            <div className="preview-header">
              <div className="preview-header-left">
                <h3>{metricPopover.title}</h3>
                <div className="preview-header-meta">
                  <span>{metricPopover.books.length} books</span>
                </div>
              </div>
              <button className="preview-close-btn" onClick={() => setMetricPopover(null)}><X size={18} /></button>
            </div>
            <div className="metric-popover-body">
              {metricPopover.books.length === 0 ? (
                <div className="preview-no-sections">등록된 북이 없습니다.</div>
              ) : (
                <div className="metric-book-list">
                  {metricPopover.books.map((book) => (
                    <div className="metric-book-row" key={book.book_slug}>
                      <FileText size={16} className="metric-book-icon" />
                      <div className="metric-book-info">
                        <span className="metric-book-title">{book.title}</span>
                        <span className="metric-book-meta">
                          {book.source_lane} · {book.section_count} sections · {book.grade}
                        </span>
                      </div>
                      <span className={`metric-book-status ${book.review_status === 'approved' ? 'approved' : ''}`}>
                        {book.review_status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlaybookLibraryPage;

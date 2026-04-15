import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  ArrowLeft,
  Activity,
  Database,
  Layers,
  Globe,
  Cpu,
  ShieldCheck,
  ShieldAlert,
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
  type BuyerPacket,
  type DataControlRoomResponse,
  type LibraryBook,
  type RepositoryCategory,
  type RepositoryFavorite,
  type RepositorySearchResult,
  type RepositoryUnansweredItem,
  uploadCustomerPackDraft,
  captureCustomerPackDraft,
  normalizeCustomerPackDraft,
  loadDataControlRoom,
  listCustomerPackDrafts,
  deleteCustomerPackDraft,
  loadCustomerPackBook,
  loadRepositoryFavorites,
  loadRepositoryUnanswered,
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

function customerPackBookTruth(book?: LibraryBook | null): string {
  if (!book) {
    return '';
  }
  return book.boundary_badge || book.runtime_truth_label || '';
}

function customerPackBookEvidenceBits(book?: LibraryBook | null): string[] {
  if (!book) {
    return [];
  }
  const bits = [
    book.approval_state ? `approval ${book.approval_state}` : '',
    book.publication_state ? `publication ${book.publication_state}` : '',
    book.source_lane ? `lane ${book.source_lane}` : '',
    book.parser_backend ? `parser ${book.parser_backend}` : '',
  ];
  return bits.filter(Boolean);
}

const PlaybookLibraryPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
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
  const [buyerPacketPopover, setBuyerPacketPopover] = useState<{ title: string; packets: BuyerPacket[] } | null>(null);
  const [bookViewer, setBookViewer] = useState<LibraryBook | null>(null);
  const [previewViewerUrl, setPreviewViewerUrl] = useState('');
  const [previewLoading, setPreviewLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [repositoryResults, setRepositoryResults] = useState<RepositorySearchResult[]>([]);
  const [repositoryFavorites, setRepositoryFavorites] = useState<RepositoryFavorite[]>([]);
  const [repositoryUnanswered, setRepositoryUnanswered] = useState<RepositoryUnansweredItem[]>([]);
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
  const repositoryAutoloadKeyRef = useRef('');

  const addLog = (tag: LogEntry['tag'], msg: string) => {
    setLogs((prev) => [{ time: nowTime(), tag, msg }, ...prev].slice(0, 10));
  };

  const refreshRepositoryFavorites = useCallback(() => {
    loadRepositoryFavorites()
      .then((payload) => setRepositoryFavorites(payload.items))
      .catch(() => setRepositoryFavorites([]));
  }, []);

  const refreshRepositoryUnanswered = useCallback(() => {
    loadRepositoryUnanswered(20)
      .then((payload) => setRepositoryUnanswered(payload.items))
      .catch(() => setRepositoryUnanswered([]));
  }, []);

  const refreshData = useCallback(() => {
    loadDataControlRoom().then(setControlRoom).catch(() => { });
    listCustomerPackDrafts().then((res) => setDrafts(res.drafts)).catch(() => { });
    refreshRepositoryFavorites();
    refreshRepositoryUnanswered();
  }, [refreshRepositoryFavorites, refreshRepositoryUnanswered]);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  useEffect(() => {
    const requestedView = (searchParams.get('view') || '').trim();
    const requestedQuery = (searchParams.get('q') || '').trim();
    if (requestedView === 'repository') {
      setViewMode('repository');
    }
    if (!requestedQuery) {
      repositoryAutoloadKeyRef.current = '';
      return;
    }
    const autoloadKey = `${requestedView}|${requestedQuery}`;
    if (repositoryAutoloadKeyRef.current === autoloadKey) {
      return;
    }
    repositoryAutoloadKeyRef.current = autoloadKey;
    setSearchQuery(requestedQuery);
    setRepositoryStage('loading');
    setRepositoryError('');
    searchRepositories(requestedQuery, 12)
      .then((payload) => {
        setRepositoryResults(payload.results);
        setRepositoryMeta({
          rewrittenQuery: payload.rewritten_query,
          authMode: payload.auth_mode,
        });
        setSelectedRepositoryNames([]);
        setRepositoryStage('done');
        addLog('info', `Repository search '${requestedQuery}' → ${payload.count} matches`);
      })
      .catch((err: any) => {
        const msg = err?.message || 'Repository search failed';
        setRepositoryStage('error');
        setRepositoryError(msg);
        setRepositoryResults([]);
        addLog('error', `Repository search failed: ${msg}`);
      });
  }, [searchParams]);

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
    const normalizedQuery = searchQuery.trim();
    setSearchParams(normalizedQuery ? { view: 'repository', q: normalizedQuery } : { view: 'repository' });
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

  const openMetricPopover = (kind: 'known' | 'approved' | 'manual' | 'customerPack' | 'candidate' | 'wikiRuntime' | 'navBacklog' | 'wikiUsage' | 'buyerGate' | 'buyerPackets' | 'derived') => {
    if (!controlRoom) return;
    const cr = controlRoom;
    let title = '';
    let books: LibraryBook[] = [];
    let packets: BuyerPacket[] = [];
    switch (kind) {
      case 'known':
        title = 'Full Source Catalog';
        books = [...(cr.known_books ?? [])];
        break;
      case 'approved':
        title = 'Operational Shortlist';
        books = [...(cr.gold_books ?? [])];
        break;
      case 'manual':
        title = 'Catalog Playbooks';
        books = [...(cr.manualbooks?.books ?? [])];
        break;
      case 'customerPack':
        title = 'Customer Pack Runtime Books';
        books = [...(cr.customer_pack_runtime_books?.books ?? [])];
        break;
      case 'wikiRuntime':
        title = 'Live Operational Wiki';
        books = [...(cr.approved_wiki_runtime_books?.books ?? [])];
        break;
      case 'navBacklog':
        title = 'Wiki Navigation Backlog';
        books = [...(cr.wiki_navigation_backlog?.books ?? [])];
        break;
      case 'wikiUsage':
        title = 'Usage';
        books = [...(cr.wiki_usage_signals?.books ?? [])];
        break;
      case 'buyerGate':
        title = 'Release Gate Surface';
        books = [...(cr.buyer_demo_gate?.books ?? [])];
        break;
      case 'buyerPackets':
        title = 'Release Candidate Packets';
        packets = [...(cr.buyer_packet_bundle?.books ?? [])];
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
    if (kind === 'buyerPackets') {
      setBuyerPacketPopover({ title, packets });
      return;
    }
    setMetricPopover({ title, books });
  };

  const openBuyerPacket = (packet: BuyerPacket) => {
    setBuyerPacketPopover(null);
    setBookViewer({
      book_slug: packet.book_slug,
      title: packet.title,
      grade: 'Release Packet',
      review_status: packet.review_status,
      source_type: 'buyer_packet_bundle',
      source_lane: 'buyer_packet_bundle',
      section_count: 1,
      code_block_count: 0,
      viewer_path: packet.viewer_path,
      source_url: packet.source_url,
      updated_at: '',
      approval_state: packet.approval_state,
      publication_state: packet.publication_state,
      runtime_truth_label: packet.runtime_truth_label,
      boundary_badge: packet.boundary_badge || 'Release Packet',
    });
  };

  const openReleaseCandidateFreeze = () => {
    if (releaseCandidatePacket) {
      openBuyerPacket(releaseCandidatePacket);
    }
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
  const customerPackRuntimeBooks = summary?.customer_pack_runtime_book_count ?? controlRoom?.customer_pack_runtime_books?.books?.length ?? 0;
  const approvedWikiRuntimeBooks = summary?.approved_wiki_runtime_book_count ?? controlRoom?.approved_wiki_runtime_books?.books?.length ?? 0;
  const allOperationalWikiBooks = [...(controlRoom?.approved_wiki_runtime_books?.books ?? [])];
  const operationalWikiBooks = allOperationalWikiBooks.slice(0, 8);
  const wikiNavigationBacklog = summary?.wiki_navigation_backlog_count ?? controlRoom?.wiki_navigation_backlog?.books?.length ?? 0;
  const wikiUsageSignals = summary?.wiki_usage_signal_count ?? controlRoom?.wiki_usage_signals?.books?.length ?? 0;
  const buyerDemoGate = summary?.buyer_demo_gate_count ?? controlRoom?.buyer_demo_gate?.books?.length ?? 0;
  const buyerPacketBundle = summary?.buyer_packet_bundle_count ?? controlRoom?.buyer_packet_bundle?.books?.length ?? 0;
  const releaseCandidateFreeze = controlRoom?.release_candidate_freeze;
  const releaseCandidatePacket = controlRoom?.buyer_packet_bundle?.books?.find(
    (packet) => packet.book_slug === 'buyer_packet__release-candidate-freeze',
  ) ?? null;
  const derivedPlaybooks = summary?.derived_playbook_count ?? 0;
  const hasMetricSourceDrift = Boolean(controlRoom?.source_of_truth_drift?.status_alignment?.mismatches?.length);
  const gate = controlRoom?.gate;
  const ownerDemo = controlRoom?.owner_demo_rehearsal;
  const gateReasons = [
    ...((gate?.reasons ?? []).slice(0, 3)),
    ...((gate?.summary?.failed_validation_checks ?? []).slice(0, 2)),
    ...((gate?.summary?.failed_data_quality_checks ?? []).slice(0, 2)),
  ].filter(Boolean).slice(0, 3);
  const ownerDemoPassRate = typeof ownerDemo?.owner_critical_scenario_pass_rate === 'number'
    ? Math.round(ownerDemo.owner_critical_scenario_pass_rate * 100)
    : 0;
  const ownerDemoBlockerCopy = ownerDemo?.blockers?.length
    ? ownerDemo.blockers.join(' · ')
    : 'No current owner-demo blockers';
  const gateBannerCopy = gate?.release_blocking
    ? `Release blocked · ${gate?.status ?? 'unknown'}`
    : `Release gate · ${gate?.status ?? 'unknown'}`;
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
            <button className="back-btn" onClick={() => navigate('/studio')}>
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
            {operationalWikiBooks.length > 0 && (
              <section className="operational-shelf box-container">
                <div className="operational-shelf-header">
                  <div>
                    <span className="operational-shelf-eyebrow">Operational Wiki</span>
                    <h2>바로 읽을 수 있는 운영 위키</h2>
                    <p>지금 제품 표면에서 바로 여는 핵심 운영 문서 묶음입니다.</p>
                  </div>
                  <button
                    type="button"
                    className="operational-shelf-link"
                    onClick={() => openMetricPopover('wikiRuntime')}
                  >
                    전체 29권 보기
                  </button>
                </div>
                <div className="operational-shelf-grid">
                  {operationalWikiBooks.map((book) => (
                    <button
                      key={book.book_slug}
                      type="button"
                      className="operational-book-card"
                      onClick={() => setBookViewer(book)}
                    >
                      <span className="operational-book-badge">Live Wiki</span>
                      <strong>{book.title}</strong>
                      <span>{book.book_slug.replace(/_/g, ' ')}</span>
                    </button>
                  ))}
                </div>
              </section>
            )}

            {allOperationalWikiBooks.length > 0 && (
              <section className="operational-library box-container">
                <div className="operational-library-header">
                  <div>
                    <span className="operational-library-eyebrow">Operational Library</span>
                    <h2>운영 위키 29권</h2>
                  </div>
                  <span className="operational-library-count">{approvedWikiRuntimeBooks.toLocaleString()} books</span>
                </div>
                <div className="operational-library-grid">
                  {allOperationalWikiBooks.map((book) => (
                    <button
                      key={`library-${book.book_slug}`}
                      type="button"
                      className="operational-library-card"
                      onClick={() => setBookViewer(book)}
                    >
                      <span className="operational-library-card-badge">Live Wiki</span>
                      <strong>{book.title}</strong>
                      <span>{book.book_slug.replace(/_/g, ' ')}</span>
                    </button>
                  ))}
                </div>
              </section>
            )}

            {releaseCandidateFreeze?.exists && (
              <section className="release-freeze-hero">
                <div className="release-freeze-hero-copy">
                  <span className="release-freeze-eyebrow">Current Freeze</span>
                  <h2>{releaseCandidateFreeze.title}</h2>
                  <p>{releaseCandidateFreeze.close || releaseCandidateFreeze.commercial_truth}</p>
                  <div className="release-freeze-meta">
                    <span>{releaseCandidateFreeze.current_stage || 'paid_poc_candidate'}</span>
                    <span>{releaseCandidateFreeze.runtime_count} runtime books</span>
                    <span>
                      owner demo {releaseCandidateFreeze.owner_demo_pass_count}/{releaseCandidateFreeze.owner_demo_scenario_count}
                    </span>
                    <span>{releaseCandidateFreeze.release_blocker_count} blockers</span>
                  </div>
                </div>
                <div className="release-freeze-hero-actions">
                  <button
                    type="button"
                    className="release-freeze-primary-btn"
                    onClick={openReleaseCandidateFreeze}
                    disabled={!releaseCandidatePacket}
                  >
                    <FileText size={16} />
                    <span>Open Packet</span>
                  </button>
                  <button
                    type="button"
                    className="release-freeze-secondary-btn"
                    onClick={() => openMetricPopover('buyerPackets')}
                  >
                    <Layers size={16} />
                    <span>Packets</span>
                  </button>
                </div>
              </section>
            )}

            {(gate || hasMetricSourceDrift) && (
              <div className="truth-banner">
                <AlertCircle size={16} />
                <div className="truth-banner-copy">
                  {gate && (
                    <>
                      <strong>{gateBannerCopy}</strong>
                      <span>{gateReasons.length > 0 ? gateReasons.join(' · ') : 'Aligned with current runtime evidence.'}</span>
                    </>
                  )}
                  {ownerDemo && (
                    <span>
                      Owner demo {ownerDemo.pass_count}/{ownerDemo.scenario_count} · {ownerDemoBlockerCopy}
                    </span>
                  )}
                  {hasMetricSourceDrift && (
                    <span>Current approval and storage counts are shown.</span>
                  )}
                </div>
              </div>
            )}

            <section className="metrics-grid metrics-grid-primary">
              <div className="metric-card metric-card-priority metric-clickable" onClick={() => openMetricPopover('known')}>
                <div className="metric-icon"><Globe size={24} /></div>
                <div className="metric-data">
                  <h3>{knownSourceBooks.toLocaleString()}</h3>
                  <p>Full Source Catalog</p>
                </div>
                <div className="metric-status online">Catalog</div>
              </div>
              <div className="metric-card metric-card-priority metric-clickable" onClick={() => openMetricPopover('approved')}>
                <div className="metric-icon"><ShieldCheck size={24} /></div>
                <div className="metric-data">
                  <h3>{approvedRuntimeBooks.toLocaleString()}</h3>
                  <p>Operational Shortlist</p>
                </div>
                <div className="metric-trend positive">
                  <BookOpen size={14} /> <span>Selected</span>
                </div>
              </div>
              <div className="metric-card metric-card-priority metric-clickable" onClick={() => openMetricPopover('wikiRuntime')}>
                <div className="metric-icon"><CheckCircle2 size={24} /></div>
                <div className="metric-data">
                  <h3>{approvedWikiRuntimeBooks.toLocaleString()}</h3>
                  <p>Live Operational Wiki</p>
                </div>
                <div className="metric-status online">Runtime</div>
              </div>
              <div className="metric-card metric-card-priority metric-clickable" onClick={() => openMetricPopover('buyerGate')}>
                <div className="metric-icon"><ShieldAlert size={24} /></div>
                <div className="metric-data">
                  <h3>{buyerDemoGate.toLocaleString()}</h3>
                  <p>Release Gate</p>
                </div>
                <div className="metric-status warning">Release</div>
              </div>
            </section>

            <section className="metrics-grid metrics-grid-secondary">
              <div className="metric-card metric-card-secondary metric-clickable" onClick={() => openMetricPopover('manual')}>
                <div className="metric-icon"><Layers size={24} /></div>
                <div className="metric-data">
                  <h3>{materializedManualBooks.toLocaleString()}</h3>
                  <p>Catalog Playbooks</p>
                </div>
                <div className="metric-status online">Materialized</div>
              </div>
              <div className="metric-card metric-card-secondary metric-clickable" onClick={() => openMetricPopover('customerPack')}>
                <div className="metric-icon"><HardDrive size={24} /></div>
                <div className="metric-data">
                  <h3>{customerPackRuntimeBooks.toLocaleString()}</h3>
                  <p>Customer Pack Runtime</p>
                </div>
                <div className="metric-status optimized">Pack</div>
              </div>
              <div className="metric-card metric-card-secondary metric-clickable" onClick={() => openMetricPopover('navBacklog')}>
                <div className="metric-icon"><Search size={24} /></div>
                <div className="metric-data">
                  <h3>{wikiNavigationBacklog.toLocaleString()}</h3>
                  <p>Wiki Navigation Backlog</p>
                </div>
                <div className="metric-status online">Signals</div>
              </div>
              <div className="metric-card metric-card-secondary metric-clickable" onClick={() => openMetricPopover('wikiUsage')}>
                <div className="metric-icon"><Star size={24} /></div>
                <div className="metric-data">
                  <h3>{wikiUsageSignals.toLocaleString()}</h3>
                  <p>Usage</p>
                </div>
                <div className="metric-status optimized">Personal</div>
              </div>
              <div className="metric-card metric-card-secondary metric-clickable" onClick={() => openMetricPopover('buyerPackets')}>
                <div className="metric-icon"><FileText size={24} /></div>
                <div className="metric-data">
                  <h3>{buyerPacketBundle.toLocaleString()}</h3>
                  <p>Release Candidate Packets</p>
                </div>
                <div className="metric-status online">Packets</div>
              </div>
              <div className="metric-card metric-card-secondary">
                <div className="metric-icon"><CheckCircle2 size={24} /></div>
                <div className="metric-data">
                  <h3>{ownerDemoPassRate}%</h3>
                  <p>Owner Demo Rehearsal</p>
                </div>
                <div className={`metric-status ${ownerDemo?.blockers?.length ? 'warning' : 'online'}`}>
                  {ownerDemo?.blockers?.length ? 'Blocking' : 'Passing'}
                </div>
              </div>
              <div className="metric-card metric-card-secondary metric-clickable" onClick={() => openMetricPopover('derived')}>
                <div className="metric-icon"><Activity size={24} /></div>
                <div className="metric-data">
                  <h3>{derivedPlaybooks.toLocaleString()}</h3>
                  <p>Derived Playbooks</p>
                </div>
                <div className="metric-status optimized">Generated</div>
              </div>
            </section>

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
                    <div className="log-empty">No activity yet.</div>
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
              <div className="repo-unanswered-strip">
                <div className="repo-panel-header">
                  <div>
                    <h2>답변하지 못한 질문</h2>
                    <p className="text-muted">
                      현재 Playbook Library에 자료가 없어 답변하지 못한 질문을 저장합니다.
                    </p>
                  </div>
                  <div className="repo-panel-badge">
                    <AlertCircle size={14} />
                    <span>{repositoryUnanswered.length} queued</span>
                  </div>
                </div>
                {repositoryUnanswered.length === 0 ? (
                  <div className="repo-empty repo-unanswered-empty">
                    <AlertCircle size={32} />
                    <p>아직 저장된 미답변 질문이 없습니다.</p>
                  </div>
                ) : (
                  <div className="repo-unanswered-list">
                    {repositoryUnanswered.map((item) => (
                      <button
                        key={`${item.timestamp}-${item.query}`}
                        type="button"
                        className="repo-unanswered-item"
                        onClick={() => {
                          setViewMode('repository');
                          setSearchQuery(item.query);
                        }}
                      >
                        <div className="repo-unanswered-query">{item.query}</div>
                        <div className="repo-unanswered-meta">
                          <span>{new Date(item.timestamp).toLocaleString()}</span>
                          {item.warnings.length > 0 ? <span>{item.warnings[0]}</span> : null}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

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
                    <button
                      type="button"
                      className="metric-book-row metric-book-row-clickable"
                      key={book.book_slug}
                      onClick={() => setBookViewer(book)}
                      disabled={!book.viewer_path}
                      title={book.viewer_path ? '문서 열기' : '뷰어 경로 없음'}
                    >
                      <FileText size={16} className="metric-book-icon" />
                      <div className="metric-book-info">
                        <span className="metric-book-title">{book.title}</span>
                        <span className="metric-book-meta">
                          {customerPackBookTruth(book) || book.source_lane} · {book.section_count} sections · {book.grade}
                        </span>
                        {customerPackBookEvidenceBits(book).length > 0 && (
                          <div className="metric-book-chip-row">
                            {customerPackBookEvidenceBits(book).map((item) => (
                              <span key={item} className="metric-book-chip">{item}</span>
                            ))}
                          </div>
                        )}
                      </div>
                      <span className={`metric-book-status ${book.review_status === 'approved' ? 'approved' : ''}`}>
                        {book.review_status}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {buyerPacketPopover && (
        <div className="preview-overlay" onClick={() => setBuyerPacketPopover(null)}>
          <div className="preview-popover" onClick={(e) => e.stopPropagation()}>
            <div className="preview-header">
              <div className="preview-header-left">
                <h3>{buyerPacketPopover.title}</h3>
                <div className="preview-header-meta">
                  <span>{buyerPacketPopover.packets.length} packets</span>
                </div>
              </div>
              <button className="preview-close-btn" onClick={() => setBuyerPacketPopover(null)}><X size={18} /></button>
            </div>
            <div className="metric-popover-body">
              {buyerPacketPopover.packets.length === 0 ? (
                <div className="preview-no-sections">등록된 buyer packet이 없습니다.</div>
              ) : (
                <div className="metric-book-list">
                  {buyerPacketPopover.packets.map((packet) => (
                    <button
                      type="button"
                      className="metric-book-row metric-book-row-clickable"
                      key={packet.book_slug}
                      onClick={() => openBuyerPacket(packet)}
                    >
                      <FileText size={16} className="metric-book-icon" />
                      <div className="metric-book-info">
                        <span className="metric-book-title">{packet.title}</span>
                        <span className="metric-book-meta">
                        {packet.boundary_badge || 'Release Packet'} · {packet.runtime_truth_label || ''}
                      </span>
                    </div>
                    <span className={`metric-book-status ${packet.review_status === 'ready' ? 'approved' : ''}`}>
                      {packet.review_status}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Book Viewer Popover */}
      {bookViewer && (
        <div className="preview-overlay" onClick={() => setBookViewer(null)}>
          <div className="preview-popover" onClick={(e) => e.stopPropagation()}>
            <div className="preview-header">
              <div className="preview-header-left">
                <h3>{bookViewer.title}</h3>
                <div className="preview-header-meta">
                  <span>{customerPackBookTruth(bookViewer) || bookViewer.source_lane}</span>
                  <span>{bookViewer.section_count} sections</span>
                  <span>{bookViewer.grade}</span>
                </div>
                {customerPackBookEvidenceBits(bookViewer).length > 0 && (
                  <div className="preview-chip-row">
                    {customerPackBookEvidenceBits(bookViewer).map((item) => (
                      <span key={item} className="preview-chip">{item}</span>
                    ))}
                  </div>
                )}
              </div>
              <button className="preview-close-btn" onClick={() => setBookViewer(null)}><X size={18} /></button>
            </div>
            <div className="preview-body">
              {bookViewer.viewer_path ? (
                <iframe
                  title={bookViewer.title}
                  className="preview-viewer-frame"
                  src={toRuntimeUrl(bookViewer.viewer_path)}
                />
              ) : (
                <div className="preview-no-sections">뷰어 경로가 없는 북입니다.</div>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default PlaybookLibraryPage;

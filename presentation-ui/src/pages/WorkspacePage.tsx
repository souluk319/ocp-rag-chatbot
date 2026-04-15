import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent, type KeyboardEvent } from 'react';
import { Group, Panel, Separator, usePanelRef } from 'react-resizable-panels';
import { Link, useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  ChevronDown,
  ChevronRight,
  Send,
  BookOpen,
  Cpu,
  ArrowRight,
  ArrowDown,
  Sparkles,
  Bot,
  Link as LinkIcon,
  Languages,
  LogOut,
  Settings,
  Plus,
  MessageSquare,
  Trash2,
  PanelLeftClose,
  PanelRightClose,
  Copy,
  Check,
  WrapText,
  Star,
  Clock3,
  NotebookPen,
} from 'lucide-react';
import gsap from 'gsap';
import './WorkspacePage.css';
import {
  type ChatCitation,
  type ChatRelatedLink,
  type CustomerPackBook,
  type CustomerPackDraft,
  type DerivedAsset,
  type LibraryBook,
  type SessionSummary,
  type WikiOverlayRecommendedPlay,
  type WikiOverlaySignalsResponse,
  type SourceMetaResponse,
  type WikiOverlayRecord,
  type WikiOverlayTargetKind,
  captureCustomerPackDraft,
  formatBytes,
  listCustomerPackDrafts,
  listSessions,
  loadCustomerPackBook,
  loadCustomerPackDraft,
  loadDataControlRoom,
  loadWikiOverlaySignals,
  loadWikiOverlays,
  loadSession,
  deleteAllSessions,
  deleteSession,
  loadSourceMeta,
  normalizeCustomerPackDraft,
  removeWikiOverlay,
  saveWikiOverlay,
  sendChat,
  toRuntimeUrl,
  uploadCustomerPackDraft,
} from '../lib/runtimeApi';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: ChatCitation[];
  suggestedQueries?: string[];
  relatedLinks?: ChatRelatedLink[];
  relatedSections?: ChatRelatedLink[];
  primarySourceLane?: string;
  primaryBoundaryTruth?: string;
  primaryRuntimeTruthLabel?: string;
  primaryBoundaryBadge?: string;
  primaryPublicationState?: string;
  primaryApprovalState?: string;
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

interface OverlayTargetDescriptor {
  kind: WikiOverlayTargetKind;
  ref: string;
  title: string;
  viewerPath: string;
  payload: Record<string, unknown>;
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
  const shortPart = Math.random().toString(36).substring(2, 8).toUpperCase();
  return `${prefix}-${shortPart}`;
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

function truthSurfaceCopy(payload?: {
  boundary_truth?: string;
  runtime_truth_label?: string;
  boundary_badge?: string;
  source_lane?: string;
  approval_state?: string;
  publication_state?: string;
  parser_backend?: string;
  pack_label?: string;
} | null): {
  label: string;
  meta: string[];
} {
  if (!payload) {
    return { label: 'Runtime', meta: [] };
  }
  const boundaryTruth = String(payload.boundary_truth || '').trim();
  const sourceLane = String(payload.source_lane || '').trim();
  const runtimeTruthLabel = String(payload.runtime_truth_label || '').trim();
  const packLabel = String(payload.pack_label || '').trim();

  if (boundaryTruth === 'private_customer_pack_runtime' || sourceLane === 'customer_source_first_pack') {
    return {
      label: 'Private Runtime',
      meta: [
        runtimeTruthLabel || 'Customer Source-First Pack',
        payload.approval_state ? `approval ${payload.approval_state}` : '',
        payload.publication_state ? `publication ${payload.publication_state}` : '',
        payload.parser_backend ? `parser ${payload.parser_backend}` : '',
      ].filter(Boolean),
    };
  }

  if (boundaryTruth === 'official_validated_runtime' || sourceLane.includes('wiki_runtime') || sourceLane.includes('approved')) {
    return {
      label: 'Validated Runtime',
      meta: [
        runtimeTruthLabel || (packLabel ? `${packLabel} Runtime` : 'Validated Pack Runtime'),
        packLabel || '',
      ].filter(Boolean),
    };
  }

  if (boundaryTruth === 'official_candidate_runtime' || sourceLane.includes('candidate')) {
    const isLegacyArchiveLane =
      sourceLane === 'wave1_gold_candidate'
      || sourceLane === 'legacy_gold_candidate_archive'
      || sourceLane === 'gold_candidate_archive';
    return {
      label: isLegacyArchiveLane ? 'Archived Runtime' : 'Candidate Runtime',
      meta: [
        runtimeTruthLabel || (packLabel ? `${packLabel} Candidate` : 'Validated Pack Candidate'),
      ].filter(Boolean),
    };
  }

  if (boundaryTruth === 'mixed_runtime_bridge' || sourceLane.includes('mixed')) {
    return {
      label: 'Mixed Runtime',
      meta: [
        runtimeTruthLabel || 'Official + Private Runtime',
      ].filter(Boolean),
    };
  }

  return {
    label: payload.boundary_badge || runtimeTruthLabel || sourceLane || 'Runtime',
    meta: [
      payload.approval_state ? `approval ${payload.approval_state}` : '',
      payload.publication_state ? `publication ${payload.publication_state}` : '',
      payload.parser_backend ? `parser ${payload.parser_backend}` : '',
    ].filter(Boolean),
  };
}

function primaryCitationTruth(citations?: ChatCitation[] | null): {
  sourceLane?: string;
  boundaryTruth?: string;
  runtimeTruthLabel?: string;
  boundaryBadge?: string;
  publicationState?: string;
  approvalState?: string;
} | null {
  if (!citations || citations.length === 0) {
    return null;
  }
  const primary = citations[0];
  return {
    sourceLane: primary.source_lane,
    boundaryTruth: primary.boundary_truth,
    runtimeTruthLabel: primary.runtime_truth_label,
    boundaryBadge: primary.boundary_badge,
    publicationState: primary.publication_state,
    approvalState: primary.approval_state,
  };
}

function formatCitationLabel(citation: ChatCitation): string {
  const base = citation.source_label || citation.book_title || citation.section;
  const truth = truthSurfaceCopy(citation);
  if (truth.label) {
    return `${truth.label} · ${base}`;
  }
  return base;
}

function citationSurfaceCopy(citation: ChatCitation): {
  badge: string;
  title: string;
  meta: string[];
} {
  const truth = truthSurfaceCopy(citation);
  const title = citation.source_label || citation.book_title || citation.section || citation.book_slug;
  const meta = [...truth.meta];
  if (!meta.length && citation.section && citation.section !== title) {
    meta.push(citation.section);
  }
  return {
    badge: truth.label || 'Runtime',
    title,
    meta,
  };
}

function truthBlockCopy(payload?: {
  boundary_truth?: string;
  runtime_truth_label?: string;
  boundary_badge?: string;
  source_lane?: string;
  approval_state?: string;
  publication_state?: string;
  parser_backend?: string;
  pack_label?: string;
} | null): {
  badge: string;
  meta: string[];
} {
  const truth = truthSurfaceCopy(payload);
  return {
    badge: truth.label || 'Runtime',
    meta: truth.meta,
  };
}

function TruthBadgeBlock({
  payload,
  badgeClassName = 'truth-badge',
  metaClassName = 'truth-meta',
  showMeta = true,
}: {
  payload?: {
    boundary_truth?: string;
    runtime_truth_label?: string;
    boundary_badge?: string;
    source_lane?: string;
    approval_state?: string;
    publication_state?: string;
    parser_backend?: string;
    pack_label?: string;
  } | null;
  badgeClassName?: string;
  metaClassName?: string;
  showMeta?: boolean;
}) {
  const truth = truthBlockCopy(payload);
  return (
    <>
      <span className={badgeClassName}>{truth.badge}</span>
      {showMeta && truth.meta.length > 0 && (
        <span className={metaClassName}>{truth.meta.join(' · ')}</span>
      )}
    </>
  );
}

function extractDraftIdFromViewerPath(viewerPath: string): string | null {
  const match = viewerPath.match(/\/playbooks\/customer-packs\/([^/]+)/);
  return match?.[1] ?? null;
}

const PACK_OPTIONS = [
  'OpenShift 4.20',
  'GitLab Self-Managed',
  'Harbor Registry',
] as const;

const SUGGESTED_QUESTIONS = [
  'Pod가 CrashLoopBackOff 상태일 때 디버깅하는 oc 명령어를 알려줘',
  'OpenShift에서 특정 네임스페이스의 리소스 사용량을 확인하는 명령어는?',
  'oc CLI로 노드 상태를 점검하고 drain하는 절차를 알려줘',
  'OpenShift Route에 TLS 인증서를 적용하는 YAML 예시를 보여줘',
  'oc adm 명령어로 클러스터 노드 상태를 진단하는 방법은?',
  'DeploymentConfig에서 롤링 업데이트 전략을 설정하는 YAML 예시를 보여줘',
  'PVC가 Pending 상태일 때 원인을 확인하는 명령어를 알려줘',
  'NetworkPolicy로 특정 Pod 간 트래픽만 허용하는 YAML 예시를 보여줘',
  'CronJob을 생성하고 실행 이력을 확인하는 oc 명령어는?',
  'OpenShift에서 Pod에 리소스 제한을 설정하는 YAML 예시를 보여줘',
  'ServiceAccount에 특정 SCC를 부여하는 명령어를 알려줘',
  'oc debug 명령어로 노드에 접속해서 디스크 상태를 확인하는 방법은?',
];

const WIKI_OVERLAY_USER_ID = 'kugnus@cywell.co.kr';

function pickRandom<T>(pool: T[], count: number): T[] {
  const copy = [...pool];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, count);
}

function runtimePathFromUrl(viewerUrl: string): string {
  try {
    const parsed = new URL(viewerUrl, window.location.origin);
    return `${parsed.pathname}${parsed.hash || ''}`;
  } catch {
    return viewerUrl;
  }
}

function buildOverlayTargetFromViewerPath(
  viewerUrl: string,
  fallbackTitle: string,
): OverlayTargetDescriptor | null {
  const runtimePath = runtimePathFromUrl(viewerUrl);
  const [pathOnly, anchorPart] = runtimePath.split('#', 2);
  const anchor = anchorPart?.trim() ?? '';

  const entityMatch = pathOnly.match(/^\/wiki\/entities\/([^/]+)\/index\.html$/);
  if (entityMatch) {
    const entitySlug = entityMatch[1];
    return {
      kind: 'entity_hub',
      ref: `entity:${entitySlug}`,
      title: fallbackTitle,
      viewerPath: runtimePath,
      payload: {
        user_id: WIKI_OVERLAY_USER_ID,
        target_kind: 'entity_hub',
        entity_slug: entitySlug,
        viewer_path: runtimePath,
      },
    };
  }

  const figureMatch = pathOnly.match(/^\/wiki\/figures\/([^/]+)\/([^/]+)\/index\.html$/);
  if (figureMatch) {
    const [, bookSlug, assetName] = figureMatch;
    return {
      kind: 'figure',
      ref: `figure:${bookSlug}:${assetName}`,
      title: fallbackTitle,
      viewerPath: runtimePath,
      payload: {
        user_id: WIKI_OVERLAY_USER_ID,
        target_kind: 'figure',
        book_slug: bookSlug,
        asset_name: assetName,
        viewer_path: runtimePath,
      },
    };
  }

  const bookMatch = pathOnly.match(/^\/playbooks\/(?:wiki-runtime\/active|wiki-runtime\/wave1|gold-candidates\/wave1)\/([^/]+)\/index\.html$/);
  if (bookMatch) {
    const bookSlug = bookMatch[1];
    if (anchor) {
      return {
        kind: 'section',
        ref: `section:${bookSlug}#${anchor}`,
        title: fallbackTitle,
        viewerPath: runtimePath,
        payload: {
          user_id: WIKI_OVERLAY_USER_ID,
          target_kind: 'section',
          book_slug: bookSlug,
          anchor,
          viewer_path: runtimePath,
        },
      };
    }
    return {
      kind: 'book',
      ref: `book:${bookSlug}`,
      title: fallbackTitle,
      viewerPath: runtimePath,
      payload: {
        user_id: WIKI_OVERLAY_USER_ID,
        target_kind: 'book',
        book_slug: bookSlug,
        viewer_path: runtimePath,
      },
    };
  }

  return null;
}

type InlineToken =
  | { kind: 'text'; value: string }
  | { kind: 'code'; value: string }
  | { kind: 'strong'; value: string }
  | { kind: 'citation'; index: number; citation?: ChatCitation };

type AnswerBlock =
  | { type: 'paragraph'; parts: InlineToken[] }
  | { type: 'heading'; level: number; parts: InlineToken[] }
  | { type: 'unordered-list'; items: InlineToken[][] }
  | { type: 'step'; number: number; paragraphs: InlineToken[][]; codeBlocks: { code: string; language: string }[] };

function buildCitationMap(citations: ChatCitation[]): Map<number, ChatCitation> {
  return new Map(citations.map((citation) => [Number(citation.index), citation]));
}

function normalizeAssistantAnswer(text: string): string {
  const stripped = String(text || '').trim().replace(/^답변:\s*/u, '');
  const lines = stripped.split('\n');
  let nextStep = 1;
  return lines
    .map((line) => {
      const match = line.match(/^(\s*)(\d+)\.\s+(.*)$/);
      if (!match || match[1].length > 0) {
        return line;
      }
      return `${match[1]}${nextStep++}. ${match[3]}`;
    })
    .join('\n');
}

function parseInlineTokens(text: string, citationsByIndex: Map<number, ChatCitation>): InlineToken[] {
  const chunks = String(text || '').split(/(`[^`]+`|\*\*[^*]+\*\*|\[\d+\])/g);
  const tokens: InlineToken[] = [];
  chunks.forEach((chunk) => {
    if (!chunk) {
      return;
    }
    if (chunk.startsWith('`') && chunk.endsWith('`') && chunk.length >= 2) {
      tokens.push({ kind: 'code', value: chunk.slice(1, -1) });
      return;
    }
    if (chunk.startsWith('**') && chunk.endsWith('**') && chunk.length >= 4) {
      tokens.push({ kind: 'strong', value: chunk.slice(2, -2) });
      return;
    }
    const citationMatch = chunk.match(/^\[(\d+)\]$/);
    if (citationMatch) {
      const index = Number(citationMatch[1]);
      tokens.push({
        kind: 'citation',
        index,
        citation: citationsByIndex.get(index),
      });
      return;
    }
    tokens.push({ kind: 'text', value: chunk });
  });
  return tokens;
}

function parseAnswerBlocks(text: string, citations: ChatCitation[]): AnswerBlock[] {
  const normalized = normalizeAssistantAnswer(text).replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  const citationsByIndex = buildCitationMap(citations);
  const lines = normalized.split('\n');
  const blocks: AnswerBlock[] = [];

  let currentStep: Extract<AnswerBlock, { type: 'step' }> | null = null;
  let stepBuffer: string[] = [];
  let paragraphBuffer: string[] = [];
  let listBuffer: InlineToken[][] = [];
  let inCode = false;
  let codeLanguage = '';
  let codeLines: string[] = [];

  const flushParagraph = (): void => {
    if (!paragraphBuffer.length) {
      return;
    }
    const textValue = paragraphBuffer.join('\n').trim();
    if (textValue) {
      blocks.push({ type: 'paragraph', parts: parseInlineTokens(textValue, citationsByIndex) });
    }
    paragraphBuffer = [];
  };

  const flushList = (): void => {
    if (!listBuffer.length) {
      return;
    }
    blocks.push({ type: 'unordered-list', items: [...listBuffer] });
    listBuffer = [];
  };

  const flushStepParagraph = (): void => {
    if (!currentStep || !stepBuffer.length) {
      return;
    }
    const textValue = stepBuffer.join('\n').trim();
    if (textValue) {
      currentStep.paragraphs.push(parseInlineTokens(textValue, citationsByIndex));
    }
    stepBuffer = [];
  };

  const flushStep = (): void => {
    if (!currentStep) {
      return;
    }
    flushStepParagraph();
    blocks.push(currentStep);
    currentStep = null;
  };

  const flushCode = (): void => {
    const code = codeLines.join('\n').trimEnd();
    if (!code) {
      codeLines = [];
      codeLanguage = '';
      return;
    }
    if (currentStep) {
      flushStepParagraph();
      currentStep.codeBlocks.push({ code, language: codeLanguage || 'text' });
    } else {
      blocks.push({
        type: 'paragraph',
        parts: [{ kind: 'code', value: code }],
      });
    }
    codeLines = [];
    codeLanguage = '';
  };

  lines.forEach((line) => {
    const fence = line.match(/^```([\w.+-]*)\s*$/);
    if (fence) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        flushParagraph();
        flushList();
        codeLanguage = fence[1] || 'text';
        inCode = true;
      }
      return;
    }

    if (inCode) {
      codeLines.push(line);
      return;
    }

    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushList();
      flushStepParagraph();
      return;
    }

    const headingMatch = trimmed.match(/^(#{1,3})\s+(.*)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      flushStep();
      blocks.push({
        type: 'heading',
        level: headingMatch[1].length,
        parts: parseInlineTokens(headingMatch[2], citationsByIndex),
      });
      return;
    }

    const orderedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (orderedMatch) {
      flushParagraph();
      flushList();
      flushStep();
      currentStep = {
        type: 'step',
        number: Number(orderedMatch[1]),
        paragraphs: [],
        codeBlocks: [],
      };
      stepBuffer.push(orderedMatch[2]);
      return;
    }

    const unorderedMatch = trimmed.match(/^[-*]\s+(.*)$/);
    if (unorderedMatch && !currentStep) {
      flushParagraph();
      listBuffer.push(parseInlineTokens(unorderedMatch[1], citationsByIndex));
      return;
    }

    if (currentStep) {
      stepBuffer.push(trimmed);
      return;
    }

    paragraphBuffer.push(trimmed);
  });

  flushParagraph();
  flushList();
  flushStep();

  if (blocks.length === 0 && normalized.trim()) {
    blocks.push({
      type: 'paragraph',
      parts: parseInlineTokens(normalized.trim(), citationsByIndex),
    });
  }

  return blocks;
}

function InlineParts({
  parts,
  onCitationClick,
}: {
  parts: InlineToken[];
  onCitationClick: (citation: ChatCitation) => void;
}) {
  return (
    <>
      {parts.map((part, index) => {
        if (part.kind === 'code') {
          return <code key={`code-${index}`} className="inline-code">{part.value}</code>;
        }
        if (part.kind === 'strong') {
          return <strong key={`strong-${index}`}>{part.value}</strong>;
        }
        if (part.kind === 'citation' && part.citation) {
          return (
            <button
              key={`citation-${index}`}
              type="button"
              className="inline-citation"
              onClick={() => onCitationClick(part.citation!)}
            >
              {part.index}
            </button>
          );
        }
        if (part.kind === 'citation') {
          return <span key={`citation-text-${index}`}>[{part.index}]</span>;
        }
        return <span key={`text-${index}`}>{part.value}</span>;
      })}
    </>
  );
}

function AnswerCodeBlock({ code, language }: { code: string; language: string }) {
  const [wrapped, setWrapped] = useState(false);
  const [copied, setCopied] = useState(false);

  async function handleCopy(): Promise<void> {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(code);
      } else {
        const helper = document.createElement('textarea');
        helper.value = code;
        helper.setAttribute('readonly', 'true');
        helper.style.position = 'fixed';
        helper.style.opacity = '0';
        document.body.appendChild(helper);
        helper.select();
        document.execCommand('copy');
        document.body.removeChild(helper);
      }
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <section className={`answer-code-block ${wrapped ? 'is-wrapped' : ''}`}>
      <div className="answer-code-header">
        <span className="answer-code-lang">{(language || 'text').toUpperCase()}</span>
        <div className="answer-code-actions">
          <button type="button" className="answer-code-action" onClick={() => { void handleCopy(); }} title={copied ? '복사됨' : '복사'}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
          </button>
          <button type="button" className={`answer-code-action ${wrapped ? 'active' : ''}`} onClick={() => setWrapped((value) => !value)} title={wrapped ? '줄바꿈 해제' : '줄바꿈'}>
            <WrapText size={14} />
          </button>
        </div>
      </div>
      <pre className="answer-code-pre"><code>{code}</code></pre>
    </section>
  );
}

function ThinkingIndicator() {
  return (
    <div className="message-row assistant animate-in">
      <div className="message-bubble glass-panel thinking-bubble">
        <div className="assistant-head thinking-head">
          <div className="assistant-avatar small">
            <Bot size={14} />
          </div>
          <div className="typing-indicator-dots">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AssistantAnswer({
  content,
  citations,
  relatedLinks,
  relatedSections,
  primarySourceLane,
  primaryBoundaryTruth,
  primaryRuntimeTruthLabel,
  primaryBoundaryBadge,
  primaryPublicationState,
  primaryApprovalState,
  onCitationClick,
  onRelatedLinkClick,
  onToggleFavoriteLink,
  onCheckSectionLink,
  isFavoriteLink,
  isCheckedSectionLink,
}: {
  content: string;
  citations: ChatCitation[];
  relatedLinks: ChatRelatedLink[];
  relatedSections: ChatRelatedLink[];
  primarySourceLane?: string;
  primaryBoundaryTruth?: string;
  primaryRuntimeTruthLabel?: string;
  primaryBoundaryBadge?: string;
  primaryPublicationState?: string;
  primaryApprovalState?: string;
  onCitationClick: (citation: ChatCitation) => void;
  onRelatedLinkClick: (link: ChatRelatedLink) => void;
  onToggleFavoriteLink: (link: ChatRelatedLink) => void;
  onCheckSectionLink: (link: ChatRelatedLink) => void;
  isFavoriteLink: (link: ChatRelatedLink) => boolean;
  isCheckedSectionLink: (link: ChatRelatedLink) => boolean;
}) {
  const [displayLength, setDisplayLength] = useState(0);

  // Real-time scroll sync during streaming — only paused when user scrolls up via mouse wheel
  useEffect(() => {
    if (displayLength > 0) {
      const chatContainer = document.querySelector('.chat-messages');
      if (chatContainer && !chatContainer.classList.contains('scroll-locked')) {
        requestAnimationFrame(() => {
          chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'auto'
          });
        });
      }
    }
  }, [displayLength]);

  // Simulated streaming effect
  useEffect(() => {
    if (displayLength < content.length) {
      const timer = setTimeout(() => {
        setDisplayLength(prev => Math.min(prev + 3, content.length));
      }, 15);
      return () => clearTimeout(timer);
    }
  }, [displayLength, content]);

  const displayedContent = content.slice(0, displayLength);
  const blocks = useMemo(() => parseAnswerBlocks(displayedContent, citations), [displayedContent, citations]);
  const truthSurface = truthSurfaceCopy({
    boundary_truth: primaryBoundaryTruth,
    runtime_truth_label: primaryRuntimeTruthLabel,
    boundary_badge: primaryBoundaryBadge,
    source_lane: primarySourceLane,
    approval_state: primaryApprovalState,
    publication_state: primaryPublicationState,
  });
  const hasTruth = Boolean(primaryBoundaryTruth || truthSurface.label);

  return (
    <div className="assistant-answer">
      <div className="assistant-head">
        <div className="assistant-avatar">
          <Bot size={18} />
        </div>
        <div className="assistant-head-copy">
              <span className="assistant-label">PlayBot</span>
              {hasTruth && (
                <div className="assistant-truth-row">
                  <TruthBadgeBlock
                    payload={{
                      boundary_truth: primaryBoundaryTruth,
                      runtime_truth_label: primaryRuntimeTruthLabel,
                      boundary_badge: primaryBoundaryBadge,
                      source_lane: primarySourceLane,
                      approval_state: primaryApprovalState,
                      publication_state: primaryPublicationState,
                    }}
                    badgeClassName="assistant-truth-chip"
                    metaClassName="assistant-truth-meta"
                    showMeta={false}
                  />
                </div>
              )}
            </div>
      </div>
      <div className="assistant-copy">
        {blocks.map((block, index) => {
          if (block.type === 'heading') {
            const Tag = block.level === 1 ? 'h2' : 'h3';
            return (
              <Tag key={`heading-${index}`} className="assistant-heading">
                <InlineParts parts={block.parts} onCitationClick={onCitationClick} />
              </Tag>
            );
          }
          if (block.type === 'unordered-list') {
            return (
              <ul key={`unordered-${index}`} className="assistant-list">
                {block.items.map((item, itemIndex) => (
                  <li key={`unordered-item-${itemIndex}`} className="assistant-list-item">
                    <InlineParts parts={item} onCitationClick={onCitationClick} />
                  </li>
                ))}
              </ul>
            );
          }
          if (block.type === 'step') {
            return (
              <div key={`step-${index}`} className="assistant-step">
                <div className="assistant-step-badge">{block.number}</div>
                <div className="assistant-step-body">
                  {block.paragraphs.map((paragraph, paragraphIndex) => (
                    <p key={`step-paragraph-${paragraphIndex}`} className="assistant-step-paragraph">
                      <InlineParts parts={paragraph} onCitationClick={onCitationClick} />
                    </p>
                  ))}
                  {block.codeBlocks.map((codeBlock, codeIndex) => (
                    <AnswerCodeBlock
                      key={`step-code-${codeIndex}`}
                      code={codeBlock.code}
                      language={codeBlock.language}
                    />
                  ))}
                </div>
              </div>
            );
          }
          const paragraphClasses = ['assistant-paragraph'];
          if (index === 0) {
            paragraphClasses.push('assistant-lead');
          }
          const singleCodePart = block.parts.length === 1 && block.parts[0]?.kind === 'code'
            ? block.parts[0]
            : null;
          if (singleCodePart) {
            return (
              <AnswerCodeBlock
                key={`code-only-${index}`}
                code={singleCodePart.value}
                language="text"
              />
            );
          }
          return (
            <p key={`paragraph-${index}`} className={paragraphClasses.join(' ')}>
              <InlineParts parts={block.parts} onCitationClick={onCitationClick} />
            </p>
          );
        })}
      </div>
      {relatedLinks.length > 0 && (
        <div className="assistant-related-group">
          <div className="suggested-query-label">관련 탐색</div>
          <div className="suggested-query-list">
            {relatedLinks.map((link, index) => (
              <div key={`${link.href}-${index}`} className="overlay-chip-row">
                <RelatedLinkCard link={link} onOpen={onRelatedLinkClick} />
                <button
                  type="button"
                  className={`overlay-mini-action ${isFavoriteLink(link) ? 'active' : ''}`}
                  onClick={() => onToggleFavoriteLink(link)}
                  title={isFavoriteLink(link) ? '즐겨찾기 해제' : '즐겨찾기'}
                >
                  <Star size={12} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
      {relatedSections.length > 0 && (
        <div className="assistant-related-group">
          <div className="suggested-query-label">정확한 절차</div>
          <div className="suggested-query-list">
            {relatedSections.map((link, index) => (
              <div key={`${link.href}-${index}`} className="overlay-chip-row">
                <button
                  className="suggested-query-chip"
                  type="button"
                  onClick={() => onRelatedLinkClick(link)}
                  title={link.summary ?? ''}
                >
                  섹션 · {link.label}
                </button>
                <button
                  type="button"
                  className={`overlay-mini-action ${isCheckedSectionLink(link) ? 'active' : ''}`}
                  onClick={() => onCheckSectionLink(link)}
                  title={isCheckedSectionLink(link) ? '체크 해제' : '체크 완료'}
                >
                  <Check size={12} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function CitationTag({
  citation,
  onOpen,
}: {
  citation: ChatCitation;
  onOpen: (citation: ChatCitation) => void;
}) {
  const surface = citationSurfaceCopy(citation);
  return (
    <button
      className="citation-tag"
      onClick={() => { onOpen(citation); }}
      type="button"
      title={formatCitationLabel(citation)}
    >
      <div className="citation-tag-topline">
        <span className="citation-tag-badge">{surface.badge}</span>
        <span className="citation-tag-link">
          <LinkIcon size={12} />
        </span>
      </div>
      <div className="citation-tag-title">{surface.title}</div>
      {surface.meta.length > 0 && (
        <div className="citation-tag-meta">{surface.meta.join(' · ')}</div>
      )}
    </button>
  );
}

function RelatedLinkCard({
  link,
  onOpen,
}: {
  link: ChatRelatedLink;
  onOpen: (link: ChatRelatedLink) => void;
}) {
  const truth = truthBlockCopy(link);
  const meta = link.summary ? [link.summary] : [];
  return (
    <button
      className="related-link-card"
      type="button"
      onClick={() => onOpen(link)}
    >
      <div className="related-link-topline">
        <span className="related-link-badge">{link.kind === 'entity' ? 'Entity' : truth.badge}</span>
        <span className="related-link-link">
          <LinkIcon size={12} />
        </span>
      </div>
      <div className="related-link-title">{link.label}</div>
      {link.kind !== 'entity' && meta.length > 0 && (
        <div className="related-link-meta">{meta.join(' · ')}</div>
      )}
    </button>
  );
}

export default function WorkspacePage() {
  const [packLabel, setPackLabel] = useState('OpenShift 4.20');
  const [packDropdownOpen, setPackDropdownOpen] = useState(false);
  const [manualBooks, setManualBooks] = useState<LibraryBook[]>([]);
  const [drafts, setDrafts] = useState<CustomerPackDraft[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [sessionId, setSessionId] = useState(() => makeId('ID'));
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

  // Session history
  const [sessionList, setSessionList] = useState<SessionSummary[]>([]);
  const [isLoadingSession, setIsLoadingSession] = useState(false);
  const [deletingSessionId, setDeletingSessionId] = useState<string | null>(null);

  // Scroll + welcome
  const [userScrolledUp, setUserScrolledUp] = useState(false);

  // Collapsible panels
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [sourcesDrawerOpen, setSourcesDrawerOpen] = useState(false);
  const [wikiOverlays, setWikiOverlays] = useState<WikiOverlayRecord[]>([]);
  const [wikiOverlaySignals, setWikiOverlaySignals] = useState<WikiOverlaySignalsResponse | null>(null);
  const [isOverlayLoading, setIsOverlayLoading] = useState(false);
  const [isOverlaySaving, setIsOverlaySaving] = useState(false);
  const [noteDraft, setNoteDraft] = useState('');
  const [noteOpen, setNoteOpen] = useState(false);

  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollAnchorRef = useRef<HTMLDivElement>(null);
  const chatMessagesRef = useRef<HTMLDivElement>(null);
  const leftPanelRef = usePanelRef();
  const rightPanelRef = usePanelRef();

  const refreshSessionList = useCallback(async () => {
    try {
      const result = await listSessions();
      setSessionList(result.sessions);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const refreshWikiOverlays = useCallback(async () => {
    setIsOverlayLoading(true);
    try {
      const [overlayResult, signalResult] = await Promise.all([
        loadWikiOverlays(WIKI_OVERLAY_USER_ID),
        loadWikiOverlaySignals(WIKI_OVERLAY_USER_ID),
      ]);
      setWikiOverlays(overlayResult.items ?? []);
      setWikiOverlaySignals(signalResult);
    } catch (error) {
      console.error(error);
    } finally {
      setIsOverlayLoading(false);
    }
  }, []);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const welcomeQuestions = useMemo(() => pickRandom(SUGGESTED_QUESTIONS, 4), [sessionId]);

  // Track user scroll-up via wheel only (not programmatic scroll)
  useEffect(() => {
    void refreshWikiOverlays();
  }, [refreshWikiOverlays]);

  useEffect(() => {
    const el = chatMessagesRef.current;
    if (!el) return;

    function handleWheel(): void {
      requestAnimationFrame(() => {
        if (!el) return;
        const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
        setUserScrolledUp(!atBottom);
        if (atBottom) {
          el.classList.remove('scroll-locked');
        } else {
          el.classList.add('scroll-locked');
        }
      });
    }

    el.addEventListener('wheel', handleWheel, { passive: true });
    return () => el.removeEventListener('wheel', handleWheel);
  }, []);

  function scrollToBottom(): void {
    const el = chatMessagesRef.current;
    if (el) {
      el.classList.remove('scroll-locked');
      setUserScrolledUp(false);
      el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
    }
  }

  function resetSession() {
    setSessionId(makeId('ID'));
    setMessages([]);
    setUserScrolledUp(false);
    void refreshSessionList();
  }

  async function handleSessionResume(targetSessionId: string): Promise<void> {
    if (isLoadingSession) return;
    setIsLoadingSession(true);
    try {
      const snapshot = await loadSession(targetSessionId);
      setSessionId(snapshot.session_id);
      setMessages(
        (snapshot.turns ?? []).flatMap((turn) => [
          { id: makeId('u'), role: 'user' as const, content: turn.query },
          {
            id: makeId('a'),
            role: 'assistant' as const,
            content: turn.answer,
            primarySourceLane: turn.primary_source_lane,
            primaryBoundaryTruth: turn.primary_boundary_truth,
            primaryRuntimeTruthLabel: turn.primary_runtime_truth_label,
            primaryBoundaryBadge: turn.primary_boundary_badge,
            primaryPublicationState: turn.primary_publication_state,
            primaryApprovalState: turn.primary_approval_state,
          },
        ]),
      );
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoadingSession(false);
    }
  }

  async function handleSessionDelete(targetSessionId: string): Promise<void> {
    if (deletingSessionId || isLoadingSession) {
      return;
    }
    const confirmed = window.confirm('이 대화 기록을 삭제할까요?');
    if (!confirmed) {
      return;
    }
    setDeletingSessionId(targetSessionId);
    try {
      await deleteSession(targetSessionId);
      setSessionList((current) => current.filter((session) => session.session_id !== targetSessionId));
      if (targetSessionId === sessionId) {
        setSessionId(makeId('ID'));
        setMessages([]);
      }
      await refreshSessionList();
    } catch (error) {
      console.error(error);
      window.alert(error instanceof Error ? error.message : '대화 기록 삭제 중 오류가 발생했습니다.');
    } finally {
      setDeletingSessionId(null);
    }
  }

  async function handleDeleteAllSessions(): Promise<void> {
    if (deletingSessionId || isLoadingSession || sessionList.length === 0) {
      return;
    }
    const confirmed = window.confirm('대화 기록을 전체 삭제할까요?');
    if (!confirmed) {
      return;
    }
    setDeletingSessionId('__all__');
    try {
      await deleteAllSessions();
      setSessionList([]);
      setSessionId(makeId('ID'));
      setMessages([]);
      await refreshSessionList();
    } catch (error) {
      console.error(error);
      window.alert(error instanceof Error ? error.message : '전체 대화 기록 삭제 중 오류가 발생했습니다.');
    } finally {
      setDeletingSessionId(null);
    }
  }

  function toggleLeftPanel(): void {
    const panel = leftPanelRef.current;
    if (!panel) return;
    if (leftCollapsed) {
      panel.expand();
      setLeftCollapsed(false);
    } else {
      panel.collapse();
      setLeftCollapsed(true);
    }
  }

  function toggleRightPanel(): void {
    const panel = rightPanelRef.current;
    if (!panel) return;
    if (rightCollapsed) {
      panel.expand();
      setRightCollapsed(false);
    } else {
      panel.collapse();
      setRightCollapsed(true);
    }
  }

  useEffect(() => {
    if (!packDropdownOpen) {
      return undefined;
    }

    function handleWindowPointerDown(event: MouseEvent): void {
      const target = event.target as HTMLElement | null;
      if (!target?.closest('.pack-selector-wrapper')) {
        setPackDropdownOpen(false);
      }
    }

    window.addEventListener('mousedown', handleWindowPointerDown);
    return () => {
      window.removeEventListener('mousedown', handleWindowPointerDown);
    };
  }, [packDropdownOpen]);

  useEffect(() => {
    const container = chatMessagesRef.current;
    if (messages.length > 0 && container && !userScrolledUp) {
      requestAnimationFrame(() => {
        try {
          container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
          });
        } catch {
          // ignore
        }
      });
    }
  }, [messages, userScrolledUp]);

  useEffect(() => {
    let animated = false;
    const ctx = gsap.context(() => {
      if (animated) return;

      const panels = containerRef.current?.querySelectorAll('.workspace-panel-item');
      if (panels && panels.length > 0) {
        gsap.from(panels, {
          opacity: 0,
          y: 20,
          stagger: 0.1,
          duration: 0.8,
          ease: 'power3.out',
          delay: 0.3,
        });
        animated = true;
      }
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
          refreshSessionList(),
        ]);
        if (cancelled) {
          return;
        }

        const runtimeBooks = Array.isArray(room.gold_books) ? room.gold_books : [];
        const nextDrafts = draftPayload.drafts ?? [];

        setPackLabel(room.active_pack.pack_label || 'OpenShift 4.20');
        setManualBooks(runtimeBooks);
        setDrafts(nextDrafts);
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

  const currentOverlayTarget = useMemo<OverlayTargetDescriptor | null>(() => {
    if (preview.kind !== 'viewer' || !preview.viewerUrl) {
      return null;
    }
    return buildOverlayTargetFromViewerPath(preview.viewerUrl, preview.title);
  }, [preview]);

  const favoriteOverlays = useMemo(
    () => wikiOverlays.filter((item) => item.kind === 'favorite'),
    [wikiOverlays],
  );
  const recentPositionOverlays = useMemo(
    () => wikiOverlays.filter((item) => item.kind === 'recent_position'),
    [wikiOverlays],
  );
  const noteOverlays = useMemo(
    () => wikiOverlays.filter((item) => item.kind === 'note'),
    [wikiOverlays],
  );
  const personalizedNextPlays = useMemo<WikiOverlayRecommendedPlay[]>(
    () => wikiOverlaySignals?.user_focus?.recommended_next_plays ?? [],
    [wikiOverlaySignals],
  );

  const currentFavorite = useMemo(
    () => favoriteOverlays.find((item) => item.target_ref === currentOverlayTarget?.ref) ?? null,
    [currentOverlayTarget, favoriteOverlays],
  );
  const currentSectionCheck = useMemo(
    () =>
      wikiOverlays.find(
        (item) => item.kind === 'check' && item.target_ref === currentOverlayTarget?.ref,
      ) ?? null,
    [currentOverlayTarget, wikiOverlays],
  );
  const currentNote = useMemo(
    () => noteOverlays.find((item) => item.target_ref === currentOverlayTarget?.ref) ?? null,
    [currentOverlayTarget, noteOverlays],
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
      subtitle: `${loadedDraft.pack_label} · ${truthSurfaceCopy(loadedBook ?? loadedDraft).label} · ${loadedDraft.quality_status}`,
      draft: loadedDraft,
      book: loadedBook,
      viewerUrl,
      derivedAssets: loadedBook?.derived_assets ?? loadedDraft.derived_assets ?? [],
    });
  }

  useEffect(() => {
    setNoteDraft(currentNote?.body ?? '');
  }, [currentNote?.body, currentOverlayTarget?.ref]);

  useEffect(() => {
    if (!currentOverlayTarget) {
      return;
    }
    if (currentOverlayTarget.kind === 'entity_hub' || currentOverlayTarget.kind === 'book' || currentOverlayTarget.kind === 'section' || currentOverlayTarget.kind === 'figure') {
      const timer = window.setTimeout(() => {
        void saveWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'recent_position',
          ...currentOverlayTarget.payload,
        })
          .then(() => refreshWikiOverlays())
          .catch((error) => console.error(error));
      }, 500);
      return () => window.clearTimeout(timer);
    }
    return;
  }, [currentOverlayTarget, refreshWikiOverlays]);

  function resetParentScroll(): void {
    requestAnimationFrame(() => {
      containerRef.current?.scrollTo(0, 0);
      const content = containerRef.current?.querySelector('.workspace-content');
      if (content) { content.scrollTop = 0; content.scrollLeft = 0; }
      const group = containerRef.current?.querySelector('.main-panel-group');
      if (group) { (group as HTMLElement).scrollTop = 0; }
    });
  }

  function animatePreviewPanel(): void {
    resetParentScroll();
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

  async function handleRelatedLinkClick(link: ChatRelatedLink): Promise<void> {
    try {
      const runtimeUrl = toRuntimeUrl(link.href);
      const label = link.kind === 'entity' ? 'Entity Hub' : 'Related Document';
      setPreview({
        kind: 'viewer',
        title: link.label,
        subtitle: label,
        viewerUrl: `${runtimeUrl}${runtimeUrl.includes('?') ? '&' : '?'}embed=1`,
      });
    } catch (error) {
      console.error(error);
    }
  }

  function overlayTargetFromLink(link: ChatRelatedLink): OverlayTargetDescriptor | null {
    return buildOverlayTargetFromViewerPath(toRuntimeUrl(link.href), link.label);
  }

  function overlayExists(kind: 'favorite' | 'check', targetRef: string): WikiOverlayRecord | null {
    return wikiOverlays.find((item) => item.kind === kind && item.target_ref === targetRef) ?? null;
  }

  async function handleToggleFavoriteCurrent(): Promise<void> {
    if (!currentOverlayTarget) {
      return;
    }
    setIsOverlaySaving(true);
    try {
      if (currentFavorite) {
        await removeWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'favorite',
          target_ref: currentFavorite.target_ref,
        });
      } else {
        await saveWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'favorite',
          title: currentOverlayTarget.title,
          summary: preview.kind === 'viewer' ? preview.subtitle : '',
          ...currentOverlayTarget.payload,
        });
      }
      await refreshWikiOverlays();
    } catch (error) {
      console.error(error);
    } finally {
      setIsOverlaySaving(false);
    }
  }

  async function handleToggleFavoriteLink(link: ChatRelatedLink): Promise<void> {
    const target = overlayTargetFromLink(link);
    if (!target) {
      return;
    }
    setIsOverlaySaving(true);
    try {
      const existing = overlayExists('favorite', target.ref);
      if (existing) {
        await removeWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'favorite',
          target_ref: existing.target_ref,
        });
      } else {
        await saveWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'favorite',
          title: link.label,
          summary: link.summary ?? '',
          ...target.payload,
        });
      }
      await refreshWikiOverlays();
    } catch (error) {
      console.error(error);
    } finally {
      setIsOverlaySaving(false);
    }
  }

  async function handleToggleSectionCheckCurrent(): Promise<void> {
    if (!currentOverlayTarget || currentOverlayTarget.kind !== 'section') {
      return;
    }
    setIsOverlaySaving(true);
    try {
      if (currentSectionCheck) {
        await removeWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'check',
          target_ref: currentSectionCheck.target_ref,
        });
      } else {
        await saveWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'check',
          status: 'checked',
          ...currentOverlayTarget.payload,
        });
      }
      await refreshWikiOverlays();
    } catch (error) {
      console.error(error);
    } finally {
      setIsOverlaySaving(false);
    }
  }

  async function handleToggleSectionCheckLink(link: ChatRelatedLink): Promise<void> {
    const target = overlayTargetFromLink(link);
    if (!target || target.kind !== 'section') {
      return;
    }
    setIsOverlaySaving(true);
    try {
      const existing = overlayExists('check', target.ref);
      if (existing) {
        await removeWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'check',
          target_ref: existing.target_ref,
        });
      } else {
        await saveWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'check',
          status: 'checked',
          ...target.payload,
        });
      }
      await refreshWikiOverlays();
    } catch (error) {
      console.error(error);
    } finally {
      setIsOverlaySaving(false);
    }
  }

  async function handleSaveCurrentNote(): Promise<void> {
    if (!currentOverlayTarget) {
      return;
    }
    const body = noteDraft.trim();
    setIsOverlaySaving(true);
    try {
      if (!body && currentNote) {
        await removeWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          overlay_id: currentNote.overlay_id,
        });
      } else if (body) {
        await saveWikiOverlay({
          user_id: WIKI_OVERLAY_USER_ID,
          kind: 'note',
          overlay_id: currentNote?.overlay_id ?? '',
          body,
          pinned: true,
          ...currentOverlayTarget.payload,
        });
      }
      await refreshWikiOverlays();
    } catch (error) {
      console.error(error);
    } finally {
      setIsOverlaySaving(false);
    }
  }

  async function handleOverlayJump(item: WikiOverlayRecord): Promise<void> {
    const href = item.resolved_target?.viewer_path;
    if (!href) {
      return;
    }
    await handleRelatedLinkClick({
      label: item.resolved_target?.title || item.title || item.target_ref,
      href,
      kind: item.target_kind === 'entity_hub' ? 'entity' : 'book',
      summary: item.resolved_target?.summary || item.summary || '',
    });
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
      window.alert(error instanceof Error ? error.message : 'Inspect Source 중 오류가 발생했습니다.');
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
      window.alert(error instanceof Error ? error.message : 'Build Book 중 오류가 발생했습니다.');
    } finally {
      setIsNormalizing(false);
    }
  }

  async function handleSend(queryOverride?: string): Promise<void> {
    const trimmed = (queryOverride ?? query).trim();
    if (!trimmed || isSending) {
      return;
    }

    const nextUserMessage: Message = {
      id: makeId('user'),
      role: 'user',
      content: trimmed,
    };
    setMessages((current) => [...current, nextUserMessage]);
    if (!queryOverride) {
      setQuery('');
    }
    setIsSending(true);

    try {
      const response = await sendChat({
        query: trimmed,
        sessionId,
        mode: 'ops',
        userId: WIKI_OVERLAY_USER_ID,
        selectedDraftIds: activeDraft ? [activeDraft.draft_id] : [],
        restrictUploadedSources: Boolean(activeDraft),
      });
      const primaryTruth = primaryCitationTruth(response.citations);

      setSessionId(response.session_id || sessionId);
      setMessages((current) => [
        ...current,
        {
          id: makeId('assistant'),
          role: 'assistant',
          content: response.answer,
          citations: response.citations ?? [],
          suggestedQueries: response.suggested_queries ?? [],
          relatedLinks: response.related_links ?? [],
          relatedSections: response.related_sections ?? [],
          primarySourceLane: primaryTruth?.sourceLane,
          primaryBoundaryTruth: primaryTruth?.boundaryTruth,
          primaryRuntimeTruthLabel: primaryTruth?.runtimeTruthLabel,
          primaryBoundaryBadge: primaryTruth?.boundaryBadge,
          primaryPublicationState: primaryTruth?.publicationState,
          primaryApprovalState: primaryTruth?.approvalState,
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
      void refreshSessionList();
    }
  }

  function handleInputKeyDown(event: KeyboardEvent<HTMLInputElement>): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
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

  const totalSourceCount = manualSources.length + draftSources.length;
  const recentOverlayItems = recentPositionOverlays.slice(0, 4);
  const favoriteOverlayItems = favoriteOverlays.slice(0, 4);
  const nextPlayItems = personalizedNextPlays.slice(0, 4);

  return (
    <div className="workspace-wrapper" ref={containerRef} data-lenis-prevent>
      <div className="bokeh-bg bokeh-1"></div>
      <div className="bokeh-bg bokeh-2"></div>

      {/* ── Header ── */}
      <header className="workspace-nav">
        <div className="nav-left">
          <Link to="/" className="nav-logo-link">
            <div className="logo-icon">
              <Sparkles size={20} />
            </div>
          </Link>
          <span className="logo-text">Playbook Studio</span>
          <span className="header-divider">|</span>
          <div className="pack-selector-wrapper">
            <button
              className="pack-selector-trigger"
              type="button"
              onClick={() => setPackDropdownOpen((prev) => !prev)}
            >
              <span>{packLabel}</span>
              <ChevronDown size={14} className={`pack-chevron ${packDropdownOpen ? 'open' : ''}`} />
            </button>
            {packDropdownOpen && (
              <div className="pack-dropdown">
                {PACK_OPTIONS.map((label) => (
                  <button
                    key={label}
                    type="button"
                    className={`pack-dropdown-item ${label === packLabel ? 'active' : ''}`}
                    onClick={() => {
                      setPackLabel(label);
                      setPackDropdownOpen(false);
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="nav-right">
          <div className="status-indicator" onClick={resetSession} title="Click to start a new session">
            <div className="status-dot"></div>
            <span className="session-id-text">{sessionId}</span>
          </div>
          <button className="nav-btn" onClick={() => navigate('/playbook-library')} type="button">Playbook Library</button>
          <button className="nav-btn lang-btn" type="button">
            <Languages size={18} />
            <span>KOR</span>
          </button>
        </div>
      </header>

      <main className="workspace-content">
        <Group orientation="horizontal" className="main-panel-group">

          {/* ── Left Panel: Chat History ── */}
          <Panel
            panelRef={leftPanelRef}
            defaultSize={20}
            minSize={15}
            collapsible={true}
            collapsedSize={0}
            onResize={(panelSize) => setLeftCollapsed(panelSize.asPercentage <= 0.5)}
            className="workspace-panel-item"
          >
            <div className={`panel-inner glass-panel no-border-radius-right ${leftCollapsed ? 'panel-collapsed-inner' : ''}`}>
              <div className="panel-header">
                <div className="header-icon"><MessageSquare size={18} /></div>
                <h3>Chat History</h3>
                <div className="session-header-actions">
                  <button className="header-action-btn" type="button" onClick={resetSession} title="New Chat">
                    <Plus size={14} />
                  </button>
                  <button
                    className="header-action-btn header-action-danger"
                    type="button"
                    onClick={() => { void handleDeleteAllSessions(); }}
                    title="Delete All Chat History"
                    disabled={Boolean(deletingSessionId) || isLoadingSession || sessionList.length === 0}
                  >
                    <Trash2 size={14} />
                  </button>
                  <button className="header-action-btn" type="button" onClick={toggleLeftPanel} title="Close sidebar">
                    <PanelLeftClose size={14} />
                  </button>
                </div>
              </div>

              <div className="session-list">
                {sessionList.length === 0 && (
                  <div className="session-list-empty">
                    <MessageSquare size={24} className="text-dim" />
                    <p>아직 대화 기록이 없습니다</p>
                  </div>
                )}
                {sessionList.map((session) => (
                  <button
                    key={session.session_id}
                    type="button"
                    className={`session-item ${session.session_id === sessionId ? 'active' : ''}`}
                    onClick={() => { void handleSessionResume(session.session_id); }}
                    disabled={isLoadingSession || deletingSessionId === session.session_id}
                  >
                    <div className="session-title">{session.session_name || session.first_query || `세션 ${session.session_id.slice(0, 8)}`}</div>
                    {(session.primary_boundary_badge || session.primary_runtime_truth_label || session.primary_source_lane) && (
                      <div className="session-truth-row">
                        <TruthBadgeBlock
                          payload={{
                            boundary_truth: session.primary_boundary_truth,
                            runtime_truth_label: session.primary_runtime_truth_label,
                            boundary_badge: session.primary_boundary_badge,
                            source_lane: session.primary_source_lane,
                            approval_state: session.primary_approval_state,
                            publication_state: session.primary_publication_state,
                          }}
                          badgeClassName="session-truth-chip"
                          metaClassName="session-truth-meta"
                          showMeta={false}
                        />
                      </div>
                    )}
                    <div className="session-meta">
                      <span>{session.turn_count} turns</span>
                      {session.updated_at && <span>{session.updated_at.slice(0, 10)}</span>}
                    </div>
                    <button
                      type="button"
                      className="session-delete-inline"
                      title="삭제"
                      onClick={(event) => {
                        event.stopPropagation();
                        void handleSessionDelete(session.session_id);
                      }}
                      disabled={Boolean(deletingSessionId) || isLoadingSession}
                    >
                      <Trash2 size={13} />
                    </button>
                  </button>
                ))}
              </div>

              <div className="user-profile-section">
                <div className="profile-container">
                  <div className="profile-avatar">
                    <img src="/user_profile_01.png" alt="User Profile" />
                    <div className="status-dot-online"></div>
                  </div>
                  <div className="profile-info">
                    <div className="profile-name">김성욱</div>
                    <div className="profile-role">kugnus@cywell.co.kr</div>
                  </div>
                  <div className="profile-actions">
                    <button className="profile-action-btn" title="Settings" type="button" onClick={(e) => e.stopPropagation()}>
                      <Settings size={16} />
                    </button>
                    <button className="profile-action-btn" title="Logout" type="button" onClick={(e) => e.stopPropagation()}>
                      <LogOut size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Panel>

          <Separator className="custom-resize-handle">
            <div className="handle-visual" />
          </Separator>

          {/* ── Center Panel: Chat ── */}
          <Panel defaultSize={45} minSize={30} className="workspace-panel-item">
            <div className="panel-inner chat-area">
              {(leftCollapsed || rightCollapsed) && (
                <div className="chat-panel-toolbar">
                  {leftCollapsed && (
                    <button className="panel-reopen-btn" type="button" onClick={toggleLeftPanel} title="Open sidebar">
                      <PanelLeftClose size={16} />
                    </button>
                  )}
                  <div className="chat-panel-toolbar-spacer" />
                  {rightCollapsed && (
                    <button className="panel-reopen-btn" type="button" onClick={toggleRightPanel} title="Open panel">
                      <PanelRightClose size={16} />
                    </button>
                  )}
                </div>
              )}
              <div className="chat-messages" ref={chatMessagesRef}>
                {messages.length === 0 && (
                  <div className="chat-welcome">
                    <div className="welcome-icon">
                      <Sparkles size={36} />
                    </div>
                    <h2 className="welcome-title">문서를 탐색하세요</h2>
                    <p className="welcome-subtitle">기술 위키 runtime 에서 근거와 문맥을 찾습니다</p>
                    <div className="welcome-question-grid">
                      {welcomeQuestions.map((q, i) => (
                        <button
                          key={`welcome-q-${i}`}
                          type="button"
                          className="welcome-question-card glass-panel"
                          onClick={() => { void handleSend(q); }}
                          disabled={isSending}
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {messages.map((message) => (
                  <div key={message.id} className={`message-row ${message.role}`}>
                    <div className="message-bubble glass-panel">
                      <div className="message-content">
                        {message.role === 'assistant' ? (
                          <AssistantAnswer
                            content={message.content}
                            citations={message.citations ?? []}
                            relatedLinks={message.relatedLinks ?? []}
                            relatedSections={message.relatedSections ?? []}
                            primarySourceLane={message.primarySourceLane}
                            primaryBoundaryTruth={message.primaryBoundaryTruth}
                            primaryRuntimeTruthLabel={message.primaryRuntimeTruthLabel}
                            primaryBoundaryBadge={message.primaryBoundaryBadge}
                            primaryPublicationState={message.primaryPublicationState}
                            primaryApprovalState={message.primaryApprovalState}
                            onCitationClick={(citation) => {
                              void handleCitationClick(citation);
                            }}
                            onRelatedLinkClick={(link) => {
                              void handleRelatedLinkClick(link);
                            }}
                            onToggleFavoriteLink={(link) => {
                              void handleToggleFavoriteLink(link);
                            }}
                            onCheckSectionLink={(link) => {
                              void handleToggleSectionCheckLink(link);
                            }}
                            isFavoriteLink={(link) => {
                              const target = overlayTargetFromLink(link);
                              return Boolean(target && overlayExists('favorite', target.ref));
                            }}
                            isCheckedSectionLink={(link) => {
                              const target = overlayTargetFromLink(link);
                              return Boolean(target && overlayExists('check', target.ref));
                            }}
                          />
                        ) : (
                          message.content
                        )}
                      </div>
                      {message.role !== 'assistant' && message.citations && message.citations.length > 0 && (
                        <div className="message-tags">
                          {message.citations.map((citation) => (
                            <CitationTag
                              key={`${message.id}-${citation.index}`}
                              citation={citation}
                              onOpen={(selected) => { void handleCitationClick(selected); }}
                            />
                          ))}
                        </div>
                      )}
                      {message.role === 'assistant' && message.suggestedQueries && message.suggestedQueries.length > 0 && (
                        <div className="suggested-query-group">
                          <div className="suggested-query-label">추천 질문</div>
                          <div className="suggested-query-list">
                            {message.suggestedQueries.map((suggestedQuery, suggestedIndex) => (
                              <button
                                key={`${message.id}-suggested-${suggestedIndex}`}
                                className="suggested-query-chip"
                                type="button"
                                onClick={() => { void handleSend(suggestedQuery); }}
                                disabled={isSending}
                              >
                                {suggestedQuery}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isSending && <ThinkingIndicator />}

                <div ref={scrollAnchorRef} />
              </div>

              {userScrolledUp && messages.length > 0 && (
                <button
                  className="scroll-to-bottom-btn"
                  type="button"
                  onClick={scrollToBottom}
                >
                  <ArrowDown size={18} />
                </button>
              )}

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

          {/* ── Right Panel: Runtime Sources + Overlay ── */}
          <Panel
            panelRef={rightPanelRef}
            defaultSize={35}
            minSize={20}
            collapsible={true}
            collapsedSize={0}
            onResize={(panelSize) => setRightCollapsed(panelSize.asPercentage <= 0.5)}
            className="workspace-panel-item"
          >
            <div className={`panel-inner glass-panel no-border-radius-left ${rightCollapsed ? 'panel-collapsed-inner' : ''}`}>
              <div className="panel-header">
                <div className="header-icon"><BookOpen size={18} /></div>
                <h3>Runtime Sources</h3>

                <button className="header-action-btn" type="button" onClick={toggleRightPanel} title="Close panel" style={{ marginLeft: 'auto' }}>
                  <PanelRightClose size={14} />
                </button>

                {/* Upload + Sources inline in header */}
                <input
                  ref={fileInputRef}
                  className="file-input-hidden"
                  type="file"
                  onChange={(event) => {
                    void handleUploadSelection(event);
                  }}
                />
                <div className="header-toolbar-actions">
                  <button
                    className="toolbar-inline-btn"
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                  >
                    <Upload size={13} />
                    <span>{isUploading ? 'Uploading...' : 'Upload'}</span>
                  </button>
                  <button
                    className={`toolbar-inline-btn ${sourcesDrawerOpen ? 'active' : ''}`}
                    type="button"
                    onClick={() => setSourcesDrawerOpen((prev) => !prev)}
                  >
                    <FileText size={13} />
                    <span>Sources ({totalSourceCount})</span>
                    <ChevronDown size={11} className={`sources-chevron ${sourcesDrawerOpen ? 'open' : ''}`} />
                  </button>
                </div>
              </div>

              {/* Sources Drawer (collapsible) */}
              {sourcesDrawerOpen && (
                <div className="sources-drawer">
                  <div className="source-list">
                    <div className={`source-section ${collapsedSections.manuals ? 'collapsed' : ''}`}>
                      <button className="section-header-btn" onClick={() => toggleSection('manuals')} type="button">
                        <div className="header-label-group">
                          {collapsedSections.manuals ? <ChevronRight size={14} /> : <ChevronDown size={14} />}
                          <span className="list-title">Validated Books</span>
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
                          <span className="list-title">Customer Packs</span>
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
              )}

              <div className="wiki-overlay-strip">
                <div className="wiki-overlay-strip-header">
                  <span>User Overlay</span>
                  {(isOverlayLoading || isOverlaySaving) && <span className="wiki-overlay-status">syncing...</span>}
                </div>
                <div className="wiki-overlay-strip-grid">
                  <div className="wiki-overlay-card">
                    <div className="wiki-overlay-card-title">
                      <Clock3 size={14} />
                      <span>Recent Position</span>
                    </div>
                    <div className="wiki-overlay-chip-list">
                      {recentOverlayItems.length > 0 ? recentOverlayItems.map((item) => (
                        <button
                          key={item.overlay_id}
                          type="button"
                          className="wiki-overlay-chip"
                          onClick={() => { void handleOverlayJump(item); }}
                        >
                          {item.resolved_target?.title || item.title || item.target_ref}
                        </button>
                      )) : <span className="wiki-overlay-empty">아직 기록이 없습니다.</span>}
                    </div>
                  </div>
                  <div className="wiki-overlay-card">
                    <div className="wiki-overlay-card-title">
                      <Star size={14} />
                      <span>Favorites</span>
                    </div>
                    <div className="wiki-overlay-chip-list">
                      {favoriteOverlayItems.length > 0 ? favoriteOverlayItems.map((item) => (
                        <button
                          key={item.overlay_id}
                          type="button"
                          className="wiki-overlay-chip"
                          onClick={() => { void handleOverlayJump(item); }}
                        >
                          {item.resolved_target?.title || item.title || item.target_ref}
                        </button>
                      )) : <span className="wiki-overlay-empty">즐겨찾기가 없습니다.</span>}
                    </div>
                  </div>
                  <div className="wiki-overlay-card">
                    <div className="wiki-overlay-card-title">
                      <ArrowRight size={14} />
                      <span>Next Reads</span>
                    </div>
                    <div className="wiki-overlay-chip-list">
                      {nextPlayItems.length > 0 ? nextPlayItems.map((item, index) => (
                        <button
                          key={`${item.source_target_ref}-${item.href}-${index}`}
                          type="button"
                          className="wiki-overlay-chip"
                          title={item.reason}
                          onClick={() => { void handleRelatedLinkClick(item); }}
                        >
                          {item.label}
                        </button>
                      )) : <span className="wiki-overlay-empty">행동 신호가 쌓이면 다음 읽기 경로가 제안됩니다.</span>}
                    </div>
                  </div>
                </div>
              </div>

              <div className="source-viewer-content">
                {preview.kind === 'empty' && (
                  <div className="empty-state">
                    <div className="empty-icon"><BookOpen size={48} className="text-dim" /></div>
                    <h4>선택된 문서가 없습니다</h4>
                    <p>채팅의 참조 태그를 눌러 원문을 확인하세요.</p>
                  </div>
                )}

                {preview.kind === 'loading' && (
                  <div className="empty-state">
                    <div className="loading-spinner-small"></div>
                    <h4>{preview.title}</h4>
                    <p>콘텐츠를 불러오는 중입니다.</p>
                  </div>
                )}

                {preview.kind === 'viewer' && (() => {
                  const previewTruth = truthSurfaceCopy(preview.meta);
                  return (
                    <div className="document-page animate-in">
                      <div className="doc-header">
                        <span className="doc-kicker">{previewTruth.label || preview.meta?.pack_label || 'Source Viewer'}</span>
                        <h2>{preview.title}</h2>
                      </div>
                      {preview.subtitle && <p className="doc-summary">{preview.subtitle}</p>}
                      {previewTruth.meta.length > 0 && (
                        <div className="doc-chip-row">
                          {previewTruth.meta.map((item) => (
                            <span key={item} className="doc-evidence-chip">{item}</span>
                          ))}
                        </div>
                      )}
                      {currentOverlayTarget && (
                        <div className="wiki-overlay-toolbar">
                          <button
                            type="button"
                            className={`wiki-overlay-action ${currentFavorite ? 'active' : ''}`}
                            onClick={() => { void handleToggleFavoriteCurrent(); }}
                            disabled={isOverlaySaving}
                          >
                            <Star size={14} />
                            <span>{currentFavorite ? 'Saved' : 'Save'}</span>
                          </button>
                          {currentOverlayTarget.kind === 'section' && (
                            <button
                              type="button"
                              className={`wiki-overlay-action ${currentSectionCheck ? 'active' : ''}`}
                              onClick={() => { void handleToggleSectionCheckCurrent(); }}
                              disabled={isOverlaySaving}
                            >
                              <Check size={14} />
                              <span>{currentSectionCheck ? 'Done' : 'Mark Done'}</span>
                            </button>
                          )}
                          <button
                            type="button"
                            className={`wiki-overlay-action ${noteOpen ? 'active' : ''}`}
                            onClick={() => setNoteOpen((value) => !value)}
                          >
                            <NotebookPen size={14} />
                            <span>Note</span>
                          </button>
                        </div>
                      )}
                      {currentOverlayTarget && noteOpen && (
                        <div className="wiki-note-panel">
                          <textarea
                            className="wiki-note-input"
                            value={noteDraft}
                            onChange={(event) => setNoteDraft(event.target.value)}
                            placeholder="이 문서, 엔터티, 섹션에 대한 개인 메모를 남기세요."
                          />
                          <div className="wiki-note-actions">
                            <button
                              type="button"
                              className="outline-btn"
                              onClick={() => { void handleSaveCurrentNote(); }}
                              disabled={isOverlaySaving}
                            >
                              {currentNote ? '노트 업데이트' : '노트 저장'}
                            </button>
                          </div>
                        </div>
                      )}
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
                          onLoad={resetParentScroll}
                        />
                      )}
                    </div>
                  );
                })()}

                {preview.kind === 'draft' && (() => {
                  const draftTruth = truthSurfaceCopy(preview.book ?? preview.draft);
                  return (
                    <div className="document-page animate-in">
                      <div className="doc-header">
                        <span className="doc-kicker">{draftTruth.label}</span>
                        <h2>{preview.title}</h2>
                      </div>
                      <p className="doc-summary">{preview.subtitle}</p>
                      <div className="doc-metadata">
                        <span>Quality {preview.draft.quality_score}</span>
                        <span>{preview.draft.playable_asset_count} assets</span>
                      </div>
                      {draftTruth.meta.length > 0 && (
                        <div className="doc-chip-row">
                          {draftTruth.meta.map((item) => (
                            <span key={item} className="doc-evidence-chip">{item}</span>
                          ))}
                        </div>
                      )}
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
                          onLoad={resetParentScroll}
                        />
                      ) : (
                        <div className="doc-section">
                          <h4>Pack Status</h4>
                          <p>{preview.draft.status}</p>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>

              <div className="panel-footer">
                {!activeDraft && (
                  <p className="footer-hint">문서를 업로드하면 검사와 북 생성을 시작합니다</p>
                )}
                <div className="footer-actions">
                  <button className="outline-btn" onClick={() => { void handleCapture(); }} type="button" disabled={!canCapture}>
                    <Cpu size={14} />
                    <span>{isCapturing ? 'Inspecting...' : 'Inspect Source'}</span>
                  </button>
                  <button className="primary-btn" onClick={() => { void handleNormalize(); }} type="button" disabled={!canNormalize}>
                    <span>{isNormalizing ? 'Building...' : 'Build Book'}</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          </Panel>
        </Group>
      </main>
    </div>
  );
}

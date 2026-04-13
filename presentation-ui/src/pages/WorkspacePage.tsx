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
} from 'lucide-react';
import gsap from 'gsap';
import './WorkspacePage.css';
import {
  type ChatCitation,
  type CustomerPackBook,
  type CustomerPackDraft,
  type DerivedAsset,
  type LibraryBook,
  type SessionSummary,
  type SourceMetaResponse,
  captureCustomerPackDraft,
  formatBytes,
  listCustomerPackDrafts,
  listSessions,
  loadCustomerPackBook,
  loadCustomerPackDraft,
  loadDataControlRoom,
  loadSession,
  deleteAllSessions,
  deleteSession,
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
  suggestedQueries?: string[];
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
  'OpenShift 클러스터 업그레이드 시 주의사항은?',
  'etcd 백업 및 복구 절차를 알려주세요',
  'Pod가 CrashLoopBackOff 상태일 때 해결 방법은?',
  'OpenShift에서 네트워크 정책을 설정하는 방법은?',
  '노드 리소스 부족 시 대처 방법은?',
  'RBAC 권한 설정 베스트 프랙티스는?',
  'Operator 업데이트 시 호환성 확인 방법은?',
  'OpenShift 인그레스 컨트롤러 설정 방법은?',
  '클러스터 인증서 갱신 절차는?',
  '스토리지 클래스 설정과 PV/PVC 관리 방법은?',
  'OpenShift 모니터링 스택 커스터마이징 방법은?',
  '멀티 클러스터 환경에서 ACM을 활용하는 방법은?',
];

function pickRandom<T>(pool: T[], count: number): T[] {
  const copy = [...pool];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, count);
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
          <button type="button" className="answer-code-action" onClick={() => { void handleCopy(); }}>
            {copied ? '복사됨' : '복사'}
          </button>
          <button type="button" className="answer-code-action" onClick={() => setWrapped((value) => !value)}>
            {wrapped ? '해제' : '줄바꿈'}
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
  onCitationClick,
}: {
  content: string;
  citations: ChatCitation[];
  onCitationClick: (citation: ChatCitation) => void;
}) {
  const [displayLength, setDisplayLength] = useState(0);

  // Real-time scroll sync during streaming — only if user hasn't scrolled up
  useEffect(() => {
    if (displayLength > 0) {
      const chatContainer = document.querySelector('.chat-messages');
      if (chatContainer) {
        const atBottom = chatContainer.scrollHeight - chatContainer.scrollTop - chatContainer.clientHeight < 80;
        if (atBottom) {
          requestAnimationFrame(() => {
            chatContainer.scrollTo({
              top: chatContainer.scrollHeight,
              behavior: 'auto'
            });
          });
        }
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

  return (
    <div className="assistant-answer">
      <div className="assistant-head">
        <div className="assistant-avatar">
          <Bot size={18} />
        </div>
        <span className="assistant-label">PlayBot</span>
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
    </div>
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

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const welcomeQuestions = useMemo(() => pickRandom(SUGGESTED_QUESTIONS, 4), [sessionId]);

  function handleChatScroll(): void {
    const el = chatMessagesRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    setUserScrolledUp(!atBottom);
  }

  function scrollToBottom(): void {
    const el = chatMessagesRef.current;
    if (el) {
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
          { id: makeId('a'), role: 'assistant' as const, content: turn.answer },
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
    if (messages.length > 0 && container) {
      const atBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 80;
      if (atBottom) {
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
    }
  }, [messages]);

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
          suggestedQueries: response.suggested_queries ?? [],
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
              <div className="chat-messages" ref={chatMessagesRef} onScroll={handleChatScroll}>
                {messages.length === 0 && (
                  <div className="chat-welcome">
                    <div className="welcome-icon">
                      <Sparkles size={36} />
                    </div>
                    <h2 className="welcome-title">무엇이든 질문하세요</h2>
                    <p className="welcome-subtitle">OpenShift 운영에 필요한 답변을 찾아드립니다</p>
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
                            onCitationClick={(citation) => {
                              void handleCitationClick(citation);
                            }}
                          />
                        ) : (
                          message.content
                        )}
                      </div>
                      {message.role !== 'assistant' && message.citations && message.citations.length > 0 && (
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

          {/* ── Right Panel: Knowledge Studio + Sources ── */}
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
                <h3>Knowledge Studio</h3>

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
              )}

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
                        onLoad={resetParentScroll}
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
                        onLoad={resetParentScroll}
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
                {!activeDraft && (
                  <p className="footer-hint">문서를 업로드하면 분석 및 플레이북 생성이 가능합니다</p>
                )}
                <div className="footer-actions">
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
            </div>
          </Panel>
        </Group>
      </main>
    </div>
  );
}

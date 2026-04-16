import { Fragment, useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ClipboardCopy,
  Loader2,
  Minus,
  XCircle,
} from 'lucide-react';
import type { ChatResponse, ChatTraceEvent } from '../lib/runtimeApi';
import {
  type ScorecardItem,
  type Severity,
  type Verdict,
  deriveSeverity,
  deriveVerdict,
  evaluateScorecard,
  summarizeScorecard,
} from './scorecardEval';
import './WorkspaceTracePanel.css';

interface WorkspaceTracePanelProps {
  query: string;
  events: ChatTraceEvent[];
  result?: ChatResponse | null;
  isSending: boolean;
}

type ViewMode = 'demo' | 'forensic';

/**
 * Backend whitelist of step IDs we know how to render. Other steps still show
 * up in the Forensic events table — only the timeline filters by this set so
 * the demo surface stays curated.
 */
const TIMELINE_STEPS: ReadonlyArray<string> = [
  'request_received',
  'route_query',
  'normalize_query',
  'rewrite_query',
  'decompose_query',
  'bm25_search',
  'vector_search',
  'fusion',
  'rerank',
  'retrieval',
  'context_assembly',
  'grounding_guard',
  'prompt_build',
  'llm_runtime',
  'deterministic_answer',
  'citation_finalize',
  'pipeline_complete',
  'stream_error',
];

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function asNumber(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function asString(value: unknown): string | null {
  return typeof value === 'string' && value.length > 0 ? value : null;
}

function formatMs(value: unknown, fallback = '–'): string {
  const num = asNumber(value);
  if (num === null) return fallback;
  if (num >= 1000) return `${(num / 1000).toFixed(2)}s`;
  if (num >= 100) return `${Math.round(num)}ms`;
  return `${num.toFixed(num < 10 ? 1 : 0)}ms`;
}

function shortSession(id: string | undefined): string {
  if (!id) return 'no-session';
  return id.length > 14 ? `${id.slice(0, 6)}…${id.slice(-4)}` : id;
}

interface DerivedStage {
  step: string;
  label: string;
  status: 'idle' | 'running' | 'done' | 'error';
  detail: string | null;
  durationMs: number | null;
  timestampMs: number | null;
  meta: Record<string, unknown>;
  ordinal: number;
}

/**
 * Collapse multiple events for the same step into a single stage entry.
 * Backend emits `running` then `done` for many steps; we keep the latest
 * status but accumulate the longest duration (`done` carries duration_ms).
 */
function collapseStages(events: ChatTraceEvent[]): DerivedStage[] {
  const byStep = new Map<string, DerivedStage>();
  events.forEach((event, index) => {
    if (!event.step) return;
    const existing = byStep.get(event.step);
    const status = ((): DerivedStage['status'] => {
      if (event.status === 'error') return 'error';
      if (event.status === 'done') return 'done';
      if (event.status === 'running') return 'running';
      return existing?.status ?? 'idle';
    })();
    const merged: DerivedStage = {
      step: event.step,
      label: event.label || existing?.label || event.step,
      status: existing?.status === 'error' ? 'error' : status,
      detail: event.detail ?? existing?.detail ?? null,
      durationMs: asNumber(event.duration_ms) ?? existing?.durationMs ?? null,
      timestampMs: asNumber(event.timestamp_ms) ?? existing?.timestampMs ?? null,
      meta: { ...(existing?.meta ?? {}), ...(event.meta ?? {}) },
      ordinal: existing?.ordinal ?? index,
    };
    byStep.set(event.step, merged);
  });
  return Array.from(byStep.values()).sort((a, b) => a.ordinal - b.ordinal);
}

function stageWidthFor(durationMs: number | null, maxDuration: number): number {
  const MIN = 92;
  const MAX = 220;
  if (durationMs === null || maxDuration <= 0) return MIN;
  const ratio = Math.min(1, Math.max(0.05, durationMs / maxDuration));
  return Math.round(MIN + (MAX - MIN) * ratio);
}

function severityToTone(severity: Severity): 'pass' | 'watch' | 'risk' | 'info' {
  if (severity === 'ok') return 'pass';
  if (severity === 'watch') return 'watch';
  if (severity === 'risk') return 'risk';
  return 'info';
}

function verdictToTone(verdict: Verdict): 'pass' | 'watch' | 'risk' | 'info' {
  switch (verdict) {
    case 'Grounded': return 'pass';
    case 'Review':   return 'watch';
    case 'NoAnswer': return 'risk';
    default:         return 'info';
  }
}

const SEVERITY_LABEL: Record<Severity, string> = {
  ok: '안정',
  watch: '주의',
  risk: '위험',
  pending: '대기',
};

const VERDICT_LABEL: Record<Verdict, string> = {
  Grounded: '근거 확보',
  Review: '검토 필요',
  NoAnswer: '답변 불가',
  Pending: '진행 중',
};

function ScoreIcon({ outcome }: { outcome: ScorecardItem['outcome'] }) {
  if (outcome === 'pass') return <Check size={14} aria-hidden="true" />;
  if (outcome === 'fail') return <XCircle size={14} aria-hidden="true" />;
  if (outcome === 'n/a') return <Minus size={14} aria-hidden="true" />;
  return <Loader2 size={14} className="wtp-spin" aria-hidden="true" />;
}

export default function WorkspaceTracePanel({
  query,
  events,
  result,
  isSending,
}: WorkspaceTracePanelProps) {
  const [view, setView] = useState<ViewMode>('demo');
  const [activeStep, setActiveStep] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Reset to Demo view + clear stage focus when a fresh turn begins.
  useEffect(() => {
    if (isSending) {
      setView('demo');
      setActiveStep(null);
      setCopied(false);
    }
  }, [isSending]);

  const stages = useMemo(() => collapseStages(events), [events]);
  const stageMap = useMemo(() => {
    const map = new Map<string, DerivedStage>();
    stages.forEach((s) => map.set(s.step, s));
    return map;
  }, [stages]);

  const verdict = deriveVerdict(result ?? null);
  const { severity, signals } = deriveSeverity(result ?? null, events);
  const scorecard = useMemo(() => evaluateScorecard(result ?? null, events), [result, events]);
  const scorecardSummary = useMemo(() => summarizeScorecard(scorecard), [scorecard]);

  const pipelineTrace = asRecord(result?.pipeline_trace);
  const retrievalTrace = asRecord(result?.retrieval_trace);
  const timings = asRecord(pipelineTrace.timings_ms);
  const totalMs = asNumber(timings.total);
  const selection = asRecord(pipelineTrace.selection);
  const selectedHits = asArray(selection.selected_hits)
    .map((hit) => asRecord(hit))
    .filter((hit) => Object.keys(hit).length > 0);
  const llm = asRecord(pipelineTrace.llm);
  const metrics = asRecord(retrievalTrace.metrics);
  const reranker = asRecord(retrievalTrace.reranker);
  const plan = asRecord(retrievalTrace.plan);
  const decomposed = asArray(retrievalTrace.decomposed_queries)
    .map((q) => (typeof q === 'string' ? q : ''))
    .filter(Boolean);

  const rewritten = asString(result?.rewritten_query);
  const showRewritten = Boolean(rewritten && rewritten !== query);

  // Pre-compute timeline real estate.
  const timelineStages = stages.filter(
    (s) => TIMELINE_STEPS.includes(s.step) || s.step === 'stream_error',
  );
  const maxDuration = Math.max(0, ...timelineStages.map((s) => s.durationMs ?? 0));

  const sessionId = result?.session_id;
  const responseKind = result?.response_kind;

  // ---- handlers ---------------------------------------------------------

  function toggleStage(step: string): void {
    setActiveStep((cur) => (cur === step ? null : step));
  }

  async function handleCopy(): Promise<void> {
    const payload = {
      query,
      rewritten_query: result?.rewritten_query ?? null,
      response_kind: responseKind ?? null,
      session_id: sessionId ?? null,
      verdict,
      severity,
      signals,
      scorecard,
      citations: result?.citations ?? [],
      warnings: result?.warnings ?? [],
      pipeline_trace: result?.pipeline_trace ?? null,
      retrieval_trace: result?.retrieval_trace ?? null,
      events,
    };
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch (err) {
      console.error('Trace copy failed', err);
    }
  }

  // ---- render -----------------------------------------------------------

  const hasAnyEvent = stages.length > 0 || isSending;

  return (
    <section className="wtp" aria-live="polite" aria-label="Test mode trace panel">
      <header className="wtp-header">
        <span className="wtp-kicker">TEST</span>
        <h2 className="wtp-title">Pipeline Audit</h2>
        <span className="wtp-session">session · {shortSession(sessionId)}</span>
        <div className="wtp-pill-group">
          <span className="wtp-pill" data-tone={verdictToTone(verdict)}>
            <span className="wtp-dot" aria-hidden="true" />
            <span>{VERDICT_LABEL[verdict]}</span>
          </span>
          <span className="wtp-pill" data-tone={severityToTone(severity)} title={signals.join(' · ') || '신호 없음'}>
            <span className="wtp-dot" aria-hidden="true" />
            <span>{SEVERITY_LABEL[severity]}</span>
          </span>
          <span className="wtp-pill" data-tone="info">
            <span>{formatMs(totalMs, isSending ? '…' : '–')}</span>
          </span>
          {responseKind ? (
            <span className="wtp-pill">
              <span>{responseKind}</span>
            </span>
          ) : null}
          <div className="wtp-toggle" role="group" aria-label="View mode">
            <button
              type="button"
              aria-pressed={view === 'demo'}
              onClick={() => setView('demo')}
            >
              Demo
            </button>
            <button
              type="button"
              aria-pressed={view === 'forensic'}
              onClick={() => setView('forensic')}
            >
              Forensic
            </button>
          </div>
        </div>
      </header>

      {/* --- Question banner ------------------------------------------ */}
      <div className="wtp-question">
        <div className="wtp-question-row">
          <span className="wtp-question-label">Question</span>
          <span className="wtp-question-text">{query || '아직 질문이 없습니다.'}</span>
        </div>
        {showRewritten ? (
          <div className="wtp-question-row">
            <span className="wtp-question-label">Rewritten</span>
            <span className="wtp-question-text is-rewritten">{rewritten}</span>
          </div>
        ) : null}
        {decomposed.length > 0 ? (
          <div className="wtp-question-row" style={{ alignItems: 'flex-start' }}>
            <span className="wtp-question-label">Subqueries</span>
            <div className="wtp-subqueries">
              {decomposed.map((sq, i) => (
                <span key={`${sq}-${i}`} className="wtp-subquery-chip">{sq}</span>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      {/* --- Stage timeline ------------------------------------------ */}
      <div className="wtp-timeline-wrap">
        <div className="wtp-timeline-head">
          <span className="wtp-section-title">
            Pipeline <strong>{timelineStages.length}/{TIMELINE_STEPS.length} stages</strong>
          </span>
          {isSending ? (
            <span className="wtp-pill" data-tone="info" aria-live="polite">
              <span className="wtp-pulse" aria-hidden="true" /> 스트리밍 중…
            </span>
          ) : null}
        </div>

        {timelineStages.length === 0 ? (
          <div className="wtp-empty">
            <strong>대기 중</strong>
            <span>질문을 보내면 백엔드 트레이스가 단계별로 채워집니다.</span>
          </div>
        ) : (
          <div className="wtp-timeline">
            {timelineStages.map((stage) => (
              <button
                key={stage.step}
                type="button"
                className="wtp-stage"
                data-status={stage.status}
                data-active={activeStep === stage.step}
                style={{ width: stageWidthFor(stage.durationMs, maxDuration) }}
                onClick={() => toggleStage(stage.step)}
                aria-pressed={activeStep === stage.step}
                aria-label={`${stage.label} ${stage.status} ${formatMs(stage.durationMs)}`}
              >
                <span className="wtp-stage-top">
                  <span className="wtp-stage-status" aria-hidden="true" />
                  <span className="wtp-stage-time">{formatMs(stage.durationMs)}</span>
                </span>
                <span className="wtp-stage-label">{stage.label}</span>
                <span className="wtp-stage-bar" aria-hidden="true">
                  <span
                    style={{
                      width: `${Math.min(100, Math.max(8, ((stage.durationMs ?? 0) / Math.max(1, maxDuration)) * 100))}%`,
                    }}
                  />
                </span>
              </button>
            ))}
          </div>
        )}

        {activeStep ? (() => {
          const stage = stageMap.get(activeStep);
          if (!stage) return null;
          const metaEntries = Object.entries(stage.meta);
          return (
            <div className="wtp-stage-detail">
              <div className="wtp-stage-detail-title">{stage.step} · {stage.status}</div>
              {stage.detail ? <div style={{ marginBottom: 10, color: '#f0f4fa' }}>{stage.detail}</div> : null}
              {metaEntries.length === 0 ? (
                <div className="wtp-stage-detail-empty">메타 데이터 없음</div>
              ) : (
                <dl className="wtp-stage-detail-body">
                  {metaEntries.map(([key, value]) => (
                    <Fragment key={key}>
                      <dt>{key}</dt>
                      <dd>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</dd>
                    </Fragment>
                  ))}
                </dl>
              )}
            </div>
          );
        })() : null}
      </div>

      {/* --- Cards ----------------------------------------------------- */}
      <div className="wtp-grid">
        {/* Citations */}
        <article className="wtp-card">
          <div className="wtp-card-header">
            <span className="wtp-card-title">Citations · 근거</span>
            <span className="wtp-card-meta">selected {selectedHits.length}</span>
          </div>
          {selectedHits.length === 0 ? (
            <p>아직 선택된 근거가 없습니다.</p>
          ) : (
            <div className="wtp-citations">
              {selectedHits.slice(0, 3).map((hit, idx) => {
                const matchingCitation = (result?.citations ?? []).find(
                  (c) => c.book_slug === hit.book_slug && (c.section_path ?? c.section) === hit.section,
                );
                const lane = (matchingCitation?.source_lane ?? 'official').toLowerCase();
                return (
                  <div key={`${hit.book_slug}-${idx}`} className="wtp-citation">
                    <div className="wtp-citation-top">
                      <span className="wtp-citation-index">#{idx + 1}</span>
                      <span className="wtp-citation-book">{String(hit.book_slug ?? 'unknown')}</span>
                      <span className="wtp-lane-badge" data-lane={lane}>
                        {lane}
                      </span>
                      <span className="wtp-citation-score">
                        score {asNumber(hit.fused_score)?.toFixed(3) ?? '–'}
                      </span>
                    </div>
                    <span className="wtp-citation-section">{String(hit.section ?? '')}</span>
                  </div>
                );
              })}
            </div>
          )}
        </article>

        {/* Retrieval & Reranker */}
        <article className="wtp-card">
          <div className="wtp-card-header">
            <span className="wtp-card-title">Retrieval · 검색</span>
            <span className="wtp-card-meta">
              {asNumber(plan.decomposed_query_count) ? `subq ${plan.decomposed_query_count}` : 'single q'}
            </span>
          </div>
          <div className="wtp-metric-row">
            <span>BM25 <strong>{asNumber(asRecord(metrics.bm25).count) ?? 0}</strong></span>
            <span>Vector <strong>{asNumber(asRecord(metrics.vector).count) ?? 0}</strong></span>
            <span>Hybrid <strong>{asNumber(asRecord(metrics.hybrid).count) ?? 0}</strong></span>
            <span>Reranked <strong>{asNumber(asRecord(metrics.reranked).count) ?? 0}</strong></span>
          </div>
          {reranker.applied ? (
            <div className="wtp-rerank">
              <div className="wtp-rerank-top">
                {String(reranker.top1_before ?? '?')}
                <span className="wtp-rerank-arrow">→</span>
                <strong>{String(reranker.top1_after ?? '?')}</strong>
                <span className="wtp-card-meta">
                  {reranker.top1_changed ? 'changed' : 'unchanged'}
                </span>
              </div>
              {asArray(reranker.rebalance_reasons).length > 0 ? (
                <div className="wtp-rerank-reasons">
                  {asArray(reranker.rebalance_reasons).slice(0, 6).map((reason, i) => (
                    <span key={`${String(reason)}-${i}`} className="wtp-reason-chip">
                      {String(reason)}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : (
            <p>리랭커 비활성 또는 미적용.</p>
          )}
        </article>

        {/* Generation */}
        <article className="wtp-card">
          <div className="wtp-card-header">
            <span className="wtp-card-title">Generation · 생성</span>
            <span className="wtp-card-meta">
              {formatMs(timings.llm_generate_total ?? timings.deterministic_total)}
            </span>
          </div>
          <h3>
            {String(llm.last_provider ?? llm.preferred_provider ?? (stageMap.has('deterministic_answer') ? 'Deterministic (rule)' : 'pending'))}
          </h3>
          <div className="wtp-metric-row">
            <span>Fallback <strong>{llm.last_fallback_used ? 'used' : 'no'}</strong></span>
            <span>
              Attempted <strong>{asArray(llm.last_attempted_providers).length || (llm.last_provider ? 1 : 0)}</strong>
            </span>
          </div>
          {asArray(llm.last_attempted_providers).length > 1 ? (
            <p>경로: {asArray(llm.last_attempted_providers).map(String).join(' → ')}</p>
          ) : null}
        </article>

        {/* Owner Scorecard */}
        <article className="wtp-card">
          <div className="wtp-card-header">
            <span className="wtp-card-title">Owner Scorecard · 계약 채점</span>
            <span className="wtp-card-meta">
              {scorecardSummary.pass}/{scorecardSummary.pass + scorecardSummary.fail} pass
              {scorecardSummary.na > 0 ? ` · ${scorecardSummary.na} n/a` : ''}
            </span>
          </div>
          <div className="wtp-scorecard">
            {scorecard.map((item) => (
              <div key={item.id} className="wtp-scoreitem" data-outcome={item.outcome}>
                <span className="wtp-score-icon" aria-hidden="true">
                  <ScoreIcon outcome={item.outcome} />
                </span>
                <span className="wtp-score-body">
                  <span className="wtp-score-label">
                    <span className="wtp-score-id">{item.id}</span>
                    {item.label}
                  </span>
                  <span className="wtp-score-rationale" title={item.question}>
                    {item.rationale}
                  </span>
                </span>
                <span className="wtp-score-mode">{item.mode}</span>
              </div>
            ))}
          </div>
          <div className="wtp-score-summary">
            <strong>
              {scorecardSummary.passRate === null
                ? '평가 대기'
                : `${Math.round(scorecardSummary.passRate * 100)}% pass`}
            </strong>
            <span>· promotion gate ≥ 90% (5턴 누적)</span>
          </div>
        </article>
      </div>

      {/* --- Forensic view ------------------------------------------- */}
      {view === 'forensic' ? (
        <div className="wtp-forensic">
          <div className="wtp-forensic-head">
            <span className="wtp-section-title">
              Forensic <strong>raw runtime payload</strong>
            </span>
            <button
              type="button"
              className="wtp-copy-btn"
              data-copied={copied}
              onClick={() => void handleCopy()}
              disabled={!hasAnyEvent}
            >
              {copied ? <CheckCircle2 size={14} /> : <ClipboardCopy size={14} />}
              {copied ? 'Copied' : 'Copy turn JSON'}
            </button>
          </div>

          {/* All events */}
          <div className="wtp-events-table" role="table" aria-label="All trace events">
            <span className="wtp-events-head" role="columnheader">t+ms</span>
            <span className="wtp-events-head" role="columnheader">dur</span>
            <span className="wtp-events-head" role="columnheader">step · status</span>
            <span className="wtp-events-head" role="columnheader">detail · meta</span>
            {events.length === 0 ? (
              <span className="wtp-events-cell" style={{ gridColumn: '1 / -1', color: 'var(--text-dim)' }}>
                no events
              </span>
            ) : (
              events.map((event, idx) => {
                const metaEntries = Object.entries(event.meta ?? {});
                const statusClass = event.status === 'error'
                  ? 'is-error'
                  : event.status === 'running'
                    ? 'is-running'
                    : '';
                return (
                  <Fragment key={`${event.step}-${idx}`}>
                    <span className="wtp-events-cell">{formatMs(event.timestamp_ms, '–')}</span>
                    <span className="wtp-events-cell">{formatMs(event.duration_ms, '–')}</span>
                    <span className={`wtp-events-cell is-step ${statusClass}`}>
                      {event.step}
                      <br />
                      <span style={{ color: 'var(--text-dim)', fontSize: '0.62rem' }}>
                        {event.status}
                      </span>
                    </span>
                    <span className="wtp-events-cell">
                      {event.label && event.label !== event.step ? (
                        <span style={{ color: '#f0f4fa' }}>{event.label}</span>
                      ) : null}
                      {event.detail ? (
                        <>
                          {event.label && event.label !== event.step ? <br /> : null}
                          {event.detail}
                        </>
                      ) : null}
                      {metaEntries.length > 0 ? (
                        <details>
                          <summary style={{ cursor: 'pointer', fontSize: '0.66rem', color: 'var(--text-dim)' }}>
                            meta · {metaEntries.length}
                          </summary>
                          <pre style={{ margin: 0, padding: '6px 0', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                            {JSON.stringify(event.meta, null, 2)}
                          </pre>
                        </details>
                      ) : null}
                    </span>
                  </Fragment>
                );
              })
            )}
          </div>

          {/* Timings */}
          {Object.keys(timings).length > 0 ? (
            <div className="wtp-timings">
              {Object.entries(timings).map(([key, ms]) => (
                <div key={key} className="wtp-timing">
                  <span>{key}</span>
                  <strong>{formatMs(ms)}</strong>
                </div>
              ))}
            </div>
          ) : null}

          {/* Raw blocks */}
          {result?.retrieval_trace ? (
            <details className="wtp-raw-block">
              <summary>
                <ChevronRight size={12} /> retrieval_trace
              </summary>
              <pre>{JSON.stringify(result.retrieval_trace, null, 2)}</pre>
            </details>
          ) : null}
          {result?.pipeline_trace ? (
            <details className="wtp-raw-block">
              <summary>
                <ChevronDown size={12} /> pipeline_trace
              </summary>
              <pre>{JSON.stringify(result.pipeline_trace, null, 2)}</pre>
            </details>
          ) : null}
          {result?.warnings && result.warnings.length > 0 ? (
            <div className="wtp-card">
              <div className="wtp-card-header">
                <span className="wtp-card-title" style={{ color: 'var(--wtp-risk)' }}>
                  <AlertTriangle size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} />
                  Warnings · {result.warnings.length}
                </span>
              </div>
              <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                {result.warnings.map((warn, i) => (
                  <li key={i}>{warn}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

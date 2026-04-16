/**
 * Pure-function scorer for the TEST-mode trace panel.
 *
 * Two responsibilities:
 *   1. Derive verdict + severity from the runtime payload (mirrors the
 *      backend chat_debug.build_turn_diagnosis severity ladder so the
 *      surface stays consistent with persisted audit logs).
 *   2. Auto-score the five OWNER_SCENARIO_SCORECARD items (owner-001 .. 005)
 *      using only what is present on the wire. Conservative on purpose —
 *      `pending`/`n/a` are first-class outcomes so a demo never claims a
 *      pass it cannot defend.
 *
 * No React imports. Safe to unit-test once a runner is in place.
 */
import type { ChatResponse, ChatTraceEvent, ChatCitation } from '../lib/runtimeApi';

export type Verdict = 'Grounded' | 'Review' | 'NoAnswer' | 'Pending';
export type Severity = 'ok' | 'watch' | 'risk' | 'pending';
export type ScoreOutcome = 'pass' | 'fail' | 'pending' | 'n/a';

export interface ScorecardItem {
  id: 'owner-001' | 'owner-002' | 'owner-003' | 'owner-004' | 'owner-005';
  label: string;
  question: string;
  outcome: ScoreOutcome;
  /** Short human-readable rationale for the chosen outcome. */
  rationale: string;
  /** auto = strict boolean; lenient = passes when minimum signal seen. */
  mode: 'auto' | 'lenient';
}

export interface SeverityResult {
  severity: Severity;
  signals: string[];
}

const FAILED_RESPONSE_KINDS = new Set(['no_answer']);

export function deriveVerdict(result: ChatResponse | null | undefined): Verdict {
  if (!result || !result.answer) return 'Pending';
  if (result.response_kind && FAILED_RESPONSE_KINDS.has(result.response_kind)) {
    return 'NoAnswer';
  }
  if (Array.isArray(result.warnings) && result.warnings.length > 0) {
    return 'Review';
  }
  return 'Grounded';
}

export function deriveSeverity(
  result: ChatResponse | null | undefined,
  events: ChatTraceEvent[],
): SeverityResult {
  const signals: string[] = [];
  let severity: Severity = 'ok';

  if (!result || !result.answer) {
    return { severity: 'pending', signals };
  }

  const warnings = Array.isArray(result.warnings) ? result.warnings : [];
  const groundingErr = events.find(
    (event) => event.step === 'grounding_guard' && event.status === 'error',
  );
  const otherErr = events.find(
    (event) => event.status === 'error' && event.step !== 'grounding_guard',
  );
  const citationCount = result.citations?.length ?? 0;

  if (warnings.length > 0) {
    severity = 'risk';
    signals.push(`경고 ${warnings.length}건`);
  }
  if (groundingErr) {
    severity = 'risk';
    signals.push('grounding_guard 차단');
  }
  if (severity === 'ok' && citationCount === 0) {
    severity = 'risk';
    signals.push('citation 0건');
  }
  if (severity === 'ok' && citationCount === 1) {
    severity = 'watch';
    signals.push('citation 1건');
  }
  if (severity === 'ok' && otherErr) {
    severity = 'watch';
    signals.push(`${otherErr.step} 오류`);
  }

  return { severity, signals };
}

function hasMixedLaneWithoutBoundary(citations: ChatCitation[]): boolean {
  return citations.some(
    (c) => c.source_lane === 'mixed' && (!c.boundary_truth || c.boundary_truth.length === 0),
  );
}

function isPrivateOrMixed(citation: ChatCitation): boolean {
  const lane = (citation.source_lane || '').toLowerCase();
  return lane === 'private' || lane === 'mixed' || lane === 'customer';
}

export function evaluateScorecard(
  result: ChatResponse | null | undefined,
  _events: ChatTraceEvent[],
): ScorecardItem[] {
  const items: ScorecardItem[] = [];
  const ready = Boolean(result && result.answer);
  const citations = result?.citations ?? [];
  const relatedLinks = result?.related_links ?? [];
  const relatedSections = result?.related_sections ?? [];
  const suggested = result?.suggested_queries ?? [];

  // owner-001 — value clarity. Per-turn we can only verify "the runtime fired
  // and returned an answer". The value statement itself is a manual judgement.
  if (!ready) {
    items.push({
      id: 'owner-001',
      label: '제품 가치 진술',
      question: '왜 이걸 사야 하나?',
      outcome: 'pending',
      rationale: '응답 대기 중',
      mode: 'lenient',
    });
  } else {
    const goodKind = !result?.response_kind || !FAILED_RESPONSE_KINDS.has(result.response_kind);
    items.push({
      id: 'owner-001',
      label: '제품 가치 진술',
      question: '왜 이걸 사야 하나?',
      outcome: goodKind ? 'pass' : 'fail',
      rationale: goodKind
        ? '런타임이 정상 응답 — 가치 진술은 시연자 멘트로 보강'
        : `response_kind=${result?.response_kind}`,
      mode: 'lenient',
    });
  }

  // owner-002 — connected wiki feel. Need citations + at least one related
  // navigation surface (links or sections).
  if (!ready) {
    items.push({
      id: 'owner-002',
      label: '연결된 위키 경험',
      question: '실제로 뭘 보게 되나?',
      outcome: 'pending',
      rationale: '응답 대기 중',
      mode: 'auto',
    });
  } else {
    const hasCitations = citations.length > 0;
    const hasNav = relatedLinks.length > 0 || relatedSections.length > 0;
    const ok = hasCitations && hasNav;
    items.push({
      id: 'owner-002',
      label: '연결된 위키 경험',
      question: '실제로 뭘 보게 되나?',
      outcome: ok ? 'pass' : 'fail',
      rationale: ok
        ? `citation ${citations.length}건 + related ${relatedLinks.length + relatedSections.length}건`
        : !hasCitations
          ? 'citation 없음'
          : 'related links/sections 없음',
      mode: 'auto',
    });
  }

  // owner-003 — source trace clickable. Every citation must have viewer_path,
  // book_slug, section_path. This is the strictest gate.
  if (!ready) {
    items.push({
      id: 'owner-003',
      label: '근거 추적성',
      question: '이 답이 어디서 왔나?',
      outcome: 'pending',
      rationale: '응답 대기 중',
      mode: 'auto',
    });
  } else if (citations.length === 0) {
    items.push({
      id: 'owner-003',
      label: '근거 추적성',
      question: '이 답이 어디서 왔나?',
      outcome: 'fail',
      rationale: 'citation 없음',
      mode: 'auto',
    });
  } else {
    const allClickable = citations.every(
      (c) => Boolean(c.viewer_path) && Boolean(c.book_slug) && Boolean(c.section_path),
    );
    items.push({
      id: 'owner-003',
      label: '근거 추적성',
      question: '이 답이 어디서 왔나?',
      outcome: allClickable ? 'pass' : 'fail',
      rationale: allClickable
        ? `${citations.length}건 모두 viewer 점프 가능`
        : 'viewer_path/book_slug/section_path 누락 citation 존재',
      mode: 'auto',
    });
  }

  // owner-004 — boundary discipline. Only meaningful when a private/customer/
  // mixed lane is involved. n/a for pure official-source turns.
  if (!ready) {
    items.push({
      id: 'owner-004',
      label: '소스 경계 라벨',
      question: '고객 문서도 넣을 수 있나?',
      outcome: 'pending',
      rationale: '응답 대기 중',
      mode: 'auto',
    });
  } else {
    const involvesPrivate = citations.some(isPrivateOrMixed);
    if (!involvesPrivate) {
      items.push({
        id: 'owner-004',
        label: '소스 경계 라벨',
        question: '고객 문서도 넣을 수 있나?',
        outcome: 'n/a',
        rationale: '이번 턴은 official 소스만 사용',
        mode: 'auto',
      });
    } else {
      const allLabeled = citations.every((c) => Boolean(c.source_lane));
      const boundaryOk = !hasMixedLaneWithoutBoundary(citations);
      const ok = allLabeled && boundaryOk;
      items.push({
        id: 'owner-004',
        label: '소스 경계 라벨',
        question: '고객 문서도 넣을 수 있나?',
        outcome: ok ? 'pass' : 'fail',
        rationale: ok
          ? '모든 citation에 source_lane 표기, mixed에는 boundary_truth 동반'
          : !allLabeled
            ? 'source_lane 라벨 누락'
            : 'mixed 차원에서 boundary_truth 누락',
        mode: 'auto',
      });
    }
  }

  // owner-005 — runtime supports navigation. Need both related navigation
  // AND at least one suggested next play.
  if (!ready) {
    items.push({
      id: 'owner-005',
      label: '운영 도움 (Next play)',
      question: '운영에 실제로 도움이 되나?',
      outcome: 'pending',
      rationale: '응답 대기 중',
      mode: 'auto',
    });
  } else {
    const hasNav = relatedLinks.length >= 1 || relatedSections.length >= 1;
    const hasNextPlay = suggested.length >= 1;
    const ok = hasNav && hasNextPlay;
    items.push({
      id: 'owner-005',
      label: '운영 도움 (Next play)',
      question: '운영에 실제로 도움이 되나?',
      outcome: ok ? 'pass' : 'fail',
      rationale: ok
        ? `related ${relatedLinks.length + relatedSections.length}건 + 추천 질문 ${suggested.length}건`
        : !hasNav
          ? 'related 경로 없음'
          : '추천 질문(next play) 없음',
      mode: 'auto',
    });
  }

  return items;
}

export interface ScorecardSummary {
  pass: number;
  fail: number;
  pending: number;
  na: number;
  total: number;
  /** pass-rate over evaluable items (excludes pending & n/a). 0..1 or null when nothing evaluable. */
  passRate: number | null;
}

export function summarizeScorecard(items: ScorecardItem[]): ScorecardSummary {
  const counts = { pass: 0, fail: 0, pending: 0, na: 0 };
  for (const item of items) {
    if (item.outcome === 'pass') counts.pass += 1;
    else if (item.outcome === 'fail') counts.fail += 1;
    else if (item.outcome === 'pending') counts.pending += 1;
    else counts.na += 1;
  }
  const evaluable = counts.pass + counts.fail;
  return {
    ...counts,
    total: items.length,
    passRate: evaluable === 0 ? null : counts.pass / evaluable,
  };
}

import { useEffect, useMemo, useRef, useState, type ChangeEvent, type ReactNode, type RefObject } from 'react';
import { BookOpen, ChevronDown, FileText, Highlighter, PanelRightClose, PenTool, Trash2, Upload } from 'lucide-react';
import { Panel, usePanelRef } from 'react-resizable-panels';
import type { WikiInkColorId, WikiInkStroke, WikiInkStyle, WikiInkTool } from '../../lib/runtimeApi';

const INK_STYLES: WikiInkStyle[] = [
  {
    id: 'cyan',
    label: 'Cyan',
    penColor: 'rgba(14, 165, 233, 0.96)',
    highlighterColor: 'rgba(34, 211, 238, 0.28)',
  },
  {
    id: 'amber',
    label: 'Amber',
    penColor: 'rgba(217, 119, 6, 0.96)',
    highlighterColor: 'rgba(250, 204, 21, 0.32)',
  },
  {
    id: 'rose',
    label: 'Rose',
    penColor: 'rgba(225, 29, 72, 0.96)',
    highlighterColor: 'rgba(251, 113, 133, 0.28)',
  },
  {
    id: 'violet',
    label: 'Violet',
    penColor: 'rgba(124, 58, 237, 0.96)',
    highlighterColor: 'rgba(167, 139, 250, 0.28)',
  },
  {
    id: 'lime',
    label: 'Lime',
    penColor: 'rgba(77, 124, 15, 0.96)',
    highlighterColor: 'rgba(163, 230, 53, 0.3)',
  },
];

type WorkspaceViewerPanelProps = {
  atlasCanvasActive: boolean;
  children: ReactNode;
  drawerContent: ReactNode;
  fileInputRef: RefObject<HTMLInputElement | null>;
  inkSurfaceKey: string;
  isInkSaving: boolean;
  isUploading: boolean;
  rightCollapsed: boolean;
  savedInkStrokes: WikiInkStroke[];
  sourcesDrawerOpen: boolean;
  testMode: boolean;
  totalSourceCount: number;
  uploadAccept: string;
  viewerSurfaceTitle: string;
  viewerVisionLabel: string;
  visionUploadLabel: string;
  visionSourcesLabel: string;
  onSaveInk: (strokes: WikiInkStroke[]) => void;
  onRightPanelCollapsedChange: (collapsed: boolean) => void;
  onToggleRightPanel: () => void;
  onToggleSourcesDrawer: () => void;
  onTriggerUpload: () => void;
  onUploadSelection: (event: ChangeEvent<HTMLInputElement>) => void;
  panelRef: ReturnType<typeof usePanelRef>;
};

export default function WorkspaceViewerPanel({
  atlasCanvasActive,
  children,
  drawerContent,
  fileInputRef,
  inkSurfaceKey,
  isInkSaving,
  isUploading,
  rightCollapsed,
  savedInkStrokes,
  sourcesDrawerOpen,
  testMode,
  totalSourceCount,
  uploadAccept,
  viewerSurfaceTitle,
  viewerVisionLabel,
  visionUploadLabel,
  visionSourcesLabel,
  onSaveInk,
  onRightPanelCollapsedChange,
  onToggleRightPanel,
  onToggleSourcesDrawer,
  onTriggerUpload,
  onUploadSelection,
  panelRef,
}: WorkspaceViewerPanelProps) {
  const stageRef = useRef<HTMLDivElement | null>(null);
  const inkPopoverRef = useRef<HTMLDivElement | null>(null);
  const drawingRef = useRef<{ pointerId: number; stroke: WikiInkStroke } | null>(null);
  const [inkEnabled, setInkEnabled] = useState(false);
  const [inkPopoverOpen, setInkPopoverOpen] = useState(false);
  const [inkTool, setInkTool] = useState<WikiInkTool>('pen');
  const [inkColorId, setInkColorId] = useState<WikiInkColorId>('cyan');
  const [inkStrokes, setInkStrokes] = useState<WikiInkStroke[]>(savedInkStrokes);
  const [activeInkStroke, setActiveInkStroke] = useState<WikiInkStroke | null>(null);
  const [inkViewport, setInkViewport] = useState({ width: 0, height: 0 });
  const atlasInkAvailable = atlasCanvasActive && !rightCollapsed;
  const activeInkStyle = INK_STYLES.find((style) => style.id === inkColorId) ?? INK_STYLES[0];
  const ActiveInkIcon = inkTool === 'highlighter' ? Highlighter : PenTool;
  const activeInkLabel = inkTool === 'highlighter' ? '형광펜' : '잉크펜';
  const activeInkColor = inkTool === 'highlighter' ? activeInkStyle.highlighterColor : activeInkStyle.penColor;
  const savedInkSnapshot = useMemo(() => JSON.stringify(savedInkStrokes), [savedInkStrokes]);
  const currentInkSnapshot = useMemo(() => JSON.stringify(inkStrokes), [inkStrokes]);
  const hasInkChanges = currentInkSnapshot !== savedInkSnapshot;
  const inkStatusLabel = isInkSaving
    ? '저장 중'
    : hasInkChanges
      ? '변경됨'
      : inkStrokes.length > 0
        ? '저장됨'
        : '비어 있음';

  useEffect(() => {
    if (!atlasInkAvailable) {
      setInkEnabled(false);
      setInkPopoverOpen(false);
    }
  }, [atlasInkAvailable]);

  useEffect(() => {
    setInkEnabled(false);
    setInkPopoverOpen(false);
    setInkStrokes(savedInkStrokes);
    setActiveInkStroke(null);
    drawingRef.current = null;
  }, [inkSurfaceKey, savedInkSnapshot]);

  useEffect(() => {
    if (!inkPopoverOpen) {
      return undefined;
    }

    const handlePointerDown = (event: PointerEvent): void => {
      const targetNode = event.target;
      if (!(targetNode instanceof Node)) {
        return;
      }
      if (inkPopoverRef.current?.contains(targetNode)) {
        return;
      }
      setInkPopoverOpen(false);
    };

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        setInkPopoverOpen(false);
      }
    };

    document.addEventListener('pointerdown', handlePointerDown);
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [inkPopoverOpen]);

  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) {
      return undefined;
    }

    const updateViewport = (): void => {
      const width = Math.max(Math.ceil(stage.getBoundingClientRect().width), 1);
      const height = Math.max(stage.scrollHeight, stage.clientHeight, 1);
      setInkViewport((current) => (
        current.width === width && current.height === height
          ? current
          : { width, height }
      ));
    };

    updateViewport();
    const resizeObserver = new ResizeObserver(() => {
      updateViewport();
    });
    resizeObserver.observe(stage);
    window.addEventListener('resize', updateViewport);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener('resize', updateViewport);
    };
  }, [children, atlasInkAvailable, inkSurfaceKey]);

  function pointFromEvent(
    event: React.PointerEvent<SVGSVGElement>,
  ): { x: number; y: number } {
    const rect = event.currentTarget.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  }

  function handleInkPointerDown(event: React.PointerEvent<SVGSVGElement>): void {
    const canStartInk = event.pointerType === 'mouse' ? event.button === 0 : event.isPrimary;
    if (!inkEnabled || !canStartInk) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    const { x, y } = pointFromEvent(event);
    const stroke: WikiInkStroke = {
      path: `M ${x.toFixed(1)} ${y.toFixed(1)}`,
      tool: inkTool,
      style: activeInkStyle,
    };
    drawingRef.current = { pointerId: event.pointerId, stroke };
    setActiveInkStroke(stroke);
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function handleInkPointerMove(event: React.PointerEvent<SVGSVGElement>): void {
    const activeStroke = drawingRef.current;
    if (!inkEnabled || !activeStroke || activeStroke.pointerId !== event.pointerId) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    const { x, y } = pointFromEvent(event);
    activeStroke.stroke = {
      ...activeStroke.stroke,
      path: `${activeStroke.stroke.path} L ${x.toFixed(1)} ${y.toFixed(1)}`,
    };
    setActiveInkStroke(activeStroke.stroke);
  }

  function finalizeInkPointer(event: React.PointerEvent<SVGSVGElement>): void {
    const activeStroke = drawingRef.current;
    if (!activeStroke || activeStroke.pointerId !== event.pointerId) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    if (activeStroke.stroke.path.trim()) {
      setInkStrokes((current) => [...current, activeStroke.stroke]);
    }
    drawingRef.current = null;
    setActiveInkStroke(null);
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  }

  function handleInkPrimaryAction(): void {
    if (!inkEnabled) {
      setInkEnabled(true);
      setInkPopoverOpen(true);
      return;
    }
    setInkPopoverOpen((current) => !current);
  }

  return (
    <Panel
      id="workspace-right"
      panelRef={panelRef}
      defaultSize={40}
      minSize={24}
      collapsible={true}
      collapsedSize={0}
      onResize={(panelSize) => onRightPanelCollapsedChange(panelSize.asPercentage <= 0.5)}
      className="workspace-panel-item"
    >
      <div className={`panel-inner workspace-viewer-panel no-border-radius-left ${rightCollapsed ? 'panel-collapsed-inner' : ''}`}>
        <div className={`panel-header ${testMode ? '' : 'viewer-panel-toolbar'}`} style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <div className="panel-header-copy" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '12px' }}>
            {testMode && <div className="header-icon"><BookOpen size={18} /></div>}
            <h3 style={{ margin: 0 }}>{viewerSurfaceTitle}</h3>
            <span className={`viewer-vision-badge ${testMode ? 'viewer-vision-badge-test' : ''}`} style={{ marginTop: 0 }}>
              {viewerVisionLabel}
            </span>
          </div>

          <div className={`viewer-utility-bar ${testMode ? '' : 'viewer-utility-bar-minimal'}`} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: 0, border: 'none', background: 'transparent' }}>
            <button
              className={`viewer-utility-btn ${sourcesDrawerOpen ? 'active' : ''}`}
              type="button"
              onClick={onToggleSourcesDrawer}
            >
              <FileText size={13} />
              <span>{`${visionSourcesLabel} (${totalSourceCount})`}</span>
              <ChevronDown size={11} className={`sources-chevron ${sourcesDrawerOpen ? 'open' : ''}`} />
            </button>
            <button
              className="viewer-utility-btn"
              type="button"
              onClick={onTriggerUpload}
              disabled={isUploading}
            >
              <Upload size={13} />
              <span>{visionUploadLabel}</span>
            </button>
            {atlasInkAvailable && (
              <div
                ref={inkPopoverRef}
                className={`viewer-ink-popover-anchor ${inkPopoverOpen ? 'open' : ''}`}
              >
                <button
                  className={`viewer-utility-btn ${inkEnabled ? 'active' : ''}`}
                  type="button"
                  onClick={handleInkPrimaryAction}
                  title={inkEnabled ? '잉크 도구 열기' : '낙서 시작'}
                >
                  <ActiveInkIcon size={13} />
                  <span>{activeInkLabel}</span>
                  <span
                    className="viewer-ink-current-dot"
                    style={{ ['--ink-current-color' as string]: activeInkColor }}
                    aria-hidden="true"
                  />
                </button>
                {inkPopoverOpen && (
                  <div className="viewer-ink-popover" role="dialog" aria-label="Ink tools">
                    <div className="viewer-ink-popover-header">
                      <strong>Ink Tools</strong>
                      <button
                        type="button"
                        className="viewer-ink-popover-close"
                        onClick={() => setInkPopoverOpen(false)}
                      >
                        완료
                      </button>
                    </div>
                    <div className={`viewer-ink-status ${hasInkChanges ? 'is-dirty' : ''}`}>
                      <span>{inkStatusLabel}</span>
                      <span>{`${inkStrokes.length} stroke${inkStrokes.length === 1 ? '' : 's'}`}</span>
                    </div>
                    <div className="viewer-ink-mode-switch" role="group" aria-label="Ink tools">
                      <button
                        type="button"
                        className={`viewer-ink-mode-btn ${inkTool === 'pen' ? 'active' : ''}`}
                        onClick={() => {
                          setInkEnabled(true);
                          setInkTool('pen');
                        }}
                      >
                        <PenTool size={13} />
                        잉크펜
                      </button>
                      <button
                        type="button"
                        className={`viewer-ink-mode-btn ${inkTool === 'highlighter' ? 'active' : ''}`}
                        onClick={() => {
                          setInkEnabled(true);
                          setInkTool('highlighter');
                        }}
                      >
                        <Highlighter size={13} />
                        형광펜
                      </button>
                    </div>
                    <div className="viewer-ink-color-row" role="group" aria-label="Ink colors">
                      {INK_STYLES.map((style) => (
                        <button
                          key={style.id}
                          type="button"
                          className={`viewer-ink-color-swatch ${inkColorId === style.id ? 'active' : ''}`}
                          style={{
                            ['--ink-swatch-color' as string]:
                              inkTool === 'highlighter' ? style.highlighterColor : style.penColor,
                          }}
                          title={`${inkTool === 'highlighter' ? '형광펜' : '잉크펜'} ${style.label}`}
                          aria-label={`${inkTool === 'highlighter' ? '형광펜' : '잉크펜'} ${style.label}`}
                          onClick={() => {
                            setInkEnabled(true);
                            setInkColorId(style.id);
                          }}
                        />
                      ))}
                    </div>
                    <div className="viewer-ink-popover-actions">
                      <button
                        className="viewer-utility-btn"
                        type="button"
                        onClick={() => {
                          setInkStrokes([]);
                          setActiveInkStroke(null);
                          drawingRef.current = null;
                        }}
                        disabled={inkStrokes.length === 0 && !activeInkStroke}
                        title="낙서 지우기"
                      >
                        <Trash2 size={13} />
                        <span>지우기</span>
                      </button>
                      <button
                        className="viewer-utility-btn"
                        type="button"
                        onClick={() => onSaveInk(inkStrokes)}
                        disabled={!hasInkChanges || isInkSaving}
                        title="낙서 저장"
                      >
                        <span>{isInkSaving ? '저장 중' : '저장'}</span>
                      </button>
                      <button
                        className="viewer-utility-btn"
                        type="button"
                        onClick={() => {
                          setInkEnabled(false);
                          setInkPopoverOpen(false);
                        }}
                        title="낙서 종료"
                      >
                        <span>끄기</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
            <button className="header-action-btn" type="button" onClick={onToggleRightPanel} title="Close panel">
              <PanelRightClose size={14} />
            </button>
          </div>
        </div>

        <input
          ref={fileInputRef}
          className="file-input-hidden"
          type="file"
          accept={uploadAccept}
          onChange={onUploadSelection}
        />

        {sourcesDrawerOpen && (
          <>
            <div
              className="sources-drawer-scrim"
              onClick={onToggleSourcesDrawer}
              aria-hidden="true"
            />
            <div className="sources-drawer-overlay" role="dialog" aria-label="Sources">
              {drawerContent}
            </div>
          </>
        )}

        <div className="source-viewer-content viewer-surface">
          <div
            ref={stageRef}
            className={`atlas-ink-stage ${inkEnabled ? 'is-inking' : ''}`}
          >
            {children}
            {atlasInkAvailable && inkViewport.width > 0 && inkViewport.height > 0 && (
              <svg
                className={`atlas-ink-overlay ${inkEnabled ? 'is-enabled' : ''} atlas-ink-overlay--${inkTool}`}
                width={inkViewport.width}
                height={inkViewport.height}
                viewBox={`0 0 ${inkViewport.width} ${inkViewport.height}`}
                onPointerDown={handleInkPointerDown}
                onPointerMove={handleInkPointerMove}
                onPointerUp={finalizeInkPointer}
                onPointerCancel={finalizeInkPointer}
                onPointerLeave={finalizeInkPointer}
              >
                {inkStrokes.map((stroke, index) => (
                  <path
                    key={`ink-path-${index}`}
                    className={`atlas-ink-path atlas-ink-path--${stroke.tool}`}
                    d={stroke.path}
                    style={{
                      stroke: stroke.tool === 'highlighter' ? stroke.style.highlighterColor : stroke.style.penColor,
                    }}
                  />
                ))}
                {activeInkStroke && (
                  <path
                    className={`atlas-ink-path atlas-ink-path-active atlas-ink-path--${activeInkStroke.tool}`}
                    d={activeInkStroke.path}
                    style={{
                      stroke: activeInkStroke.tool === 'highlighter'
                        ? activeInkStroke.style.highlighterColor
                        : activeInkStroke.style.penColor,
                    }}
                  />
                )}
              </svg>
            )}
          </div>
        </div>
      </div>
    </Panel>
  );
}

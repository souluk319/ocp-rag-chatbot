import type { ChangeEvent, ReactNode, RefObject } from 'react';
import { BookOpen, ChevronDown, FileText, PanelRightClose, Upload } from 'lucide-react';
import { Panel, usePanelRef } from 'react-resizable-panels';

type WorkspaceViewerPanelProps = {
  children: ReactNode;
  drawerContent: ReactNode;
  fileInputRef: RefObject<HTMLInputElement | null>;
  isUploading: boolean;
  rightCollapsed: boolean;
  sourcesDrawerOpen: boolean;
  testMode: boolean;
  totalSourceCount: number;
  uploadAccept: string;
  viewerSurfaceTitle: string;
  viewerVisionLabel: string;
  visionUploadLabel: string;
  visionSourcesLabel: string;
  onRightPanelCollapsedChange: (collapsed: boolean) => void;
  onToggleRightPanel: () => void;
  onToggleSourcesDrawer: () => void;
  onTriggerUpload: () => void;
  onUploadSelection: (event: ChangeEvent<HTMLInputElement>) => void;
  panelRef: ReturnType<typeof usePanelRef>;
};

export default function WorkspaceViewerPanel({
  children,
  drawerContent,
  fileInputRef,
  isUploading,
  rightCollapsed,
  sourcesDrawerOpen,
  testMode,
  totalSourceCount,
  uploadAccept,
  viewerSurfaceTitle,
  viewerVisionLabel,
  visionUploadLabel,
  visionSourcesLabel,
  onRightPanelCollapsedChange,
  onToggleRightPanel,
  onToggleSourcesDrawer,
  onTriggerUpload,
  onUploadSelection,
  panelRef,
}: WorkspaceViewerPanelProps) {
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
          {children}
        </div>
      </div>
    </Panel>
  );
}

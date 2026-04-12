import { useState, useEffect, useRef } from 'react';
import { 
  Group, 
  Panel, 
  Separator 
} from 'react-resizable-panels';
import { Link } from 'react-router-dom';
import { 
  Upload, 
  Plus, 
  Search, 
  FileText, 
  ChevronDown, 
  Send, 
  BookOpen, 
  Cpu, 
  Database,
  ArrowRight,
  Sparkles,
  Link as LinkIcon
} from 'lucide-react';
import gsap from 'gsap';
import './WorkspacePage.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tags?: string[];
}

interface SourceFile {
  id: string;
  name: string;
  size: string;
  type: string;
  selected: boolean;
}

export default function WorkspacePage() {
  const [sources, setSources] = useState<SourceFile[]>([
    { id: '1', name: 'ocp_install_guide_v4.20.pdf', size: '2.4 MB', type: 'PDF', selected: true },
    { id: '2', name: 'etcd_backup_restore.md', size: '12 KB', type: 'Markdown', selected: true },
    { id: '3', name: 'cluster_monitoring_setup.json', size: '45 KB', type: 'JSON', selected: false },
  ]);

  const [messages, setMessages] = useState<Message[]>([
    { 
      id: 'm1', 
      role: 'assistant', 
      content: '반갑습니다! Playbook Studio에 오신 것을 환영합니다. 로드된 4.20 매뉴얼북을 기반으로 무엇을 도와드릴까요?',
    },
    {
      id: 'm2',
      role: 'user',
      content: 'etcd 백업 절차에 대해 알려줘.'
    },
    {
      id: 'm3',
      role: 'assistant',
      content: 'OpenShift 4.20 환경에서 etcd 백업은 클러스터 복구를 위한 필수 절차입니다. 주로 `cluster-etcd-operator`를 통해 관리되며, `etcd-snapshot-backup.sh` 스크립트를 사용하여 스냅샷을 생성합니다.',
      tags: ['etcd_backup_restore.md', 'Source Document']
    }
  ]);

  const [activeSource, setActiveSource] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.workspace-panel-item', {
        opacity: 0,
        y: 20,
        stagger: 0.1,
        duration: 0.8,
        ease: 'power3.out',
        delay: 0.2
      });
      
      gsap.from('.bokeh-bg', {
        opacity: 0,
        scale: 0.8,
        duration: 2,
        ease: 'power2.out'
      });
    }, containerRef);
    return () => ctx.revert();
  }, []);

  const handleUploadClick = () => {
    setIsUploading(true);
    setTimeout(() => {
      const newFile: SourceFile = {
        id: Math.random().toString(36).substr(2, 9),
        name: `new_uploaded_document_${sources.length + 1}.pdf`,
        size: '1.2 MB',
        type: 'PDF',
        selected: true
      };
      setSources([...sources, newFile]);
      setIsUploading(false);
    }, 1500);
  };

  const handleTagClick = (tag: string) => {
    setActiveSource(tag);
    // GSAP animation for the right panel highlight
    gsap.fromTo('.source-viewer-content', 
      { backgroundColor: 'rgba(0, 209, 255, 0.1)' },
      { backgroundColor: 'transparent', duration: 1 }
    );
  };

  return (
    <div className="workspace-wrapper" ref={containerRef}>
      {/* Background Orbs */}
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
            <span>OCP v4.20 Active</span>
          </div>
          <button className="nav-btn">Export Library</button>
        </div>
      </header>

      <main className="workspace-content">
        <Group autoSaveId="workspace-layout" orientation="horizontal" className="main-panel-group">
          
          {/* LEFT PANEL: Source Manager */}
          <Panel defaultSize={20} minSize={15} className="workspace-panel-item">
            <div className="panel-inner glass-panel no-border-radius-right">
              <div className="panel-header">
                <div className="header-icon"><Database size={18} /></div>
                <h3>Knowledge Source</h3>
              </div>
              
              <div className="source-picker-container">
                <div className="picker-label">Enterprise Pack</div>
                <div className="custom-select">
                  <span>OpenShift Container Platform v4.20</span>
                  <ChevronDown size={16} />
                </div>
              </div>

              <div className="upload-zone" onClick={handleUploadClick}>
                {isUploading ? (
                  <div className="loading-spinner-small"></div>
                ) : (
                  <>
                    <Upload size={24} className="upload-icon" />
                    <p>Click to add or drag file</p>
                    <span className="text-dim">PDF, Markdown, JSON</span>
                  </>
                )}
              </div>

              <div className="source-list">
                <div className="list-title">Active Documents ({sources.length})</div>
                {sources.map(file => (
                  <div key={file.id} className={`source-item ${file.selected ? 'selected' : ''}`}>
                    <div className="item-main">
                      <FileText size={16} className="file-icon" />
                      <span className="file-name">{file.name}</span>
                    </div>
                    <div className="item-meta">{file.size} · {file.type}</div>
                  </div>
                ))}
              </div>
            </div>
          </Panel>

          <Separator className="custom-resize-handle">
            <div className="handle-visual" />
          </Separator>

          {/* MIDDLE PANEL: Chat Engine */}
          <Panel defaultSize={45} minSize={30} className="workspace-panel-item">
            <div className="panel-inner chat-area">
              <div className="chat-messages">
                {messages.map((m) => (
                  <div key={m.id} className={`message-row ${m.role}`}>
                    <div className="message-bubble glass-panel">
                      <div className="message-content">{m.content}</div>
                      {m.tags && (
                        <div className="message-tags">
                          {m.tags.map(tag => (
                            <button 
                              key={tag} 
                              className="citation-tag"
                              onClick={() => handleTagClick(tag)}
                            >
                              <LinkIcon size={12} />
                              {tag}
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
                  <input type="text" placeholder="질문을 입력하거나 문서를 탐색하세요..." />
                  <button className="send-btn">
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </div>
          </Panel>

          <Separator className="custom-resize-handle">
            <div className="handle-visual" />
          </Separator>

          {/* RIGHT PANEL: Knowledge Studio */}
          <Panel defaultSize={35} minSize={20} className="workspace-panel-item">
            <div className="panel-inner glass-panel no-border-radius-left">
              <div className="panel-header">
                <div className="header-icon"><BookOpen size={18} /></div>
                <h3>Knowledge Studio</h3>
              </div>
              
              <div className="source-viewer-content">
                {activeSource ? (
                  <div className="document-page animate-in">
                    <div className="doc-header">
                      <span className="doc-kicker">Playbook Source</span>
                      <h2>{activeSource}</h2>
                    </div>
                    <div className="doc-body">
                      <p className="doc-summary">이 문서는 OpenShift 4.20의 <strong>etcd 백업 및 복구</strong> 가이드를 기반으로 생성된 플레이북입니다.</p>
                      <div className="doc-section">
                        <h4>1. Prerequisites</h4>
                        <ul>
                          <li>접근 권한: cluster-admin</li>
                          <li>필요 도구: oc CLI</li>
                        </ul>
                      </div>
                      <div className="doc-section">
                        <h4>2. Backup Procedure</h4>
                        <div className="code-block-mock">
                          $ oc debug node/node-name<br/>
                          $ /usr/local/bin/cluster-etcd-operator-snapshot-backup.sh /assets/backup
                        </div>
                        <p>위 명령어를 실행하면 `/assets/backup` 경로에 스냅샷이 저장됩니다.</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="empty-state">
                    <div className="empty-icon"><BookOpen size={48} className="text-dim" /></div>
                    <h4>선택된 문서가 없습니다</h4>
                    <p>채팅의 출처 태그를 클릭하거나<br/>왼쪽 리스트에서 문서를 선택해 라이브러리를 구축하세요.</p>
                  </div>
                )}
              </div>
              
              <div className="panel-footer">
                <button className="outline-btn">
                  <Cpu size={14} />
                  <span>Analyze Content</span>
                </button>
                <button className="primary-btn">
                  <span>Create Playbook</span>
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

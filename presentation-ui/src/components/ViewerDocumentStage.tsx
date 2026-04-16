import { useEffect, useRef } from 'react';

export interface ViewerDocumentPayload {
  html: string;
  inlineStyles: string[];
  bodyClassName: string;
  interactionPolicy?: {
    codeCopy?: boolean;
    codeWrapToggle?: boolean;
    recentPositionTracking?: boolean;
    anchorNavigation?: boolean;
  };
}

const VIEWER_READER_POLISH = `
  :host {
    display: block;
    color: #161b22;
  }

  .viewer-root {
    min-height: 100%;
  }

  .viewer-root main {
    width: min(100%, 1320px) !important;
    padding: 18px 24px 48px !important;
  }

  .viewer-root .reader-layout {
    grid-template-columns: minmax(0, 1fr) minmax(260px, 320px) !important;
    gap: 22px !important;
    margin-top: 18px !important;
  }

  .viewer-root .reader-main,
  .viewer-root .section-list,
  .viewer-root .section-body,
  .viewer-root .table-wrap,
  .viewer-root .code-block,
  .viewer-root table {
    min-width: 0;
  }

  .viewer-root .section-list {
    gap: 0 !important;
  }

  .viewer-root .section-card + .section-card,
  .viewer-root .embedded-section + .embedded-section {
    margin-top: 32px !important;
    padding-top: 32px !important;
  }

  .viewer-root .section-header {
    gap: 8px !important;
    padding-bottom: 14px !important;
    margin-bottom: 18px !important;
  }

  .viewer-root .section-header h2 {
    max-width: 18ch;
  }

  .viewer-root .section-body {
    gap: 18px !important;
  }

  .viewer-root .section-body p,
  .viewer-root .section-body li,
  .viewer-root .section-body td {
    color: #2f3742 !important;
  }

  .viewer-root .figure-block {
    margin: 22px 0 !important;
    padding: 18px !important;
  }

  .viewer-root .figure-block img {
    box-shadow: 0 18px 40px rgba(17, 20, 24, 0.08);
  }

  .viewer-root .table-wrap {
    overflow-x: auto !important;
  }

  .viewer-root .code-block pre {
    overflow-x: auto !important;
  }

  .viewer-root .code-block.is-wrapped pre,
  .viewer-root .code-block.is-wrapped code {
    white-space: pre-wrap !important;
    word-break: break-word !important;
  }

  @media (max-width: 1100px) {
    .viewer-root .reader-layout {
      grid-template-columns: 1fr !important;
    }

    .viewer-root .reader-sidebar {
      position: static !important;
    }
  }
`;

function isViewerHref(href: string): boolean {
  try {
    const parsed = new URL(href, window.location.origin);
    return (
      parsed.pathname.startsWith('/playbooks/')
      || parsed.pathname.startsWith('/docs/ocp/')
      || parsed.pathname.startsWith('/wiki/entities/')
      || parsed.pathname.startsWith('/wiki/figures/')
    );
  } catch {
    return false;
  }
}

export default function ViewerDocumentStage({
  viewerDocument,
  onNavigateViewerPath,
  className,
}: {
  viewerDocument: ViewerDocumentPayload;
  onNavigateViewerPath?: (viewerPath: string) => void;
  className?: string;
}) {
  const hostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) {
      return;
    }
    const root = host.shadowRoot ?? host.attachShadow({ mode: 'open' });
    root.replaceChildren();

    viewerDocument.inlineStyles.forEach((styleText) => {
      const style = document.createElement('style');
      style.textContent = styleText;
      root.appendChild(style);
    });

    const polishStyle = document.createElement('style');
    polishStyle.textContent = VIEWER_READER_POLISH;
    root.appendChild(polishStyle);

    const wrapper = document.createElement('div');
    wrapper.className = ['viewer-root', 'is-embedded', viewerDocument.bodyClassName].filter(Boolean).join(' ');
    wrapper.innerHTML = viewerDocument.html;
    root.appendChild(wrapper);

    root.querySelectorAll('a[href]').forEach((node) => {
      const anchor = node as HTMLAnchorElement;
      const href = anchor.getAttribute('href') ?? '';
      if (!href || href.startsWith('#') || isViewerHref(href)) {
        return;
      }
      if (!anchor.hasAttribute('target')) {
        anchor.setAttribute('target', '_blank');
      }
      anchor.setAttribute('rel', 'noreferrer');
    });

    const handleClick = async (event: Event): Promise<void> => {
      const target = event.target as HTMLElement | null;
      const anchor = target?.closest('a[href]') as HTMLAnchorElement | null;
      if (anchor) {
        const href = anchor.getAttribute('href') ?? '';
        if (href.startsWith('#')) {
          event.preventDefault();
          const targetId = href.slice(1);
          const targetNode = root.getElementById(targetId) ?? root.querySelector(`[id="${CSS.escape(targetId)}"]`);
          if (targetNode instanceof HTMLElement) {
            targetNode.scrollIntoView({ block: 'start', behavior: 'smooth' });
          }
          return;
        }
        if (href && isViewerHref(href) && onNavigateViewerPath) {
          event.preventDefault();
          const parsed = new URL(href, window.location.origin);
          onNavigateViewerPath(`${parsed.pathname}${parsed.search}${parsed.hash}`);
          return;
        }
      }

      const button = target?.closest('button');
      if (!button) {
        return;
      }
      if (button.classList.contains('copy-button')) {
        const copyPayload = button.getAttribute('data-copy') ?? '""';
        const defaultLabel = button.getAttribute('data-label-default') ?? '복사';
        try {
          const text = JSON.parse(copyPayload) as string;
          if (navigator.clipboard?.writeText) {
            await navigator.clipboard.writeText(text);
          }
          button.textContent = '복사됨';
          button.classList.add('is-copied');
          window.setTimeout(() => {
            button.textContent = defaultLabel;
            button.classList.remove('is-copied');
          }, 1400);
        } catch {
          button.textContent = '실패';
          window.setTimeout(() => {
            button.textContent = defaultLabel;
          }, 1400);
        }
        return;
      }
      if (button.classList.contains('icon-button')) {
        const codeBlock = button.closest('.code-block');
        if (!codeBlock) {
          return;
        }
        codeBlock.classList.toggle('is-wrapped');
        const wrapped = codeBlock.classList.contains('is-wrapped');
        button.setAttribute('aria-pressed', wrapped ? 'true' : 'false');
        button.textContent = wrapped
          ? button.getAttribute('data-label-active') ?? '줄바꿈 해제'
          : button.getAttribute('data-label-default') ?? '줄바꿈';
      }
    };

    root.addEventListener('click', handleClick);
    return () => {
      root.removeEventListener('click', handleClick);
    };
  }, [onNavigateViewerPath, viewerDocument]);

  return <div className={className} ref={hostRef} />;
}

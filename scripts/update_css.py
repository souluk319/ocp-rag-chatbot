import sys, re

content = open("c:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/viewer_page.py", "r", encoding="utf-8").read()

new_css = """<style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
          
          :root {
            color-scheme: light;
            --bg: #ffffff;
            --panel: #ffffff;
            --panel-soft: #f9fafb;
            --line: #e2e8f0;
            --line-strong: #cbd5e1;
            --ink: #0f172a;
            --ink-soft: #334155;
            --muted: #64748b;
            --accent: #2563eb;
            --accent-soft: #eff6ff;
            --border-radius: 12px;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
          }
          * {
            box-sizing: border-box;
          }
          body {
            margin: 0;
            background: var(--bg);
            color: var(--ink);
            font-family: 'Inter', 'Noto Sans KR', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
          body.is-embedded {
            background: #ffffff;
            margin: 0;
            padding: 0;
          }
          main {
            width: min(1000px, calc(100vw - 48px));
            max-width: none;
            margin: 0 auto;
            padding: 40px 0 80px;
          }
          body.is-embedded main {
            width: 100%;
            margin: 0;
            padding: 32px 48px;
            min-height: 100%;
          }
          .study-document-embedded {
            min-height: 100%;
            padding: 0;
            border: 0;
            background: transparent;
            box-shadow: none;
          }
          
          /* Hero Section */
          .hero {
            margin: 0 0 50px;
            padding: 0 0 40px;
            border-bottom: 1px solid var(--line);
          }
          body.is-embedded .hero {
            margin: 0 0 32px;
            padding: 0;
            border-bottom: 0;
          }
          .hero-main {
            display: grid;
            gap: 16px;
            max-width: 80ch;
          }
          .eyebrow {
            color: var(--accent);
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
          }
          h1 {
            margin: 0;
            font-size: clamp(2.2rem, 4.5vw, 3.2rem);
            line-height: 1.15;
            letter-spacing: -0.02em;
            font-weight: 800;
            color: var(--ink);
          }
          body.is-embedded h1 {
            font-size: clamp(1.8rem, 3.8vw, 2.6rem);
            margin-bottom: 8px;
          }
          .summary {
            margin: 0;
            color: var(--ink-soft);
            font-size: 1.125rem;
            line-height: 1.7;
          }
          .hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            margin-top: 12px;
          }
          .meta-pill, .hero-meta a {
            display: inline-flex;
            align-items: center;
            min-height: 32px;
            padding: 0 16px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: var(--panel-soft);
            color: var(--ink-soft);
            font-size: 0.875rem;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s ease;
          }
          .meta-pill:hover, .hero-meta a:hover {
            background: #f1f5f9;
            border-color: var(--line-strong);
            color: var(--ink);
          }
          .meta-pill-accent {
            color: var(--accent);
            border-color: #bfdbfe;
            background: var(--accent-soft);
          }
          
          /* Layout */
          .reader-layout {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(260px, 300px);
            justify-content: space-between;
            gap: 80px;
            align-items: start;
          }
          .reader-main {
            min-width: 0;
          }
          .reader-sidebar {
            position: sticky;
            top: 40px;
            display: grid;
            gap: 32px;
          }
          
          /* Auto-hide sidebar if embedded */
          body.is-embedded .reader-sidebar {
            display: none !important;
          }
          body.is-embedded .reader-layout {
            grid-template-columns: 1fr;
            max-width: 900px;
            margin: 0 auto;
          }
          
          /* Quick Navigation */
          .reader-outline-card {
            display: grid;
            gap: 16px;
            padding: 24px;
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            background: var(--panel);
            box-shadow: var(--shadow-sm);
          }
          .reader-outline-label {
            color: var(--ink);
            font-size: 0.875rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
          .reader-outline-links {
            display: grid;
            gap: 14px;
          }
          .reader-outline-link {
            display: block;
            color: var(--muted);
            text-decoration: none;
            font-size: 0.9375rem;
            line-height: 1.5;
            padding-left: 14px;
            border-left: 2px solid var(--line);
            transition: all 0.2s ease;
          }
          .reader-outline-link:hover {
            color: var(--accent);
            border-left-color: var(--accent);
          }
          
          /* Sections */
          .section-list {
            display: grid;
            gap: 80px;
          }
          .section-card {
            scroll-margin-top: 40px;
            border: 0;
            background: transparent;
            box-shadow: none;
          }
          body.is-embedded .section-list {
            gap: 40px;
          }
          body.is-embedded .section-card + .section-card {
            padding-top: 40px;
            border-top: 1px solid var(--line);
          }
          .section-card.is-target {
            padding: 40px;
            margin: -40px;
            border-radius: calc(var(--border-radius) + 12px);
            background: var(--accent-soft);
            border: 1px solid #bfdbfe;
          }
          body.is-embedded .section-card.is-target {
            margin: 0;
            padding: 32px 40px;
            border-left: 4px solid var(--accent);
            border-radius: 0 16px 16px 0;
            border-top: 0;
            border-bottom: 0;
            border-right: 0;
            background: linear-gradient(90deg, #eff6ff 0%, #ffffff 100%);
            box-shadow: none;
          }
          
          .section-header {
            margin-bottom: 32px;
          }
          .section-meta {
            color: var(--accent);
            font-size: 0.9375rem;
            font-weight: 600;
            margin-bottom: 12px;
            display: block;
          }
          .section-card h2 {
            margin: 0;
            font-size: clamp(1.75rem, 3.5vw, 2.25rem);
            font-weight: 700;
            color: var(--ink);
            line-height: 1.3;
            letter-spacing: -0.01em;
          }
          
          /* Body Text */
          .section-body {
            display: grid;
            gap: 28px;
          }
          .section-body p, .section-body li, .section-body td {
            font-size: 1.0625rem;
            line-height: 1.85;
            color: var(--ink-soft);
            margin: 0;
          }
          .section-body h3 {
            margin: 40px 0 16px;
            font-size: 1.375rem;
            font-weight: 700;
            color: var(--ink);
            letter-spacing: -0.01em;
          }
          .section-body a {
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
            border-bottom: 1px solid transparent;
            transition: border-bottom-color 0.2s ease;
          }
          .section-body a:hover {
            border-bottom-color: var(--accent);
          }
          
          /* Lists */
          .section-body ul, .section-body ol, .procedure-list {
            padding-left: 28px;
            margin: 0;
            display: grid;
            gap: 16px;
          }
          
          /* Code blocks */
          .section-body code {
            display: inline-block;
            padding: 0.125rem 0.375rem;
            border-radius: 6px;
            background: #f1f5f9;
            border: 1px solid var(--line);
            color: #db2777;
            font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
          }
          .code-block {
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            overflow: hidden;
            background: #0f172a;
            box-shadow: var(--shadow-sm);
            margin: 16px 0;
          }
          .code-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 20px;
            border-bottom: 1px solid #1e293b;
            background: #0f172a;
          }
          .code-label {
            color: #94a3b8;
            font-size: 0.8125rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
          .code-actions {
            display: flex;
            gap: 12px;
          }
          .icon-button {
            width: 32px;
            height: 32px;
            padding: 0;
            border: 0;
            border-radius: 6px;
            background: transparent;
            color: #94a3b8;
            cursor: pointer;
            display: grid;
            place-items: center;
            transition: all 0.2s ease;
          }
          .icon-button:hover {
            background: #1e293b;
            color: #f8fafc;
          }
          .code-block pre {
            margin: 0;
            padding: 24px;
            overflow-x: auto;
            color: #f8fafc;
            font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
            font-size: 0.875rem;
            line-height: 1.7;
          }
          .code-block code {
            background: transparent;
            border: 0;
            padding: 0;
            color: inherit;
          }
          .code-block.overflow-toggle.is-wrapped pre,
          .code-block.overflow-wrap pre {
            white-space: pre-wrap;
            overflow-x: hidden;
            overflow-y: auto;
            overflow-wrap: anywhere;
          }
          .code-block.overflow-toggle.is-wrapped code,
          .code-block.overflow-wrap code {
            white-space: inherit;
            overflow-wrap: inherit;
          }
          
          /* Notes */
          .note-card {
            padding: 24px 32px;
            margin: 16px 0;
            border-radius: var(--border-radius);
            background: var(--panel-soft);
            border-left: 4px solid var(--muted);
          }
          .note-title {
            font-weight: 700;
            color: var(--ink);
            margin-bottom: 12px;
            font-size: 1rem;
          }
          .note-warning, .note-caution { border-left-color: #f59e0b; background: #fffbeb; }
          .note-warning .note-title, .note-caution .note-title { color: #b45309; }
          .note-note { border-left-color: #3b82f6; background: #eff6ff; }
          .note-note .note-title { color: #1d4ed8; }
          .note-important { border-left-color: #8b5cf6; background: #f5f3ff; }
          .note-important .note-title { color: #5b21b6; }
          .note-tip { border-left-color: #10b981; background: #ecfdf5; }
          .note-tip .note-title { color: #047857; }
          
          /* Tables */
          .table-wrap {
            overflow-x: auto;
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-sm);
            margin: 24px 0;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            background: var(--panel);
          }
          th, td {
            padding: 16px 24px;
            text-align: left;
            border-bottom: 1px solid var(--line);
          }
          th {
            background: var(--panel-soft);
            font-weight: 600;
            font-size: 0.9375rem;
            color: var(--ink);
          }
          tr:last-child td { border-bottom: 0; }
          
          /* Figures */
          .figure-block {
            margin: 40px 0;
            padding: 32px;
            background: var(--panel-soft);
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            text-align: center;
          }
          .figure-block img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: var(--shadow-sm);
            margin: 0 auto;
          }
          .figure-block figcaption {
            margin-top: 20px;
            font-size: 0.9375rem;
            color: var(--muted);
          }
          
          /* Embedded Source Overrides */
          .embedded-origin-row {
            margin-bottom: 32px;
          }
          .embedded-origin-link {
            display: inline-flex;
            align-items: center;
            height: 36px;
            padding: 0 20px;
            border-radius: 999px;
            background: var(--panel-soft);
            border: 1px solid var(--line);
            color: var(--ink-soft);
            text-decoration: none;
            font-size: 0.9375rem;
            font-weight: 500;
            transition: all 0.2s ease;
          }
          .embedded-origin-link:hover {
            background: var(--line);
            color: var(--ink);
          }
          
          @media (max-width: 1100px) {
            .reader-layout {
              grid-template-columns: 1fr;
              padding: 0 24px;
            }
            .reader-sidebar {
              display: none;
            }
          }
          .wiki-parent-card, .wiki-card {
            border: 1px solid var(--line);
            border-radius: var(--border-radius);
            padding: 24px;
            background: var(--panel);
            box-shadow: var(--shadow-sm);
            margin: 16px 0;
          }
          .wiki-parent-card p, .wiki-card p {
            color: var(--ink-soft);
            line-height: 1.7;
          }
          .wiki-parent-card a, .wiki-card a {
            color: var(--ink);
            font-weight: 600;
            text-decoration: none;
          }
          .wiki-parent-eyebrow {
            color: var(--accent);
            font-size: 0.8125rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 8px;
          }
</style>""".replace('{', '{{').replace('}', '}}')

# Replace exact CSS block
new_content = re.sub(r"<style>.*?</style>", new_css, content, flags=re.DOTALL)

# Inject JS safely
script_tag = """
        <script>
          if (window.self !== window.top) {
            document.body.classList.add("is-embedded");
          }
        </script>
"""
if "window.self !== window.top" not in new_content:
    new_content = new_content.replace("</body>", script_tag + "\n      </body>")

with open("c:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/app/viewer_page.py", "w", encoding="utf-8") as f:
    f.write(new_content)
    
print("File successfully updated using exact regex replacement.")

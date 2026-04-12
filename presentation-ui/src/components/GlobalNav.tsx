import { Languages } from 'lucide-react';
import './GlobalNav.css';

export default function GlobalNav() {
  return (
    <nav className="global-nav">
      <div className="nav-actions">
        <button className="lang-toggle-btn glass-panel" title="Switch Language">
          <Languages size={20} />
          <span>KOR</span>
        </button>
      </div>
    </nav>
  );
}

import { BrowserRouter as Router, Navigate, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import ProjectDetailsPage from './pages/ProjectDetailsPage';
import WorkspacePage from './pages/WorkspacePage';
import PlaybookLibraryPage from './pages/PlaybookLibraryPage';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/details" element={<ProjectDetailsPage />} />
        <Route path="/studio" element={<WorkspacePage />} />
        <Route path="/workspace" element={<Navigate to="/studio" replace />} />
        <Route path="/playbook-library" element={<PlaybookLibraryPage />} />
        <Route path="/playbook-library/control-tower" element={<PlaybookLibraryPage />} />
        <Route path="/playbook-library/repository" element={<PlaybookLibraryPage />} />
      </Routes>
    </Router>
  );
}

export default App;

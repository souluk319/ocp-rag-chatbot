import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import ProjectDetailsPage from './pages/ProjectDetailsPage';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/details" element={<ProjectDetailsPage />} />
      </Routes>
    </Router>
  );
}

export default App;

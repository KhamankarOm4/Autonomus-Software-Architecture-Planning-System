import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';
import Home from './pages/Home/Home';
import NewProject from './pages/NewProject/NewProject';
import Dashboard from './pages/Dashboard/Dashboard';
import Results from './pages/Results/Results';
import { ProjectProvider } from './context/ProjectContext';
import './index.css';

function App() {
  return (
    <ProjectProvider>
      <Router>
        <div className="app-container">
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/new-project" element={<NewProject />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/results" element={<Results />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ProjectProvider>
  );
}

export default App;

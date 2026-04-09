import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectContext } from '../../context/ProjectContext';
import './Dashboard.css';

const Dashboard = () => {
  const { isLoading, error, analysisResult, projectData, resetProject } = useProjectContext();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !error && analysisResult) {
      navigate('/results');
    }
  }, [isLoading, error, analysisResult, navigate]);

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="error-container">
          <h2>Analysis Failed</h2>
          <p>{error}</p>
          <button className="retry-btn" onClick={() => navigate('/new-project')}>
            Go Back & Retry
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
          <div className="spinner"></div>
          <h2>Agents are analyzing your request...</h2>
          <p>
            Please wait while our AI agents collaborate to generate a comprehensive
            architecture plan for your {projectData.mode} approach. This may take a minute.
          </p>
        </div>
      </div>
    );
  }

  // If we end up here without anything active
  return (
    <div className="dashboard-page">
      <div className="dashboard-loading" style={{ border: '1px solid var(--border-color)', boxShadow: 'none' }}>
        <h2>No Active Analysis</h2>
        <p>Start a new project to see the dashboard in action.</p>
        <button 
          className="retry-btn" 
          style={{ background: 'var(--accent-cyan)', color: 'var(--bg-primary)', marginTop: '2rem' }} 
          onClick={() => navigate('/new-project')}
        >
          Start Planning
        </button>
      </div>
    </div>
  );
};

export default Dashboard;

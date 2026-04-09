import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Layers, FileText, BarChart2, AlertTriangle, Database } from 'lucide-react';
import { useProjectContext } from '../../context/ProjectContext';
import './Results.css';

const Results = () => {
  const { analysisResult, projectData } = useProjectContext();
  const navigate = useNavigate();

  useEffect(() => {
    if (!analysisResult) {
      navigate('/dashboard');
    }
  }, [analysisResult, navigate]);

  if (!analysisResult) return null;

  const { analysis_report, architecture_plan, ast_summary, warning, graph } = analysisResult;

  return (
    <div className="results-page">
      <div className="results-header">
        <div>
          <h1 className="results-title">Analysis Results</h1>
          <p className="results-subtitle">
            Project: <strong style={{ color: 'var(--text-primary)' }}>{projectData.name}</strong> •
            Mode: <strong style={{ color: 'var(--text-primary)', textTransform: 'capitalize' }}>{projectData.mode}</strong>
          </p>
        </div>
        <div className="results-actions">
          <button className="btn-outline" onClick={() => window.print()}>
            Export PDF
          </button>
          <button
            className="btn-outline"
            style={{ borderColor: 'var(--accent-cyan)', color: 'var(--accent-cyan)' }}
            onClick={() => navigate('/new-project')}
          >
            New Analysis
          </button>
        </div>
      </div>

      {warning && (
        <div className="warning-banner">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', fontWeight: 600 }}>
            <AlertTriangle size={18} /> Warning
          </div>
          <p>{warning}</p>
        </div>
      )}

      <div className="results-grid">
        <div className="results-main">
          {architecture_plan && (
            <div className="result-card">
              <div className="result-card-title">
                <Layers size={24} /> Architecture Plan
              </div>
              <div className="markdown-body">
                <ReactMarkdown>{architecture_plan}</ReactMarkdown>
              </div>
            </div>
          )}

          {analysis_report && (
            <div className="result-card">
              <div className="result-card-title">
                <FileText size={24} /> Detailed Analysis Report
              </div>
              <div className="markdown-body">
                <ReactMarkdown>{analysis_report}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>

        <div className="results-sidebar">
          {ast_summary && (
            <div className="result-card">
              <div className="result-card-title">
                <BarChart2 size={24} /> AST Summary
              </div>
              <div className="markdown-body">
                <pre style={{ margin: 0, fontSize: '0.85rem' }}>{ast_summary}</pre>
              </div>
            </div>
          )}

          {/* Simple Graph Representation */}
          {graph && graph.nodes && graph.nodes.length > 0 && (
            <div className="result-card">
              <div className="result-card-title">
                <Database size={24} /> Architecture Entities
              </div>
              <ul style={{ paddingLeft: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                {graph.nodes.map(node => (
                  <li key={node.id} style={{ marginBottom: '0.5rem' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>{node.label}</strong>
                    {node.description && <span style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{node.description}</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Results;

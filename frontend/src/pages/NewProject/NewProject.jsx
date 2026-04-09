import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ArrowRight, Layers, Upload, CheckCircle } from 'lucide-react';
import { useProjectContext } from '../../context/ProjectContext';
import { runGreenfieldAnalysis, runBrownfieldAnalysis } from '../../services/api';
import './NewProject.css';

const STEPS = [
  { id: 1, label: 'Project Info', sub: 'Basic details' },
  { id: 2, label: 'Mode & Domain', sub: 'Project type' },
  { id: 3, label: 'Requirements', sub: 'Specifications' },
  { id: 4, label: 'Review', sub: 'Confirm & submit' },
];

const slideVariants = {
  enter: (dir) => ({ x: dir > 0 ? 60 : -60, opacity: 0 }),
  center: { x: 0, opacity: 1, transition: { duration: 0.35, ease: 'easeOut' } },
  exit: (dir) => ({ x: dir > 0 ? -60 : 60, opacity: 0, transition: { duration: 0.25 } }),
};

const NewProject = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { projectData, updateProjectData, setAnalysisResult, setIsLoading, setError } = useProjectContext();

  const [step, setStep] = useState(1);
  const [dir, setDir] = useState(1);
  const [localData, setLocalData] = useState({
    name: projectData.name || '',
    mode: location.state?.mode || projectData.mode || 'greenfield',
    requirements: projectData.requirements || '',
    input: projectData.input || '',
  });

  const update = (field, value) => setLocalData((p) => ({ ...p, [field]: value }));

  const goNext = () => {
    setDir(1);
    setStep((s) => Math.min(s + 1, 4));
  };

  const goBack = () => {
    if (step === 1) return navigate('/');
    setDir(-1);
    setStep((s) => s - 1);
  };

  const canContinue = () => {
    if (step === 1) return localData.name.trim().length > 0;
    if (step === 2) return true;
    if (step === 3) {
      const val = localData.mode === 'greenfield' ? localData.requirements : localData.input;
      return val.trim().length > 0;
    }
    return true;
  };

  const handleSubmit = async () => {
    updateProjectData(localData);
    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);
    navigate('/dashboard');

    try {
      let result;
      if (localData.mode === 'greenfield') {
        result = await runGreenfieldAnalysis(localData.requirements);
      } else {
        result = await runBrownfieldAnalysis(localData.input);
      }
      setAnalysisResult(result);
      navigate('/results');
    } catch (err) {
      const detail = err?.detail || (typeof err === 'string' ? err : 'Analysis failed. Please try again.');
      setError(detail);
      navigate('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="new-project-page">
      <div className="new-project-header">
        <h1>Set Up Your <span className="cyan">Architecture Project</span></h1>
        <p>Configure your project settings to get personalized architecture recommendations</p>
      </div>

      {/* Stepper */}
      <div className="stepper">
        {STEPS.map((s) => (
          <div
            key={s.id}
            className={`stepper-item ${step === s.id ? 'active' : step > s.id ? 'done' : ''}`}
          >
            <div className="stepper-circle">
              {step > s.id ? <CheckCircle size={18} /> : s.id}
            </div>
            <div className="stepper-label">
              <div className="stepper-label-title">{s.label}</div>
              <div className="stepper-label-sub">{s.sub}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Form Card */}
      <AnimatePresence mode="wait" custom={dir}>
        <motion.div
          key={step}
          className="form-card"
          custom={dir}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
        >
          {step === 1 && (
            <>
              <div className="form-card-title">Project Information</div>
              <div className="form-group">
                <label className="form-label">Project Name</label>
                <input
                  className="form-input"
                  type="text"
                  placeholder="e.g. E-Commerce Platform"
                  value={localData.name}
                  onChange={(e) => update('name', e.target.value)}
                />
                <p className="form-hint">Give your project a descriptive name</p>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="form-card-title">Mode & Domain</div>
              <div className="form-group">
                <label className="form-label">Select Project Mode</label>
                <div className="mode-select-grid">
                  {[
                    {
                      value: 'greenfield',
                      icon: <Layers size={20} />,
                      title: 'Greenfield',
                      desc: 'Start from scratch with fresh architecture planning',
                    },
                    {
                      value: 'brownfield',
                      icon: <Upload size={20} />,
                      title: 'Brownfield',
                      desc: 'Analyze and evolve your existing codebase',
                    },
                  ].map((m) => (
                    <button
                      key={m.value}
                      type="button"
                      className={`mode-select-card ${localData.mode === m.value ? 'selected' : ''}`}
                      onClick={() => update('mode', m.value)}
                    >
                      <div className="mode-select-icon">{m.icon}</div>
                      <div className="mode-select-title">{m.title}</div>
                      <div className="mode-select-desc">{m.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <div className="form-card-title">
                {localData.mode === 'greenfield' ? 'Define Requirements' : 'Provide Codebase Input'}
              </div>
              {localData.mode === 'greenfield' ? (
                <div className="form-group">
                  <label className="form-label">Functional & Non-Functional Requirements</label>
                  <textarea
                    className="form-textarea"
                    placeholder="e.g. Build a scalable multi-tenant SaaS platform with REST APIs, PostgreSQL, JWT auth, Redis caching, and real-time notifications..."
                    value={localData.requirements}
                    onChange={(e) => update('requirements', e.target.value)}
                  />
                  <p className="form-hint">Describe what your system needs to do and any constraints</p>
                </div>
              ) : (
                <div className="form-group">
                  <label className="form-label">Codebase Description or File Path</label>
                  <textarea
                    className="form-textarea"
                    placeholder="Paste a code snippet, describe your existing system, or provide a local folder path..."
                    value={localData.input}
                    onChange={(e) => update('input', e.target.value)}
                  />
                  <p className="form-hint">Provide code snippets, descriptions, or a local file path to analyze</p>
                </div>
              )}
            </>
          )}

          {step === 4 && (
            <>
              <div className="form-card-title">Review & Confirm</div>
              <div className="review-section">
                <div className="review-section-title">Project Name</div>
                <div className="review-value">{localData.name}</div>
              </div>
              <div className="review-section">
                <div className="review-section-title">Mode</div>
                <div className="review-value" style={{ textTransform: 'capitalize' }}>{localData.mode}</div>
              </div>
              <div className="review-section">
                <div className="review-section-title">
                  {localData.mode === 'greenfield' ? 'Requirements' : 'Input'}
                </div>
                <div className="review-value" style={{ maxHeight: 120, overflowY: 'auto' }}>
                  {localData.mode === 'greenfield' ? localData.requirements : localData.input}
                </div>
              </div>
            </>
          )}

          <div className="form-nav">
            <button className="btn-back" onClick={goBack}>
              <ArrowLeft size={16} /> Back
            </button>
            {step < 4 ? (
              <button className="btn-continue" onClick={goNext} disabled={!canContinue()}>
                Continue <ArrowRight size={16} />
              </button>
            ) : (
              <button className="btn-continue" onClick={handleSubmit}>
                Start Analysis <ArrowRight size={16} />
              </button>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default NewProject;

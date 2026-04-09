import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Layers,
  TrendingUp,
  Zap,
  GitMerge,
  BarChart2,
  ShieldCheck,
  FileSearch,
  FileEdit,
  Upload,
  Brain,
} from 'lucide-react';
import './Home.css';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: 'easeOut' },
  }),
};

const AGENT_CARDS = [
  {
    icon: <FileSearch size={22} />,
    iconClass: 'cyan',
    title: 'Analysis Agent',
    desc: 'Intelligent agent that deeply analyzes your codebase, identifying patterns, dependencies, and potential issues.',
  },
  {
    icon: <Brain size={22} />,
    iconClass: 'blue',
    title: 'Planning Agent',
    desc: 'Strategic agent that recommends architecture patterns, suggests improvements, and creates evolution roadmaps.',
  },
  {
    icon: <GitMerge size={22} />,
    iconClass: 'amber',
    title: 'Agentic Collaboration',
    desc: 'Watch both agents work together in real-time, sharing insights and building comprehensive architecture plans.',
  },
  {
    icon: <Layers size={22} />,
    iconClass: 'green',
    title: 'Greenfield & Brownfield',
    desc: 'Whether starting fresh or evolving existing systems, our agents adapt to your project context.',
  },
  {
    icon: <BarChart2 size={22} />,
    iconClass: 'purple',
    title: 'Visual Architecture',
    desc: 'Interactive diagrams showing layered architecture, module dependencies, and system boundaries.',
  },
  {
    icon: <ShieldCheck size={22} />,
    iconClass: 'red',
    title: 'Risk Analysis',
    desc: 'Identify bottlenecks, security concerns, and scalability issues before they become problems.',
  },
];

const ARCH_LAYERS = [
  { title: 'Presentation Layer', color: 'cyan', items: ['React UI', 'API Gateway', 'Auth'] },
  { title: 'Business Logic', color: 'blue', items: ['Services', 'Validators', 'Processors'] },
  { title: 'Data Access', color: 'green', items: ['Repositories', 'Cache', 'ORM'] },
  { title: 'Infrastructure', color: 'amber', items: ['Database', 'Message Queue', 'Storage'] },
];

const Home = () => {
  return (
    <div className="home">
      {/* ── HERO ── */}
      <section className="hero">
        <motion.div className="hero-badge" variants={fadeUp} initial="hidden" animate="visible" custom={0}>
          <span className="hero-badge-dot" />
          Powered by Agentic AI
        </motion.div>

        <motion.h1 className="hero-title" variants={fadeUp} initial="hidden" animate="visible" custom={1}>
          Autonomous <span className="cyan">Software</span>
          <br />
          Architecture <span className="cyan">Planning</span>
        </motion.h1>

        <motion.p className="hero-description" variants={fadeUp} initial="hidden" animate="visible" custom={2}>
          AI-powered architecture planning and evolution. Two intelligent agents collaborate to
          analyze, plan, and optimize your software architecture—before and after development.
        </motion.p>

        <motion.div className="hero-buttons" variants={fadeUp} initial="hidden" animate="visible" custom={3}>
          <Link to="/new-project" className="btn-primary">
            Start New Project <ArrowRight size={18} />
          </Link>
          <Link to="/new-project" state={{ mode: 'brownfield' }} className="btn-secondary">
            Analyze Existing Project
          </Link>
        </motion.div>

        <motion.div className="hero-tags" variants={fadeUp} initial="hidden" animate="visible" custom={4}>
          {[
            { icon: <Layers size={14} />, label: 'Greenfield Planning' },
            { icon: <TrendingUp size={14} />, label: 'Brownfield Analysis' },
            { icon: <Zap size={14} />, label: 'Real-time Collaboration' },
          ].map((tag) => (
            <span key={tag.label} className="hero-tag">
              {tag.icon} {tag.label}
            </span>
          ))}
        </motion.div>
      </section>

      {/* ── DASHBOARD PREVIEW ── */}
      <section className="dashboard-preview-section">
        <motion.p
          className="section-label"
          initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
        >
          Architecture Analysis Dashboard
        </motion.p>
        <motion.div
          className="dashboard-window"
          initial={{ opacity: 0, y: 40, scale: 0.97 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="window-header">
            <span className="window-dot red" />
            <span className="window-dot yellow" />
            <span className="window-dot green" />
            <span className="window-title">Architecture Analysis Dashboard</span>
          </div>
          <div className="arch-grid">
            {ARCH_LAYERS.map((layer) => (
              <div key={layer.title} className={`arch-layer ${layer.color}`}>
                <div className="arch-layer-title">{layer.title}</div>
                {layer.items.map((item) => (
                  <div key={item} className="arch-layer-item">{item}</div>
                ))}
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ── AGENTS SECTION ── */}
      <section className="agents-section">
        <motion.h2
          className="section-title"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
        >
          Powered by <span className="cyan">Intelligent Agents</span>
        </motion.h2>
        <motion.p
          className="section-subtitle"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          transition={{ delay: 0.1 }}
        >
          Two specialized AI agents collaborate to deliver comprehensive architecture insights and
          actionable recommendations.
        </motion.p>

        <div className="agent-cards">
          {AGENT_CARDS.map((card, i) => (
            <motion.div
              key={card.title}
              className="agent-card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.5 }}
            >
              <div className={`agent-icon ${card.iconClass}`}>{card.icon}</div>
              <div className="agent-card-title">{card.title}</div>
              <p className="agent-card-desc">{card.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── MODES SECTION ── */}
      <section className="modes-section">
        <motion.h2
          className="section-title"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
        >
          Two Modes, <span className="cyan">One Powerful Workflow</span>
        </motion.h2>
        <motion.p
          className="section-subtitle"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          transition={{ delay: 0.1 }}
        >
          Whether you're starting from scratch or evolving an existing system, our agents adapt to your
          needs.
        </motion.p>

        <div className="modes-grid">
          {/* Greenfield */}
          <motion.div
            className="mode-card"
            initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
            transition={{ duration: 0.55 }}
          >
            <div className="mode-card-header">
              <div className="mode-icon"><Layers size={22} /></div>
              <div>
                <div className="mode-card-title">Greenfield Mode</div>
                <div className="mode-card-subtitle">For new projects</div>
              </div>
            </div>
            <ul className="mode-steps">
              {[
                { icon: <FileEdit size={16} />, title: 'Define Requirements', desc: 'Enter functional and non-functional requirements for your new project' },
                { icon: <Zap size={16} />, title: 'Agent Analysis', desc: 'AI agents collaborate to analyze requirements and constraints' },
                { icon: <Layers size={16} />, title: 'Architecture Plan', desc: 'Receive a comprehensive architecture with patterns and justifications' },
              ].map((s) => (
                <li key={s.title} className="mode-step">
                  <div className="step-icon">{s.icon}</div>
                  <div className="step-info">
                    <div className="step-title">{s.title}</div>
                    <div className="step-desc">{s.desc}</div>
                  </div>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Brownfield */}
          <motion.div
            className="mode-card"
            initial={{ opacity: 0, x: 30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
            transition={{ duration: 0.55 }}
          >
            <div className="mode-card-header">
              <div className="mode-icon"><Upload size={22} /></div>
              <div>
                <div className="mode-card-title">Brownfield Mode</div>
                <div className="mode-card-subtitle">For existing projects</div>
              </div>
            </div>
            <ul className="mode-steps">
              {[
                { icon: <Upload size={16} />, title: 'Upload Codebase', desc: 'Provide your existing code via file upload or repository link' },
                { icon: <FileSearch size={16} />, title: 'Deep Analysis', desc: 'Analysis agent examines structure, dependencies, and patterns' },
                { icon: <TrendingUp size={16} />, title: 'Evolution Roadmap', desc: 'Get recommendations for improvements and modernization paths' },
              ].map((s) => (
                <li key={s.title} className="mode-step">
                  <div className="step-icon">{s.icon}</div>
                  <div className="step-info">
                    <div className="step-title">{s.title}</div>
                    <div className="step-desc">{s.desc}</div>
                  </div>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="home-cta">
        <motion.h2
          className="section-title"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
        >
          Ready to plan your <span className="cyan">architecture?</span>
        </motion.h2>
        <motion.p
          className="section-subtitle"
          initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
          transition={{ delay: 0.1 }}
        >
          Start your first architecture project in minutes.
        </motion.p>
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 }}>
          <Link to="/new-project" className="btn-primary">
            Start New Project <ArrowRight size={18} />
          </Link>
        </motion.div>
      </section>
    </div>
  );
};

export default Home;

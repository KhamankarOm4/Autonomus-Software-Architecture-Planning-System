import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Brain } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <Link to="/" className="logo">
        <div className="logo-icon">
          <Brain size={24} color="#040d1a" />
        </div>
        <div className="logo-text">
          <span className="logo-title">ArchAI</span>
          <span className="logo-subtitle">Planner</span>
        </div>
      </Link>

      <div className="nav-links">
        <NavLink 
          to="/" 
          className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          end
        >
          Home
        </NavLink>
        <NavLink 
          to="/new-project" 
          className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
        >
          New Project
        </NavLink>
        <NavLink 
          to="/dashboard" 
          className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
        >
          Dashboard
        </NavLink>
        <NavLink 
          to="/results" 
          className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
        >
          Results
        </NavLink>
      </div>

      <Link to="/new-project" className="nav-cta">
        Start Planning
      </Link>
    </nav>
  );
};

export default Navbar;

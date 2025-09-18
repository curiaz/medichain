import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import RoleSelectionModal from '../components/RoleSelectionModal';
import Footer from '../components/Footer';
import '../assets/styles/LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const [headerStyle, setHeaderStyle] = useState({});
  const statsRef = useRef(null);
  const [statsAnimated, setStatsAnimated] = useState(false);
  const [statsValues, setStatsValues] = useState({
    accuracy: 99.9,
    patients: 10,
    encryption: 256
  });
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);

  const handleGetStarted = () => {
    setIsRoleModalOpen(true);
  };

  const handleRoleSelect = (role) => {
    if (role === 'doctor') {
      navigate('/signup?role=doctor');
    } else if (role === 'patient') {
      navigate('/signup?role=patient');
    }
  };

  const closeRoleModal = () => {
    setIsRoleModalOpen(false);
  };

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 100) {
        setHeaderStyle({
          background: 'rgba(255, 255, 255, 0.98)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        });
      } else {
        setHeaderStyle({
          background: 'rgba(255, 255, 255, 0.95)',
          boxShadow: 'none',
        });
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    let timers = [];
    let isCleanedUp = false;

    const animateStats = () => {
      if (isCleanedUp) return;

      const stats = [
        { key: 'accuracy', target: 99.9, suffix: '%' },
        { key: 'patients', target: 10, suffix: 'K+' },
        { key: 'encryption', target: 256, suffix: '-bit' },
      ];

      stats.forEach((stat) => {
        let current = 0;
        const increment = stat.target / 50;
        const timer = setInterval(() => {
          if (isCleanedUp) {
            clearInterval(timer);
            return;
          }

          current += increment;
          if (current >= stat.target) {
            setStatsValues(prev => ({
              ...prev,
              [stat.key]: stat.target
            }));
            clearInterval(timer);
            timers = timers.filter(t => t !== timer);
          } else {
            setStatsValues(prev => ({
              ...prev,
              [stat.key]: Math.floor(current)
            }));
          }
        }, 50);
        
        timers.push(timer);
      });
    };

    const observerOptions = {
      threshold: 0.5,
      rootMargin: '0px 0px -50px 0px',
    };

    const statsObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !statsAnimated && !isCleanedUp) {
          setStatsAnimated(true);
          animateStats();
        }
      });
    }, observerOptions);

    if (statsRef.current) {
      statsObserver.observe(statsRef.current);
    }

    return () => {
      isCleanedUp = true;
      if (statsRef.current) {
        statsObserver.unobserve(statsRef.current);
      }
      timers.forEach(timer => {
        clearInterval(timer);
      });
      timers = [];
    };
  }, [statsAnimated]);

  const handleSmoothScroll = (e, targetId) => {
    e.preventDefault();
    const target = document.querySelector(targetId);
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    }
  };

  return (
    <div className="medichain">
      {/* Floating Medical Crosses */}
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>

      {/* Hero Section */}
      <section className="hero">
        {/* Header */}
        <header className="header" style={headerStyle}>
          <div className="nav-container">
            <div className="logo-container">
              <div className="logo-icon">+</div>
              <div className="logo-text">MEDICHAIN</div>
            </div>
            <nav className="nav-links">
              <a
                className="nav-link"
                onClick={(e) => handleSmoothScroll(e, '#features')}
              >
                Features
              </a>
              <a
                className="nav-link"
                onClick={(e) => handleSmoothScroll(e, '#about')}
              >
                About
              </a>
              <a
                className="nav-link"
                onClick={(e) => handleSmoothScroll(e, '#security')}
              >
                Security
              </a>
              <a
                className="nav-link"
                onClick={() => navigate('/contact')}
              >
                Contact
              </a>
            </nav>
            <div className="cta-buttons">
              <button
                className="btn btn-secondary"
                onClick={() => navigate('/login')}
              >
                Log In
              </button>
              <button
                className="btn btn-primary"
                onClick={handleGetStarted}
              >
                Get Started
              </button>
            </div>
          </div>
        </header>

        {/* Hero Content */}
        <div className="hero-content">
          <div className="hero-text">
            <div className="hero-badge">🚀 Next-Gen Healthcare Platform</div>
            <h1 className="hero-title">
              The Future of <span className="highlight">Healthcare</span> is Here
            </h1>
            <p className="hero-subtitle">
              Revolutionary AI-powered diagnosis combined with secure blockchain health records. 
              Experience healthcare that's intelligent, secure, and designed for the digital age.
            </p>
            <div className="hero-buttons">
              <button
                className="btn btn-primary btn-large"
                onClick={() => navigate('/ai-health')}
              >
                Try AI Health Assistant
              </button>
              <button
                className="btn btn-secondary btn-large"
                onClick={(e) => handleSmoothScroll(e, '#features')}
              >
                Learn More
              </button>
            </div>
            <div className="hero-stats" ref={statsRef}>
              <div className="stat">
                <span className="stat-number">{statsValues.accuracy}%</span>
                <span className="stat-label">Accuracy Rate</span>
              </div>
              <div className="stat">
                <span className="stat-number">{statsValues.patients}K+</span>
                <span className="stat-label">Patients Served</span>
              </div>
              <div className="stat">
                <span className="stat-number">{statsValues.encryption}-bit</span>
                <span className="stat-label">Encryption</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="container">
          <div className="section-header">
            <div className="section-badge">✨ Revolutionary Technology</div>
            <h2 className="section-title">Why Choose MediChain?</h2>
            <p className="section-subtitle">
              Experience the perfect fusion of artificial intelligence and blockchain technology, 
              designed to revolutionize healthcare delivery and patient data management.
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-item-icon">🤖</div>
              <h3>AI-Driven Diagnosis</h3>
              <p>
                Receive fast and reliable diagnostic results with our AI technology, which analyzes symptoms and medical data to support healthcare decisions.
              </p>
            </div>
            <div className="feature-item">
              <div className="feature-item-icon">⛓️</div>
              <h3>Blockchain Records</h3>
              <p>
                Patient health records are securely stored on blockchain, making them tamper-proof and always accessible for trusted medical use.
              </p>
            </div>
            <div className="feature-item">
              <div className="feature-item-icon">🔐</div>
              <h3>Advanced Encryption</h3>
              <p>
                All sensitive medical information is protected by strong encryption, keeping patient data private and secure at every step.
              </p>
            </div>
            <div className="feature-item">
              <div className="feature-item-icon">⚡</div>
              <h3>Real-time Analytics</h3>
              <p>
                Instantly view health trends and analytics to help improve care and make informed decisions for better patient outcomes.
              </p>
            </div>
            <div className="feature-item">
              <div className="feature-item-icon">🌐</div>
              <h3>Interoperability</h3>
              <p>
                Effortlessly share and integrate patient data across healthcare systems, ensuring smooth collaboration between providers.
              </p>
            </div>
            <div className="feature-item">
              <div className="feature-item-icon">📱</div>
              <h3>Mobile-First Design</h3>
              <p>
                Access your dashboard and records anywhere, on any device, with a platform designed for healthcare professionals on the move.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />

      {/* Role Selection Modal */}
      <RoleSelectionModal 
        isOpen={isRoleModalOpen}
        onClose={closeRoleModal}
        onRoleSelect={handleRoleSelect}
      />
    </div>
  );
};

export default LandingPage;
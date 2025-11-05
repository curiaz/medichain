import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faJs, faPython, faCss3Alt } from '@fortawesome/free-brands-svg-icons';
import { faCube } from '@fortawesome/free-solid-svg-icons';
import RoleSelectionModal from '../components/RoleSelectionModal';
import Footer from '../components/Footer';
import medichainLogo from '../assets/medichain_logo.png';
import '../assets/styles/LandingPage.css';
import { API_CONFIG, buildURL } from '../config/api';

const LandingPage = () => {
  const navigate = useNavigate();
  const [headerStyle, setHeaderStyle] = useState({});
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);

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

  const openPrivacyModal = () => setShowPrivacyModal(true);
  const closePrivacyModal = () => {
    const modal = document.querySelector('.landing-modal-content');
    if (modal) {
      modal.classList.add('modal-closing');
      setTimeout(() => setShowPrivacyModal(false), 250);
    } else {
      setShowPrivacyModal(false);
    }
  };
  const openTermsModal = () => setShowTermsModal(true);
  const closeTermsModal = () => {
    const modal = document.querySelector('.landing-modal-content');
    if (modal) {
      modal.classList.add('modal-closing');
      setTimeout(() => setShowTermsModal(false), 250);
    } else {
      setShowTermsModal(false);
    }
  };

  const handleContactInputChange = (e) => {
    const { name, value } = e.target;
    setContactForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitMessage('');

    try {
      const response = await fetch(buildURL(API_CONFIG.ENDPOINTS.CONTACT), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(contactForm)
      });

      const result = await response.json();

      if (result.success) {
        setSubmitMessage('Thank you! Your message has been sent successfully.');
        setContactForm({
          name: '',
          email: '',
          phone: '',
          subject: '',
          message: ''
        });
      } else {
        setSubmitMessage('Error: ' + (result.error || 'Failed to send message'));
      }
    } catch (error) {
      setSubmitMessage('Error: Failed to send message. Please try again later.');
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 100) {
        setHeaderStyle({
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          background: 'rgba(255, 255, 255, 0.98)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          zIndex: 1000,
          transition: 'all 0.3s ease',
        });
      } else {
        setHeaderStyle({
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          background: 'rgba(255, 255, 255, 0.95)',
          boxShadow: 'none',
          zIndex: 1000,
          transition: 'all 0.3s ease',
        });
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Reveal on scroll animations
  useEffect(() => {
    const elements = document.querySelectorAll('.reveal');
    if (!elements.length) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal-visible');
          }
        });
      },
      { threshold: 0.15 }
    );
    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const handleSmoothScroll = (e, targetId) => {
    e.preventDefault();
    const target = document.querySelector(targetId);
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    }
    setIsMobileNavOpen(false);
  };

  return (
    <div className="medichain">
      {/* Floating Medical Crosses */}
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>
      <div className="floating-cross">+</div>

      {/* Header */}
      <header className="header" style={headerStyle}>
        <div className="nav-container">
          <div
            className="logo-container"
            onClick={(e) => handleSmoothScroll(e, '.hero')} // Scroll to the top (hero section)
            style={{ cursor: 'pointer' }}
          >
            <div className="logo-icon">
              <img src={medichainLogo} alt="MediChain Logo" className="logo-image" />
            </div>
            <div className="logo-text">MEDICHAIN</div>
          </div>
          <nav className="nav-links">
            <button
              className="nav-link"
              onClick={(e) => handleSmoothScroll(e, '#about')}
              type="button"
            >
              About
            </button>
            <button
              className="nav-link"
              onClick={(e) => handleSmoothScroll(e, '#features')}
              type="button"
            >
              Features
            </button>
            <button
              className="nav-link"
              onClick={(e) => handleSmoothScroll(e, '#contact')}
              type="button"
            >
              Contact Us
            </button>
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
              Sign Up
            </button>
          </div>
          <button
            className={`mobile-menu-button ${isMobileNavOpen ? 'open' : ''}`}
            aria-label="Toggle navigation menu"
            aria-expanded={isMobileNavOpen}
            onClick={() => setIsMobileNavOpen((v) => !v)}
            type="button"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
        {isMobileNavOpen && (
          <div className="mobile-nav">
            <button className="nav-link" onClick={(e) => handleSmoothScroll(e, '#about')} type="button">About</button>
            <button className="nav-link" onClick={(e) => handleSmoothScroll(e, '#features')} type="button">Features</button>
            <button className="nav-link" onClick={(e) => handleSmoothScroll(e, '#contact')} type="button">Contact Us</button>
            <div className="mobile-cta">
              <button className="btn btn-secondary" onClick={() => { setIsMobileNavOpen(false); navigate('/login'); }}>Log In</button>
              <button className="btn btn-primary" onClick={() => { setIsMobileNavOpen(false); handleGetStarted(); }}>Sign Up</button>
            </div>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="hero">
        {/* Hero Content */}
        <div className="hero-content">
          <div className="hero-text reveal">
            <div className="hero-badge">🚀 Next-Gen Healthcare Platform</div>
            <h1 className="hero-title">
              The Future of <span className="highlight">Healthcare</span> is Here
            </h1>
            <p className="hero-subtitle">
              Secure health records combined with modern healthcare solutions. 
              Experience healthcare that's secure, efficient, and designed for the digital age.
            </p>
            <div className="hero-buttons">
              <button
                className="btn btn-primary btn-extra-large"
                onClick={handleGetStarted}
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about" id="about">
        <div className="container about-container">
          {/* Description Section */}
          <div className="about-description-section reveal">
            <h2 className="about-title">About MediChain</h2>
            <p className="about-description">
              MediChain is a groundbreaking healthcare platform that combines the power of artificial intelligence and blockchain technology. Our mission is to revolutionize the healthcare industry by providing secure, efficient, and intelligent solutions for managing patient health records and delivering accurate diagnoses.
            </p>
            <p className="about-description">
              With MediChain, healthcare professionals can leverage AI-driven tools to analyze symptoms and medical data, enabling faster and more reliable diagnostic recommendations. This ensures better decision-making and improved patient outcomes, saving valuable time and resources.
            </p>
          </div>

          {/* Built On Section */}
          <div className="about-built-on-section reveal">
            <h2 className="about-title">What MediChain is Built On</h2>
            <p className="about-description">
              MediChain is powered by cutting-edge technologies, including artificial intelligence for accurate diagnostics, blockchain for secure and immutable health records, and advanced encryption protocols to ensure data privacy and security.
            </p>
            <div className="tech-logos">
              <div className="tech-logo-link" aria-label="JavaScript">
                <FontAwesomeIcon icon={faJs} className="tech-logo" title="JavaScript" />
              </div>
              <div className="tech-logo-link" aria-label="Tailwind CSS">
                <FontAwesomeIcon icon={faCss3Alt} className="tech-logo" title="Tailwind CSS" />
              </div>
              <div className="tech-logo-link" aria-label="Python">
                <FontAwesomeIcon icon={faPython} className="tech-logo" title="Python" />
              </div>
              <div className="tech-logo-link" aria-label="Blockchain">
                <FontAwesomeIcon icon={faCube} className="tech-logo" title="Blockchain" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="landing_features" id="features">
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
            <div className="feature-item reveal">
              <div className="feature-item-icon">🤖</div>
              <h3>AI-Driven Diagnosis</h3>
              <p>
                Receive fast and reliable diagnostic results with our AI technology, which analyzes symptoms and medical data to support healthcare decisions.
              </p>
            </div>
            <div className="feature-item reveal">
              <div className="feature-item-icon">⛓️</div>
              <h3>Blockchain Records</h3>
              <p>
                Patient health records are securely stored on blockchain, making them tamper-proof and always accessible for trusted medical use.
              </p>
            </div>
            <div className="feature-item reveal">
              <div className="feature-item-icon">🔐</div>
              <h3>Advanced Encryption</h3>
              <p>
                All sensitive medical information is protected by strong encryption, keeping patient data private and secure at every step.
              </p>
            </div>
            <div className="feature-item reveal">
              <div className="feature-item-icon">⚡</div>
              <h3>Real-time Analytics</h3>
              <p>
                Instantly view health trends and analytics to help improve care and make informed decisions for better patient outcomes.
              </p>
            </div>
            <div className="feature-item reveal">
              <div className="feature-item-icon">🌐</div>
              <h3>Interoperability</h3>
              <p>
                Effortlessly share and integrate patient data across healthcare systems, ensuring smooth collaboration between providers.
              </p>
            </div>
            <div className="feature-item reveal">
              <div className="feature-item-icon">📱</div>
              <h3>Mobile-First Design</h3>
              <p>
                Access your dashboard and records anywhere, on any device, with a platform designed for healthcare professionals on the move.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Us Section */}
      <section className="contact" id="contact">
        <div className="container contact-container reveal">
          <h2 className="contact-title">Contact Us</h2>
          <div className="contact-info">
            <p><strong>Email:</strong> <a href="mailto:medichain173@gmail.com" className="email-link">medichain173@gmail.com</a></p>
            <p><strong>Phone:</strong> +1 (234) 567-890</p>
            <p><strong>Address:</strong> <a href="https://www.facebook.com/TaguigCityUniversity" target="_blank" rel="noopener noreferrer" className="email-link">Taguig City University</a></p>
          </div>
          <form className="contact-form" onSubmit={handleContactSubmit}>
            <input 
              type="text" 
              name="name" 
              placeholder="Your Name" 
              value={contactForm.name}
              onChange={handleContactInputChange}
              required 
            />
            <input 
              type="email" 
              name="email" 
              placeholder="Your Email" 
              value={contactForm.email}
              onChange={handleContactInputChange}
              required 
            />
            <input 
              type="tel" 
              name="phone" 
              placeholder="Your Phone Number" 
              value={contactForm.phone}
              onChange={handleContactInputChange}
            />
            <input 
              type="text" 
              name="subject" 
              placeholder="Subject" 
              value={contactForm.subject}
              onChange={handleContactInputChange}
              required 
            />
            <textarea 
              name="message" 
              placeholder="Your Message" 
              rows="5" 
              value={contactForm.message}
              onChange={handleContactInputChange}
              required
              className="contact-message-textarea"
            ></textarea>
            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Sending...' : 'Submit'}
            </button>
            {submitMessage && (
              <div className={`submit-message ${
                submitMessage.includes('Error') ? 'error' : 'success'
              }`}>
                {submitMessage}
              </div>
            )}
          </form>
        </div>
      </section>

      {/* Footer */}
      <Footer 
        onPrivacyClick={openPrivacyModal}
        onTermsClick={openTermsModal}
      />

      {/* Role Selection Modal */}
      <RoleSelectionModal 
        isOpen={isRoleModalOpen}
        onClose={closeRoleModal}
        onRoleSelect={handleRoleSelect}
      />

      {/* Privacy Policy Modal */}
      {showPrivacyModal && (
        <div className="landing-modal-overlay" onClick={closePrivacyModal}>
          <div className="landing-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="landing-modal-header">
              <h2>Privacy Policy – MediChain</h2>
              <button className="landing-modal-close" onClick={closePrivacyModal}>
                ×
              </button>
            </div>
            <div className="landing-modal-body">
              <p><strong>Effective Date:</strong> September 29, 2025</p>
              <br />
              <p>At MediChain, we value your trust. This Privacy Policy explains how we collect, use, and protect your information when you use our system.</p>
              <br />
              <h3>Information We Collect</h3>
              <ul>
                <li>Personal details (name, contact info, date of birth).</li>
                <li>Medical records and health-related data you choose to share.</li>
                <li>Login credentials and activity logs.</li>
              </ul>
              <br />
              <h3>How We Use Your Information</h3>
              <ul>
                <li>To provide healthcare services through verified doctors.</li>
                <li>To maintain secure medical records for your access.</li>
                <li>To improve our system's reliability and features.</li>
              </ul>
              <br />
              <h3>Data Protection</h3>
              <ul>
                <li>All data is stored securely with encryption.</li>
                <li>Access is limited to authorized personnel only.</li>
                <li>We follow industry standards for protecting health information.</li>
              </ul>
              <br />
              <h3>Sharing of Information</h3>
              <ul>
                <li>We do not sell or rent your personal data.</li>
                <li>Data may be shared only with verified healthcare providers you connect with.</li>
                <li>We may disclose information if required by law.</li>
              </ul>
              <br />
              <h3>Your Rights</h3>
              <ul>
                <li>You can access, update, or request deletion of your account.</li>
                <li>You may withdraw consent at any time.</li>
              </ul>
              <br />
              <h3>Contact Us</h3>
              <p>For questions, email us at: <a href="mailto:medichain173@gmail.com" className="landing-modal-email-link">medichain173@gmail.com</a></p>
              <br />
              <p>By using MediChain, you agree to this Privacy Policy.</p>
            </div>
          </div>
        </div>
      )}

      {/* Terms of Service Modal */}
      {showTermsModal && (
        <div className="landing-modal-overlay" onClick={closeTermsModal}>
          <div className="landing-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="landing-modal-header">
              <h2>Terms of Service – MediChain</h2>
              <button className="landing-modal-close" onClick={closeTermsModal}>
                ×
              </button>
            </div>
            <div className="landing-modal-body">
              <p><strong>Effective Date:</strong> September 29, 2025</p>
              <br />
              <p>Welcome to MediChain! By using our platform, you agree to these terms:</p>
              <br />
              <h3>Eligibility</h3>
              <p>You must be at least 18 years old or have guardian consent to use MediChain.</p>
              <br />
              <h3>Use of Service</h3>
              <ul>
                <li>MediChain connects users with verified doctors.</li>
                <li>Users are responsible for the accuracy of the information they provide.</li>
                <li>Accounts must not be shared or misused.</li>
              </ul>
              <br />
              <h3>No Emergency Services</h3>
              <p>MediChain is <strong>not for emergencies</strong>. In urgent cases, call your local emergency hotline.</p>
              <br />
              <h3>Doctor Verification</h3>
              <p>We verify doctors before approving their accounts, but MediChain is not responsible for medical outcomes.</p>
              <br />
              <h3>User Responsibilities</h3>
              <ul>
                <li>Provide truthful information.</li>
                <li>Respect other users and healthcare providers.</li>
                <li>Do not misuse the platform for unlawful activities.</li>
              </ul>
              <br />
              <h3>Limitation of Liability</h3>
              <p>MediChain provides a platform for healthcare access. We are not liable for medical advice, diagnosis, or treatment provided by doctors through the system.</p>
              <br />
              <h3>Modifications</h3>
              <p>We may update these Terms at any time. Continued use of MediChain means you accept the new Terms.</p>
              <br />
              <h3>Contact Us</h3>
              <p>For support, email us at: <a href="mailto:medichain173@gmail.com" className="landing-modal-email-link">medichain173@gmail.com</a></p>
              <br />
              <p>By using MediChain, you agree to these Terms of Service.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;
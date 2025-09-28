import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faJs, faPython, faCss3Alt } from '@fortawesome/free-brands-svg-icons';
import { faCube } from '@fortawesome/free-solid-svg-icons';
import RoleSelectionModal from '../components/RoleSelectionModal';
import Footer from '../components/Footer';
import medichainLogo from '../assets/medichain_logo.png';
import '../assets/styles/LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const [headerStyle, setHeaderStyle] = useState({});
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');

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
      const response = await fetch('http://localhost:5000/contact', {
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
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
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
                className="btn btn-primary btn-extra-large"
                onClick={() => navigate('/ai-health')}
              >
                Try AI Diagnosis & Prescription
              </button>
              <p className="ai-disclaimer">
                Note: This is only a predicted condition. Please seek professional medical advice for accurate diagnosis.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about" id="about">
        <div className="container about-container">
          {/* Description Section */}
          <div className="about-description-section">
            <h2 className="about-title">About MediChain</h2>
            <p className="about-description">
              MediChain is a groundbreaking healthcare platform that combines the power of artificial intelligence and blockchain technology. Our mission is to revolutionize the healthcare industry by providing secure, efficient, and intelligent solutions for managing patient health records and delivering accurate diagnoses.
            </p>
            <p className="about-description">
              With MediChain, healthcare professionals can leverage AI-driven tools to analyze symptoms and medical data, enabling faster and more reliable diagnostic recommendations. This ensures better decision-making and improved patient outcomes, saving valuable time and resources.
            </p>
          </div>

          {/* Built On Section */}
          <div className="about-built-on-section">
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

      {/* Contact Us Section */}
      <section className="contact" id="contact">
        <div className="container contact-container">
          <h2 className="contact-title">Contact Us</h2>
          <div className="contact-info">
            <p><strong>Email:</strong> support@medichain.com</p>
            <p><strong>Phone:</strong> +1 (234) 567-890</p>
            <p><strong>Address:</strong> Taguig City University</p>
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
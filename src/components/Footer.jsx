import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Footer.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTwitter, faFacebookF, faGithub } from '@fortawesome/free-brands-svg-icons';

const Footer = ({ onPrivacyClick, onTermsClick }) => {
  const navigate = useNavigate();
  const currentYear = new Date().getFullYear();

  const handleNavigation = (path) => {
    navigate(path);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const scrollToFeature = (featureName) => {
    // Find all feature items
    const featureItems = document.querySelectorAll('.feature-item');
    const targetFeature = Array.from(featureItems).find(item => {
      const heading = item.querySelector('h3');
      return heading && heading.textContent.includes(featureName);
    });
    
    if (targetFeature) {
      // Scroll to the feature
      targetFeature.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Add highlight animation
      targetFeature.classList.add('feature-highlight');
      setTimeout(() => {
        targetFeature.classList.remove('feature-highlight');
      }, 1500);
    }
  };

  const handleNewsletterSubmit = (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    if (email) {
      // Add newsletter subscription logic here
      alert('Thank you for subscribing!');
      e.target.reset();
    }
  };

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          {/* Company Info */}
          <div className="footer-section">
            <h3 className="footer-title">MediChain</h3>
            <p className="footer-description">
              AI-Driven Diagnosis & Blockchain Health Records System
            </p>
            <div className="social-links">
              <a 
                href="https://x.com/medichainn" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="social-link"
                aria-label="Follow us on Twitter/X"
              >
                <FontAwesomeIcon icon={faTwitter} />
              </a>
              <a 
                href="https://www.facebook.com/profile.php?id=61581467434658" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="social-link"
                aria-label="Follow us on Facebook"
              >
                <FontAwesomeIcon icon={faFacebookF} />
              </a>
              <a 
                href="https://github.com/curiaz/medichain" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="social-link"
                aria-label="View our code on GitHub"
              >
                <FontAwesomeIcon icon={faGithub} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="footer-section">
            <h4 className="footer-subtitle">Quick Links</h4>
            <ul className="footer-links">
              <li>
                <button 
                  onClick={scrollToTop} 
                  className="footer-link"
                  aria-label="Scroll to top of page"
                >
                  Home
                </button>
              </li>
              <li>
                <button 
                  onClick={() => handleNavigation('/dashboard')} 
                  className="footer-link"
                  aria-label="Go to Dashboard"
                >
                  Dashboard
                </button>
              </li>
              <li>
                <button 
                  onClick={() => handleNavigation('/login')} 
                  className="footer-link"
                  aria-label="Go to Login page"
                >
                  Login
                </button>
              </li>
              <li>
                <button 
                  onClick={() => handleNavigation('/signup')} 
                  className="footer-link"
                  aria-label="Go to Sign Up page"
                >
                  Sign Up
                </button>
              </li>
            </ul>
          </div>

          {/* Features */}
          <div className="footer-section">
            <h4 className="footer-subtitle">Features</h4>
            <ul className="footer-links">
              <li>
                <button 
                  onClick={() => scrollToFeature('AI-Driven Diagnosis')} 
                  className="footer-link"
                  aria-label="View AI Diagnosis feature"
                >
                  AI Diagnosis
                </button>
              </li>
              <li>
                <button 
                  onClick={() => scrollToFeature('Blockchain Records')} 
                  className="footer-link"
                  aria-label="View Blockchain Records feature"
                >
                  Blockchain Records
                </button>
              </li>
              <li>
                <button 
                  onClick={() => scrollToFeature('Advanced Encryption')} 
                  className="footer-link"
                  aria-label="View Secure Encryption feature"
                >
                  Secure Encryption
                </button>
              </li>
              <li>
                <button 
                  onClick={() => scrollToFeature('Real-time Analytics')} 
                  className="footer-link"
                  aria-label="View Real-time Analytics feature"
                >
                  Real-time Analytics
                </button>
              </li>
            </ul>
          </div>

          {/* Contact & Newsletter Combined */}
          <div className="footer-section">
            <h4 className="footer-subtitle">Contact & Updates</h4>
            <ul className="footer-links">
              <li>
                <a 
                  href="mailto:support@medichain.com" 
                  className="footer-link"
                  aria-label="Send us an email"
                >
                  support@medichain.com
                </a>
              </li>
              <li>
                <a 
                  href="tel:+1234567890" 
                  className="footer-link"
                  aria-label="Call us"
                >
                  +1 (234) 567-890
                </a>
              </li>
              <li>
                <a 
                  href="https://www.facebook.com/TaguigCityUniversity" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="footer-link"
                  aria-label="Visit Taguig City University Facebook page"
                >
                  Taguig City University
                </a>
              </li>
            </ul>
            
            <form className="newsletter-form" onSubmit={handleNewsletterSubmit}>
              <input 
                type="email" 
                name="email"
                placeholder="Enter your email" 
                className="newsletter-input"
                required
                aria-label="Enter your email for newsletter"
              />
              <button 
                type="submit" 
                className="newsletter-btn"
                aria-label="Subscribe to newsletter"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p className="copyright">
              © {currentYear} MediChain. All rights reserved. | Academic Project - <a href="https://www.facebook.com/TaguigCityUniversity" target="_blank" rel="noopener noreferrer" className="university-link">Taguig City University</a>
            </p>
            <div className="footer-bottom-links">
              <button 
                onClick={onPrivacyClick} 
                className="footer-bottom-link"
                aria-label="View Privacy Policy"
              >
                Privacy Policy
              </button>
              <button 
                onClick={onTermsClick} 
                className="footer-bottom-link"
                aria-label="View Terms of Service"
              >
                Terms of Service
              </button>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
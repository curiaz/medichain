import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  const navigate = useNavigate();
  const currentYear = new Date().getFullYear();

  const handleNavigation = (path) => {
    navigate(path);
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
                href="https://twitter.com" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="social-link"
                aria-label="Follow us on Twitter"
              >
                <i className="fab fa-twitter"></i>
              </a>
              <a 
                href="https://facebook.com" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="social-link"
                aria-label="Follow us on Facebook"
              >
                <i className="fab fa-facebook-f"></i>
              </a>
              <a 
                href="https://linkedin.com" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="social-link"
                aria-label="Connect with us on LinkedIn"
              >
                <i className="fab fa-linkedin-in"></i>
              </a>
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="social-link"
                aria-label="View our code on GitHub"
              >
                <i className="fab fa-github"></i>
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="footer-section">
            <h4 className="footer-subtitle">Quick Links</h4>
            <ul className="footer-links">
              <li>
                <button 
                  onClick={() => handleNavigation('/')} 
                  className="footer-link"
                  aria-label="Go to Home page"
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
                  onClick={() => handleNavigation('/#features')} 
                  className="footer-link"
                  aria-label="Learn about AI Diagnostics"
                >
                  AI Diagnostics
                </button>
              </li>
              <li>
                <button 
                  onClick={() => handleNavigation('/#features')} 
                  className="footer-link"
                  aria-label="Learn about Blockchain Records"
                >
                  Blockchain Records
                </button>
              </li>
              <li>
                <button 
                  onClick={() => handleNavigation('/#features')} 
                  className="footer-link"
                  aria-label="Learn about Secure Encryption"
                >
                  Secure Encryption
                </button>
              </li>
              <li>
                <button 
                  onClick={() => handleNavigation('/#features')} 
                  className="footer-link"
                  aria-label="Learn about Real-time Analytics"
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
                <span className="footer-link">Taguig City University</span>
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
              © {currentYear} MediChain. All rights reserved. | Academic Project - Taguig City University
            </p>
            <div className="footer-bottom-links">
              <button 
                onClick={() => handleNavigation('/privacy')} 
                className="footer-bottom-link"
                aria-label="View Privacy Policy"
              >
                Privacy Policy
              </button>
              <button 
                onClick={() => handleNavigation('/terms')} 
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
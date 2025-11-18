import React, { useState } from 'react';
import { User } from 'lucide-react';
import '../assets/styles/OnboardingFormPopup.css';

const OnboardingFormPopup = ({ onSkip, onContinue, user, isSaving = false }) => {
  const [formData, setFormData] = useState({
    date_of_birth: '',
    phone: '',
    gender: '',
    address: '',
    city: '',
    state: '',
    zip_code: ''
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.date_of_birth.trim()) {
      newErrors.date_of_birth = 'Date of birth is required';
    }
    
    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    }
    
    if (!formData.gender.trim()) {
      newErrors.gender = 'Gender is required';
    }
    
    if (!formData.address.trim()) {
      newErrors.address = 'Address is required';
    }
    
    if (!formData.city.trim()) {
      newErrors.city = 'City is required';
    }
    
    if (!formData.state.trim()) {
      newErrors.state = 'State is required';
    }
    
    if (!formData.zip_code.trim()) {
      newErrors.zip_code = 'ZIP/Postal code is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleContinue = () => {
    if (validateForm()) {
      onContinue(formData);
    }
  };

  const isFormValid = () => {
    return formData.date_of_birth.trim() &&
           formData.phone.trim() &&
           formData.gender.trim() &&
           formData.address.trim() &&
           formData.city.trim() &&
           formData.state.trim() &&
           formData.zip_code.trim();
  };

  return (
    <div className="onboarding-popup-overlay">
      <div className="onboarding-popup-content" onClick={(e) => e.stopPropagation()}>
        <div className="onboarding-popup-icon">
          <User size={48} color="#2196F3" strokeWidth={2} />
        </div>
        
        <h2 className="onboarding-popup-title">Let Us Know You!</h2>
        
        <p className="onboarding-popup-subtitle">
          Help us personalize your experience by providing some basic information.
        </p>
        
        <form className="onboarding-form" onSubmit={(e) => e.preventDefault()}>
          <div className="onboarding-form-row">
            <div className="onboarding-form-group">
              <label htmlFor="date_of_birth">Date of Birth *</label>
              <input
                type="date"
                id="date_of_birth"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleChange}
                className={errors.date_of_birth ? 'error' : ''}
                required
              />
              {errors.date_of_birth && <span className="error-message">{errors.date_of_birth}</span>}
            </div>
            
            <div className="onboarding-form-group">
              <label htmlFor="phone">Phone Number *</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="e.g., 09123456789"
                className={errors.phone ? 'error' : ''}
                required
              />
              {errors.phone && <span className="error-message">{errors.phone}</span>}
            </div>
          </div>
          
          <div className="onboarding-form-group">
            <label htmlFor="gender">Gender *</label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className={errors.gender ? 'error' : ''}
              required
            >
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
            {errors.gender && <span className="error-message">{errors.gender}</span>}
          </div>
          
          <div className="onboarding-form-group">
            <label htmlFor="address">Address *</label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="Street address"
              className={errors.address ? 'error' : ''}
              required
            />
            {errors.address && <span className="error-message">{errors.address}</span>}
          </div>
          
          <div className="onboarding-form-row">
            <div className="onboarding-form-group">
              <label htmlFor="city">City *</label>
              <input
                type="text"
                id="city"
                name="city"
                value={formData.city}
                onChange={handleChange}
                placeholder="City"
                className={errors.city ? 'error' : ''}
                required
              />
              {errors.city && <span className="error-message">{errors.city}</span>}
            </div>
            
            <div className="onboarding-form-group">
              <label htmlFor="state">State *</label>
              <input
                type="text"
                id="state"
                name="state"
                value={formData.state}
                onChange={handleChange}
                placeholder="State"
                className={errors.state ? 'error' : ''}
                required
              />
              {errors.state && <span className="error-message">{errors.state}</span>}
            </div>
          </div>
          
          <div className="onboarding-form-group">
            <label htmlFor="zip_code">ZIP/Postal Code *</label>
            <input
              type="text"
              id="zip_code"
              name="zip_code"
              value={formData.zip_code}
              onChange={handleChange}
              placeholder="ZIP/Postal code"
              className={errors.zip_code ? 'error' : ''}
              required
            />
            {errors.zip_code && <span className="error-message">{errors.zip_code}</span>}
          </div>
          
          <p className="onboarding-disclaimer">
            We keep your information private and use it only for your account.
          </p>
          
          <div className="onboarding-form-actions">
            <button
              type="button"
              className="onboarding-button skip-button"
              onClick={onSkip}
            >
              Skip for now
            </button>
            <button
              type="button"
              className="onboarding-button continue-button"
              onClick={handleContinue}
              disabled={!isFormValid() || isSaving}
            >
              {isSaving ? 'Saving...' : 'Continue'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OnboardingFormPopup;


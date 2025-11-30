import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, MapPin, Phone, Building, FileText, Image as ImageIcon, 
  Upload, X, CheckCircle, AlertCircle, ChevronRight, ChevronLeft
} from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';
import { showToast } from './CustomToast';
import { API_CONFIG } from '../config/api';
import ImageCropper from './ImageCropper';
import SignaturePadModal from './SignaturePadModal';
import '../assets/styles/DoctorSignupSteps.css';

const DoctorSignupSteps = ({ 
  email, 
  token, 
  onComplete,
  onBack 
}) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(3); // Start at step 3 (after OTP)
  const [savingStep, setSavingStep] = useState(false);
  
  // Step 3: Doctor Information
  const [doctorInfo, setDoctorInfo] = useState({
    prcLicenseNumber: "",
    prcExpirationDate: "",
    affiliationType: "",
    clinicHospitalAffiliation: "",
    professionalAddress: "",
    hospitalClinicContactNumber: ""
  });
  const [infoErrors, setInfoErrors] = useState({});
  
  // Step 4: Documents
  const [doctorDocuments, setDoctorDocuments] = useState({
    prcIdFront: null,
    prcIdBack: null,
    ptr: null,
    boardCertificate: null,
    clinicHospitalId: null,
    supportingDocument: null
  });
  const [documentPreviews, setDocumentPreviews] = useState({});
  const [documentErrors, setDocumentErrors] = useState({});
  
  // E-Signature
  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [pendingDocType, setPendingDocType] = useState(null);
  const [eSignature, setESignature] = useState(null);
  
  // Step 5: Profile Photo
  const [profilePhoto, setProfilePhoto] = useState(null);
  const [profilePhotoPreview, setProfilePhotoPreview] = useState(null);
  const [photoError, setPhotoError] = useState("");
  const [showCropper, setShowCropper] = useState(false);
  const [originalImageSrc, setOriginalImageSrc] = useState(null);
  
  // Step 6: Preview
  const [previewData, setPreviewData] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  
  const fileInputRefs = {
    prcIdFront: useRef(null),
    prcIdBack: useRef(null),
    ptr: useRef(null),
    boardCertificate: useRef(null),
    clinicHospitalId: useRef(null),
    supportingDocument: useRef(null),
    profilePhoto: useRef(null)
  };
  
  const API_URL = API_CONFIG.API_URL;
  
  // Step 3: Handle doctor information input
  const handleInfoChange = (field, value) => {
    setDoctorInfo(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error for this field
    if (infoErrors[field]) {
      setInfoErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };
  
  const validateStep3 = () => {
    const errors = {};
    
    if (!doctorInfo.prcLicenseNumber.trim()) {
      errors.prcLicenseNumber = "PRC License Number is required";
    }
    
    if (!doctorInfo.prcExpirationDate) {
      errors.prcExpirationDate = "PRC Expiration Date is required";
    } else {
      const expDate = new Date(doctorInfo.prcExpirationDate);
      const today = new Date();
      if (expDate <= today) {
        errors.prcExpirationDate = "Expiration date must be in the future";
      }
    }
    
    if (!doctorInfo.affiliationType) {
      errors.affiliationType = "Please select an affiliation type";
    }
    
    if (doctorInfo.affiliationType === 'clinic_hospital' || doctorInfo.affiliationType === 'independent_private') {
      if (!doctorInfo.clinicHospitalAffiliation.trim()) {
        errors.clinicHospitalAffiliation = "Clinic/Hospital Affiliation is required";
      }
    }
    
    if (!doctorInfo.professionalAddress.trim()) {
      errors.professionalAddress = "Professional Address is required";
    }
    
    if (doctorInfo.affiliationType === 'clinic_hospital' || doctorInfo.affiliationType === 'independent_private') {
      if (!doctorInfo.hospitalClinicContactNumber.trim()) {
        errors.hospitalClinicContactNumber = "Hospital/Clinic Contact Number is required";
      }
    }
    
    setInfoErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleStep3Submit = async (e) => {
    e.preventDefault();
    
    if (!validateStep3()) {
      showToast.error("Please fill in all required fields correctly");
      return;
    }
    
    setSavingStep(true);
    
    try {
      const response = await fetch(`${API_URL}/auth/doctor-signup/step3`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(doctorInfo)
      });
      
      const result = await response.json();
      
      if (result.success) {
        showToast.success("Information saved successfully!");
        setCurrentStep(4);
      } else {
        showToast.error(result.error || "Failed to save information");
      }
    } catch (error) {
      console.error("Error saving doctor info:", error);
      showToast.error("Failed to save information. Please try again.");
    } finally {
      setSavingStep(false);
    }
  };
  
  // Step 4: Handle document uploads
  const handleDocumentChange = async (docType, file) => {
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      showToast.error("Please upload a valid file (PDF, JPG, or PNG)");
      return;
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      showToast.error("File size must be less than 5MB");
      return;
    }
    
    // Convert file to base64 for storage
    try {
      const base64Data = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
      
      // Store file with base64 data
      setDoctorDocuments(prev => ({
        ...prev,
        [docType]: {
          file: file,
          name: file.name,
          size: file.size,
          type: file.type,
          data: base64Data, // Full data URL
          base64: base64Data.split(',')[1] // Raw base64 string
        }
      }));
      
      // Create preview for images
      if (file.type.startsWith('image/')) {
        setDocumentPreviews(prev => ({
          ...prev,
          [docType]: base64Data
        }));
      } else {
        // For PDFs, just show file name
        setDocumentPreviews(prev => ({
          ...prev,
          [docType]: file.name
        }));
      }
      
      // Show signature modal if PRC ID is uploaded and signature not yet collected
      if ((docType === 'prcIdFront' || docType === 'prcIdBack') && !eSignature) {
        setPendingDocType(docType);
        setShowSignatureModal(true);
      }
    } catch (error) {
      console.error(`Error converting file ${file.name} to base64:`, error);
      showToast.error(`Failed to process file ${file.name}. Please try again.`);
      return;
    }
    
    // Clear error
    if (documentErrors[docType]) {
      setDocumentErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[docType];
        return newErrors;
      });
    }
  };
  
  // Handle signature save
  const handleSignatureSave = (signatureDataURL) => {
    setESignature(signatureDataURL);
    setShowSignatureModal(false);
    setPendingDocType(null);
    showToast.success("E-signature saved successfully! It will be encrypted and stored securely.");
  };
  
  // Handle signature modal close
  const handleSignatureClose = () => {
    setShowSignatureModal(false);
    setPendingDocType(null);
  };
  
  const removeDocument = (docType) => {
    setDoctorDocuments(prev => ({
      ...prev,
      [docType]: null
    }));
    setDocumentPreviews(prev => {
      const newPreviews = { ...prev };
      delete newPreviews[docType];
      return newPreviews;
    });
  };
  
  const validateStep4 = () => {
    const errors = {};
    
    // PRC ID Front and Back are required
    if (!doctorDocuments.prcIdFront) {
      errors.prcIdFront = "PRC ID (Front) is required";
    }
    
    if (!doctorDocuments.prcIdBack) {
      errors.prcIdBack = "PRC ID (Back) is required";
    }
    
    // E-signature is required
    if (!eSignature) {
      errors.eSignature = "E-signature is required";
    }
    
    // If "Not affiliated" is selected, supporting document is required
    if (doctorInfo.affiliationType === 'not_affiliated' && !doctorDocuments.supportingDocument) {
      errors.supportingDocument = "Supporting document is required for non-affiliated doctors";
    }
    
    setDocumentErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleStep4Submit = async (e) => {
    e.preventDefault();
    
    if (!validateStep4()) {
      showToast.error("Please upload all required documents");
      return;
    }
    
    setSavingStep(true);
    
    try {
      const formData = new FormData();
      
      // Append all documents with base64 data
      Object.keys(doctorDocuments).forEach(docType => {
        const doc = doctorDocuments[docType];
        if (doc) {
          // If it's an object with file and base64 data, append both
          if (doc.file && doc.base64) {
            formData.append(docType, doc.file); // File for backward compatibility
            formData.append(`${docType}_base64`, doc.base64); // Base64 data
            formData.append(`${docType}_data`, doc.data); // Full data URL
          } else if (doc instanceof File) {
            // Legacy: if it's just a File object, append as-is
            formData.append(docType, doc);
          }
        }
      });
      
      // Append e-signature if available
      if (eSignature) {
        // Convert data URL to blob and append
        const signatureBlob = await fetch(eSignature).then(res => res.blob());
        formData.append('eSignature', signatureBlob, 'e-signature.png');
        // Also append as base64 for easier backend processing
        const signatureBase64 = eSignature.split(',')[1];
        formData.append('eSignature_base64', signatureBase64);
        formData.append('eSignature_data', eSignature);
      }
      
      const response = await fetch(`${API_URL}/auth/doctor-signup/step4`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        showToast.success("Documents uploaded successfully!");
        if (result.e_signature_saved) {
          showToast.success("E-signature encrypted and stored securely!");
        }
        setCurrentStep(5);
      } else {
        // Handle specific error for signature update after approval
        if (result.error && result.error.includes("cannot be updated after admin approval")) {
          showToast.error("E-signature cannot be changed after admin approval. Please contact support if you need to update it.");
        } else {
          showToast.error(result.error || "Failed to upload documents");
        }
      }
    } catch (error) {
      console.error("Error uploading documents:", error);
      showToast.error("Failed to upload documents. Please try again.");
    } finally {
      setSavingStep(false);
    }
  };
  
  // Step 5: Handle profile photo upload
  const handlePhotoChange = (file) => {
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      setPhotoError("Please upload a JPG or PNG image");
      return;
    }
    
    // Validate file size
    if (file.size > 5 * 1024 * 1024) {
      setPhotoError("File size must be less than 5MB");
      return;
    }
    
    // Validate image dimensions
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);
    
    img.onload = () => {
      if (img.width < 400 || img.height < 400) {
        URL.revokeObjectURL(objectUrl);
        setPhotoError("Image must be at least 400x400 pixels");
        return;
      }
      
      setPhotoError("");
      
      // Create preview and show cropper
      const reader = new FileReader();
      reader.onloadend = () => {
        setOriginalImageSrc(reader.result);
        setShowCropper(true);
      };
      reader.readAsDataURL(file);
    };
    
    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      setPhotoError("Invalid image file");
    };
    
    img.src = objectUrl;
  };

  const handleCropComplete = (croppedBlob) => {
    // Convert blob to file
    const croppedFile = new File([croppedBlob], 'profile-photo.jpg', { type: 'image/jpeg' });
    setProfilePhoto(croppedFile);
    
    // Create preview from cropped image
    const reader = new FileReader();
    reader.onloadend = () => {
      setProfilePhotoPreview(reader.result);
    };
    reader.readAsDataURL(croppedBlob);
    
    setShowCropper(false);
    setOriginalImageSrc(null);
  };

  const handleCancelCrop = () => {
    setShowCropper(false);
    setOriginalImageSrc(null);
    if (fileInputRefs.profilePhoto.current) {
      fileInputRefs.profilePhoto.current.value = '';
    }
  };
  
  const handleStep5Submit = async (e) => {
    e.preventDefault();
    
    if (!profilePhoto) {
      setPhotoError("Profile photo is required");
      return;
    }
    
    setSavingStep(true);
    
    try {
      const formData = new FormData();
      formData.append('profilePhoto', profilePhoto);
      
      const response = await fetch(`${API_URL}/auth/doctor-signup/step5`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        showToast.success("Profile photo uploaded successfully!");
        // Load preview data
        await loadPreviewData();
        setCurrentStep(6);
      } else {
        showToast.error(result.error || "Failed to upload profile photo");
      }
    } catch (error) {
      console.error("Error uploading profile photo:", error);
      showToast.error("Failed to upload profile photo. Please try again.");
    } finally {
      setSavingStep(false);
    }
  };
  
  // Step 6: Preview and Submit
  const loadPreviewData = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/doctor-signup/preview`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setPreviewData(result.data);
      }
    } catch (error) {
      console.error("Error loading preview data:", error);
    }
  };
  
  // Load existing doctor info when component mounts
  useEffect(() => {
    const loadExistingData = async () => {
      try {
        const response = await fetch(`${API_URL}/auth/doctor-signup/preview`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        const result = await response.json();
        
        if (result.success && result.data) {
          const data = result.data;
          // Populate doctorInfo state with existing data
          setDoctorInfo({
            prcLicenseNumber: data.prc_license_number || "",
            prcExpirationDate: data.prc_expiration_date ? data.prc_expiration_date.split('T')[0] : "",
            affiliationType: data.affiliation_type || "",
            clinicHospitalAffiliation: data.clinic_hospital_affiliation || "",
            professionalAddress: data.professional_address || "",
            hospitalClinicContactNumber: data.hospital_clinic_contact_number || ""
          });
        }
      } catch (error) {
        console.error("Error loading existing data:", error);
      }
    };
    
    loadExistingData();
  }, [API_URL, token]);
  
  // Load preview data when step 6 is reached
  useEffect(() => {
    if (currentStep === 6) {
      loadPreviewData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentStep]);
  
  const handleFinalSubmit = async () => {
    setSubmitting(true);
    
    try {
      const response = await fetch(`${API_URL}/auth/doctor-signup/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        showToast.success("Application submitted successfully! Your account is pending verification.");
        // Store token and user data
        localStorage.setItem('medichain_token', token);
        if (result.data?.user) {
          localStorage.setItem('medichain_user', JSON.stringify(result.data.user));
        }
        // Redirect to doctor dashboard
        setTimeout(() => {
          navigate('/dashboard', { replace: true });
        }, 1500); // Small delay to show success message
        // Call onComplete callback if provided
        if (onComplete) {
          onComplete();
        }
      } else {
        showToast.error(result.error || "Failed to submit application");
      }
    } catch (error) {
      console.error("Error submitting application:", error);
      showToast.error("Failed to submit application. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <div className="doctor-signup-steps">
      {/* Progress Indicator */}
      <div className="steps-progress">
        <div className={`step-indicator ${currentStep >= 1 ? 'completed' : ''} ${currentStep === 1 ? 'active' : ''}`}>
          <span>1</span>
          <label>Account</label>
        </div>
        <div className={`step-indicator ${currentStep >= 2 ? 'completed' : ''} ${currentStep === 2 ? 'active' : ''}`}>
          <span>2</span>
          <label>Email</label>
        </div>
        <div className={`step-indicator ${currentStep >= 3 ? 'completed' : ''} ${currentStep === 3 ? 'active' : ''}`}>
          <span>3</span>
          <label>Info</label>
        </div>
        <div className={`step-indicator ${currentStep >= 4 ? 'completed' : ''} ${currentStep === 4 ? 'active' : ''}`}>
          <span>4</span>
          <label>Documents</label>
        </div>
        <div className={`step-indicator ${currentStep >= 5 ? 'completed' : ''} ${currentStep === 5 ? 'active' : ''}`}>
          <span>5</span>
          <label>Photo</label>
        </div>
        <div className={`step-indicator ${currentStep >= 6 ? 'completed' : ''} ${currentStep === 6 ? 'active' : ''}`}>
          <span>6</span>
          <label>Review</label>
        </div>
      </div>
      
      {/* Step 3: Doctor Information */}
      {currentStep === 3 && (
        <div className="step-content">
          <div className="step-header">
            <h2>Professional Information</h2>
            <p>Please provide your professional details</p>
          </div>
          
          <form onSubmit={handleStep3Submit} className="doctor-signup-form">
            <div className="form-group">
              <label htmlFor="prcLicenseNumber">PRC License Number *</label>
              <input
                id="prcLicenseNumber"
                type="text"
                value={doctorInfo.prcLicenseNumber}
                onChange={(e) => handleInfoChange('prcLicenseNumber', e.target.value)}
                placeholder="Enter your PRC License Number"
                className={infoErrors.prcLicenseNumber ? 'error' : ''}
                required
              />
              {infoErrors.prcLicenseNumber && (
                <span className="error-message">{infoErrors.prcLicenseNumber}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="prcExpirationDate">PRC Expiration Date *</label>
              <div className="input-with-icon">
                <Calendar className="input-icon" size={20} />
                <input
                  id="prcExpirationDate"
                  type="date"
                  value={doctorInfo.prcExpirationDate}
                  onChange={(e) => handleInfoChange('prcExpirationDate', e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className={infoErrors.prcExpirationDate ? 'error' : ''}
                  required
                />
              </div>
              {infoErrors.prcExpirationDate && (
                <span className="error-message">{infoErrors.prcExpirationDate}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="specialization">Specialization / Field</label>
              <input
                id="specialization"
                type="text"
                value="General Practitioner"
                readOnly
                disabled
                style={{ cursor: 'not-allowed', backgroundColor: '#f5f5f5' }}
              />
            </div>
            
            <div className="form-group">
              <label>Affiliation Type *</label>
              <div className="radio-group">
                <label className="radio-option">
                  <input
                    type="radio"
                    name="affiliationType"
                    value="clinic_hospital"
                    checked={doctorInfo.affiliationType === 'clinic_hospital'}
                    onChange={(e) => handleInfoChange('affiliationType', e.target.value)}
                    required
                  />
                  <span>Clinic / Hospital</span>
                </label>
                <label className="radio-option">
                  <input
                    type="radio"
                    name="affiliationType"
                    value="independent_private"
                    checked={doctorInfo.affiliationType === 'independent_private'}
                    onChange={(e) => handleInfoChange('affiliationType', e.target.value)}
                    required
                  />
                  <span>Independent / Private Practice</span>
                </label>
                <label className="radio-option">
                  <input
                    type="radio"
                    name="affiliationType"
                    value="not_affiliated"
                    checked={doctorInfo.affiliationType === 'not_affiliated'}
                    onChange={(e) => handleInfoChange('affiliationType', e.target.value)}
                    required
                  />
                  <span>Not affiliated (License holder only)</span>
                </label>
              </div>
              {infoErrors.affiliationType && (
                <span className="error-message">{infoErrors.affiliationType}</span>
              )}
              
              {doctorInfo.affiliationType === 'not_affiliated' && (
                <div className="info-alert">
                  <AlertCircle size={16} />
                  <span>Upload supporting document (PTR, Board Exam Certificate, Residency Certificate).</span>
                </div>
              )}
            </div>
            
            {(doctorInfo.affiliationType === 'clinic_hospital' || doctorInfo.affiliationType === 'independent_private') && (
              <>
                <div className="form-group">
                  <label htmlFor="clinicHospitalAffiliation">Clinic/Hospital Affiliation *</label>
                  <div className="input-with-icon">
                    <Building className="input-icon" size={20} />
                    <input
                      id="clinicHospitalAffiliation"
                      type="text"
                      value={doctorInfo.clinicHospitalAffiliation}
                      onChange={(e) => handleInfoChange('clinicHospitalAffiliation', e.target.value)}
                      placeholder="Enter clinic or hospital name"
                      className={infoErrors.clinicHospitalAffiliation ? 'error' : ''}
                      required
                    />
                  </div>
                  {infoErrors.clinicHospitalAffiliation && (
                    <span className="error-message">{infoErrors.clinicHospitalAffiliation}</span>
                  )}
                </div>
                
                <div className="form-group">
                  <label htmlFor="hospitalClinicContactNumber">Hospital/Clinic Contact Number *</label>
                  <div className="input-with-icon">
                    <Phone className="input-icon" size={20} />
                    <input
                      id="hospitalClinicContactNumber"
                      type="tel"
                      value={doctorInfo.hospitalClinicContactNumber}
                      onChange={(e) => handleInfoChange('hospitalClinicContactNumber', e.target.value)}
                      placeholder="Enter contact number"
                      className={infoErrors.hospitalClinicContactNumber ? 'error' : ''}
                      required
                    />
                  </div>
                  {infoErrors.hospitalClinicContactNumber && (
                    <span className="error-message">{infoErrors.hospitalClinicContactNumber}</span>
                  )}
                </div>
              </>
            )}
            
            <div className="form-group">
              <label htmlFor="professionalAddress">Professional Address *</label>
              <div className="input-with-icon">
                <MapPin className="input-icon" size={20} />
                <textarea
                  id="professionalAddress"
                  value={doctorInfo.professionalAddress}
                  onChange={(e) => handleInfoChange('professionalAddress', e.target.value)}
                  placeholder="Enter your professional practice address"
                  rows={3}
                  className={infoErrors.professionalAddress ? 'error' : ''}
                  required
                />
              </div>
              {infoErrors.professionalAddress && (
                <span className="error-message">{infoErrors.professionalAddress}</span>
              )}
            </div>
            
            <div className="form-actions">
              <button
                type="button"
                onClick={onBack}
                className="btn-secondary"
                disabled={savingStep}
              >
                <ChevronLeft size={20} />
                Back
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={savingStep}
              >
                {savingStep ? (
                  <>
                    <LoadingSpinner size="small" text="" color="#ffffff" />
                    Saving...
                  </>
                ) : (
                  <>
                    Continue
                    <ChevronRight size={20} />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
      
      {/* Step 4: Document Upload */}
      {currentStep === 4 && (
        <div className="step-content">
          <div className="step-header">
            <h2>Upload Documents</h2>
            <p>Please upload your verification documents</p>
          </div>
          
          <form onSubmit={handleStep4Submit} className="doctor-signup-form">
            <div className="documents-section">
              <h3>Required Documents</h3>
              
              <div className="document-upload-group">
                <label htmlFor="prcIdFront">PRC ID (Front) *</label>
                <div className="file-upload-area">
                  <input
                    ref={fileInputRefs.prcIdFront}
                    id="prcIdFront"
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleDocumentChange('prcIdFront', e.target.files[0])}
                    style={{ display: 'none' }}
                  />
                  {doctorDocuments.prcIdFront ? (
                    <div className="file-preview">
                      {documentPreviews.prcIdFront && typeof documentPreviews.prcIdFront === 'string' && documentPreviews.prcIdFront.startsWith('data:image') ? (
                        <img src={documentPreviews.prcIdFront} alt="PRC ID Front" />
                      ) : (
                        <FileText size={48} />
                      )}
                      <span>{doctorDocuments.prcIdFront.name}</span>
                      <button
                        type="button"
                        onClick={() => removeDocument('prcIdFront')}
                        className="remove-file"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => fileInputRefs.prcIdFront.current?.click()}
                      className="upload-button"
                    >
                      <Upload size={20} />
                      Upload PRC ID (Front)
                    </button>
                  )}
                </div>
                {documentErrors.prcIdFront && (
                  <span className="error-message">{documentErrors.prcIdFront}</span>
                )}
              </div>
              
              <div className="document-upload-group">
                <label htmlFor="prcIdBack">PRC ID (Back) *</label>
                <div className="file-upload-area">
                  <input
                    ref={fileInputRefs.prcIdBack}
                    id="prcIdBack"
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleDocumentChange('prcIdBack', e.target.files[0])}
                    style={{ display: 'none' }}
                  />
                  {doctorDocuments.prcIdBack ? (
                    <div className="file-preview">
                      {documentPreviews.prcIdBack && typeof documentPreviews.prcIdBack === 'string' && documentPreviews.prcIdBack.startsWith('data:image') ? (
                        <img src={documentPreviews.prcIdBack} alt="PRC ID Back" />
                      ) : (
                        <FileText size={48} />
                      )}
                      <span>{doctorDocuments.prcIdBack.name}</span>
                      <button
                        type="button"
                        onClick={() => removeDocument('prcIdBack')}
                        className="remove-file"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => fileInputRefs.prcIdBack.current?.click()}
                      className="upload-button"
                    >
                      <Upload size={20} />
                      Upload PRC ID (Back)
                    </button>
                  )}
                </div>
                {documentErrors.prcIdBack && (
                  <span className="error-message">{documentErrors.prcIdBack}</span>
                )}
              </div>
              
              {doctorInfo.affiliationType === 'not_affiliated' && (
                <div className="document-upload-group">
                  <label htmlFor="supportingDocument">Supporting Document * (PTR, Board Exam Certificate, Residency Certificate)</label>
                  <div className="file-upload-area">
                    <input
                      ref={fileInputRefs.supportingDocument}
                      id="supportingDocument"
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => handleDocumentChange('supportingDocument', e.target.files[0])}
                      style={{ display: 'none' }}
                    />
                    {doctorDocuments.supportingDocument ? (
                      <div className="file-preview">
                        {documentPreviews.supportingDocument && typeof documentPreviews.supportingDocument === 'string' && documentPreviews.supportingDocument.startsWith('data:image') ? (
                          <img src={documentPreviews.supportingDocument} alt="Supporting Document" />
                        ) : (
                          <FileText size={48} />
                        )}
                        <span>{doctorDocuments.supportingDocument.name}</span>
                        <button
                          type="button"
                          onClick={() => removeDocument('supportingDocument')}
                          className="remove-file"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => fileInputRefs.supportingDocument.current?.click()}
                        className="upload-button"
                      >
                        <Upload size={20} />
                        Upload Supporting Document
                      </button>
                    )}
                  </div>
                  {documentErrors.supportingDocument && (
                    <span className="error-message">{documentErrors.supportingDocument}</span>
                  )}
                </div>
              )}
            </div>
            
            <div className="documents-section">
              <h3>Optional Documents (Recommended)</h3>
              
              <div className="document-upload-group">
                <label htmlFor="ptr">PTR (Professional Tax Receipt)</label>
                <div className="file-upload-area">
                  <input
                    ref={fileInputRefs.ptr}
                    id="ptr"
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleDocumentChange('ptr', e.target.files[0])}
                    style={{ display: 'none' }}
                  />
                  {doctorDocuments.ptr ? (
                    <div className="file-preview">
                      {documentPreviews.ptr && typeof documentPreviews.ptr === 'string' && documentPreviews.ptr.startsWith('data:image') ? (
                        <img src={documentPreviews.ptr} alt="PTR" />
                      ) : (
                        <FileText size={48} />
                      )}
                      <span>{doctorDocuments.ptr.name}</span>
                      <button
                        type="button"
                        onClick={() => removeDocument('ptr')}
                        className="remove-file"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => fileInputRefs.ptr.current?.click()}
                      className="upload-button"
                    >
                      <Upload size={20} />
                      Upload PTR
                    </button>
                  )}
                </div>
              </div>
              
              <div className="document-upload-group">
                <label htmlFor="boardCertificate">Board Certificate / Diplomate Certificate</label>
                <div className="file-upload-area">
                  <input
                    ref={fileInputRefs.boardCertificate}
                    id="boardCertificate"
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleDocumentChange('boardCertificate', e.target.files[0])}
                    style={{ display: 'none' }}
                  />
                  {doctorDocuments.boardCertificate ? (
                    <div className="file-preview">
                      {documentPreviews.boardCertificate && typeof documentPreviews.boardCertificate === 'string' && documentPreviews.boardCertificate.startsWith('data:image') ? (
                        <img src={documentPreviews.boardCertificate} alt="Board Certificate" />
                      ) : (
                        <FileText size={48} />
                      )}
                      <span>{doctorDocuments.boardCertificate.name}</span>
                      <button
                        type="button"
                        onClick={() => removeDocument('boardCertificate')}
                        className="remove-file"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => fileInputRefs.boardCertificate.current?.click()}
                      className="upload-button"
                    >
                      <Upload size={20} />
                      Upload Board Certificate
                    </button>
                  )}
                </div>
              </div>
              
              {(doctorInfo.affiliationType === 'clinic_hospital' || doctorInfo.affiliationType === 'independent_private') && (
                <div className="document-upload-group">
                  <label htmlFor="clinicHospitalId">Clinic/Hospital ID</label>
                  <div className="file-upload-area">
                    <input
                      ref={fileInputRefs.clinicHospitalId}
                      id="clinicHospitalId"
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => handleDocumentChange('clinicHospitalId', e.target.files[0])}
                      style={{ display: 'none' }}
                    />
                    {doctorDocuments.clinicHospitalId ? (
                      <div className="file-preview">
                        {documentPreviews.clinicHospitalId && typeof documentPreviews.clinicHospitalId === 'string' && documentPreviews.clinicHospitalId.startsWith('data:image') ? (
                          <img src={documentPreviews.clinicHospitalId} alt="Clinic/Hospital ID" />
                        ) : (
                          <FileText size={48} />
                        )}
                        <span>{doctorDocuments.clinicHospitalId.name}</span>
                        <button
                          type="button"
                          onClick={() => removeDocument('clinicHospitalId')}
                          className="remove-file"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => fileInputRefs.clinicHospitalId.current?.click()}
                        className="upload-button"
                      >
                        <Upload size={20} />
                        Upload Clinic/Hospital ID
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            <div className="documents-section">
              <h3>E-Signature *</h3>
              
              <div className="document-upload-group">
                <label>E-Signature</label>
                <div className="file-upload-area">
                  {eSignature ? (
                    <div className="file-preview">
                      <img src={eSignature} alt="E-Signature" style={{ maxHeight: '100px', border: '1px solid #e0e0e0', borderRadius: '4px' }} />
                      <span>E-Signature saved</span>
                      <button
                        type="button"
                        onClick={() => setShowSignatureModal(true)}
                        className="btn-change-signature"
                        style={{ marginLeft: '8px', padding: '4px 12px', fontSize: '12px' }}
                      >
                        Change
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setShowSignatureModal(true)}
                      className="upload-button"
                    >
                      <Upload size={20} />
                      Add E-Signature
                    </button>
                  )}
                </div>
                {documentErrors.eSignature && (
                  <span className="error-message">{documentErrors.eSignature}</span>
                )}
                <p style={{ fontSize: '12px', color: '#666', marginTop: '8px', fontStyle: 'italic' }}>
                  Sign inside the box below. This will serve as your official e-signature for diagnosis and prescription.
                </p>
              </div>
            </div>
            
            <div className="form-actions">
              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                className="btn-secondary"
                disabled={savingStep}
              >
                <ChevronLeft size={20} />
                Back
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={savingStep}
              >
                {savingStep ? (
                  <>
                    <LoadingSpinner size="small" text="" color="#ffffff" />
                    Uploading...
                  </>
                ) : (
                  <>
                    Continue
                    <ChevronRight size={20} />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
      
      {/* Step 5: Profile Photo */}
      {currentStep === 5 && (
        <div className="step-content">
          <div className="step-header">
            <h2>Upload Profile Photo</h2>
            <p>Please upload a professional profile photo</p>
          </div>
          
          <form onSubmit={handleStep5Submit} className="doctor-signup-form">
            <div className="photo-upload-section">
              <div className="photo-guidelines">
                <h3>Photo Guidelines</h3>
                <ul>
                  <li><strong>Clear Face Visibility:</strong> Face must be fully visible, no masks, sunglasses, or heavy filters</li>
                  <li><strong>Professional Appearance:</strong> Plain background, professional attire (polo, coat, medical uniform)</li>
                  <li><strong>High Quality:</strong> Minimum 400×400px, not blurry, no screenshots</li>
                  <li><strong>File Format:</strong> JPG/JPEG or PNG, max 5MB</li>
                  <li><strong>No Filters:</strong> Avoid beauty filters or excessive editing</li>
                  <li><strong>Purpose:</strong> Helps admin verify identity and builds patient trust</li>
                </ul>
              </div>
              
              <div className="photo-upload-area">
                <input
                  ref={fileInputRefs.profilePhoto}
                  id="profilePhoto"
                  type="file"
                  accept=".jpg,.jpeg,.png"
                  onChange={(e) => handlePhotoChange(e.target.files[0])}
                  style={{ display: 'none' }}
                />
                
                {profilePhotoPreview ? (
                  <div className="photo-preview-container">
                    <div className="photo-preview">
                      <img src={profilePhotoPreview} alt="Profile Preview" />
                    </div>
                    <div className="photo-preview-actions">
                      <button
                        type="button"
                        onClick={() => {
                          if (fileInputRefs.profilePhoto.current) {
                            fileInputRefs.profilePhoto.current.value = '';
                            fileInputRefs.profilePhoto.current.click();
                          }
                        }}
                        className="btn-change-photo"
                        title="Change Photo"
                      >
                        Change Photo
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setProfilePhoto(null);
                          setProfilePhotoPreview(null);
                          if (fileInputRefs.profilePhoto.current) {
                            fileInputRefs.profilePhoto.current.value = '';
                          }
                        }}
                        className="btn-remove-photo"
                        title="Remove Photo"
                      >
                        Remove Photo
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => fileInputRefs.profilePhoto.current?.click()}
                    className="upload-photo-button"
                  >
                    <ImageIcon size={48} />
                    <span>Click to Upload Profile Photo</span>
                    <small>JPG or PNG, min 400×400px, max 5MB</small>
                  </button>
                )}
                
                {photoError && (
                  <span className="error-message">{photoError}</span>
                )}
              </div>
            </div>
            
            <div className="form-actions">
              <button
                type="button"
                onClick={() => setCurrentStep(4)}
                className="btn-secondary"
                disabled={savingStep}
              >
                <ChevronLeft size={20} />
                Back
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={savingStep || !profilePhoto}
              >
                {savingStep ? (
                  <>
                    <LoadingSpinner size="small" text="" color="#ffffff" />
                    Uploading...
                  </>
                ) : (
                  <>
                    Continue
                    <ChevronRight size={20} />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Image Cropper Modal */}
      {showCropper && originalImageSrc && (
        <ImageCropper
          imageSrc={originalImageSrc}
          onCrop={handleCropComplete}
          onCancel={handleCancelCrop}
          aspectRatio={1}
        />
      )}
      
      {/* E-Signature Modal */}
      <SignaturePadModal
        isOpen={showSignatureModal}
        onClose={handleSignatureClose}
        onSave={handleSignatureSave}
      />
      
      {/* Step 6: Preview & Submit */}
      {currentStep === 6 && (
        <div className="step-content">
          <div className="step-header">
            <h2>Review & Submit</h2>
            <p>Please review all information before submitting</p>
          </div>
          
          {previewData ? (
            <div className="preview-section">
              <div className="preview-card">
                <h3>Professional Information</h3>
                <div className="preview-item">
                  <label>PRC License Number:</label>
                  <span>{previewData.prc_license_number || 'N/A'}</span>
                </div>
                <div className="preview-item">
                  <label>PRC Expiration Date:</label>
                  <span>{previewData.prc_expiration_date ? new Date(previewData.prc_expiration_date).toLocaleDateString() : 'N/A'}</span>
                </div>
                <div className="preview-item">
                  <label>Specialization:</label>
                  <span>{previewData.specialization || 'General Practitioner'}</span>
                </div>
                <div className="preview-item">
                  <label>Affiliation Type:</label>
                  <span>
                    {previewData.affiliation_type === 'clinic_hospital' && 'Clinic / Hospital'}
                    {previewData.affiliation_type === 'independent_private' && 'Independent / Private Practice'}
                    {previewData.affiliation_type === 'not_affiliated' && 'Not affiliated'}
                    {!previewData.affiliation_type && 'N/A'}
                  </span>
                </div>
                {previewData.clinic_hospital_affiliation && (
                  <div className="preview-item">
                    <label>Clinic/Hospital Affiliation:</label>
                    <span>{previewData.clinic_hospital_affiliation}</span>
                  </div>
                )}
                <div className="preview-item">
                  <label>Professional Address:</label>
                  <span>{previewData.professional_address || 'N/A'}</span>
                </div>
                {previewData.hospital_clinic_contact_number && (
                  <div className="preview-item">
                    <label>Hospital/Clinic Contact:</label>
                    <span>{previewData.hospital_clinic_contact_number}</span>
                  </div>
                )}
              </div>
              
              <div className="preview-card">
                <h3>Uploaded Documents</h3>
                {previewData.documents && previewData.documents.length > 0 ? (
                  <div className="documents-list">
                    {previewData.documents.map((doc, idx) => (
                      <div key={idx} className="document-item">
                        <FileText size={20} />
                        <span>{doc.document_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        <CheckCircle size={16} className="check-icon" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: '#999', fontStyle: 'italic' }}>No documents uploaded</p>
                )}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <LoadingSpinner size="medium" text="Loading preview data..." />
            </div>
          )}
          
          <div className="form-actions">
            <button
              type="button"
              onClick={() => setCurrentStep(5)}
              className="btn-secondary"
              disabled={submitting}
            >
              <ChevronLeft size={20} />
              Back
            </button>
            <button
              type="button"
              onClick={handleFinalSubmit}
              className="btn-primary"
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <LoadingSpinner size="small" text="" color="#ffffff" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle size={20} />
                  Submit Application
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorSignupSteps;


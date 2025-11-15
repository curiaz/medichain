import React, { useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import { Upload, X, File, ArrowLeft, ArrowRight } from "lucide-react";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/DocumentUpload.css";

const DocumentUpload = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const doctor = location.state?.doctor;
  const symptoms = location.state?.symptoms || [];
  
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (files) => {
    const newFiles = Array.from(files).map(file => ({
      id: Date.now() + Math.random(),
      file: file,
      name: file.name,
      size: file.size,
      type: file.type
    }));
    
    setUploadedFiles([...uploadedFiles, ...newFiles]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(uploadedFiles.filter(f => f.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleNext = () => {
    // Navigate to date/time selection with symptoms and documents
    navigate("/select-date-time", {
      state: {
        doctor: doctor,
        symptoms: symptoms,
        symptomKeys: location.state?.symptomKeys || [],
        documents: uploadedFiles,
        appointmentType: location.state?.appointmentType || "general-practitioner"
      }
    });
  };

  const handleSkip = () => {
    // Allow skipping document upload
    navigate("/select-date-time", {
      state: {
        doctor: doctor,
        symptoms: symptoms,
        symptomKeys: location.state?.symptomKeys || [],
        documents: [],
        appointmentType: location.state?.appointmentType || "general-practitioner"
      }
    });
  };

  if (!doctor) {
    navigate("/select-gp");
    return null;
  }

  return (
    <div className="dashboard-container fade-in">
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>+</span>
        ))}
      </div>

      <Header />

      <main className="dashboard-main-content">
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <button
              className="back-button-header"
              onClick={() => navigate("/symptoms-selection", { state: { doctor, symptoms } })}
              aria-label="Go back"
            >
              <ArrowLeft size={24} />
            </button>
            <h1 className="dashboard-title">UPLOAD DOCUMENTS</h1>
            <p className="dashboard-subtitle">
              Upload lab test results, medical reports, or other relevant documents for Dr. {doctor.first_name} {doctor.last_name}
            </p>
          </div>

          {/* Selected Symptoms Summary */}
          {symptoms.length > 0 && (
            <div className="symptoms-summary-box">
              <h3 className="summary-title">Selected Symptoms</h3>
              <div className="symptoms-summary-list">
                {symptoms.map((symptom, index) => (
                  <span key={index} className="symptom-tag">{symptom}</span>
                ))}
              </div>
            </div>
          )}

          {/* Upload Area */}
          <div className="document-upload-container">
            <div
              className={`upload-dropzone ${isDragging ? "dragging" : ""}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload size={48} className="upload-icon" />
              <h3 className="upload-title">Upload Documents</h3>
              <p className="upload-subtitle">
                Drag and drop files here, or click to browse
              </p>
              <p className="upload-hint">
                Supported formats: PDF, JPG, PNG, DOC, DOCX (Max 10MB per file)
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                onChange={(e) => {
                  if (e.target.files) {
                    handleFileSelect(e.target.files);
                  }
                }}
                style={{ display: "none" }}
              />
            </div>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="uploaded-files-container">
                <h3 className="uploaded-files-title">
                  Uploaded Files ({uploadedFiles.length})
                </h3>
                <div className="uploaded-files-list">
                  {uploadedFiles.map((file) => (
                    <div key={file.id} className="uploaded-file-item">
                      <div className="file-icon-wrapper">
                        <File size={24} />
                      </div>
                      <div className="file-info">
                        <div className="file-name">{file.name}</div>
                        <div className="file-size">{formatFileSize(file.size)}</div>
                      </div>
                      <button
                        className="remove-file-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile(file.id);
                        }}
                        aria-label={`Remove ${file.name}`}
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Navigation Buttons */}
          <div className="document-navigation">
            <button
              className="back-button-docs"
              onClick={() => navigate("/symptoms-selection", { state: { doctor } })}
            >
              <ArrowLeft size={18} />
              Back
            </button>
            <div className="document-nav-right">
              <button
                className="skip-button-docs"
                onClick={handleSkip}
              >
                Skip
              </button>
              <button
                className="next-button-docs"
                onClick={handleNext}
              >
                Next
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DocumentUpload;


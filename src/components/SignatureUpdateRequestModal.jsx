import React, { useState, useRef } from 'react';
import SignaturePad from 'signature_pad';
import { X, AlertCircle, Upload } from 'lucide-react';
import SignaturePadModal from './SignaturePadModal';
import '../assets/styles/SignatureUpdateRequestModal.css';

const SignatureUpdateRequestModal = ({ isOpen, onClose, onRequestUpdate, currentSignature }) => {
  const [showWarning, setShowWarning] = useState(true);
  const [showSignaturePad, setShowSignaturePad] = useState(false);
  const [newSignature, setNewSignature] = useState(null);
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef(null);

  const handleRequestClick = () => {
    setShowWarning(false);
  };

  const handleSignatureSave = (signatureDataURL) => {
    setNewSignature(signatureDataURL);
    setShowSignaturePad(false);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setNewSignature(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!newSignature) {
      alert('Please provide a new signature');
      return;
    }
    if (!reason.trim()) {
      alert('Please provide a reason for the signature change');
      return;
    }

    setSubmitting(true);
    try {
      await onRequestUpdate(newSignature, reason);
      // Reset form
      setNewSignature(null);
      setReason('');
      setShowWarning(true);
      onClose();
    } catch (error) {
      console.error('Error submitting request:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setShowWarning(true);
    setNewSignature(null);
    setReason('');
    setShowSignaturePad(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="signature-update-modal-overlay" onClick={handleClose}>
      <div className="signature-update-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="signature-update-modal-header">
          <h2>Request E-Signature Update</h2>
          <button
            type="button"
            className="signature-update-modal-close"
            onClick={handleClose}
            aria-label="Close"
          >
            <X size={24} />
          </button>
        </div>

        <div className="signature-update-modal-body">
          {showWarning ? (
            <div className="signature-update-warning">
              <AlertCircle size={48} className="warning-icon" />
              <h3>Admin Approval Required</h3>
              <p>
                Changing your e-signature requires admin approval for security reasons.
                Your request will be reviewed before the new signature is activated.
              </p>
              <button
                type="button"
                className="btn-request-update"
                onClick={handleRequestClick}
              >
                Request Update
              </button>
            </div>
          ) : (
            <>
              <div className="signature-update-form">
                <div className="form-section">
                  <h3>Current Signature</h3>
                  {currentSignature && (
                    <div className="signature-preview">
                      <img src={currentSignature} alt="Current Signature" />
                    </div>
                  )}
                </div>

                <div className="form-section">
                  <h3>New Signature</h3>
                  <div className="signature-upload-options">
                    <button
                      type="button"
                      className="btn-signature-option"
                      onClick={() => setShowSignaturePad(true)}
                    >
                      Draw Signature
                    </button>
                    <label className="btn-signature-option">
                      <Upload size={18} />
                      Upload Image
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/png,image/jpeg,image/jpg"
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                      />
                    </label>
                  </div>
                  {newSignature && (
                    <div className="signature-preview">
                      <img src={newSignature} alt="New Signature" />
                      <button
                        type="button"
                        className="btn-remove-signature"
                        onClick={() => setNewSignature(null)}
                      >
                        Remove
                      </button>
                    </div>
                  )}
                </div>

                <div className="form-section">
                  <h3>Reason for Change *</h3>
                  <textarea
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="e.g., My signature has changed, or I need to update my signature style..."
                    rows={4}
                    className="reason-textarea"
                    required
                  />
                </div>
              </div>

              <div className="signature-update-modal-actions">
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={handleClose}
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn-submit"
                  onClick={handleSubmit}
                  disabled={submitting || !newSignature || !reason.trim()}
                >
                  {submitting ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Signature Pad Modal */}
      <SignaturePadModal
        isOpen={showSignaturePad}
        onClose={() => setShowSignaturePad(false)}
        onSave={handleSignatureSave}
      />
    </div>
  );
};

export default SignatureUpdateRequestModal;




import React, { useRef, useEffect, useState } from 'react';
import SignaturePad from 'signature_pad';
import { X } from 'lucide-react';
import '../assets/styles/SignaturePadModal.css';

const SignaturePadModal = ({ isOpen, onClose, onSave }) => {
  const canvasRef = useRef(null);
  const signaturePadRef = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);

  useEffect(() => {
    if (isOpen && canvasRef.current) {
      // Initialize SignaturePad
      const canvas = canvasRef.current;
      
      // Set up canvas dimensions first
      const resizeCanvas = () => {
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * ratio;
        canvas.height = rect.height * ratio;
        const ctx = canvas.getContext('2d');
        ctx.scale(ratio, ratio);
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `${rect.height}px`;
      };

      resizeCanvas();
      
      // Initialize SignaturePad after canvas is sized
      signaturePadRef.current = new SignaturePad(canvas, {
        backgroundColor: 'rgb(255, 255, 255)',
        penColor: 'rgb(0, 0, 0)',
        minWidth: 1,
        maxWidth: 3,
      });

      // Handle window resize
      const handleResize = () => {
        if (signaturePadRef.current) {
          const data = signaturePadRef.current.toData();
          resizeCanvas();
          signaturePadRef.current.fromData(data);
        }
      };

      window.addEventListener('resize', handleResize);

      // Listen for signature changes
      const handleBeginStroke = () => {
        setIsEmpty(false);
      };
      
      signaturePadRef.current.addEventListener('beginStroke', handleBeginStroke);

      return () => {
        window.removeEventListener('resize', handleResize);
        if (signaturePadRef.current) {
          signaturePadRef.current.removeEventListener('beginStroke', handleBeginStroke);
          signaturePadRef.current.clear();
          signaturePadRef.current = null;
        }
      };
    } else {
      // Clean up when modal closes
      if (signaturePadRef.current) {
        signaturePadRef.current.clear();
        signaturePadRef.current = null;
      }
      setIsEmpty(true);
    }
  }, [isOpen]);

  const handleClear = () => {
    if (signaturePadRef.current) {
      signaturePadRef.current.clear();
      setIsEmpty(true);
    }
  };

  const handleSave = () => {
    if (signaturePadRef.current && !signaturePadRef.current.isEmpty()) {
      // Get signature as PNG data URL
      const dataURL = signaturePadRef.current.toDataURL('image/png');
      onSave(dataURL);
      onClose();
    }
  };

  const handleClose = () => {
    if (signaturePadRef.current) {
      signaturePadRef.current.clear();
    }
    setIsEmpty(true);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="signature-modal-overlay" onClick={handleClose}>
      <div className="signature-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="signature-modal-header">
          <h2>E-Signature</h2>
          <button
            type="button"
            className="signature-modal-close"
            onClick={handleClose}
            aria-label="Close"
          >
            <X size={24} />
          </button>
        </div>
        
        <div className="signature-modal-body">
          <p className="signature-instruction">
            Sign inside the box below. This will serve as your official e-signature for diagnosis and prescription.
          </p>
          
          <div className="signature-canvas-container">
            <canvas
              ref={canvasRef}
              className="signature-canvas"
            />
          </div>
          
          <div className="signature-modal-actions">
            <button
              type="button"
              className="btn-clear"
              onClick={handleClear}
            >
              Clear
            </button>
            <button
              type="button"
              className="btn-save"
              onClick={handleSave}
              disabled={isEmpty}
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignaturePadModal;


import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import { CreditCard, ArrowLeft, Check, AlertCircle, Calendar, Clock, User, Stethoscope, QrCode, Smartphone } from "lucide-react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { API_CONFIG } from "../config/api";
import QRCode from "qrcode";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/Payment.css";

const Payment = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, getFirebaseToken } = useAuth();
  
  const doctor = location.state?.doctor;
  const selectedDate = location.state?.selectedDate;
  const selectedTime = location.state?.selectedTime;
  const symptoms = location.state?.symptoms || [];
  const documents = location.state?.documents || [];
  const medicineAllergies = location.state?.medicineAllergies || "";
  const appointmentType = location.state?.appointmentType || "general-practitioner";

  const [consultationFee, setConsultationFee] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState("credit_card");
  const [cardNumber, setCardNumber] = useState("");
  const [cardName, setCardName] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [cvv, setCvv] = useState("");
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  
  // GCash QR Code states
  const [gcashQRCode, setGcashQRCode] = useState(null);
  const [gcashReference, setGcashReference] = useState(null);
  const [gcashPolling, setGcashPolling] = useState(false);
  const [gcashVerified, setGcashVerified] = useState(false);
  const [gcashReferenceInput, setGcashReferenceInput] = useState("");
  const [verifyingReference, setVerifyingReference] = useState(false);
  const pollingIntervalRef = useRef(null);

  // Format time to 12-hour format
  const formatTimeTo12Hour = (time24) => {
    if (!time24) return '';
    const [hours, minutes] = time24.split(':');
    const hour = parseInt(hours, 10);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  useEffect(() => {
    if (!doctor || !selectedDate || !selectedTime) {
      navigate("/select-gp");
      return;
    }

    // Fetch doctor's consultation fee
    const fetchDoctorFee = async () => {
      try {
        setLoading(true);
        
        // First, check if doctor object already has consultation_fee
        if (doctor && doctor.consultation_fee) {
          setConsultationFee(parseFloat(doctor.consultation_fee));
          setLoading(false);
          return;
        }
        
        // Otherwise, fetch from API
        const token = await getFirebaseToken();
        
        const response = await axios.get(
          `${API_CONFIG.API_URL}/appointments/doctors/approved`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          const doctorData = response.data.doctors.find(
            d => d.firebase_uid === doctor.firebase_uid
          );
          
          if (doctorData && doctorData.consultation_fee) {
            setConsultationFee(parseFloat(doctorData.consultation_fee));
          } else {
            // Default fee if not set (testing with 1 peso)
            setConsultationFee(1.00);
          }
        }
      } catch (err) {
        console.error("Error fetching doctor fee:", err);
        // Default fee on error (testing with 1 peso)
        setConsultationFee(1.00);
      } finally {
        setLoading(false);
      }
    };

    fetchDoctorFee();
  }, [doctor, selectedDate, selectedTime, navigate, getFirebaseToken]);

  const handleCardNumberChange = (e) => {
    let value = e.target.value.replace(/\s/g, '');
    if (value.length <= 16) {
      // Add spaces every 4 digits
      value = value.match(/.{1,4}/g)?.join(' ') || value;
      setCardNumber(value);
    }
  };

  const handleExpiryChange = (e) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length <= 4) {
      if (value.length >= 2) {
        value = value.slice(0, 2) + '/' + value.slice(2);
      }
      setExpiryDate(value);
    }
  };

  const handleCvvChange = (e) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length <= 3) {
      setCvv(value);
    }
  };

  // Generate GCash QR Code from API data
  const generateGCashQRFromData = async (qrData) => {
    try {
      // Generate QR code from data provided by GCash API
      const qrCodeDataUrl = await QRCode.toDataURL(qrData, {
        width: 300,
        margin: 3,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        },
        errorCorrectionLevel: 'H' // High error correction for better scanning
      });

      setGcashQRCode(qrCodeDataUrl);
      console.log("✅ GCash QR code generated from API data");
    } catch (err) {
      console.error("Error generating GCash QR code from API data:", err);
      setError("Failed to generate QR code. Please try again.");
    }
  };

  // Use your GCash Business QR code image with insta Pay logo
  const generateGCashQR = async (referenceNumber) => {
    try {
      // Use the static QR code image from public folder
      // This is your actual GCash Business QR code with insta Pay logo
      const qrImagePath = `${process.env.PUBLIC_URL || ''}/images/gcash-qr-code.jpg`;
      
      // Set the QR code image
      setGcashQRCode(qrImagePath);
      console.log("✅ Using your GCash Business QR code (insta Pay)");
      console.log("📝 Amount: ₱", consultationFee.toFixed(2));
      console.log("📝 Reference:", referenceNumber);
      
    } catch (err) {
      console.error("Error loading GCash QR code:", err);
      setError("Failed to load QR code. Please check that public/images/gcash-qr-code.jpg exists.");
    }
  };

  // Poll for payment verification - Auto-confirm booking when payment detected
  const pollPaymentStatus = async (referenceNumber) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    let pollCount = 0;
    const maxPolls = 100; // Stop after 5 minutes (100 * 3 seconds)

    const poll = async () => {
      try {
        pollCount++;
        
        // Stop polling after max attempts
        if (pollCount > maxPolls) {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
          }
          setGcashPolling(false);
          setError("Payment verification timeout. Please contact support if payment was completed.");
          return;
        }

        const token = await getFirebaseToken();
        const response = await axios.get(
          `${API_CONFIG.API_URL}/appointments/payment/verify/${referenceNumber}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        console.log(`[GCash Payment] Poll #${pollCount} - Status:`, response.data.status);

        if (response.data.success && response.data.status === 'paid') {
          // Payment detected! Stop polling
          setGcashVerified(true);
          setGcashPolling(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
          }
          
          console.log("✅ GCash payment confirmed! Auto-confirming booking...");
          
          // Auto-confirm booking immediately when payment is detected
          navigate("/book-appointment-form", {
            state: {
              doctor: doctor,
              appointmentType: appointmentType,
              selectedDate: selectedDate,
              selectedTime: selectedTime,
              symptoms: symptoms,
              symptomKeys: location.state?.symptomKeys || [],
              documents: documents,
              medicineAllergies: medicineAllergies,
              payment: {
                transaction_id: referenceNumber,
                amount: consultationFee,
                payment_method: 'gcash',
                status: 'paid',
              },
            },
          });
        }
      } catch (err) {
        console.error("Error polling payment status:", err);
        // Don't stop polling on error, keep trying
      }
    };

    // Start polling immediately, then every 3 seconds
    poll(); // First check immediately
    pollingIntervalRef.current = setInterval(poll, 3000);
    setGcashPolling(true);
  };

  // Handle GCash payment initiation
  const handleGCashPayment = async () => {
    try {
      setProcessing(true);
      setError(null);

      const token = await getFirebaseToken();
      
      // Create payment request to get reference number
      const paymentResponse = await axios.post(
        `${API_CONFIG.API_URL}/appointments/payment`,
        {
          amount: consultationFee,
          payment_method: 'gcash',
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (paymentResponse.data.success) {
        const referenceNumber = paymentResponse.data.transaction_id;
        setGcashReference(referenceNumber);
        
        // Use your static GCash Business QR code image
        await generateGCashQR(referenceNumber);
        
        // Start polling for payment verification
        pollPaymentStatus(referenceNumber);
      } else {
        setError(paymentResponse.data.error || "Failed to initiate GCash payment");
      }
    } catch (err) {
      console.error("GCash payment error:", err);
      setError(err.response?.data?.error || "Failed to initiate GCash payment");
    } finally {
      setProcessing(false);
    }
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Reset GCash state when payment method changes
  useEffect(() => {
    if (paymentMethod !== 'gcash') {
      setGcashQRCode(null);
      setGcashReference(null);
      setGcashPolling(false);
      setGcashVerified(false);
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    }
  }, [paymentMethod]);

  const handlePayment = async () => {
    // If GCash, use different handler
    if (paymentMethod === 'gcash') {
      await handleGCashPayment();
      return;
    }

    // Validate card form
    if (!cardNumber || cardNumber.replace(/\s/g, '').length !== 16) {
      setError("Please enter a valid 16-digit card number");
      return;
    }

    if (!cardName.trim()) {
      setError("Please enter cardholder name");
      return;
    }

    if (!expiryDate || expiryDate.length !== 5) {
      setError("Please enter a valid expiry date (MM/YY)");
      return;
    }

    if (!cvv || cvv.length !== 3) {
      setError("Please enter a valid CVV");
      return;
    }

    try {
      setProcessing(true);
      setError(null);

      let token;
      try {
        token = await getFirebaseToken();
      } catch (tokenError) {
        console.error("Error getting Firebase token:", tokenError);
        setError("Authentication error. Please log in again.");
        setProcessing(false);
        return;
      }

      // Process payment (simulate payment processing)
      // In production, this would integrate with Stripe, PayPal, etc.
      console.log("[Payment] Sending payment request:", {
        amount: consultationFee,
        payment_method: paymentMethod,
        url: `${API_CONFIG.API_URL}/appointments/payment`
      });
      
      const paymentResponse = await axios.post(
        `${API_CONFIG.API_URL}/appointments/payment`,
        {
          amount: consultationFee,
          payment_method: paymentMethod,
          card_number: cardNumber.replace(/\s/g, ''),
          card_name: cardName,
          expiry_date: expiryDate,
          cvv: cvv,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          timeout: 30000, // 30 second timeout
        }
      );
      
      console.log("[Payment] Payment response:", paymentResponse.data);

      if (paymentResponse.data.success) {
        // Navigate to booking form with payment details
        navigate("/book-appointment-form", {
          state: {
            doctor: doctor,
            appointmentType: appointmentType,
            selectedDate: selectedDate,
            selectedTime: selectedTime,
            symptoms: symptoms,
            symptomKeys: location.state?.symptomKeys || [],
            documents: documents,
            medicineAllergies: medicineAllergies,
            payment: {
              transaction_id: paymentResponse.data.transaction_id,
              amount: consultationFee,
              payment_method: paymentMethod,
              status: 'paid',
            },
          },
        });
      } else {
        setError(paymentResponse.data.error || "Payment processing failed");
      }
    } catch (err) {
      console.error("Payment error:", err);
      console.error("Payment error response:", err.response);
      console.error("Payment error data:", err.response?.data);
      
      // Extract error message from various possible locations
      const errorMessage = 
        err.response?.data?.error || 
        err.response?.data?.message ||
        err.message ||
        "Payment processing failed. Please try again.";
      
      setError(errorMessage);
    } finally {
      setProcessing(false);
    }
  };

  if (!doctor || !selectedDate || !selectedTime) {
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

      <button
        className="back-button-header"
        onClick={() => navigate("/document-upload", {
          state: {
            doctor: doctor,
            symptoms: symptoms,
            symptomKeys: location.state?.symptomKeys || [],
            documents: documents,
            medicineAllergies: medicineAllergies,
            appointmentType: appointmentType,
            selectedDate: selectedDate,
            selectedTime: selectedTime,
          }
        })}
        aria-label="Go back"
      >
        <ArrowLeft size={24} />
      </button>

      <main className="dashboard-main-content">
        <div className="payment-container">
          <div className="payment-header">
            <h1 className="payment-title">Payment</h1>
            <p className="payment-subtitle">Complete your payment to confirm your appointment</p>
          </div>

          {error && (
            <div className="payment-error">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          <div className="payment-content">
            {/* Appointment Summary */}
            <div className="payment-summary">
              <h2>Appointment Summary</h2>
              <div className="summary-item">
                <User size={20} />
                <div>
                  <span className="summary-label">Doctor</span>
                  <span className="summary-value">
                    Dr. {doctor.first_name} {doctor.last_name}
                  </span>
                </div>
              </div>
              <div className="summary-item">
                <Stethoscope size={20} />
                <div>
                  <span className="summary-label">Specialization</span>
                  <span className="summary-value">{doctor.specialization}</span>
                </div>
              </div>
              <div className="summary-item">
                <Calendar size={20} />
                <div>
                  <span className="summary-label">Date</span>
                  <span className="summary-value">{formatDate(selectedDate)}</span>
                </div>
              </div>
              <div className="summary-item">
                <Clock size={20} />
                <div>
                  <span className="summary-label">Time</span>
                  <span className="summary-value">{formatTimeTo12Hour(selectedTime)}</span>
                </div>
              </div>
              <div className="summary-total">
                <span className="total-label">Consultation Fee</span>
                <span className="total-amount">₱{consultationFee.toFixed(2)}</span>
              </div>
            </div>

            {/* Payment Form */}
            <div className="payment-form-container">
              <h2>Payment Details</h2>
              
              <div className="payment-method-selection">
                <label>Payment Method</label>
                <div className="payment-methods">
                  <button
                    className={`payment-method-btn ${paymentMethod === 'credit_card' ? 'active' : ''}`}
                    onClick={() => setPaymentMethod('credit_card')}
                  >
                    <CreditCard size={20} />
                    Credit Card
                  </button>
                  <button
                    className={`payment-method-btn ${paymentMethod === 'debit_card' ? 'active' : ''}`}
                    onClick={() => setPaymentMethod('debit_card')}
                  >
                    <CreditCard size={20} />
                    Debit Card
                  </button>
                  <button
                    className={`payment-method-btn ${paymentMethod === 'gcash' ? 'active' : ''}`}
                    onClick={() => setPaymentMethod('gcash')}
                  >
                    <Smartphone size={20} />
                    GCash
                  </button>
                </div>
              </div>

              {/* GCash QR Code Display */}
              {paymentMethod === 'gcash' && (
                <div className="gcash-payment-container">
                  {!gcashQRCode ? (
                    <div className="gcash-init">
                      <div className="gcash-info">
                        <Smartphone size={48} className="gcash-icon" />
                        <h3>Pay with GCash</h3>
                        <p>Scan the QR code with your GCash app to complete payment</p>
                        <p className="gcash-amount">Amount: ₱{consultationFee.toFixed(2)}</p>
                      </div>
                      <button
                        className="payment-submit-btn gcash-generate-btn"
                        onClick={handleGCashPayment}
                        disabled={processing || loading}
                      >
                        {processing ? (
                          <>
                            <div className="spinner"></div>
                            Generating QR Code...
                          </>
                        ) : (
                          <>
                            <QrCode size={20} />
                            Generate GCash QR Code
                          </>
                        )}
                      </button>
                    </div>
                  ) : (
                    <div className="gcash-qr-display">
                      <div className="gcash-qr-header">
                        <h3>Scan with GCash App</h3>
                        <p>Open GCash on your phone and scan this QR code</p>
                      </div>
                      
                      {/* Scan Instructions */}
                      <div className="gcash-scan-instructions">
                        <div className="scan-step">
                          <div className="step-number">1</div>
                          <div className="step-content">
                            <strong>Open GCash App</strong>
                            <p>On your mobile phone</p>
                          </div>
                        </div>
                        <div className="scan-step">
                          <div className="step-number">2</div>
                          <div className="step-content">
                            <strong>Tap "Scan QR"</strong>
                            <p>In the GCash app</p>
                          </div>
                        </div>
                        <div className="scan-step">
                          <div className="step-number">3</div>
                          <div className="step-content">
                            <strong>Point camera at QR code</strong>
                            <p>On this screen</p>
                          </div>
                        </div>
                      </div>
                      
                      {/* QR Code Display - Simple and clean like GCash app */}
                      <div className="gcash-qr-code-wrapper">
                        <img src={gcashQRCode} alt="GCash QR Code" className="gcash-qr-code" />
                        {gcashVerified && (
                          <div className="gcash-verified-badge">
                            <Check size={24} />
                            Payment Verified!
                          </div>
                        )}
                      </div>

                      {/* Payment Details */}
                      <div className="gcash-merchant-info">
                        <div className="gcash-merchant-name">MEDICHAIN</div>
                        <div className="gcash-merchant-details">
                          <div className="gcash-detail-item">
                            <span className="gcash-detail-label">GCash Account:</span>
                            <span className="gcash-detail-value">{process.env.REACT_APP_GCASH_MERCHANT_ACCOUNT || "09171234567"}</span>
                          </div>
                          <div className="gcash-detail-item">
                            <span className="gcash-detail-label">Amount:</span>
                            <span className="gcash-detail-value">₱{consultationFee.toFixed(2)}</span>
                          </div>
                          <div className="gcash-detail-item">
                            <span className="gcash-detail-label">Reference:</span>
                            <span className="gcash-detail-value">{gcashReference}</span>
                          </div>
                        </div>
                        <div className="gcash-payment-instructions">
                          <p><strong>📱 How to Pay:</strong></p>
                          <p>1. Open GCash app and tap <strong>"Scan QR"</strong></p>
                          <p>2. Scan the QR code above</p>
                          <p>3. <strong>IMPORTANT:</strong> Enter amount: <strong style={{color: '#d32f2f', fontSize: '1.1rem'}}>₱{consultationFee.toFixed(2)}</strong></p>
                          <p>4. In the message/notes field, type: <strong style={{color: '#1976d2'}}>{gcashReference}</strong></p>
                          <p>5. Review and complete the payment</p>
                          <div style={{marginTop: '15px', padding: '12px', background: '#e3f2fd', borderRadius: '8px', borderLeft: '4px solid #2196F3'}}>
                            <p style={{margin: '0', color: '#1565c0', fontSize: '0.9rem', fontWeight: '600'}}>
                              💡 <strong>Tip:</strong> Make sure to enter the exact amount and reference number for payment verification!
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Payment Status */}
                      {gcashPolling && !gcashVerified && (
                        <div className="gcash-status">
                          <div className="spinner"></div>
                          <p>Waiting for payment verification...</p>
                          <p className="gcash-status-note">
                            After completing payment in GCash, enter your GCash reference number below to verify your payment.
                          </p>
                          
                          {/* GCash Reference Number Input */}
                          <div className="gcash-reference-input-container">
                            <label htmlFor="gcash-reference-input" className="gcash-reference-label">
                              Enter GCash Reference Number:
                            </label>
                            <div className="gcash-reference-input-group">
                              <input
                                id="gcash-reference-input"
                                type="text"
                                className="gcash-reference-input"
                                placeholder="Enter reference number from GCash"
                                value={gcashReferenceInput}
                                onChange={(e) => setGcashReferenceInput(e.target.value.toUpperCase())}
                                disabled={verifyingReference}
                              />
                              <button
                                className="gcash-verify-reference-btn"
                                onClick={async () => {
                                  if (!gcashReferenceInput.trim()) {
                                    setError("Please enter your GCash reference number");
                                    return;
                                  }
                                  
                                  try {
                                    setVerifyingReference(true);
                                    setError(null);
                                    
                                    const token = await getFirebaseToken();
                                    const response = await axios.post(
                                      `${API_CONFIG.API_URL}/appointments/payment/verify-reference`,
                                      {
                                        gcash_reference_number: gcashReferenceInput.trim(),
                                        transaction_id: gcashReference
                                      },
                                      {
                                        headers: {
                                          Authorization: `Bearer ${token}`,
                                          "Content-Type": "application/json",
                                        },
                                      }
                                    );
                                    
                                    if (response.data.success) {
                                      setGcashVerified(true);
                                      setGcashPolling(false);
                                      if (pollingIntervalRef.current) {
                                        clearInterval(pollingIntervalRef.current);
                                      }
                                      
                                      // Navigate to booking form
                                      navigate("/book-appointment-form", {
                                        state: {
                                          doctor: doctor,
                                          appointmentType: appointmentType,
                                          selectedDate: selectedDate,
                                          selectedTime: selectedTime,
                                          symptoms: symptoms,
                                          symptomKeys: location.state?.symptomKeys || [],
                                          documents: documents,
                                          medicineAllergies: medicineAllergies,
                                          payment: {
                                            transaction_id: gcashReference,
                                            amount: consultationFee,
                                            payment_method: 'gcash',
                                            status: 'paid',
                                          },
                                        },
                                      });
                                    }
                                  } catch (err) {
                                    console.error("Error verifying reference:", err);
                                    setError(err.response?.data?.error || "Reference number not found. Please check and try again.");
                                  } finally {
                                    setVerifyingReference(false);
                                  }
                                }}
                                disabled={verifyingReference || !gcashReferenceInput.trim()}
                              >
                                {verifyingReference ? (
                                  <>
                                    <div className="spinner-small"></div>
                                    Verifying...
                                  </>
                                ) : (
                                  <>
                                    <Check size={18} />
                                    Verify Payment
                                  </>
                                )}
                              </button>
                            </div>
                            <p className="gcash-reference-help">
                              💡 Find your reference number in your GCash transaction history or receipt
                            </p>
                          </div>
                        </div>
                      )}
                      
                      {gcashVerified && (
                        <div className="gcash-success">
                          <Check size={24} />
                          <p>Payment confirmed! Confirming your booking...</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Card Payment Form - Only show if not GCash */}
              {paymentMethod !== 'gcash' && (
                <>
                  <div className="form-group">
                    <label htmlFor="cardNumber">Card Number</label>
                    <input
                      type="text"
                      id="cardNumber"
                      placeholder="1234 5678 9012 3456"
                      value={cardNumber}
                      onChange={handleCardNumberChange}
                      maxLength={19}
                      disabled={processing}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="cardName">Cardholder Name</label>
                    <input
                      type="text"
                      id="cardName"
                      placeholder="John Doe"
                      value={cardName}
                      onChange={(e) => setCardName(e.target.value)}
                      disabled={processing}
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="expiryDate">Expiry Date</label>
                      <input
                        type="text"
                        id="expiryDate"
                        placeholder="MM/YY"
                        value={expiryDate}
                        onChange={handleExpiryChange}
                        maxLength={5}
                        disabled={processing}
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="cvv">CVV</label>
                      <input
                        type="text"
                        id="cvv"
                        placeholder="123"
                        value={cvv}
                        onChange={handleCvvChange}
                        maxLength={3}
                        disabled={processing}
                      />
                    </div>
                  </div>

                  <button
                    className="payment-submit-btn"
                    onClick={handlePayment}
                    disabled={processing || loading}
                  >
                    {processing ? (
                      <>
                        <div className="spinner"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <Check size={20} />
                        Pay ₱{consultationFee.toFixed(2)} & Continue
                      </>
                    )}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Payment;


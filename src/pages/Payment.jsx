import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import { CreditCard, ArrowLeft, Check, AlertCircle, Calendar, Clock, User, Stethoscope } from "lucide-react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { API_CONFIG } from "../config/api";
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
            // Default fee if not set
            setConsultationFee(500.00);
          }
        }
      } catch (err) {
        console.error("Error fetching doctor fee:", err);
        // Default fee on error
        setConsultationFee(500.00);
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

  const handlePayment = async () => {
    // Validate form
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
                </div>
              </div>

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
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Payment;


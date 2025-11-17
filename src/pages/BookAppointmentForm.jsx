import React, { useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import { Calendar, Clock, User, Stethoscope, ArrowLeft, Check, AlertCircle } from "lucide-react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { auth } from "../config/firebase";
import { API_CONFIG } from "../config/api";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/BookAppointmentForm.css";

// Get current time in Asia/Manila timezone
const getManilaNow = () => {
  const now = new Date();
  // Convert to Manila time (UTC+8)
  const manilaOffset = 8 * 60; // Manila is UTC+8
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
  const manilaTime = new Date(utc + (manilaOffset * 60000));
  return manilaTime;
};

// Filter out past time slots based on Manila timezone
const filterPastTimeSlots = (date, timeSlots) => {
  if (!date || !timeSlots || timeSlots.length === 0) return [];
  
  const now = getManilaNow();
  const today = now.toISOString().split('T')[0];
  
  // If it's today, filter out past times
  if (date === today) {
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentMinutes = currentHour * 60 + currentMinute;
    
    return timeSlots.filter(time => {
      const [hours, minutes] = time.split(':').map(Number);
      const slotMinutes = hours * 60 + minutes;
      return slotMinutes > currentMinutes;
    });
  }
  
  // For future dates, return all slots
  return timeSlots;
};

const BookAppointmentForm = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, loading: authLoading, getFirebaseToken } = useAuth();
  
  // Try to get doctor from location.state first, then from sessionStorage as fallback
  let doctorFromState = location.state?.doctor;
  let doctorFromStorage = null;
  
  try {
    const storedDoctor = sessionStorage.getItem('selectedDoctor');
    if (storedDoctor) {
      doctorFromStorage = JSON.parse(storedDoctor);
      console.log("✅ BookAppointmentForm: Found doctor in sessionStorage");
    }
  } catch (e) {
    console.warn("⚠️ BookAppointmentForm: Could not read doctor from sessionStorage:", e);
  }
  
  const doctor = doctorFromState || doctorFromStorage;

  const [availability, setAvailability] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [notes, setNotes] = useState("");
  const [followUpCheckup, setFollowUpCheckup] = useState(false);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const fetchDoctorAvailability = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Check authentication
      if (!isAuthenticated || !user) {
        console.log("❌ BookAppointmentForm: Not authenticated, redirecting to login");
        navigate("/login", { replace: true });
        return;
      }

      // Get Firebase token (required for @firebase_auth_required endpoints)
      let token = null;
      let tokenSource = 'unknown';
      
      // Try to get Firebase token first
      try {
        const currentUser = auth.currentUser;
        if (currentUser) {
          console.log("🔍 BookAppointmentForm: Getting Firebase token from currentUser...");
          token = await currentUser.getIdToken(true); // Force refresh to get fresh token
          tokenSource = 'firebase';
          console.log("✅ BookAppointmentForm: Got fresh Firebase token (length:", token.length, ")");
        } else {
          console.warn("⚠️ BookAppointmentForm: auth.currentUser is null");
        }
      } catch (firebaseError) {
        console.warn("⚠️ BookAppointmentForm: Could not get Firebase token:", firebaseError);
      }
      
      // Fallback to medichain_token if Firebase token not available
      if (!token) {
        token = localStorage.getItem('medichain_token');
        tokenSource = 'medichain_token';
        if (token) {
          console.log("✅ BookAppointmentForm: Using medichain_token as fallback (length:", token.length, ")");
        }
      }
      
      if (!token) {
        console.log("❌ BookAppointmentForm: No token found, redirecting to login");
        setError("Session expired. Please log in again.");
        navigate("/login", { replace: true });
        return;
      }

      console.log("✅ BookAppointmentForm: Token obtained from", tokenSource);
      console.log("✅ BookAppointmentForm: Fetching availability for doctor:", doctor.firebase_uid);

      const response = await axios.get(
        `${API_CONFIG.API_URL}/appointments/availability/${doctor.firebase_uid}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.success) {
        // New format: { "2025-11-06": ["07:00", "07:30", ...], ... }
        // Old format: [{ date: "2025-11-06", time_slots: [...] }, ...]
        const avail = response.data.availability || {};
        
        if (typeof avail === 'object' && !Array.isArray(avail)) {
          // New format: object with dates as keys
          const sortedDates = Object.keys(avail).sort();
          const now = getManilaNow();
          const today = now.toISOString().split('T')[0];
          
          // Filter out past dates and filter past time slots for today
          const formattedAvailability = sortedDates
            .filter(date => date >= today) // Only include today and future dates
            .map(date => {
              const timeSlots = avail[date] || [];
              // Filter past time slots for today
              const filteredSlots = filterPastTimeSlots(date, timeSlots);
              return {
                date,
                time_slots: filteredSlots
              };
            })
            .filter(slot => slot.time_slots.length > 0); // Remove dates with no available slots
          
          setAvailability(formattedAvailability);
        } else if (Array.isArray(avail)) {
          // Old format: array
          const today = getManilaNow().toISOString().split('T')[0];
          const futureAvailability = avail.filter(
            slot => slot.date >= today
          ).sort((a, b) => new Date(a.date) - new Date(b.date));
          setAvailability(futureAvailability);
        } else {
          setAvailability([]);
        }
      } else {
        setError(response.data.error || "Failed to load availability");
      }
    } catch (err) {
      console.error("Error fetching availability:", err);
      setError("Failed to load doctor's availability");
    } finally {
      setLoading(false);
    }
  }, [doctor, isAuthenticated, user, navigate]);

  // Fetch user profile to get date of birth
  const fetchUserProfile = useCallback(async () => {
    if (!isAuthenticated || !user) {
      return;
    }

    try {
      // Get authentication token
      let token = null;
      try {
        const currentUser = auth.currentUser;
        if (currentUser) {
          token = await currentUser.getIdToken(true);
        }
      } catch (firebaseError) {
        console.warn("⚠️ BookAppointmentForm: Could not get Firebase token for profile:", firebaseError);
      }
      
      if (!token) {
        token = localStorage.getItem('medichain_token');
      }
      
      if (!token) {
        console.warn("⚠️ BookAppointmentForm: No token available to fetch profile");
        return;
      }

      // Fetch user profile
      const response = await axios.get('http://localhost:5000/api/profile/patient', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (response.data?.success && response.data?.profile) {
        const profileData = response.data.profile.user_profile || response.data.profile;
        const dob = profileData.date_of_birth;
        
        if (dob) {
          // Format date to YYYY-MM-DD for input field
          const dobDate = new Date(dob);
          if (!isNaN(dobDate.getTime())) {
            const formattedDob = dobDate.toISOString().split('T')[0];
            setDateOfBirth(formattedDob);
            console.log("✅ BookAppointmentForm: Loaded date of birth from profile:", formattedDob);
          }
        }
      }
    } catch (err) {
      console.warn("⚠️ BookAppointmentForm: Could not fetch user profile for DOB:", err);
      // Continue without pre-filling DOB - user can still enter it manually
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    console.log("🔍 BookAppointmentForm: Component mounted");
    console.log("🔍 BookAppointmentForm: location.state =", location.state);
    console.log("🔍 BookAppointmentForm: doctor =", doctor);
    console.log("🔍 BookAppointmentForm: selectedDate =", location.state?.selectedDate);
    console.log("🔍 BookAppointmentForm: selectedTime =", location.state?.selectedTime);
    console.log("🔍 BookAppointmentForm: authLoading =", authLoading);
    console.log("🔍 BookAppointmentForm: isAuthenticated =", isAuthenticated);
    console.log("🔍 BookAppointmentForm: user =", user);
    
    // Wait for AuthContext to finish loading
    if (authLoading) {
      console.log("⏳ BookAppointmentForm: AuthContext still loading, waiting...");
      setLoading(true);
      return;
    }
    
    // Check authentication after loading is complete
    if (!isAuthenticated || !user) {
      console.log("❌ BookAppointmentForm: Not authenticated, redirecting to login");
      setError("Please log in to continue");
      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1000);
      return;
    }
    
    if (!doctor) {
      console.log("❌ BookAppointmentForm: No doctor found, redirecting to /select-gp");
      setError("No doctor selected. Redirecting to doctor selection...");
      setTimeout(() => {
        navigate("/select-gp");
      }, 2000);
      return;
    }
    
    // Fetch user profile to pre-fill date of birth
    fetchUserProfile();
    
    // If date and time are passed from SelectDateTime, use them
    const dateFromState = location.state?.selectedDate;
    const timeFromState = location.state?.selectedTime;
    const dateFromStorage = sessionStorage.getItem('selectedDate');
    const timeFromStorage = sessionStorage.getItem('selectedTime');
    
    if (dateFromState && timeFromState) {
      console.log("✅ BookAppointmentForm: Date and time pre-selected from state");
      setSelectedDate(dateFromState);
      setSelectedTime(timeFromState);
    } else if (dateFromStorage && timeFromStorage) {
      console.log("✅ BookAppointmentForm: Date and time pre-selected from sessionStorage");
      setSelectedDate(dateFromStorage);
      setSelectedTime(timeFromStorage);
    }
    
    console.log("✅ BookAppointmentForm: Doctor found, fetching availability");
    fetchDoctorAvailability();
  }, [doctor, navigate, location, isAuthenticated, user, authLoading, fetchDoctorAvailability, fetchUserProfile]);

  const handleBookAppointment = async () => {
    if (!selectedDate || !selectedTime) {
      setError("Please select both date and time");
      return;
    }

    if (!dateOfBirth) {
      setError("Please enter your date of birth");
      return;
    }

    if (!doctor) {
      setError("Doctor information is missing. Please go back and select a doctor again.");
      return;
    }

    try {
      setBooking(true);
      setError(null);

      // Check authentication
      if (!isAuthenticated || !user) {
        console.log("❌ BookAppointmentForm: Not authenticated, redirecting to login");
        navigate("/login", { replace: true });
        return;
      }

      // Get authentication token (@auth_required accepts both Firebase and JWT tokens)
      let token = null;
      let tokenSource = 'unknown';
      
      // Strategy 1: Try to get Firebase token using AuthContext helper
      try {
        if (getFirebaseToken) {
          console.log("🔍 BookAppointmentForm: Attempting to get Firebase token via AuthContext...");
          token = await getFirebaseToken();
          tokenSource = 'firebase_via_authcontext';
          console.log("✅ BookAppointmentForm: Got Firebase token via AuthContext (length:", token.length, ")");
        }
      } catch (authContextError) {
        console.warn("⚠️ BookAppointmentForm: Could not get token via AuthContext:", authContextError);
      }
      
      // Strategy 2: Try to get Firebase token from auth.currentUser
      if (!token) {
        try {
          // Wait a bit for auth state to sync if currentUser is null
          let currentUser = auth.currentUser;
          if (!currentUser && user?.uid) {
            console.log("🔍 BookAppointmentForm: currentUser is null, waiting for auth state sync...");
            await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms
            currentUser = auth.currentUser;
          }
          
          if (currentUser) {
            console.log("🔍 BookAppointmentForm: Getting Firebase token from currentUser...");
            token = await currentUser.getIdToken(true); // Force refresh to get fresh token
            tokenSource = 'firebase';
            console.log("✅ BookAppointmentForm: Got fresh Firebase token (length:", token.length, ")");
          } else {
            console.warn("⚠️ BookAppointmentForm: auth.currentUser is null after wait");
          }
        } catch (firebaseError) {
          console.warn("⚠️ BookAppointmentForm: Could not get Firebase token:", firebaseError);
        }
      }
      
      // Strategy 3: Check stored Firebase token
      if (!token) {
        const storedFirebaseToken = sessionStorage.getItem('firebase_id_token') || 
                                    localStorage.getItem('firebase_id_token');
        if (storedFirebaseToken) {
          console.log("✅ BookAppointmentForm: Using stored Firebase token");
          token = storedFirebaseToken;
          tokenSource = 'stored_firebase';
        }
      }
      
      // Fallback to medichain_token if Firebase token not available
      // @auth_required decorator accepts both Firebase tokens and JWT tokens (medichain_token)
      if (!token) {
        token = localStorage.getItem('medichain_token');
        tokenSource = 'medichain_token';
        if (token) {
          console.log("✅ BookAppointmentForm: Using medichain_token (length:", token.length, ")");
          console.log("ℹ️ BookAppointmentForm: @auth_required decorator accepts JWT tokens");
        }
      }
      
      if (!token) {
        console.log("❌ BookAppointmentForm: No token found, redirecting to login");
        setError("Session expired. Please log in again.");
        navigate("/login", { replace: true });
        return;
      }

      console.log("✅ BookAppointmentForm: Token obtained from", tokenSource);
      console.log("✅ BookAppointmentForm: Booking appointment with:", {
        doctor_firebase_uid: doctor.firebase_uid,
        appointment_date: selectedDate,
        appointment_time: selectedTime,
        appointment_type: location.state?.appointmentType || "general-practitioner",
      });

      // Prepare document data (convert File objects to base64)
      const documentData = await Promise.all(
        (location.state?.documents || []).map(async (doc) => {
          try {
            // If doc is a File object, convert to base64
            if (doc instanceof File || (doc.file && doc.file instanceof File)) {
              const file = doc.file || doc;
              
              // Check file size (limit to 5MB to avoid database issues)
              const maxSize = 5 * 1024 * 1024; // 5MB
              if (file.size > maxSize) {
                throw new Error(`File ${file.name} is too large. Maximum size is 5MB.`);
              }
              
              return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                  try {
                    const base64String = reader.result;
                    // Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
                    const base64Data = base64String.includes(',') 
                      ? base64String.split(',')[1] 
                      : base64String;
                    
                    resolve({
                      name: file.name,
                      size: file.size,
                      type: file.type,
                      data: base64Data, // Store base64 data
                    });
                  } catch (err) {
                    reject(new Error(`Failed to process file ${file.name}: ${err.message}`));
                  }
                };
                reader.onerror = () => reject(new Error(`Failed to read file ${file.name}`));
                reader.readAsDataURL(file);
              });
            } else {
              // If it's already metadata, just return it (might already have base64)
              return {
                name: doc.name || doc.filename,
                size: doc.size,
                type: doc.type,
                data: doc.data || doc.base64, // Preserve existing base64 if present
              };
            }
          } catch (err) {
            console.error(`Error processing document: ${err.message}`);
            throw new Error(`Failed to process document: ${err.message}`);
          }
        })
      );

      const response = await axios.post(
        `${API_CONFIG.API_URL}/appointments`,
        {
          doctor_firebase_uid: doctor.firebase_uid,
          appointment_date: selectedDate,
          appointment_time: selectedTime,
          appointment_type: location.state?.appointmentType || "general-practitioner",
          date_of_birth: dateOfBirth,
          notes: notes,
          follow_up_checkup: followUpCheckup,
          symptoms: location.state?.symptomKeys || location.state?.symptoms || [],
          documents: documentData,
          medicine_allergies: location.state?.medicineAllergies || "",
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data.success) {
        setSuccess(true);
        // Clear sessionStorage after successful booking
        sessionStorage.removeItem('selectedDoctor');
        sessionStorage.removeItem('selectedDate');
        sessionStorage.removeItem('selectedTime');
        sessionStorage.removeItem('appointmentType');
        
        // Trigger notification refresh event
        window.dispatchEvent(new CustomEvent('appointmentBooked', { 
          detail: { appointmentId: response.data.appointment?.id } 
        }));
        
        setTimeout(() => {
          navigate("/dashboard");
        }, 2000);
      } else {
        setError(response.data.error || "Failed to book appointment");
      }
    } catch (err) {
      console.error("❌ BookAppointmentForm: Error booking appointment:", err);
      console.error("❌ BookAppointmentForm: Error response:", err.response?.data);
      console.error("❌ BookAppointmentForm: Error status:", err.response?.status);
      
      if (err.response?.status === 401) {
        const errorMsg = err.response?.data?.error || err.response?.data?.details || "Invalid token. Please log in again.";
        console.error("❌ BookAppointmentForm: 401 Unauthorized - Token invalid");
        setError(errorMsg);
        // Optionally redirect to login after showing error
        setTimeout(() => {
          navigate("/login", { replace: true });
        }, 3000);
      } else {
        setError(err.response?.data?.error || "Failed to book appointment. Please try again.");
      }
    } finally {
      setBooking(false);
    }
  };

  // Convert 24-hour format to 12-hour format with AM/PM
  const formatTimeTo12Hour = (time24) => {
    if (!time24) return '';
    const [hours, minutes] = time24.split(':');
    const hour = parseInt(hours, 10);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
  };

  const getAvailableTimesForDate = () => {
    if (!selectedDate) return [];
    const dateSlot = availability.find(slot => slot.date === selectedDate);
    if (!dateSlot) return [];
    
    const timeSlots = dateSlot.time_slots || [];
    // Filter out past time slots based on Manila timezone
    return filterPastTimeSlots(selectedDate, timeSlots);
  };

  if (!doctor) {
    return null;
  }

  return (
    <div className="dashboard-container fade-in">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            +
          </span>
        ))}
      </div>

      <Header />

      <main className="dashboard-main-content">
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">BOOK APPOINTMENT</h1>
            <p className="dashboard-subtitle">
              Schedule your appointment with Dr. {doctor.first_name} {doctor.last_name}
            </p>
          </div>

          {/* Success Message */}
          {success && (
            <div className="alert alert-success">
              <Check size={24} />
              <div>
                <strong>Appointment Booked!</strong>
                <p>Redirecting to dashboard...</p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="alert alert-error">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {/* Doctor Info Card */}
          <div className="doctor-info-card">
            <div className="doctor-info-header">
              <div className="doctor-avatar-large">
                <User size={48} />
              </div>
              <div className="doctor-info-details">
                <h2>Dr. {doctor.first_name} {doctor.last_name}</h2>
                <p className="doctor-specialization-text">
                  <Stethoscope size={18} />
                  {doctor.specialization}
                </p>
              </div>
            </div>
          </div>

          {/* Booking Form */}
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading available slots...</p>
            </div>
          ) : availability.length === 0 ? (
            <div className="no-availability-message">
              <Calendar size={48} />
              <h3>No Available Slots</h3>
              <p>This doctor currently has no available appointment slots.</p>
              <button className="back-button-inline" onClick={() => navigate("/select-gp")}>
                <ArrowLeft size={18} />
                Choose Another Doctor
              </button>
            </div>
          ) : (
            <div className="booking-form-card">
              {/* If date and time are pre-selected, show summary view */}
              {selectedDate && selectedTime ? (
                <>
                  <h3 className="form-section-title">
                    <Check size={20} />
                    Appointment Details
                  </h3>

                  {/* Selected Appointment Summary */}
                  <div className="appointment-summary">
                    <h4>Selected Appointment</h4>
                    <div className="summary-details">
                      <div className="summary-item">
                        <User size={18} />
                        <span>Dr. {doctor.first_name} {doctor.last_name}</span>
                      </div>
                      <div className="summary-item">
                        <Calendar size={18} />
                        <span>
                          {new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })}
                        </span>
                      </div>
                      <div className="summary-item">
                        <Clock size={18} />
                        <span>{formatTimeTo12Hour(selectedTime)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Allow changing date/time if needed */}
                  <div className="form-group" style={{ marginTop: '24px' }}>
                    <button
                      className="change-selection-button"
                      onClick={() => {
                        // Navigate back to SelectDateTime page
                        navigate("/select-date-time", {
                          state: {
                            doctor: doctor,
                            appointmentType: location.state?.appointmentType || "general-practitioner",
                          },
                        });
                      }}
                      style={{
                        padding: '8px 16px',
                        background: 'transparent',
                        border: '1px solid #2196F3',
                        color: '#2196F3',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        fontWeight: '500'
                      }}
                    >
                      Change Date & Time
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <h3 className="form-section-title">
                    <Calendar size={20} />
                    Select Appointment Date & Time
                  </h3>

                  {/* Date Selection */}
                  <div className="form-group">
                    <label className="form-label">Select Date</label>
                    <div className="date-options-grid">
                      {availability.map((slot) => (
                        <button
                          key={slot.date}
                          className={`date-option ${selectedDate === slot.date ? 'selected' : ''}`}
                          onClick={() => {
                            setSelectedDate(slot.date);
                            setSelectedTime(""); // Reset time when date changes
                          }}
                        >
                          <Calendar size={16} />
                          <span className="date-text">
                            {new Date(slot.date + 'T00:00:00').toLocaleDateString('en-US', {
                              weekday: 'short',
                              month: 'short',
                              day: 'numeric'
                            })}
                          </span>
                          <span className="slots-count">{slot.time_slots.length} slots</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Time Selection */}
                  {selectedDate && (
                    <div className="form-group">
                      <label className="form-label">Select Time</label>
                      <div className="time-options-grid">
                        {getAvailableTimesForDate().map((time) => (
                          <button
                            key={time}
                            className={`time-option ${selectedTime === time ? 'selected' : ''}`}
                            onClick={() => setSelectedTime(time)}
                          >
                            <Clock size={16} />
                            {formatTimeTo12Hour(time)}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Date of Birth */}
              <div className="form-group">
                <label className="form-label">Date of Birth <span style={{ color: '#ef4444' }}>*</span></label>
                <input
                  type="date"
                  className="form-input"
                  value={dateOfBirth}
                  onChange={(e) => setDateOfBirth(e.target.value)}
                  required
                  max={new Date().toISOString().split('T')[0]}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontFamily: 'inherit'
                  }}
                />
                <small style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '4px', display: 'block' }}>
                  Required for medical records and prescriptions
                </small>
              </div>

              {/* Follow-up Checkup */}
              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={followUpCheckup}
                    onChange={(e) => setFollowUpCheckup(e.target.checked)}
                    style={{
                      width: '20px',
                      height: '20px',
                      cursor: 'pointer',
                      accentColor: '#2196F3'
                    }}
                  />
                  <span>This is a follow-up checkup</span>
                </label>
              </div>

              {/* Notes */}
              <div className="form-group">
                <label className="form-label">Additional Notes (Optional)</label>
                <textarea
                  className="form-textarea"
                  rows="4"
                  placeholder="Any specific concerns or information for the doctor..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              {/* Appointment Summary - Only show if date/time selected but not pre-selected (i.e., user selected in this form) */}
              {selectedDate && selectedTime && !location.state?.selectedDate && !location.state?.selectedTime && (
                <div className="appointment-summary">
                  <h4>Appointment Summary</h4>
                  <div className="summary-details">
                    <div className="summary-item">
                      <User size={18} />
                      <span>Dr. {doctor.first_name} {doctor.last_name}</span>
                    </div>
                    <div className="summary-item">
                      <Calendar size={18} />
                      <span>
                        {new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-US', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </span>
                    </div>
                    <div className="summary-item">
                      <Clock size={18} />
                      <span>{formatTimeTo12Hour(selectedTime)}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="form-actions">
                <button
                  className="cancel-button"
                  onClick={() => navigate("/select-gp")}
                  disabled={booking}
                >
                  <ArrowLeft size={18} />
                  Back
                </button>
                <button
                  className="book-button"
                  onClick={handleBookAppointment}
                  disabled={!selectedDate || !selectedTime || !dateOfBirth || booking}
                >
                  {booking ? (
                    <>
                      <div className="button-spinner"></div>
                      Booking...
                    </>
                  ) : (
                    <>
                      <Check size={18} />
                      Confirm Booking
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default BookAppointmentForm;

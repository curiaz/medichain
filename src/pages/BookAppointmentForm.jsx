import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import { Calendar, Clock, User, Stethoscope, ArrowLeft, Check, AlertCircle } from "lucide-react";
import axios from "axios";
import { auth } from "../config/firebase";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/BookAppointmentForm.css";

const BookAppointmentForm = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { doctor } = location.state || {};

  const [availability, setAvailability] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    console.log("🔍 BookAppointmentForm: Component mounted");
    console.log("🔍 BookAppointmentForm: location.state =", location.state);
    console.log("🔍 BookAppointmentForm: doctor =", doctor);
    console.log("🔍 BookAppointmentForm: selectedDate =", location.state?.selectedDate);
    console.log("🔍 BookAppointmentForm: selectedTime =", location.state?.selectedTime);
    
    if (!doctor) {
      console.log("❌ BookAppointmentForm: No doctor found, redirecting to /select-gp");
      navigate("/select-gp");
      return;
    }
    
    // If date and time are passed from SelectDateTime, use them
    if (location.state?.selectedDate && location.state?.selectedTime) {
      console.log("✅ BookAppointmentForm: Date and time pre-selected");
      setSelectedDate(location.state.selectedDate);
      setSelectedTime(location.state.selectedTime);
    }
    
    console.log("✅ BookAppointmentForm: Doctor found, fetching availability");
    fetchDoctorAvailability();
  }, [doctor]);

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

  const fetchDoctorAvailability = async () => {
    try {
      setLoading(true);
      setError(null);

      const currentUser = auth.currentUser;
      if (!currentUser) {
        navigate("/login");
        return;
      }

      const token = await currentUser.getIdToken();

      const response = await axios.get(
        `http://localhost:5000/api/appointments/availability/${doctor.firebase_uid}`,
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
  };

  const handleBookAppointment = async () => {
    if (!selectedDate || !selectedTime) {
      setError("Please select both date and time");
      return;
    }

    try {
      setBooking(true);
      setError(null);

      const currentUser = auth.currentUser;
      if (!currentUser) {
        navigate("/login");
        return;
      }

      const token = await currentUser.getIdToken();

      const response = await axios.post(
        "http://localhost:5000/api/appointments",
        {
          doctor_firebase_uid: doctor.firebase_uid,
          appointment_date: selectedDate,
          appointment_time: selectedTime,
          appointment_type: location.state?.appointmentType || "general-practitioner",
          notes: notes,
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
        setTimeout(() => {
          navigate("/dashboard");
        }, 2000);
      } else {
        setError(response.data.error || "Failed to book appointment");
      }
    } catch (err) {
      console.error("Error booking appointment:", err);
      setError(err.response?.data?.error || "Failed to book appointment. Please try again.");
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

              {/* Selected Appointment Summary */}
              {selectedDate && selectedTime && (
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
                  disabled={!selectedDate || !selectedTime || booking}
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

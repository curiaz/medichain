import React, { useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import { Calendar, ArrowLeft, Check, AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { auth } from "../config/firebase";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/SelectDateTime.css";

// Get current time in Asia/Manila timezone
const getManilaNow = () => {
  const now = new Date();
  // Convert to Manila time (UTC+8)
  const manilaOffset = 8 * 60; // Manila is UTC+8
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
  const manilaTime = new Date(utc + (manilaOffset * 60000));
  return manilaTime;
};

// Format a date to YYYY-MM-DD string consistently
// This ensures calendar dates match backend dates which use Manila timezone
// For calendar dates (no time component), we format directly to avoid timezone conversion issues
const formatDateManila = (date) => {
  if (!date) return '';
  // Format date components directly to avoid timezone conversion issues
  // This ensures dates match between frontend and backend regardless of browser timezone
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// Filter out past time slots based on Manila timezone
// If current time is past a slot, show the next available slot onwards
const filterPastTimeSlots = (date, timeSlots) => {
  if (!date || !timeSlots || timeSlots.length === 0) return [];
  
  const now = getManilaNow();
  const today = now.toISOString().split('T')[0];
  
  // If it's today, filter out past times
  if (date === today) {
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentMinutes = currentHour * 60 + currentMinute;
    
    // Filter out past time slots and return only future slots
    // If it's past 7:00 AM (420 minutes), only show 7:30 AM (450 minutes) onwards
    return timeSlots.filter(time => {
      const [hours, minutes] = time.split(':').map(Number);
      const slotMinutes = hours * 60 + minutes;
      
      // Only include slots that are strictly in the future
      // This ensures if current time is 7:15 AM, we show 7:30 AM onwards, not 7:00 AM
      return slotMinutes > currentMinutes;
    });
  }
  
  // For future dates, return all slots (they're already filtered for booked slots by backend)
  return timeSlots;
};

const SelectDateTime = () => {
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
      console.log("✅ SelectDateTime: Found doctor in sessionStorage");
    }
  } catch (e) {
    console.warn("⚠️ SelectDateTime: Could not read doctor from sessionStorage:", e);
  }
  
  const doctor = doctorFromState || doctorFromStorage;

  const [availability, setAvailability] = useState([]);
  const [rawAvailability, setRawAvailability] = useState({}); // Store raw availability data
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [availableDates, setAvailableDates] = useState([]); // Array of date strings that have slots

  const fetchDoctorAvailability = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Check authentication
      if (!isAuthenticated || !user) {
        console.log("❌ SelectDateTime: Not authenticated, redirecting to login");
        navigate("/login", { replace: true });
        return;
      }

      // Get Firebase token (required for @firebase_auth_required endpoints)
      let token = null;
      let tokenSource = 'unknown';
      
      // Strategy 1: Try to get Firebase token using AuthContext helper
      try {
        if (getFirebaseToken) {
          console.log("🔍 SelectDateTime: Attempting to get Firebase token via AuthContext...");
          token = await getFirebaseToken();
          tokenSource = 'firebase_via_authcontext';
          console.log("✅ SelectDateTime: Got Firebase token via AuthContext (length:", token.length, ")");
        }
      } catch (authContextError) {
        console.warn("⚠️ SelectDateTime: Could not get token via AuthContext:", authContextError);
      }
      
      // Strategy 2: Try to get Firebase token from auth.currentUser
      if (!token) {
        try {
          const currentUser = auth.currentUser;
          if (currentUser) {
            console.log("🔍 SelectDateTime: Getting Firebase token from currentUser...");
            token = await currentUser.getIdToken(true); // Force refresh to get fresh token
            tokenSource = 'firebase';
            console.log("✅ SelectDateTime: Got fresh Firebase token (length:", token.length, ")");
          } else {
            console.warn("⚠️ SelectDateTime: auth.currentUser is null");
          }
        } catch (firebaseError) {
          console.warn("⚠️ SelectDateTime: Could not get Firebase token:", firebaseError);
        }
      }
      
      // Fallback to medichain_token if Firebase token not available
      if (!token) {
        token = localStorage.getItem('medichain_token');
        tokenSource = 'medichain_token';
        if (token) {
          console.log("✅ SelectDateTime: Using medichain_token as fallback (length:", token.length, ")");
        }
      }
      
      if (!token) {
        console.log("❌ SelectDateTime: No token found, redirecting to login");
        setError("Session expired. Please log in again.");
        navigate("/login", { replace: true });
        return;
      }

      console.log("✅ SelectDateTime: Token obtained from", tokenSource);
      console.log("✅ SelectDateTime: Fetching availability for doctor:", doctor.firebase_uid);
      console.log("✅ SelectDateTime: Full doctor object:", doctor);

      const response = await axios.get(
        `https://medichainn.onrender.com/api/appointments/availability/${doctor.firebase_uid}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          timeout: 10000, // 10 second timeout
        }
      );

      console.log("✅ SelectDateTime: Availability response:", response.data);
      console.log("✅ SelectDateTime: Response status:", response.status);

      if (response.data.success) {
        const avail = response.data.availability || {};
        
        console.log("🔍 SelectDateTime: Raw availability data:", avail);
        console.log("🔍 SelectDateTime: Availability type:", typeof avail);
        console.log("🔍 SelectDateTime: Is array?", Array.isArray(avail));
        
        // Store raw availability for later use
        if (typeof avail === 'object' && !Array.isArray(avail)) {
          setRawAvailability(avail);
        } else if (Array.isArray(avail)) {
          // Convert array to object format for consistency
          const availObj = {};
          avail.forEach(slot => {
            if (slot.date && slot.time_slots) {
              availObj[slot.date] = slot.time_slots;
            }
          });
          setRawAvailability(availObj);
        }
        
        if (typeof avail === 'object' && !Array.isArray(avail)) {
          // New format: object with dates as keys
          const sortedDates = Object.keys(avail).sort();
          console.log("🔍 SelectDateTime: Found", sortedDates.length, "dates with availability");
          const now = getManilaNow();
          const today = now.toISOString().split('T')[0];
          
          // Filter out past dates and filter past time slots for today
          const formattedAvailability = sortedDates
            .filter(date => date >= today) // Only include today and future dates
            .map(date => {
              const timeSlots = avail[date] || [];
              // Filter past time slots only for today
              const filteredSlots = filterPastTimeSlots(date, timeSlots);
              return {
                date,
                time_slots: filteredSlots
              };
            })
            .filter(slot => slot.time_slots.length > 0); // Remove dates with no available slots after filtering
          
          console.log("✅ SelectDateTime: Formatted availability:", formattedAvailability);
          console.log("✅ SelectDateTime: Total dates with slots:", formattedAvailability.length);
          
          // Extract available dates for calendar highlighting - include all future dates that have raw availability
          const datesWithSlots = sortedDates.filter(date => date >= today && (avail[date] || []).length > 0);
          console.log("📅 SelectDateTime: Today is:", today);
          console.log("📅 SelectDateTime: Available dates for highlighting:", datesWithSlots);
          console.log("📅 SelectDateTime: Raw availability keys:", sortedDates);
          setAvailableDates(datesWithSlots);
          
          if (formattedAvailability.length === 0) {
            console.warn("⚠️ SelectDateTime: No future dates with available slots");
            setError("No available slots found. The doctor may not have set their availability schedule.");
          }
          
          setAvailability(formattedAvailability);
        } else if (Array.isArray(avail)) {
          // Old format: array
          console.log("🔍 SelectDateTime: Found array format with", avail.length, "entries");
          const today = getManilaNow().toISOString().split('T')[0];
          const futureAvailability = avail.filter(
            slot => slot.date >= today
          ).sort((a, b) => new Date(a.date) - new Date(b.date));
          
          // Extract available dates for calendar highlighting
          const datesWithSlots = futureAvailability.map(slot => slot.date);
          setAvailableDates(datesWithSlots);
          
          setAvailability(futureAvailability);
        } else {
          console.log("⚠️ SelectDateTime: Empty availability");
          setAvailability([]);
          setAvailableDates([]);
          setError("Doctor has not set their availability schedule yet.");
        }
      } else {
        console.error("❌ SelectDateTime: API returned success=false:", response.data);
        setError(response.data.error || "Failed to load availability");
        setAvailability([]);
        setAvailableDates([]);
      }
    } catch (err) {
      console.error("❌ SelectDateTime: Error fetching availability:", err);
      console.error("❌ SelectDateTime: Error response:", err.response);
      console.error("❌ SelectDateTime: Error status:", err.response?.status);
      console.error("❌ SelectDateTime: Error data:", err.response?.data);
      
      if (err.response?.status === 401) {
        console.log("❌ SelectDateTime: 401 Unauthorized - token may be expired or invalid");
        console.log("❌ SelectDateTime: Attempting to refresh Firebase token...");
        
        // Try to refresh Firebase token
        try {
          const currentUser = auth.currentUser;
          if (currentUser) {
            const refreshedToken = await currentUser.getIdToken(true);
            console.log("✅ SelectDateTime: Got refreshed token, retrying...");
            
            // Retry with refreshed token
            const retryResponse = await axios.get(
              `https://medichainn.onrender.com/api/appointments/availability/${doctor.firebase_uid}`,
              {
                headers: {
                  Authorization: `Bearer ${refreshedToken}`,
                },
                timeout: 10000, // 10 second timeout
              }
            );
            
            if (retryResponse.data.success) {
              console.log("✅ SelectDateTime: Retry successful!");
                // Process the response same as above
              const avail = retryResponse.data.availability || {};
              
              // Store raw availability
              if (typeof avail === 'object' && !Array.isArray(avail)) {
                setRawAvailability(avail);
              } else if (Array.isArray(avail)) {
                const availObj = {};
                avail.forEach(slot => {
                  if (slot.date && slot.time_slots) {
                    availObj[slot.date] = slot.time_slots;
                  }
                });
                setRawAvailability(availObj);
              }
              
              if (typeof avail === 'object' && !Array.isArray(avail)) {
                const sortedDates = Object.keys(avail).sort();
                const now = getManilaNow();
                const today = now.toISOString().split('T')[0];
                const formattedAvailability = sortedDates
                  .filter(date => date >= today)
                  .map(date => {
                    const timeSlots = avail[date] || [];
                    const filteredSlots = filterPastTimeSlots(date, timeSlots);
                    return { date, time_slots: filteredSlots };
                  })
                  .filter(slot => slot.time_slots.length > 0);
                
                const datesWithSlots = sortedDates.filter(date => date >= today && (avail[date] || []).length > 0);
                setAvailableDates(datesWithSlots);
                setAvailability(formattedAvailability);
                setLoading(false);
                return; // Success, exit early
              } else if (Array.isArray(avail)) {
                const today = getManilaNow().toISOString().split('T')[0];
                const futureAvailability = avail.filter(
                  slot => slot.date >= today
                ).sort((a, b) => new Date(a.date) - new Date(b.date));
                const datesWithSlots = futureAvailability.map(slot => slot.date);
                setAvailableDates(datesWithSlots);
                setAvailability(futureAvailability);
                setLoading(false);
                return; // Success, exit early
              }
            }
          }
        } catch (retryError) {
          console.error("❌ SelectDateTime: Retry also failed:", retryError);
          console.error("❌ SelectDateTime: Retry error response:", retryError.response);
          console.error("❌ SelectDateTime: Retry error status:", retryError.response?.status);
        }
        
        setError("Session expired. Please log in again.");
        setAvailability([]);
        setAvailableDates([]);
        setTimeout(() => {
          navigate("/login", { replace: true });
        }, 2000);
      } else if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        console.error("❌ SelectDateTime: Request timed out");
        setError("Request timed out. Please check your connection and try again.");
        setAvailability([]);
        setAvailableDates([]);
      } else if (err.response?.status === 404) {
        console.error("❌ SelectDateTime: Doctor not found");
        setError("Doctor not found or availability not set.");
        setAvailability([]);
        setAvailableDates([]);
      } else if (err.response?.status >= 500) {
        console.error("❌ SelectDateTime: Server error");
        setError("Server error. Please try again later.");
        setAvailability([]);
        setAvailableDates([]);
      } else if (err.message === 'Network Error' || !err.response) {
        console.error("❌ SelectDateTime: Network error - backend may not be running");
        setError("Cannot connect to server. Please ensure the backend is running and try again.");
        setAvailability([]);
        setAvailableDates([]);
      } else {
        console.error("❌ SelectDateTime: Unknown error:", err.message);
        setError(`Failed to load doctor's availability: ${err.message || 'Unknown error'}`);
        setAvailability([]);
        setAvailableDates([]);
      }
    } finally {
      setLoading(false);
    }
  }, [doctor, isAuthenticated, user, navigate, getFirebaseToken]);

  useEffect(() => {
    console.log("🔍 SelectDateTime: Component mounted");
    console.log("🔍 SelectDateTime: location.state =", location.state);
    console.log("🔍 SelectDateTime: doctor =", doctor);
    console.log("🔍 SelectDateTime: location.pathname =", location.pathname);
    console.log("🔍 SelectDateTime: authLoading =", authLoading);
    console.log("🔍 SelectDateTime: isAuthenticated =", isAuthenticated);
    console.log("🔍 SelectDateTime: user =", user);
    
    // Wait for AuthContext to finish loading
    if (authLoading) {
      console.log("⏳ SelectDateTime: AuthContext still loading, waiting...");
      setLoading(true);
      return;
    }
    
    // Check authentication after loading is complete
    if (!isAuthenticated || !user) {
      console.log("❌ SelectDateTime: Not authenticated (isAuthenticated:", isAuthenticated, ", user:", user, "), redirecting to login");
      setError("Please log in to continue");
      setLoading(false);
      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1000);
      return;
    }
    
    // Check if doctor exists, if not try to get from location state or redirect
    if (!doctor) {
      console.log("❌ SelectDateTime: No doctor found in location.state");
      console.log("❌ SelectDateTime: Full location object:", location);
      
      // Don't redirect immediately - show error message first
      setError("No doctor selected. Redirecting to doctor selection...");
      setLoading(false);
      
      // Redirect after a short delay to show error message
      const redirectTimer = setTimeout(() => {
        console.log("🔄 SelectDateTime: Redirecting to /select-gp");
        navigate("/select-gp", { replace: true });
      }, 2000);
      
      return () => clearTimeout(redirectTimer);
    }
    
    console.log("✅ SelectDateTime: Doctor found, fetching availability");
    console.log("✅ SelectDateTime: Doctor details:", {
      firebase_uid: doctor.firebase_uid,
      name: `${doctor.first_name} ${doctor.last_name}`,
      email: doctor.email
    });
    
    fetchDoctorAvailability();
  }, [doctor, navigate, location, isAuthenticated, user, authLoading, fetchDoctorAvailability]);

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
    
    // First, try to find in the availability array (filtered availability)
    const dateSlot = availability.find(slot => slot.date === selectedDate);
    if (dateSlot && dateSlot.time_slots && dateSlot.time_slots.length > 0) {
      // Already filtered, return as is
      return dateSlot.time_slots;
    }
    
    // If not found in filtered availability, check raw availability
    // This handles cases where the date exists but was filtered out during initial processing
    if (Object.keys(rawAvailability).length > 0) {
      const rawTimeSlots = rawAvailability[selectedDate];
      if (rawTimeSlots && Array.isArray(rawTimeSlots) && rawTimeSlots.length > 0) {
        // Filter past time slots for this specific date
        const filteredSlots = filterPastTimeSlots(selectedDate, rawTimeSlots);
        console.log(`✅ SelectDateTime: Found ${filteredSlots.length} time slots for ${selectedDate} in raw availability`);
        return filteredSlots;
      }
    }
    
    // If no availability found for this date, return empty array
    console.log(`⚠️ SelectDateTime: No time slots found for date ${selectedDate}`);
    return [];
  };

  // Helper function to get calendar days for current month
  const getCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    
    // First day of the month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    // Days to show (including previous month's trailing days)
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add previous month's trailing days
    const prevMonth = new Date(year, month, 0);
    const prevMonthDays = prevMonth.getDate();
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const dayDate = new Date(year, month - 1, prevMonthDays - i);
      days.push({
        date: prevMonthDays - i,
        isCurrentMonth: false,
        fullDate: formatDateManila(dayDate)
      });
    }
    
    // Add current month's days
    for (let day = 1; day <= daysInMonth; day++) {
      const dayDate = new Date(year, month, day);
      const fullDate = formatDateManila(dayDate);
      days.push({
        date: day,
        isCurrentMonth: true,
        fullDate: fullDate,
        hasSlots: availableDates.includes(fullDate)
      });
    }
    
    // Add next month's leading days to fill the grid
    const remainingDays = 42 - days.length; // 6 rows * 7 days
    for (let day = 1; day <= remainingDays; day++) {
      const dayDate = new Date(year, month + 1, day);
      days.push({
        date: day,
        isCurrentMonth: false,
        fullDate: formatDateManila(dayDate)
      });
    }
    
    return days;
  };

  const navigateMonth = (direction) => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + direction, 1));
  };

  const formatMonthYear = (date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const handleDateSelect = (date) => {
    console.log("🔍 SelectDateTime: Date selected:", date);
    setSelectedDate(date);
    setSelectedTime(""); // Reset time when date changes
  };

  const handleTimeSelect = (time) => {
    console.log("🔍 SelectDateTime: Time selected:", time);
    setSelectedTime(time);
  };

  const handleContinue = () => {
    if (!selectedDate || !selectedTime) {
      setError("Please select both date and time");
      return;
    }

    if (!doctor) {
      console.error("❌ SelectDateTime: No doctor object available");
      setError("Doctor information is missing. Please go back and select a doctor again.");
      return;
    }

    console.log("✅ SelectDateTime: Continuing to booking form");
    console.log("🔍 SelectDateTime: Selected date:", selectedDate);
    console.log("🔍 SelectDateTime: Selected time:", selectedTime);
    console.log("🔍 SelectDateTime: Doctor object:", doctor);
    console.log("🔍 SelectDateTime: Doctor firebase_uid:", doctor.firebase_uid);
    
    // Store doctor in sessionStorage as backup
    try {
      sessionStorage.setItem('selectedDoctor', JSON.stringify(doctor));
      sessionStorage.setItem('selectedDate', selectedDate);
      sessionStorage.setItem('selectedTime', selectedTime);
      sessionStorage.setItem('appointmentType', location.state?.appointmentType || "general-practitioner");
      console.log("✅ SelectDateTime: Doctor and selections stored in sessionStorage");
    } catch (e) {
      console.warn("⚠️ SelectDateTime: Could not store in sessionStorage:", e);
    }
    
    // Navigate to symptoms selection with selected date and time
    navigate("/symptoms-selection", {
      state: {
        doctor: doctor,
        appointmentType: location.state?.appointmentType || "general-practitioner",
        selectedDate: selectedDate,
        selectedTime: selectedTime,
      },
      replace: false, // Don't replace history so user can go back
    });
  };

  // Don't render the main content if doctor is missing - wait for redirect
  if (!doctor) {
    return (
      <div className="dashboard-container fade-in">
        <Header />
        <main className="dashboard-main-content">
          <div className="dashboard-header-section">
            <div className="error-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
              <AlertCircle size={48} style={{ color: '#e74c3c', marginBottom: '20px' }} />
              <p className="error-message" style={{ fontSize: '1.1rem', marginBottom: '20px' }}>
                {error || "No doctor selected. Please select a doctor first."}
              </p>
              <button 
                className="retry-button" 
                onClick={() => navigate("/select-gp", { replace: true })}
                style={{
                  padding: '12px 24px',
                  background: 'linear-gradient(135deg, #2196F3, #00BCD4)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '25px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Go Back to Select GP
              </button>
            </div>
          </div>
        </main>
      </div>
    );
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

      {/* Back Button */}
      <button
        className="back-button-header"
        onClick={() => navigate("/select-gp")}
        aria-label="Go back"
      >
        <ArrowLeft size={24} />
      </button>

      <main className="dashboard-main-content">
        <div className="select-date-time-container">
          {/* Header */}
          <div className="select-date-time-header">
            <h1>Select date & time slot</h1>
            <p className="timezone-note">
              The timing you see is in your local time zone (Asia/Manila | GMT+08:00)
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="alert alert-error">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {/* Loading State */}
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
            <>
              {/* Calendar Section */}
              <div className="calendar-wrapper">
                <div className="calendar-header">
                  <button
                    className="calendar-nav-button"
                    onClick={() => navigateMonth(-1)}
                    aria-label="Previous month"
                  >
                    <ChevronLeft size={20} />
                  </button>
                  <div className="calendar-month-year">
                    {formatMonthYear(currentMonth)}
                  </div>
                  <button
                    className="calendar-nav-button"
                    onClick={() => navigateMonth(1)}
                    aria-label="Next month"
                  >
                    <ChevronRight size={20} />
                  </button>
                </div>

                <div className="calendar-weekdays">
                  <div className="calendar-weekday">SUN</div>
                  <div className="calendar-weekday">MON</div>
                  <div className="calendar-weekday">TUE</div>
                  <div className="calendar-weekday">WED</div>
                  <div className="calendar-weekday">THU</div>
                  <div className="calendar-weekday">FRI</div>
                  <div className="calendar-weekday">SAT</div>
                </div>

                <div className="calendar-grid">
                  {getCalendarDays().map((day, index) => {
                    const isSelected = selectedDate === day.fullDate;
                    const isCurrentMonth = day.isCurrentMonth;
                    
                    // Get today's date
                    const today = getManilaNow().toISOString().split('T')[0];
                    const isPast = day.fullDate < today;

                    // Check if this date has available slots (either in filtered or raw availability)
                    const hasAvailableSlots = availableDates.includes(day.fullDate) || 
                                             (rawAvailability[day.fullDate] && rawAvailability[day.fullDate].length > 0);

                    // For current month dates, show as available if:
                    // 1. Not in the past
                    // 2. Has available slots (either in availableDates or rawAvailability)
                    const shouldShowAsAvailable = isCurrentMonth && !isPast && hasAvailableSlots;
                    const isClickable = shouldShowAsAvailable;

                    return (
                      <button
                        key={index}
                        className={`calendar-date ${
                          !isCurrentMonth ? 'other-month' : ''
                        } ${
                          isSelected ? 'selected' : 
                          shouldShowAsAvailable ? 'available' : 
                          'unavailable'
                        }`}
                        onClick={() => {
                          if (isClickable) {
                            handleDateSelect(day.fullDate);
                          }
                        }}
                        disabled={!isClickable}
                      >
                        {day.date}
                      </button>
                    );
                  })}
                </div>

                <div className="calendar-legend">
                  <div className="legend-item">
                    <div className="legend-dot available"></div>
                    <span style={{ color: '#999' }}>Available time slot</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-dot selected"></div>
                    <span style={{ color: '#2196F3', fontWeight: '600' }}>Selected date</span>
                  </div>
                </div>
              </div>

              {/* Time Slot Selection */}
              {selectedDate && (
                <div className="time-slot-section">
                  <h3 className="time-slot-header">Select Time</h3>
                  {getAvailableTimesForDate().length > 0 ? (
                    <div className="time-slots-container">
                      <div className="time-slots-wrapper">
                        {getAvailableTimesForDate().map((time) => {
                          const isSelected = selectedTime === time;
                          const time12Hour = formatTimeTo12Hour(time);
                          const [hour, period] = time12Hour.split(' ');
                          
                          return (
                            <button
                              key={time}
                              className={`time-slot-item ${isSelected ? 'selected' : ''}`}
                              onClick={() => handleTimeSelect(time)}
                            >
                              <div className="time-slot-hour">{hour}</div>
                              <div className="time-slot-period">{period}</div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ) : (
                    <div className="no-time-slots">
                      No available times for this date
                    </div>
                  )}
                </div>
              )}

              {/* Continue Button */}
              {selectedDate && selectedTime && (
                <div className="continue-button-container">
                  <button
                    className="continue-button"
                    onClick={handleContinue}
                  >
                    <Check size={20} />
                    Continue
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default SelectDateTime;


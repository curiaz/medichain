import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Header from "./Header";
import { Clock, Plus, Trash2, Save, AlertCircle } from "lucide-react";
import axios from "axios";
import { auth } from "../config/firebase";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/DoctorAvailability.css";

const DoctorAvailability = ({ embedded = false }) => {
  const navigate = useNavigate();
  const [availability, setAvailability] = useState({
    time_ranges: [
      { start_time: "07:00", end_time: "17:00", interval: 30 }
    ]
  });
  const [isAcceptingAppointments, setIsAcceptingAppointments] = useState(null); // Start with null, will be set from API
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const fetchAvailability = useCallback(async () => {
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
        "http://localhost:5000/api/appointments/availability",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.success) {
        const avail = response.data.availability || {};
        let accepting = response.data.is_accepting_appointments;
        
        console.log(`📥 Raw API response for is_accepting_appointments:`, accepting, `(type: ${typeof accepting})`);
        
        // CRITICAL: Only default to true if the value is truly missing (undefined/null)
        // If it's false, we MUST preserve false
        if (accepting === undefined || accepting === null) {
          // Value not provided by API - default to true only if truly missing
          accepting = true;
          console.log(`⚠️  is_accepting_appointments was undefined/null, defaulting to true`);
        } else {
          // Value exists - convert to boolean properly, preserving false
          if (typeof accepting === 'string') {
            accepting = accepting.toLowerCase() === 'true' || accepting === '1';
            console.log(`🔄 Converted string "${response.data.is_accepting_appointments}" to boolean: ${accepting}`);
          } else {
            // Use Boolean() conversion which preserves false correctly
            accepting = Boolean(accepting);
            console.log(`✅ Using boolean value: ${accepting} (preserving false if it was false)`);
          }
        }
        
        console.log(`📥 Loaded accepting appointments state: ${accepting} (from API: ${response.data.is_accepting_appointments})`);
        setIsAcceptingAppointments(accepting);
        
        // Handle both old format (array) and new format (object)
        if (Array.isArray(avail)) {
          // Old format - convert to new format
          setAvailability({
            time_ranges: [
              { start_time: "07:00", end_time: "17:00", interval: 30 }
            ]
          });
        } else if (avail.time_ranges && Array.isArray(avail.time_ranges)) {
          // New format with multiple ranges
          setAvailability(avail);
        } else if (avail.start_time && avail.end_time) {
          // Legacy single range format - convert to new format
          setAvailability({
            time_ranges: [
              {
                start_time: avail.start_time || "07:00",
                end_time: avail.end_time || "17:00",
                interval: avail.interval || 30
              }
            ]
          });
        } else {
          setAvailability({
            time_ranges: [
              { start_time: "07:00", end_time: "17:00", interval: 30 }
            ]
          });
        }
      } else {
        setError(response.data.error || "Failed to load availability");
      }
    } catch (err) {
      console.error("Error fetching availability:", err);
      setError("Failed to load availability. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchAvailability();
  }, [fetchAvailability]);

  const saveAvailability = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const currentUser = auth.currentUser;
      if (!currentUser) {
        navigate("/login");
        return;
      }

      const token = await currentUser.getIdToken();

      // Ensure availability structure is correct
      const availabilityData = {
        time_ranges: availability.time_ranges.map(range => ({
          start_time: range.start_time, // Should be in HH:MM format (24-hour)
          end_time: range.end_time,     // Should be in HH:MM format (24-hour)
          interval: parseInt(range.interval) || 30
        }))
      };

      console.log("Saving availability:", availabilityData);

      const response = await axios.put(
        "http://localhost:5000/api/appointments/availability",
        { 
          availability: availabilityData,
          is_accepting_appointments: isAcceptingAppointments
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data.success) {
        setSuccess("Availability updated successfully! This schedule applies to all days of the week.");
        setTimeout(() => setSuccess(null), 5000);
      } else {
        setError(response.data.error || "Failed to save availability");
        setTimeout(() => setError(null), 5000);
      }
    } catch (err) {
      console.error("Error saving availability:", err);
      const errorMessage = err.response?.data?.error || err.response?.data?.message || err.message || "Failed to save availability. Please try again.";
      console.error("Error details:", {
        status: err.response?.status,
        data: err.response?.data,
        message: errorMessage
      });
      setError(errorMessage);
      setTimeout(() => setError(null), 5000);
    } finally {
      setSaving(false);
    }
  };

  const handleToggleAcceptingAppointments = async (newValue) => {
    // Optimistically update UI first
    const previousValue = isAcceptingAppointments;
    setIsAcceptingAppointments(newValue);
    
    // Save immediately to database
    try {
      const currentUser = auth.currentUser;
      if (!currentUser) {
        setIsAcceptingAppointments(previousValue); // Revert on auth error
        navigate("/login");
        return;
      }

      const token = await currentUser.getIdToken();

      console.log(`🔄 Toggling accepting appointments to: ${newValue}`);
      const response = await axios.put(
        "http://localhost:5000/api/appointments/availability",
        { 
          availability: availability,
          is_accepting_appointments: newValue
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data.success) {
        console.log(`✅ Accepting appointments ${newValue ? 'enabled' : 'disabled'} successfully`);
        console.log(`✅ Response data:`, response.data);
        setSuccess(`Appointments ${newValue ? 'enabled' : 'disabled'} successfully`);
        setTimeout(() => setSuccess(null), 3000);
        
        // IMPORTANT: Update state from response to ensure consistency
        const savedValue = response.data.is_accepting_appointments;
        let finalValue = savedValue;
        if (savedValue === undefined || savedValue === null) {
          finalValue = newValue; // Use the value we just saved
        } else if (typeof savedValue === 'string') {
          finalValue = savedValue.toLowerCase() === 'true' || savedValue === '1';
        } else {
          finalValue = Boolean(savedValue);
        }
        
        console.log(`✅ Setting toggle state to: ${finalValue} (from response: ${savedValue})`);
        setIsAcceptingAppointments(finalValue);
        
        // Trigger storage event to refresh in other tabs/components
        window.dispatchEvent(new Event('storage'));
        localStorage.setItem('availability_updated', Date.now().toString());
        
        // Don't call fetchAvailability here - we already have the correct state from response
      } else {
        console.error("❌ Failed to update accepting appointments:", response.data.error);
        setError(response.data.error || "Failed to update status");
        setTimeout(() => setError(null), 3000);
        // Revert the toggle on error
        setIsAcceptingAppointments(previousValue);
      }
    } catch (err) {
      console.error("❌ Error updating accepting appointments:", err);
      console.error("❌ Error details:", {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
      const errorMessage = err.response?.data?.error || err.response?.data?.message || err.message || "Failed to update status";
      setError(errorMessage);
      setTimeout(() => setError(null), 3000);
      // Revert the toggle on error
      setIsAcceptingAppointments(previousValue);
    }
  };

  const handleAvailabilityChange = (index, field, value) => {
    const updatedRanges = [...availability.time_ranges];
    updatedRanges[index] = {
      ...updatedRanges[index],
      [field]: field === 'interval' ? parseInt(value) : value
    };
    setAvailability({
      ...availability,
      time_ranges: updatedRanges
    });
  };

  // Convert 24-hour format to 12-hour format with AM/PM for preview
  const formatTimeTo12Hour = (time24) => {
    if (!time24) return '';
    const [hours, minutes] = time24.split(':');
    const hour = parseInt(hours, 10);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
  };

  const addTimeRange = () => {
    setAvailability({
      ...availability,
      time_ranges: [
        ...availability.time_ranges,
        { start_time: "09:00", end_time: "17:00", interval: 30 }
      ]
    });
  };

  const removeTimeRange = (index) => {
    if (availability.time_ranges.length > 1) {
      const updatedRanges = availability.time_ranges.filter((_, i) => i !== index);
      setAvailability({
        ...availability,
        time_ranges: updatedRanges
      });
    } else {
      setError("You must have at least one time range");
      setTimeout(() => setError(null), 3000);
    }
  };

  const generateTimeSlots = () => {
    if (!availability.time_ranges || availability.time_ranges.length === 0) {
      return [];
    }

    const allSlots = [];
    
    availability.time_ranges.forEach((range) => {
      if (!range.start_time || !range.end_time || !range.interval) {
        return;
      }

      // Generate slots for this time range
      const [startHour, startMin] = range.start_time.split(':').map(Number);
      const [endHour, endMin] = range.end_time.split(':').map(Number);
      
      const startMinutes = startHour * 60 + startMin;
      const endMinutes = endHour * 60 + endMin;
      const interval = range.interval;

      for (let minutes = startMinutes; minutes < endMinutes; minutes += interval) {
        const hour = Math.floor(minutes / 60);
        const min = minutes % 60;
        const timeStr = `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;
        if (!allSlots.includes(timeStr)) {
          allSlots.push(timeStr);
        }
      }
    });

    return allSlots.sort();
  };

  const handleSave = () => {
    if (!availability.time_ranges || availability.time_ranges.length === 0) {
      setError("Please add at least one time range");
      return;
    }

    // Validate each time range
    for (let i = 0; i < availability.time_ranges.length; i++) {
      const range = availability.time_ranges[i];
      
      if (!range.start_time || !range.end_time) {
        setError(`Time range ${i + 1}: Please set both start and end times`);
        return;
      }

      const [startHour, startMin] = range.start_time.split(':').map(Number);
      const [endHour, endMin] = range.end_time.split(':').map(Number);
      
      if (endHour * 60 + endMin <= startHour * 60 + startMin) {
        setError(`Time range ${i + 1}: End time must be after start time`);
        return;
      }

      // Check for overlaps with other ranges
      for (let j = i + 1; j < availability.time_ranges.length; j++) {
        const otherRange = availability.time_ranges[j];
        const [otherStartHour, otherStartMin] = otherRange.start_time.split(':').map(Number);
        const [otherEndHour, otherEndMin] = otherRange.end_time.split(':').map(Number);
        
        const rangeStart = startHour * 60 + startMin;
        const rangeEnd = endHour * 60 + endMin;
        const otherStart = otherStartHour * 60 + otherStartMin;
        const otherEnd = otherEndHour * 60 + otherEndMin;

        // Check if ranges overlap
        if (!(rangeEnd <= otherStart || rangeStart >= otherEnd)) {
          setError(`Time ranges ${i + 1} and ${j + 1} overlap. Please adjust them.`);
          return;
        }
      }
    }

    saveAvailability();
  };

  return (
    <>
      {!embedded ? (
        <>
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
                  <h1 className="dashboard-title">MANAGE AVAILABILITY</h1>
                  <p className="dashboard-subtitle">
                    Set your available dates and times for patient appointments
                  </p>
                </div>
              </div>

              <div>
                {/* Success/Error Messages */}
                {success && (
                  <div className="alert alert-success">
                    <AlertCircle size={20} />
                    {success}
                  </div>
                )}

                {error && (
                  <div className="alert alert-error">
                    <AlertCircle size={20} />
                    {error}
                  </div>
                )}

                {/* Availability Settings Form */}
                <div className="availability-form-card">
                  <h3 className="form-card-title">
                    <Clock size={20} />
                    Set Your Weekly Availability
                  </h3>
                  <p style={{ marginBottom: '20px', color: '#666', fontSize: '0.95rem' }}>
                    This schedule will apply to all days of the week (Monday to Sunday). You can add multiple time ranges.
                  </p>
                  
                  {loading ? (
                    <div className="loading-container">
                      <div className="loading-spinner"></div>
                      <p>Loading availability...</p>
                    </div>
                  ) : (
                    <>
                      {/* Toggle Button for Accepting Appointments */}
                      <div style={{ 
                        marginBottom: '24px', 
                        padding: '16px', 
                        backgroundColor: '#f5f5f5', 
                        borderRadius: '8px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}>
                        <div>
                          <label style={{ 
                            fontSize: '1rem', 
                            fontWeight: '600', 
                            color: '#333',
                            display: 'block',
                            marginBottom: '4px'
                          }}>
                            Accepting Appointments
                          </label>
                          <span style={{ fontSize: '0.85rem', color: '#666' }}>
                            {isAcceptingAppointments 
                              ? 'Patients can book appointments with you' 
                              : 'Patients will see you as unavailable'}
                            </span>
                        </div>
                <button
                  onClick={() => handleToggleAcceptingAppointments(!isAcceptingAppointments)}
                  style={{
                    width: '56px',
                    height: '32px',
                    borderRadius: '16px',
                    border: 'none',
                    cursor: 'pointer',
                    position: 'relative',
                    backgroundColor: isAcceptingAppointments ? '#2196F3' : '#ccc',
                    transition: 'background-color 0.3s',
                    padding: '0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: isAcceptingAppointments ? 'flex-end' : 'flex-start',
                    paddingLeft: isAcceptingAppointments ? '0' : '4px',
                    paddingRight: isAcceptingAppointments ? '4px' : '0'
                  }}
                  aria-label={isAcceptingAppointments ? 'Disable appointments' : 'Enable appointments'}
                >
                          <span style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            backgroundColor: 'white',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                            transition: 'transform 0.3s'
                          }} />
                        </button>
                      </div>
                      
                      {availability.time_ranges.map((range, index) => (
                        <div key={index} className="time-range-card" style={{ 
                          marginBottom: '16px', 
                          padding: '16px', 
                          border: '2px solid #E3F2FD', 
                          borderRadius: '12px',
                          backgroundColor: 'rgba(227, 242, 253, 0.3)',
                          transition: 'all 0.3s ease'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                            <h4 style={{ margin: 0, color: '#1976D2', fontSize: '1rem', fontWeight: '600' }}>
                              Range {index + 1}
                            </h4>
                            {availability.time_ranges.length > 1 && (
                              <button
                                onClick={() => removeTimeRange(index)}
                                className="delete-range-btn"
                                style={{
                                  padding: '6px 10px',
                                  background: 'transparent',
                                  color: '#1976D2',
                                  border: '1px solid #BBDEFB',
                                  borderRadius: '6px',
                                  cursor: 'pointer',
                                  fontSize: '0.85rem',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  transition: 'all 0.2s ease'
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = '#E3F2FD';
                                  e.currentTarget.style.borderColor = '#1976D2';
                                  e.currentTarget.style.color = '#0D47A1';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = 'transparent';
                                  e.currentTarget.style.borderColor = '#BBDEFB';
                                  e.currentTarget.style.color = '#1976D2';
                                }}
                              >
                                <Trash2 size={14} />
                              </button>
                            )}
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                            <div className="form-group" style={{ marginBottom: 0 }}>
                              <label style={{ fontSize: '0.85rem', marginBottom: '4px' }}>Start</label>
                              <input
                                type="time"
                                className="form-input"
                                value={range.start_time}
                                onChange={(e) => handleAvailabilityChange(index, 'start_time', e.target.value)}
                                style={{ padding: '8px 12px', fontSize: '0.9rem' }}
                              />
                            </div>

                            <div className="form-group" style={{ marginBottom: 0 }}>
                              <label style={{ fontSize: '0.85rem', marginBottom: '4px' }}>End</label>
                              <input
                                type="time"
                                className="form-input"
                                value={range.end_time}
                                onChange={(e) => handleAvailabilityChange(index, 'end_time', e.target.value)}
                                style={{ padding: '8px 12px', fontSize: '0.9rem' }}
                              />
                            </div>

                            <div className="form-group" style={{ marginBottom: 0 }}>
                              <label style={{ fontSize: '0.85rem', marginBottom: '4px' }}>Interval</label>
                              <select
                                className="form-input"
                                value={range.interval}
                                onChange={(e) => handleAvailabilityChange(index, 'interval', parseInt(e.target.value))}
                                style={{ padding: '8px 12px', fontSize: '0.9rem' }}
                              >
                                <option value={15}>15 min</option>
                                <option value={25}>25 min</option>
                                <option value={30}>30 min</option>
                              </select>
                            </div>
                          </div>
                        </div>
                      ))}

                      <button
                        onClick={addTimeRange}
                        style={{
                          width: '100%',
                          padding: '12px',
                          background: 'linear-gradient(135deg, #2196F3, #00BCD4)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '12px',
                          cursor: 'pointer',
                          fontSize: '1rem',
                          fontWeight: '600',
                          marginBottom: '24px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px'
                        }}
                      >
                        <Plus size={20} />
                        Add Another Time Range
                      </button>

                      {/* Preview Time Slots */}
                      <div className="selected-times" style={{ marginTop: '24px' }}>
                        <label>Combined Time Slots Preview:</label>
                        <div className="time-tags">
                          {generateTimeSlots().map((time, idx) => (
                            <span key={idx} className="time-tag">
                              <Clock size={14} />
                              {formatTimeTo12Hour(time)}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Save Button */}
                      <div className="save-section" style={{ marginTop: '24px' }}>
                        <button
                          className="save-button"
                          onClick={handleSave}
                          disabled={saving}
                        >
                          <Save size={20} />
                          {saving ? "Saving..." : "Save Availability"}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </main>
          </div>
        </>
      ) : (
        <div className="embedded-availability-content">
          {/* Success/Error Messages */}
          {success && (
            <div className="alert alert-success">
              <AlertCircle size={20} />
              {success}
            </div>
          )}

          {error && (
            <div className="alert alert-error">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {/* Availability Settings Form */}
          {loading || isAcceptingAppointments === null ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading availability...</p>
            </div>
          ) : (
            <>
              {/* Toggle Button for Accepting Appointments */}
              <div style={{ 
                marginBottom: '16px', 
                padding: '12px', 
                backgroundColor: '#f5f5f5', 
                borderRadius: '8px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <label style={{ 
                    fontSize: '0.95rem', 
                    fontWeight: '600', 
                    color: '#333',
                    display: 'block',
                    marginBottom: '2px'
                  }}>
                    Accepting Appointments
                  </label>
                  <span style={{ fontSize: '0.8rem', color: '#666' }}>
                    {isAcceptingAppointments 
                      ? 'Available for booking' 
                      : 'Not available'}
                    </span>
                </div>
                <button
                  onClick={() => handleToggleAcceptingAppointments(!isAcceptingAppointments)}
                  style={{
                    width: '48px',
                    height: '28px',
                    borderRadius: '14px',
                    border: 'none',
                    cursor: 'pointer',
                    position: 'relative',
                    backgroundColor: isAcceptingAppointments ? '#2196F3' : '#ccc',
                    transition: 'background-color 0.3s',
                    padding: '0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: isAcceptingAppointments ? 'flex-end' : 'flex-start',
                    paddingLeft: isAcceptingAppointments ? '0' : '3px',
                    paddingRight: isAcceptingAppointments ? '3px' : '0'
                  }}
                  aria-label={isAcceptingAppointments ? 'Disable appointments' : 'Enable appointments'}
                >
                  <span style={{
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    backgroundColor: 'white',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    transition: 'transform 0.3s'
                  }} />
                </button>
              </div>
              
              {availability.time_ranges.map((range, index) => (
                <div key={index} style={{ 
                  marginBottom: '12px', 
                  padding: '14px', 
                  border: '2px solid #E3F2FD', 
                  borderRadius: '10px',
                  backgroundColor: 'rgba(227, 242, 253, 0.3)',
                  transition: 'all 0.3s ease'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <span style={{ fontWeight: '600', color: '#1976D2', fontSize: '0.9rem' }}>
                      Range {index + 1}
                    </span>
                    {availability.time_ranges.length > 1 && (
                      <button
                        onClick={() => removeTimeRange(index)}
                        style={{
                          padding: '5px 8px',
                          background: 'transparent',
                          color: '#1976D2',
                          border: '1px solid #BBDEFB',
                          borderRadius: '5px',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          display: 'flex',
                          alignItems: 'center',
                          transition: 'all 0.2s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = '#FFEBEE';
                          e.currentTarget.style.borderColor = '#EF5350';
                          e.currentTarget.style.color = '#C62828';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'transparent';
                          e.currentTarget.style.borderColor = '#BBDEFB';
                          e.currentTarget.style.color = '#1976D2';
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>Start</label>
                      <input
                        type="time"
                        className="form-input"
                        value={range.start_time}
                        onChange={(e) => handleAvailabilityChange(index, 'start_time', e.target.value)}
                        style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                      />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>End</label>
                      <input
                        type="time"
                        className="form-input"
                        value={range.end_time}
                        onChange={(e) => handleAvailabilityChange(index, 'end_time', e.target.value)}
                        style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                      />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>Interval</label>
                      <select
                        className="form-input"
                        value={range.interval}
                        onChange={(e) => handleAvailabilityChange(index, 'interval', parseInt(e.target.value))}
                        style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                      >
                        <option value={15}>15 min</option>
                        <option value={25}>25 min</option>
                        <option value={30}>30 min</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))}

              <button
                onClick={addTimeRange}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: 'linear-gradient(135deg, #2196F3, #00BCD4)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '600',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}
              >
                <Plus size={16} />
                Add Range
              </button>

              {/* Preview Time Slots */}
              <div className="selected-times" style={{ marginTop: '12px' }}>
                <label>Preview:</label>
                <div className="time-tags">
                  {generateTimeSlots().slice(0, 10).map((time, idx) => (
                    <span key={idx} className="time-tag">
                      <Clock size={14} />
                      {formatTimeTo12Hour(time)}
                    </span>
                  ))}
                  {generateTimeSlots().length > 10 && (
                    <span className="time-tag" style={{ opacity: 0.7 }}>
                      +{generateTimeSlots().length - 10} more
                    </span>
                  )}
                </div>
              </div>

              {/* Save Button */}
              <div className="save-section" style={{ marginTop: '16px' }}>
                <button
                  className="save-button"
                  onClick={handleSave}
                  disabled={saving}
                  style={{ width: '100%', padding: '12px' }}
                >
                  <Save size={18} />
                  {saving ? "Saving..." : "Save Schedule"}
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default DoctorAvailability;

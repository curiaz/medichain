import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "./Header";
import { Calendar, Clock, Plus, Trash2, Save, AlertCircle } from "lucide-react";
import axios from "axios";
import { auth } from "../config/firebase";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/DoctorAvailability.css";

const DoctorAvailability = () => {
  const navigate = useNavigate();
  const [availability, setAvailability] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [newSlot, setNewSlot] = useState({
    date: "",
    time_slots: []
  });
  const [newTime, setNewTime] = useState("");

  useEffect(() => {
    fetchAvailability();
  }, []);

  const fetchAvailability = async () => {
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
        setAvailability(response.data.availability || []);
      } else {
        setError(response.data.error || "Failed to load availability");
      }
    } catch (err) {
      console.error("Error fetching availability:", err);
      setError("Failed to load availability. Please try again.");
    } finally {
      setLoading(false);
    }
  };

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

      const response = await axios.put(
        "http://localhost:5000/api/appointments/availability",
        { availability },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.data.success) {
        setSuccess("Availability updated successfully!");
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.data.error || "Failed to save availability");
      }
    } catch (err) {
      console.error("Error saving availability:", err);
      setError("Failed to save availability. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const addTimeSlot = () => {
    if (!newTime) {
      setError("Please select a time");
      return;
    }

    if (!newSlot.time_slots.includes(newTime)) {
      setNewSlot({
        ...newSlot,
        time_slots: [...newSlot.time_slots, newTime].sort()
      });
      setNewTime("");
    }
  };

  const removeTimeFromNew = (time) => {
    setNewSlot({
      ...newSlot,
      time_slots: newSlot.time_slots.filter(t => t !== time)
    });
  };

  const addDateSlot = () => {
    if (!newSlot.date) {
      setError("Please select a date");
      return;
    }

    if (newSlot.time_slots.length === 0) {
      setError("Please add at least one time slot");
      return;
    }

    // Check if date already exists
    const existingIndex = availability.findIndex(slot => slot.date === newSlot.date);
    
    if (existingIndex >= 0) {
      // Merge time slots
      const updated = [...availability];
      updated[existingIndex].time_slots = [
        ...new Set([...updated[existingIndex].time_slots, ...newSlot.time_slots])
      ].sort();
      setAvailability(updated);
    } else {
      // Add new date
      setAvailability([...availability, newSlot].sort((a, b) => 
        new Date(a.date) - new Date(b.date)
      ));
    }

    // Reset form
    setNewSlot({ date: "", time_slots: [] });
    setError(null);
  };

  const removeDateSlot = (date) => {
    setAvailability(availability.filter(slot => slot.date !== date));
  };

  const removeTimeSlot = (date, time) => {
    setAvailability(availability.map(slot => {
      if (slot.date === date) {
        const updatedTimeSlots = slot.time_slots.filter(t => t !== time);
        return updatedTimeSlots.length > 0 
          ? { ...slot, time_slots: updatedTimeSlots }
          : null;
      }
      return slot;
    }).filter(slot => slot !== null));
  };

  // Generate time options (9 AM to 5 PM, 1-hour intervals)
  const timeOptions = [];
  for (let hour = 9; hour <= 17; hour++) {
    timeOptions.push(`${hour.toString().padStart(2, '0')}:00`);
    if (hour < 17) {
      timeOptions.push(`${hour.toString().padStart(2, '0')}:30`);
    }
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
            <h1 className="dashboard-title">MANAGE AVAILABILITY</h1>
            <p className="dashboard-subtitle">
              Set your available dates and times for patient appointments
            </p>
          </div>

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

          {/* Add New Availability Slot */}
          <div className="availability-form-card">
            <h3 className="form-card-title">
              <Plus size={20} />
              Add New Availability
            </h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Date</label>
                <input
                  type="date"
                  className="form-input"
                  value={newSlot.date}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setNewSlot({ ...newSlot, date: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Time Slot</label>
                <div className="time-input-group">
                  <select
                    className="form-input"
                    value={newTime}
                    onChange={(e) => setNewTime(e.target.value)}
                  >
                    <option value="">Select time</option>
                    {timeOptions.map(time => (
                      <option key={time} value={time}>{time}</option>
                    ))}
                  </select>
                  <button 
                    className="add-time-button"
                    onClick={addTimeSlot}
                    type="button"
                  >
                    <Plus size={18} />
                    Add
                  </button>
                </div>
              </div>
            </div>

            {/* Preview Selected Times */}
            {newSlot.time_slots.length > 0 && (
              <div className="selected-times">
                <label>Selected Times for {newSlot.date}:</label>
                <div className="time-tags">
                  {newSlot.time_slots.map(time => (
                    <span key={time} className="time-tag">
                      <Clock size={14} />
                      {time}
                      <button onClick={() => removeTimeFromNew(time)}>×</button>
                    </span>
                  ))}
                </div>
              </div>
            )}

            <button 
              className="add-slot-button"
              onClick={addDateSlot}
              disabled={!newSlot.date || newSlot.time_slots.length === 0}
            >
              <Calendar size={18} />
              Add to Schedule
            </button>
          </div>

          {/* Current Availability */}
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading availability...</p>
            </div>
          ) : (
            <div className="current-availability">
              <h3 className="section-title">Current Availability</h3>
              
              {availability.length === 0 ? (
                <div className="no-availability">
                  <Calendar size={48} />
                  <p>No availability set yet</p>
                  <span>Add dates and times above to get started</span>
                </div>
              ) : (
                <div className="availability-grid">
                  {availability.map((slot) => (
                    <div key={slot.date} className="availability-card">
                      <div className="card-header">
                        <div className="date-info">
                          <Calendar size={20} />
                          <span className="date-text">
                            {new Date(slot.date + 'T00:00:00').toLocaleDateString('en-US', {
                              weekday: 'long',
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })}
                          </span>
                        </div>
                        <button
                          className="delete-button"
                          onClick={() => removeDateSlot(slot.date)}
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                      
                      <div className="time-slots">
                        {slot.time_slots.map((time) => (
                          <div key={time} className="time-slot">
                            <Clock size={16} />
                            <span>{time}</span>
                            <button
                              className="remove-time"
                              onClick={() => removeTimeSlot(slot.date, time)}
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Save Button */}
          {availability.length > 0 && (
            <div className="save-section">
              <button
                className="save-button"
                onClick={saveAvailability}
                disabled={saving}
              >
                <Save size={20} />
                {saving ? "Saving..." : "Save Availability"}
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DoctorAvailability;

import React, { useEffect, useState, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import { Search, Stethoscope, Mail, ArrowLeft } from "lucide-react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/SelectGP.css";

const SelectGP = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, getFirebaseToken } = useAuth();
  const [doctors, setDoctors] = useState([]);
  const [filteredDoctors, setFilteredDoctors] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchApprovedDoctors = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // DEBUG: Log component mount
      console.log("🔍 SelectGP: fetchApprovedDoctors called");
      console.log("🔍 SelectGP: location.state =", location.state);
      console.log("🔍 SelectGP: isAuthenticated =", isAuthenticated);
      console.log("🔍 SelectGP: user =", user);

      // Check if user is authenticated via AuthContext
      // Note: ProtectedRoute already handles authentication, but we check here for extra safety
      if (!isAuthenticated || !user) {
        console.log("⚠️ SelectGP: AuthContext says not authenticated, but ProtectedRoute should handle this");
        console.log("⚠️ SelectGP: Waiting for ProtectedRoute to redirect...");
        // Don't redirect here - let ProtectedRoute handle it
        setLoading(false);
        return;
      }
      
      console.log("✅ SelectGP: User authenticated, fetching token...");

      // Try multiple token sources with fallback
      let token = null;
      
      // First, try to get Firebase token from AuthContext
      try {
        if (getFirebaseToken) {
          console.log("🔍 SelectGP: Attempting to get Firebase token via getFirebaseToken...");
          token = await getFirebaseToken();
          console.log("✅ SelectGP: Got Firebase token via getFirebaseToken");
        }
      } catch (firebaseError) {
        console.warn("⚠️ SelectGP: Failed to get Firebase token via getFirebaseToken:", firebaseError);
      }
      
      // Fallback to localStorage token
      if (!token) {
        console.log("🔍 SelectGP: Trying localStorage token...");
        token = localStorage.getItem('medichain_token');
        if (token) {
          console.log("✅ SelectGP: Got token from localStorage");
        }
      }
      
      // Final fallback: try sessionStorage
      if (!token) {
        console.log("🔍 SelectGP: Trying sessionStorage token...");
        token = sessionStorage.getItem('medichain_token');
        if (token) {
          console.log("✅ SelectGP: Got token from sessionStorage");
        }
      }
      
      if (!token) {
        console.log("❌ SelectGP: No token found in any source");
        setError("Session expired. Please log in again.");
        setLoading(false);
        // Don't redirect - let ProtectedRoute handle it
        return;
      }
      
      console.log("✅ SelectGP: Token found, making API call...");
      console.log("🔍 SelectGP: API URL:", "https://medichainn.onrender.com/api/appointments/doctors/approved");

      const response = await axios.get(
        "https://medichainn.onrender.com/api/appointments/doctors/approved",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log("✅ SelectGP: API Response received:", response.data);
      console.log("🔍 SelectGP: Response success:", response.data?.success);
      console.log("🔍 SelectGP: Doctors count:", response.data?.doctors?.length || 0);

      if (response.data.success) {
        const doctorsList = response.data.doctors || [];
        console.log("✅ SelectGP: Setting doctors:", doctorsList.length);
        setDoctors(doctorsList);
        setFilteredDoctors(doctorsList);
        
        if (doctorsList.length === 0) {
          console.warn("⚠️ SelectGP: No doctors returned from API");
          setError("No approved doctors available at this time. Please check back later.");
        }
      } else {
        console.error("❌ SelectGP: API returned error:", response.data.message || response.data.error);
        setError(response.data.message || response.data.error || "Failed to load doctors");
      }
    } catch (err) {
      console.error("❌ SelectGP: Error fetching doctors:", err);
      console.error("❌ SelectGP: Error details:", {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText
      });
      
      if (err.response?.status === 401) {
        console.error("❌ SelectGP: Authentication failed (401)");
        setError("Session expired. Please log in again.");
        navigate("/login");
      } else if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
        console.error("❌ SelectGP: Network error - backend may not be running");
        setError("Cannot connect to server. Please ensure the backend is running on port 5000.");
      } else {
        console.error("❌ SelectGP: Other error:", err);
        setError(err.response?.data?.error || err.response?.data?.message || "Failed to load doctors. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user, navigate, location.state]);

  useEffect(() => {
    fetchApprovedDoctors();
  }, [fetchApprovedDoctors]);

  useEffect(() => {
    // Filter doctors based on search query
    if (searchQuery.trim() === "") {
      setFilteredDoctors(doctors);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = doctors.filter((doctor) => {
        const name = `${doctor.first_name} ${doctor.last_name}`.toLowerCase();
        const specialization = doctor.specialization?.toLowerCase() || "";
        return name.includes(query) || specialization.includes(query);
      });
      setFilteredDoctors(filtered);
    }
  }, [searchQuery, doctors]);

  const handleSelectDoctor = (doctor) => {
    console.log("🔍 SelectGP: handleSelectDoctor called for", doctor.email);
    console.log("🔍 SelectGP: doctor.has_availability =", doctor.has_availability);
    console.log("🔍 SelectGP: Full doctor object:", JSON.stringify(doctor, null, 2));
    
    if (!doctor.has_availability) {
      console.log("❌ SelectGP: Doctor has no availability, not navigating");
      return;
    }
    
    // Store doctor in sessionStorage as backup
    try {
      sessionStorage.setItem('selectedDoctor', JSON.stringify(doctor));
      sessionStorage.setItem('appointmentType', location.state?.appointmentType || "general-practitioner");
      console.log("✅ SelectGP: Doctor stored in sessionStorage");
    } catch (e) {
      console.warn("⚠️ SelectGP: Could not store doctor in sessionStorage:", e);
    }
    
    // Navigate to symptoms selection page (new flow)
    console.log("✅ SelectGP: Navigating to /symptoms-selection");
    console.log("✅ SelectGP: Navigation state:", {
      doctor: doctor,
      appointmentType: location.state?.appointmentType || "general-practitioner",
    });
    
    navigate("/symptoms-selection", {
      state: {
        doctor: doctor,
        appointmentType: location.state?.appointmentType || "general-practitioner",
      },
      replace: false, // Don't replace history
    });
  };

  // Debug: Log render state
  console.log("🎨 SelectGP: Rendering component");
  console.log("🎨 SelectGP: loading =", loading);
  console.log("🎨 SelectGP: error =", error);
  console.log("🎨 SelectGP: doctors count =", doctors.length);
  console.log("🎨 SelectGP: filteredDoctors count =", filteredDoctors.length);

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

      {/* Back Button in Header Area */}
      <button
        className="back-button-header"
        onClick={() => navigate("/book-appointment")}
        aria-label="Go back"
      >
        <ArrowLeft size={24} />
      </button>

      <main className="dashboard-main-content">
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">SELECT GP</h1>
            <p className="dashboard-subtitle">
              Choose a General Practitioner for your consultation
            </p>
          </div>

          {/* Search Bar inside header */}
          <div className="search-container">
            <div className="search-input-wrapper">
              <Search size={20} className="search-icon" />
              <input
                type="text"
                className="search-input"
                placeholder="Search by doctor name or specialization..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading available doctors...</p>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="error-container">
              <p className="error-message">{error}</p>
              <button className="retry-button" onClick={fetchApprovedDoctors}>
                Retry
              </button>
            </div>
          )}

          {/* Doctors List inside header */}
          {!loading && !error && (
            <>
              {filteredDoctors.length === 0 && doctors.length === 0 ? (
                <div className="no-results-container">
                  <Stethoscope size={48} />
                  <p>No approved doctors available at this time</p>
                  <p style={{ fontSize: '0.9rem', color: '#999', marginTop: '8px' }}>
                    Please check back later or contact support if you need assistance.
                  </p>
                  <button className="retry-button" onClick={fetchApprovedDoctors} style={{ marginTop: '16px' }}>
                    Refresh
                  </button>
                </div>
              ) : filteredDoctors.length === 0 && doctors.length > 0 ? (
                <div className="no-results-container">
                  <Stethoscope size={48} />
                  <p>No doctors found matching your search</p>
                  {searchQuery && (
                    <button
                      className="clear-search-button"
                      onClick={() => setSearchQuery("")}
                    >
                      Clear Search
                    </button>
                  )}
                </div>
              ) : (
                <div className="doctors-grid">
                  {filteredDoctors.map((doctor) => (
                    <div
                      key={doctor.firebase_uid}
                      className={`doctor-card ${!doctor.has_availability ? 'unavailable' : ''}`}
                      onClick={(e) => {
                        // Only handle card click if button wasn't clicked
                        if (e.target.closest('.select-doctor-button')) {
                          return; // Button click will handle it
                        }
                        if (doctor.has_availability) {
                          console.log("🖱️ SelectGP: Card clicked for doctor:", doctor.email);
                          handleSelectDoctor(doctor);
                        }
                      }}
                      style={{ cursor: doctor.has_availability ? 'pointer' : 'not-allowed' }}
                    >
                      <div className="doctor-header">
                        <div className="doctor-avatar">
                          <Stethoscope size={32} />
                        </div>
                        <div className="doctor-info">
                          <h3 className="doctor-name">
                            Dr. {doctor.first_name} {doctor.last_name}
                          </h3>
                          <p className="doctor-specialization">
                            <Stethoscope size={16} />
                            {doctor.specialization}
                          </p>
                        </div>
                      </div>
                      <div className="doctor-details">
                        <div className="doctor-detail-item">
                          <Mail size={16} />
                          <span>{doctor.email}</span>
                        </div>
                        <div className="doctor-status">
                          <span className="status-badge verified">
                            ✓ Verified
                          </span>
                          {!doctor.has_availability && (
                            <span className="status-badge not-available">
                              Not Available
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="doctor-actions">
                        <button 
                          className="select-doctor-button"
                          disabled={!doctor.has_availability}
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation(); // Prevent card click
                            console.log("🖱️ SelectGP: Button clicked for doctor:", doctor.email);
                            console.log("🖱️ SelectGP: doctor.has_availability =", doctor.has_availability);
                            if (doctor.has_availability) {
                              console.log("🖱️ SelectGP: Calling handleSelectDoctor");
                              handleSelectDoctor(doctor);
                            } else {
                              console.log("❌ SelectGP: Doctor has no availability, button disabled");
                            }
                          }}
                          style={{
                            opacity: doctor.has_availability ? 1 : 0.5,
                            cursor: doctor.has_availability ? 'pointer' : 'not-allowed'
                          }}
                        >
                          {doctor.has_availability ? 'Select' : 'No Slots Available'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Results Count */}
              {filteredDoctors.length > 0 && (
                <div className="results-count">
                  Showing {filteredDoctors.length} of {doctors.length} available
                  doctors
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default SelectGP;

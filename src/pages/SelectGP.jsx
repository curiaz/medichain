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
  const { user, isAuthenticated } = useAuth();
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
      if (!isAuthenticated || !user) {
        console.log("❌ SelectGP: Not authenticated, redirecting to /login");
        setError("Please log in to view doctors");
        setLoading(false);
        navigate("/login");
        return;
      }
      
      console.log("✅ SelectGP: User authenticated, fetching token...");

      // Get token from localStorage (works for both Firebase and Supabase auth)
      const token = localStorage.getItem('medichain_token');
      
      if (!token) {
        console.log("❌ SelectGP: No token found, redirecting to /login");
        setError("Session expired. Please log in again.");
        setLoading(false);
        navigate("/login");
        return;
      }
      
      console.log("✅ SelectGP: Token found, making API call...");

      const response = await axios.get(
        "http://localhost:5000/api/appointments/doctors/approved",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.success) {
        setDoctors(response.data.doctors);
        setFilteredDoctors(response.data.doctors);
      } else {
        setError(response.data.message || "Failed to load doctors");
      }
    } catch (err) {
      console.error("Error fetching doctors:", err);
      if (err.response?.status === 401) {
        setError("Session expired. Please log in again.");
        navigate("/login");
      } else {
        setError("Failed to load doctors. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
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
    // Navigate to appointment booking form with doctor details
    navigate("/book-appointment-form", {
      state: {
        doctor: doctor,
        appointmentType: location.state?.appointmentType || "general-practitioner",
      },
    });
  };

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
              {filteredDoctors.length === 0 ? (
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
                      onClick={() => doctor.has_availability && handleSelectDoctor(doctor)}
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

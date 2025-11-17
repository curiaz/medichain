import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "./Header";
import { Search, X, Check, ArrowLeft, ArrowRight, Loader2 } from "lucide-react";
import axios from "axios";
import { API_CONFIG } from "../config/api";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/SymptomsSelection.css";

const SymptomsSelection = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const doctor = location.state?.doctor;
  
  const [symptoms, setSymptoms] = useState([]); // Full symptom objects with key and display
  const [selectedSymptoms, setSelectedSymptoms] = useState([]); // Selected symptom keys
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredSymptoms, setFilteredSymptoms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Restore selected symptoms from navigation state (when coming back from document upload)
  useEffect(() => {
    if (location.state?.symptomKeys && location.state.symptomKeys.length > 0) {
      setSelectedSymptoms(location.state.symptomKeys);
      console.log('✅ Restored selected symptoms:', location.state.symptomKeys);
    }
  }, [location.state]);

  // Fetch symptoms from backend
  useEffect(() => {
    const fetchSymptoms = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.get(`${API_CONFIG.API_URL}/symptoms`);
        
        if (response.data.success) {
          setSymptoms(response.data.symptoms);
          setFilteredSymptoms(response.data.symptoms);
          console.log(`✅ Loaded ${response.data.symptoms.length} symptoms from Supabase`);
        } else {
          setError(response.data.message || "Failed to load symptoms");
        }
      } catch (err) {
        console.error("Error fetching symptoms:", err);
        setError("Failed to load symptoms. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchSymptoms();
  }, []);

  useEffect(() => {
    if (!doctor) {
      navigate("/select-gp");
    }
  }, [doctor, navigate]);

  useEffect(() => {
    if (searchQuery.trim() === "") {
      setFilteredSymptoms(symptoms);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = symptoms.filter(symptom =>
        symptom.display.toLowerCase().includes(query) ||
        symptom.key.toLowerCase().includes(query)
      );
      setFilteredSymptoms(filtered);
    }
  }, [searchQuery, symptoms]);

  const toggleSymptom = (symptomKey) => {
    if (selectedSymptoms.includes(symptomKey)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptomKey));
    } else {
      setSelectedSymptoms([...selectedSymptoms, symptomKey]);
    }
  };

  const removeSymptom = (symptomKey) => {
    setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptomKey));
  };

  const getSymptomDisplay = (symptomKey) => {
    const symptom = symptoms.find(s => s.key === symptomKey);
    return symptom ? symptom.display : symptomKey;
  };

  const handleNext = () => {
    if (selectedSymptoms.length === 0) {
      alert("Please select at least one symptom");
      return;
    }
    
    // Convert symptom keys to display names for user-friendly display
    const symptomDisplayNames = selectedSymptoms.map(key => getSymptomDisplay(key));
    
    // Store symptoms and navigate to document upload
    navigate("/document-upload", {
      state: {
        doctor: doctor,
        symptoms: symptomDisplayNames, // Display names for UI
        symptomKeys: selectedSymptoms, // Original keys for backend processing
        appointmentType: location.state?.appointmentType || "general-practitioner"
      }
    });
  };

  if (!doctor) {
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

      <main className="dashboard-main-content">
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <button
              className="back-button-header"
              onClick={() => navigate("/select-gp")}
              aria-label="Go back"
            >
              <ArrowLeft size={24} />
            </button>
            <h1 className="dashboard-title">SELECT SYMPTOMS</h1>
            <p className="dashboard-subtitle">
              Choose the symptoms you're experiencing for Dr. {doctor.first_name} {doctor.last_name}
            </p>
          </div>

          {/* Desktop Two-Column Layout */}
          <div className="symptoms-page-wrapper">
            {/* Main Content - Symptoms List */}
            <div className="symptoms-main-content">
              {/* Search Bar */}
              <div className="symptoms-search-container">
                <div className="symptoms-search-wrapper">
                  <Search size={20} className="symptoms-search-icon" />
                  <input
                    type="text"
                    className="symptoms-search-input"
                    placeholder="Search symptoms..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  {searchQuery && (
                    <button
                      className="clear-search-btn"
                      onClick={() => setSearchQuery("")}
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              </div>

              {/* Loading State */}
              {loading && (
                <div className="symptoms-loading">
                  <Loader2 size={32} className="spinning" />
                  <p>Loading symptoms from database...</p>
                </div>
              )}

              {/* Error State */}
              {error && !loading && (
                <div className="symptoms-error">
                  <p>{error}</p>
                  <button onClick={() => window.location.reload()}>Retry</button>
                </div>
              )}

              {/* Selected Symptoms - Mobile Only */}
              {!loading && !error && selectedSymptoms.length > 0 && (
                <div className="selected-symptoms-container">
                  <h3 className="selected-symptoms-title">Selected Symptoms ({selectedSymptoms.length})</h3>
                  <div className="selected-symptoms-bubbles">
                    {selectedSymptoms.map((symptomKey) => (
                      <div key={symptomKey} className="selected-symptom-bubble">
                        <span>{getSymptomDisplay(symptomKey)}</span>
                        <button
                          className="remove-symptom-btn"
                          onClick={() => removeSymptom(symptomKey)}
                          aria-label={`Remove ${getSymptomDisplay(symptomKey)}`}
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Symptoms Grid */}
              {!loading && !error && (
                <div className="symptoms-grid-container">
                  <h3 className="symptoms-grid-title">
                    {searchQuery ? `Search Results (${filteredSymptoms.length})` : `Available Symptoms (${symptoms.length})`}
                  </h3>
                  {filteredSymptoms.length === 0 ? (
                    <div className="no-symptoms-found">
                      <p>No symptoms found matching "{searchQuery}"</p>
                      <button
                        className="clear-search-button"
                        onClick={() => setSearchQuery("")}
                      >
                        Clear Search
                      </button>
                    </div>
                  ) : (
                    <div className="symptoms-grid">
                      {filteredSymptoms.map((symptom) => {
                        const isSelected = selectedSymptoms.includes(symptom.key);
                        return (
                          <button
                            key={symptom.key}
                            className={`symptom-bubble ${isSelected ? "selected" : ""}`}
                            onClick={() => toggleSymptom(symptom.key)}
                          >
                            {isSelected && <Check size={16} className="check-icon" />}
                            <span>{symptom.display}</span>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* Navigation Buttons - Mobile Only */}
              <div className="symptoms-navigation">
                <button
                  className="back-button-symptoms"
                  onClick={() => navigate("/select-gp")}
                >
                  <ArrowLeft size={18} />
                  Back
                </button>
                <button
                  className="next-button-symptoms"
                  onClick={handleNext}
                  disabled={selectedSymptoms.length === 0 || loading}
                >
                  Next
                  <ArrowRight size={18} />
                </button>
              </div>
            </div>

            {/* Sidebar - Desktop Only */}
            <div className="symptoms-sidebar">
              <div className="symptoms-sidebar-card">
                <h3>Selected Symptoms</h3>
                
                {/* Stats */}
                <div className="symptoms-sidebar-stats">
                  <span className="count">{selectedSymptoms.length}</span>
                  <span className="label">
                    {selectedSymptoms.length === 1 ? 'Symptom Selected' : 'Symptoms Selected'}
                  </span>
                </div>

                {/* Selected Symptoms List */}
                {selectedSymptoms.length > 0 ? (
                  <div className="selected-symptoms-sidebar">
                    <div className="selected-symptoms-bubbles">
                      {selectedSymptoms.map((symptomKey) => (
                        <div key={symptomKey} className="selected-symptom-bubble">
                          <span>{getSymptomDisplay(symptomKey)}</span>
                          <button
                            className="remove-symptom-btn"
                            onClick={() => removeSymptom(symptomKey)}
                            aria-label={`Remove ${getSymptomDisplay(symptomKey)}`}
                          >
                            <X size={14} />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '32px 16px', 
                    color: '#999',
                    fontSize: '14px'
                  }}>
                    No symptoms selected yet. Click on symptoms to select them.
                  </div>
                )}

                {/* Navigation Buttons - Desktop */}
                <div className="symptoms-navigation-desktop">
                  <button
                    className="next-button-symptoms-desktop"
                    onClick={handleNext}
                    disabled={selectedSymptoms.length === 0 || loading}
                  >
                    Next
                    <ArrowRight size={18} />
                  </button>
                  <button
                    className="back-button-symptoms-desktop"
                    onClick={() => navigate("/select-gp")}
                  >
                    <ArrowLeft size={18} />
                    Back
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SymptomsSelection;


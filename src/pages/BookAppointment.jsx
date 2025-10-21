import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "./Header";
import { Calendar, Stethoscope, Users, Heart } from "lucide-react";
import "../assets/styles/ModernDashboard.css";
import "../assets/styles/BookAppointment.css";

const BookAppointment = () => {
  const navigate = useNavigate();

  const appointmentTypes = [
    {
      id: "general-practitioner",
      title: "General Practitioner",
      subtitle: "Consultation",
      description: "Book a consultation with a General Practitioner for routine checkups and general health concerns",
      icon: <Stethoscope size={48} />,
      available: true,
      route: "/select-gp"
    },
    {
      id: "specialist",
      title: "Specialist",
      subtitle: "Expert Consultation",
      description: "Schedule an appointment with a medical specialist for specific health conditions",
      icon: <Users size={48} />,
      available: false,
      route: "/select-specialist"
    },
    {
      id: "emergency",
      title: "Emergency",
      subtitle: "Urgent Care",
      description: "For urgent medical attention and emergency healthcare services",
      icon: <Heart size={48} />,
      available: false,
      route: "/emergency"
    }
  ];

  const handleSelectType = (type) => {
    if (type.available) {
      navigate(type.route, { state: { appointmentType: type.id } });
    } else {
      alert("This service is coming soon!");
    }
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

      <main className="dashboard-main-content">
        <div className="dashboard-header-section">
          <div className="dashboard-title-section">
            <h1 className="dashboard-title">
              <Calendar size={32} style={{ marginRight: "12px" }} />
              BOOK AN APPOINTMENT
            </h1>
            <p className="dashboard-subtitle">Choose the type of appointment you need</p>
          </div>
        </div>

        <div className="appointment-types-container">
          {appointmentTypes.map((type) => (
            <div
              key={type.id}
              className={`appointment-type-card ${!type.available ? 'unavailable' : ''}`}
              onClick={() => handleSelectType(type)}
            >
              <div className="appointment-icon">
                {type.icon}
              </div>
              <div className="appointment-content">
                <h3>{type.title}</h3>
                <p className="appointment-subtitle">{type.subtitle}</p>
                <p className="appointment-description">{type.description}</p>
                {type.available ? (
                  <span className="appointment-status available">Available Now</span>
                ) : (
                  <span className="appointment-status coming-soon">Coming Soon</span>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="back-button-container">
          <button className="back-button" onClick={() => navigate('/dashboard')}>
            ← Back to Dashboard
          </button>
        </div>
      </main>
    </div>
  );
};

export default BookAppointment;

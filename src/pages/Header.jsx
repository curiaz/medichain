import React from "react"
import { NavLink, useNavigate } from "react-router-dom"
import { Settings, User, LogOut } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import "../assets/styles/Header.css"

const Header = () => {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header className="dashboard-header">
      <div className="header-left">
        {/* Text-based Logo */}
        <div className="logo-container">
          <div>
            MEDICHAIN
          </div>
        </div>

        <nav className="nav-links">
          <NavLink 
            to="/dashboard" 
            className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
          >
            DASHBOARD
          </NavLink>

          <NavLink 
            to="/patients" 
            className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
          >
            PATIENTS
          </NavLink>

          <NavLink 
            to="/prescriptions" 
            className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
          >
            PRESCRIPTIONS
          </NavLink>
        </nav>
      </div>

      <div className="header-right">
        <button className="icon-button" title="Settings">
          <Settings size={20} />
        </button>
        <button className="icon-button" title="Profile">
          <User size={20} />
        </button>
        <button className="icon-button" onClick={handleLogout} title="Logout">
          <LogOut size={20} />
        </button>
      </div>
    </header>
  )
}

export default Header

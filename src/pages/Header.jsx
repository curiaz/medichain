import React, { useState } from "react"
import { NavLink, useNavigate } from "react-router-dom"
import { Menu, X, User, LogOut } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import MedichainLogo from "../components/MedichainLogo"
import "../assets/styles/Header.css"

const Header = () => {
  const { logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleProfileClick = () => {
    console.log('Profile icon clicked in Header!')
    navigate('/profile')
  }

  return (
    <header className="dashboard-header">
      <div className="dashboard-header-container">
        {/* Left: Logo */}
        <div className="header-left">
          <div className="logo-container" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <MedichainLogo size={40} usePng={true} />
            <div>
              MEDICHAIN
            </div>
          </div>
        </div>

        {/* Center: Navigation */}
        <div className="header-center">
          <nav className="nav-links">
            <NavLink 
              to="/dashboard" 
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              DASHBOARD
            </NavLink>

            <NavLink 
              to="/notifications" 
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              NOTIFICATIONS
            </NavLink>
          </nav>
        </div>

        {/* Right: Action Buttons */}
        <div className="header-right">
          {/* Desktop: Profile and Logout buttons */}
          <button className="icon-button desktop-only" title="Profile" onClick={handleProfileClick}>
            <User size={20} />
          </button>
          <button className="icon-button desktop-only" onClick={handleLogout} title="Logout">
            <LogOut size={20} />
          </button>
          
          {/* Mobile: Burger menu only */}
          <button className="icon-button mobile-only burger-menu-button" title="Menu" aria-expanded={mobileOpen} onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
      {mobileOpen && (
        <div className="mobile-dashboard-nav" role="navigation">
          <NavLink to="/dashboard" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")} onClick={() => setMobileOpen(false)}>DASHBOARD</NavLink>
          <NavLink to="/notifications" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")} onClick={() => setMobileOpen(false)}>NOTIFICATIONS</NavLink>
          <button className="nav-link" onClick={() => { setMobileOpen(false); handleProfileClick(); }}>PROFILE</button>
          <button className="nav-link" onClick={handleLogout}>LOG OUT</button>
        </div>
      )}
    </header>
  )
}

export default Header

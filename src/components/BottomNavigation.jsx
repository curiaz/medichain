import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import { Home, Bell, User, Calendar, FileText } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import "../assets/styles/BottomNavigation.css";

const BottomNavigation = () => {
  const location = useLocation();
  const { user } = useAuth();

  // Don't show bottom nav on landing, login, or signup pages
  const hideBottomNav = [
    "/",
    "/login",
    "/signup",
    "/reset-password",
  ].includes(location.pathname);

  if (hideBottomNav) return null;

  // Role-based navigation items
  const patientNavItems = [
    {
      path: "/dashboard",
      icon: Home,
      label: "Home",
      matchPaths: ["/dashboard"],
    },
    {
      path: "/book-appointment",
      icon: Calendar,
      label: "Appointments",
      matchPaths: ["/book-appointment", "/select-gp", "/book-appointment-form", "/my-appointments"],
    },
    {
      path: "/notifications",
      icon: Bell,
      label: "Notifications",
    },
    {
      path: "/profile",
      icon: User,
      label: "Profile",
    },
  ];

  const doctorNavItems = [
    {
      path: "/dashboard",
      icon: Home,
      label: "Home",
      matchPaths: ["/dashboard"],
    },
    {
      path: "/patients",
      icon: FileText,
      label: "Patients",
      matchPaths: ["/patients", "/patient-list"],
    },
    {
      path: "/notifications",
      icon: Bell,
      label: "Notifications",
    },
    {
      path: "/profile",
      icon: User,
      label: "Profile",
    },
  ];

  const navItems = user?.role === "doctor" ? doctorNavItems : patientNavItems;

  const isActiveItem = (item) => {
    if (location.pathname === item.path) return true;
    if (item.matchPaths) {
      return item.matchPaths.some(path => location.pathname.startsWith(path));
    }
    return false;
  };

  return (
    <nav className="bottom-navigation">
      {navItems.map((item) => {
        const Icon = item.icon;
        const active = isActiveItem(item);
        
        return (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `bottom-nav-item ${isActive || active ? "active" : ""}`
            }
          >
            <Icon size={24} />
            <span className="bottom-nav-label">{item.label}</span>
          </NavLink>
        );
      })}
    </nav>
  );
};

export default BottomNavigation;


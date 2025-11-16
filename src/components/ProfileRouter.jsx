import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProfileRouter = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      // Redirect based on user role
      if (user.profile?.role === 'doctor') {
        navigate('/doctor-profile', { replace: true });
      } else {
        navigate('/profile', { replace: true });
      }
    }
  }, [user, navigate]);

  // Show loading state while determining role
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '60vh' 
    }}>
      <div style={{ textAlign: 'center' }}>
        <div className="profile-loading-spinner"></div>
        <p>Loading profile...</p>
      </div>
    </div>
  );
};

export default ProfileRouter;

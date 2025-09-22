import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  sendPasswordResetEmail,
  updateProfile,
  onAuthStateChanged
} from 'firebase/auth';
import { auth } from '../config/firebase';
import { SupabaseService, USER_ROLES } from '../config/supabase';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sign up with email and password
  const signup = async (email, password, additionalData) => {
    try {
      setError(null);
      
      // Create Firebase user
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Update Firebase profile
      await updateProfile(user, {
        displayName: `${additionalData.firstName} ${additionalData.lastName}`
      });

      // Create user profile in Supabase
      const profileData = {
        email: email,
        first_name: additionalData.firstName,
        last_name: additionalData.lastName,
        phone: additionalData.phone || null,
        role: additionalData.role,
        gender: additionalData.gender || null,
        date_of_birth: additionalData.dateOfBirth || null
      };

      const result = await SupabaseService.createUserProfile(user.uid, profileData);
      
      if (!result.success) {
        throw new Error(result.error);
      }

      // If user is a doctor, create doctor profile
      if (additionalData.role === USER_ROLES.DOCTOR) {
        await SupabaseService.createDoctorProfile(user.uid, {
          license_number: additionalData.licenseNumber,
          specialization: additionalData.specialization,
          years_of_experience: additionalData.experience || 0,
          hospital_affiliation: additionalData.hospital || null,
          bio: additionalData.bio || null
        });
      }

      return { success: true, user };
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Sign in with email and password
  const login = async (email, password) => {
    try {
      setError(null);
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return { success: true, user: userCredential.user };
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Sign out
  const logout = async () => {
    try {
      setError(null);
      await signOut(auth);
      setCurrentUser(null);
      setUserProfile(null);
      return { success: true };
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Reset password
  const resetPassword = async (email) => {
    try {
      setError(null);
      await sendPasswordResetEmail(auth, email);
      return { success: true };
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Update user profile
  const updateUserProfile = async (updates) => {
    try {
      setError(null);
      
      if (!currentUser) {
        throw new Error('No user logged in');
      }

      // Update Firebase display name if name changed
      if (updates.first_name || updates.last_name) {
        await updateProfile(currentUser, {
          displayName: `${updates.first_name || userProfile.first_name} ${updates.last_name || userProfile.last_name}`
        });
      }

      // Update Supabase profile
      const result = await SupabaseService.updateUserProfile(currentUser.uid, updates);
      
      if (!result.success) {
        throw new Error(result.error);
      }

      // Update local state
      setUserProfile(prev => ({ ...prev, ...updates }));
      
      return { success: true, data: result.data };
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  // Load user profile from Supabase
  const loadUserProfile = async (uid) => {
    try {
      const result = await SupabaseService.getUserProfile(uid);
      if (result.success) {
        setUserProfile(result.data);
        return result.data;
      } else {
        console.error('Failed to load user profile:', result.error);
        return null;
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      return null;
    }
  };

  // Check if user has specific role
  const hasRole = (role) => {
    return userProfile && userProfile.role === role;
  };

  // Check if user is doctor
  const isDoctor = () => hasRole(USER_ROLES.DOCTOR);

  // Check if user is patient
  const isPatient = () => hasRole(USER_ROLES.PATIENT);

  // Check if user is admin
  const isAdmin = () => hasRole(USER_ROLES.ADMIN);

  // Listen for auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setCurrentUser(user);
        // Load user profile from Supabase
        await loadUserProfile(user.uid);
      } else {
        setCurrentUser(null);
        setUserProfile(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  // Context value
  const value = {
    // User state
    currentUser,
    userProfile,
    loading,
    error,
    
    // Authentication methods
    signup,
    login,
    logout,
    resetPassword,
    
    // Profile methods
    updateUserProfile,
    loadUserProfile,
    
    // Role checking methods
    hasRole,
    isDoctor,
    isPatient,
    isAdmin,
    
    // Utility
    isAuthenticated: !!currentUser,
    userId: currentUser?.uid || null,
    userEmail: currentUser?.email || null,
    userName: userProfile ? `${userProfile.first_name} ${userProfile.last_name}` : currentUser?.displayName || null,
    userRole: userProfile?.role || null
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

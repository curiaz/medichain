"""
MediChain Healthcare System - Complete Firebase Auth + Supabase Integration
This file contains the complete setup for Firebase Authentication with Supabase backend
"""

# =====================================================
# 1. FRONTEND (React) - Firebase Auth Setup
# =====================================================

# File: src/services/authService.js
"""
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword,
  sendPasswordResetEmail,
  updatePassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup
} from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// Auth Service Class
class AuthService {
  
  // Sign up with email/password
  async signUp(email, password, userData) {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Get Firebase ID token
      const idToken = await user.getIdToken();
      
      // Create patient record in Supabase via backend
      const response = await fetch('/api/auth/create-patient', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify({
          firebase_uid: user.uid,
          email: user.email,
          ...userData
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to create patient record');
      }
      
      return { user, success: true };
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  }
  
  // Sign in with email/password
  async signIn(email, password) {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Get user profile from Supabase
      const idToken = await user.getIdToken();
      const profile = await this.fetchUserProfile(idToken);
      
      return { user, profile, success: true };
    } catch (error) {
      console.error('Signin error:', error);
      throw error;
    }
  }
  
  // Google Sign In
  async signInWithGoogle() {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;
      const idToken = await user.getIdToken();
      
      // Create or get patient record
      const response = await fetch('/api/auth/create-or-get-patient', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify({
          firebase_uid: user.uid,
          email: user.email,
          full_name: user.displayName,
          photo_url: user.photoURL
        })
      });
      
      const profile = await response.json();
      return { user, profile, success: true };
    } catch (error) {
      console.error('Google signin error:', error);
      throw error;
    }
  }
  
  // Password Reset
  async resetPassword(email) {
    try {
      await sendPasswordResetEmail(auth, email);
      return { success: true, message: 'Password reset email sent' };
    } catch (error) {
      console.error('Password reset error:', error);
      throw error;
    }
  }
  
  // Change Password
  async changePassword(currentPassword, newPassword) {
    try {
      const user = auth.currentUser;
      if (!user) throw new Error('No user logged in');
      
      // Re-authenticate user first
      await signInWithEmailAndPassword(auth, user.email, currentPassword);
      
      // Update password
      await updatePassword(user, newPassword);
      
      return { success: true, message: 'Password updated successfully' };
    } catch (error) {
      console.error('Change password error:', error);
      throw error;
    }
  }
  
  // Fetch user profile from Supabase
  async fetchUserProfile(idToken) {
    try {
      const response = await fetch('/api/auth/profile', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch profile');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Profile fetch error:', error);
      throw error;
    }
  }
  
  // Sign out
  async signOut() {
    try {
      await signOut(auth);
      return { success: true };
    } catch (error) {
      console.error('Signout error:', error);
      throw error;
    }
  }
  
  // Auth state observer
  onAuthStateChanged(callback) {
    return onAuthStateChanged(auth, callback);
  }
}

export const authService = new AuthService();
"""

# =====================================================
# 2. REACT COMPONENTS - Authentication UI
# =====================================================

# File: src/components/Auth/SignUp.jsx
"""
import React, { useState } from 'react';
import { authService } from '../../services/authService';

const SignUp = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    dateOfBirth: '',
    role: 'patient' // or 'doctor'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      await authService.signUp(formData.email, formData.password, {
        full_name: formData.fullName,
        date_of_birth: formData.dateOfBirth,
        role: formData.role
      });
      
      // Redirect to dashboard or profile completion
      window.location.href = '/dashboard';
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up for MediChain</h2>
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Full Name"
          value={formData.fullName}
          onChange={(e) => setFormData({...formData, fullName: e.target.value})}
          required
        />
        
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
        
        <input
          type="date"
          placeholder="Date of Birth"
          value={formData.dateOfBirth}
          onChange={(e) => setFormData({...formData, dateOfBirth: e.target.value})}
          required
        />
        
        <select
          value={formData.role}
          onChange={(e) => setFormData({...formData, role: e.target.value})}
        >
          <option value="patient">Patient</option>
          <option value="doctor">Doctor</option>
        </select>
        
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          required
        />
        
        <input
          type="password"
          placeholder="Confirm Password"
          value={formData.confirmPassword}
          onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
          required
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>
      
      <button onClick={() => authService.signInWithGoogle()}>
        Sign Up with Google
      </button>
    </div>
  );
};

export default SignUp;
"""

# File: src/components/Auth/SignIn.jsx
"""
import React, { useState } from 'react';
import { authService } from '../../services/authService';

const SignIn = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await authService.signIn(email, password);
      console.log('User signed in:', result.user);
      console.log('User profile:', result.profile);
      
      // Redirect based on role
      const role = result.profile?.role || 'patient';
      window.location.href = role === 'doctor' ? '/doctor-dashboard' : '/patient-dashboard';
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signin-container">
      <h2>Sign In to MediChain</h2>
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>
      
      <button onClick={() => authService.signInWithGoogle()}>
        Sign In with Google
      </button>
      
      <a href="/reset-password">Forgot Password?</a>
    </div>
  );
};

export default SignIn;
"""

print("✅ Frontend Firebase Auth components ready!")
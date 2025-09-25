/**
 * User Data Clearing Utility
 * Clears Firebase Auth users and Supabase user data
 */

import { auth } from '../config/firebase';
import { signOut } from 'firebase/auth';
import SupabaseService from '../services/SupabaseService';

/**
 * Clear local storage and session data
 */
export const clearLocalData = () => {
  try {
    // Clear localStorage
    localStorage.clear();
    
    // Clear sessionStorage
    sessionStorage.clear();
    
    // Clear specific keys that might persist
    const keysToRemove = [
      'medichain_user',
      'medichain_token',
      'firebase_user',
      'user_profile',
      'auth_token',
      'supabase.auth.token',
      'sb-medichain-auth-token'
    ];
    
    keysToRemove.forEach(key => {
      localStorage.removeItem(key);
      sessionStorage.removeItem(key);
    });
    
    console.log('✅ Local data cleared successfully');
    return true;
  } catch (error) {
    console.error('❌ Error clearing local data:', error);
    return false;
  }
};

/**
 * Sign out current user from Firebase
 */
export const signOutCurrentUser = async () => {
  try {
    if (auth.currentUser) {
      await signOut(auth);
      console.log('✅ User signed out from Firebase');
    }
    return true;
  } catch (error) {
    console.error('❌ Error signing out user:', error);
    return false;
  }
};

/**
 * Clear all user data from Supabase (profiles, medical records, etc.)
 * WARNING: This will delete all user data permanently
 */
export const clearSupabaseUserData = async () => {
  try {
    console.log('🧹 Starting Supabase user data cleanup...');
    
    // Clear user profiles
    const profileResult = await SupabaseService.client
      .from('user_profiles')
      .delete()
      .neq('id', '00000000-0000-0000-0000-000000000000'); // Keep system records if any
    
    if (profileResult.error) {
      console.warn('Warning clearing profiles:', profileResult.error.message);
    } else {
      console.log('✅ User profiles cleared');
    }
    
    // Clear medical records
    const medicalResult = await SupabaseService.client
      .from('medical_records')
      .delete()
      .neq('id', '00000000-0000-0000-0000-000000000000');
    
    if (medicalResult.error) {
      console.warn('Warning clearing medical records:', medicalResult.error.message);
    } else {
      console.log('✅ Medical records cleared');
    }
    
    // Clear AI diagnoses
    const aiResult = await SupabaseService.client
      .from('ai_diagnoses')
      .delete()
      .neq('id', '00000000-0000-0000-0000-000000000000');
    
    if (aiResult.error) {
      console.warn('Warning clearing AI diagnoses:', aiResult.error.message);
    } else {
      console.log('✅ AI diagnoses cleared');
    }
    
    // Clear appointments
    const appointmentResult = await SupabaseService.client
      .from('appointments')
      .delete()
      .neq('id', '00000000-0000-0000-0000-000000000000');
    
    if (appointmentResult.error) {
      console.warn('Warning clearing appointments:', appointmentResult.error.message);
    } else {
      console.log('✅ Appointments cleared');
    }
    
    console.log('✅ Supabase user data cleanup completed');
    return true;
  } catch (error) {
    console.error('❌ Error clearing Supabase data:', error);
    return false;
  }
};

/**
 * Complete user data reset
 * Clears everything: local data, Firebase auth, and Supabase data
 */
export const completeUserDataReset = async () => {
  try {
    console.log('🔄 Starting complete user data reset...');
    
    // Step 1: Sign out current user
    await signOutCurrentUser();
    
    // Step 2: Clear local data
    clearLocalData();
    
    // Step 3: Clear Supabase data
    await clearSupabaseUserData();
    
    console.log('✅ Complete user data reset finished');
    console.log('📝 You can now create new accounts');
    
    // Optional: Reload the page after a short delay
    setTimeout(() => {
      window.location.reload();
    }, 2000);
    
    return true;
  } catch (error) {
    console.error('❌ Error during complete reset:', error);
    return false;
  }
};

/**
 * Quick reset function for development
 */
export const devReset = async () => {
  if (process.env.NODE_ENV === 'development') {
    console.log('🔧 Development reset initiated...');
    await completeUserDataReset();
  } else {
    console.warn('⚠️ Dev reset only available in development mode');
  }
};

// Export default function for easy import
export default {
  clearLocalData,
  signOutCurrentUser,
  clearSupabaseUserData,
  completeUserDataReset,
  devReset
};
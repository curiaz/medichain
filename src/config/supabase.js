// Enhanced Supabase Configuration for MediChain
import { createClient } from '@supabase/supabase-js';

// Supabase credentials - get these from your Supabase dashboard
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://royvcmfbcghamnbnxdgb.supabase.co';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4MDQwOTksImV4cCI6MjA2ODM4MDA5OX0.By2hJPp_2vn141HOPUDE-svm1m1sKtqhfHNSYTuf658';

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    // Disable Supabase auth since we're using Firebase
    autoRefreshToken: false,
    persistSession: false,
    detectSessionInUrl: false
  }
});

// Database table names
export const TABLES = {
  USER_PROFILES: 'user_profiles',
  MEDICAL_RECORDS: 'medical_records',
  DOCTOR_PROFILES: 'doctor_profiles', 
  APPOINTMENTS: 'appointments',
  AI_DIAGNOSES: 'ai_diagnoses',
  PRESCRIPTIONS: 'prescriptions'
};

// User roles
export const USER_ROLES = {
  PATIENT: 'patient',
  DOCTOR: 'doctor',
  ADMIN: 'admin'
};

// Database operations wrapper class
export class SupabaseService {
  
  // User Profile Operations
  static async createUserProfile(userId, profileData) {
    try {
      const { data, error } = await supabase
        .from(TABLES.USER_PROFILES)
        .insert({
          firebase_uid: userId,
          ...profileData
        })
        .select()
        .single();
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error creating user profile:', error);
      return { success: false, error: error.message };
    }
  }

  static async getUserProfile(userId) {
    try {
      const { data, error } = await supabase
        .from(TABLES.USER_PROFILES)
        .select('*')
        .eq('firebase_uid', userId)
        .single();
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching user profile:', error);
      return { success: false, error: error.message };
    }
  }

  static async updateUserProfile(userId, updates) {
    try {
      const { data, error } = await supabase
        .from(TABLES.USER_PROFILES)
        .update(updates)
        .eq('firebase_uid', userId)
        .select()
        .single();
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error updating user profile:', error);
      return { success: false, error: error.message };
    }
  }

  // Medical Records Operations
  static async createMedicalRecord(recordData) {
    try {
      const { data, error } = await supabase
        .from(TABLES.MEDICAL_RECORDS)
        .insert(recordData)
        .select()
        .single();
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error creating medical record:', error);
      return { success: false, error: error.message };
    }
  }

  static async getPatientRecords(patientId) {
    try {
      const { data, error } = await supabase
        .from(TABLES.MEDICAL_RECORDS)
        .select(`
          *,
          doctor_profile:doctor_profiles(first_name, last_name, specialization)
        `)
        .eq('patient_firebase_uid', patientId)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching patient records:', error);
      return { success: false, error: error.message };
    }
  }

  // AI Diagnosis Operations
  static async saveAIDiagnosis(diagnosisData) {
    try {
      const { data, error } = await supabase
        .from(TABLES.AI_DIAGNOSES)
        .insert(diagnosisData)
        .select()
        .single();
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error saving AI diagnosis:', error);
      return { success: false, error: error.message };
    }
  }

  static async getAIDiagnosisHistory(userId) {
    try {
      const { data, error } = await supabase
        .from(TABLES.AI_DIAGNOSES)
        .select('*')
        .eq('user_firebase_uid', userId)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching AI diagnosis history:', error);
      return { success: false, error: error.message };
    }
  }

  // Doctor Operations
  static async getAllDoctors() {
    try {
      const { data, error } = await supabase
        .from(TABLES.DOCTOR_PROFILES)
        .select(`
          *,
          user_profile:user_profiles(first_name, last_name, email, phone)
        `);
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching doctors:', error);
      return { success: false, error: error.message };
    }
  }

  // Appointment Operations
  static async createAppointment(appointmentData) {
    try {
      const { data, error } = await supabase
        .from(TABLES.APPOINTMENTS)
        .insert(appointmentData)
        .select()
        .single();
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error creating appointment:', error);
      return { success: false, error: error.message };
    }
  }

  static async getUserAppointments(userId, role) {
    try {
      const column = role === USER_ROLES.DOCTOR ? 'doctor_firebase_uid' : 'patient_firebase_uid';
      
      const { data, error } = await supabase
        .from(TABLES.APPOINTMENTS)
        .select(`
          *,
          patient_profile:user_profiles!appointments_patient_firebase_uid_fkey(first_name, last_name, email),
          doctor_profile:user_profiles!appointments_doctor_firebase_uid_fkey(first_name, last_name, email)
        `)
        .eq(column, userId)
        .order('appointment_date', { ascending: true });
      
      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching appointments:', error);
      return { success: false, error: error.message };
    }
  }
}

export default supabase;

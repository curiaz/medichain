// Database Service for MediChain
// Connects to Supabase backend to provide real data instead of mock data

import { supabase, TABLES } from '../config/supabase';
import { auth } from '../config/firebase';

export class DatabaseService {
  
  // Dashboard Statistics
  static async getDoctorStats(doctorId) {
    try {
      // Get total patients assigned to this doctor
      const { data: patients, error: patientsError } = await supabase
        .from('medical_records')
        .select('patient_firebase_uid', { count: 'exact' })
        .eq('doctor_firebase_uid', doctorId);

      if (patientsError) throw patientsError;

      // Get pending AI reviews (AI diagnoses not yet reviewed by doctor)
      const { data: pendingReviews, error: reviewsError } = await supabase
        .from(TABLES.AI_DIAGNOSES)
        .select('*', { count: 'exact' })
        .is('doctor_review_status', null)
        .eq('assigned_doctor_uid', doctorId);

      if (reviewsError) throw reviewsError;

      // Get total AI consultations this doctor has reviewed
      const { data: aiConsultations, error: consultationsError } = await supabase
        .from(TABLES.AI_DIAGNOSES)
        .select('*', { count: 'exact' })
        .eq('assigned_doctor_uid', doctorId)
        .not('doctor_review_status', 'is', null);

      if (consultationsError) throw consultationsError;

      // Get recent activity (records created in last 7 days)
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      
      const { data: recentActivity, error: activityError } = await supabase
        .from('medical_records')
        .select('*', { count: 'exact' })
        .eq('doctor_firebase_uid', doctorId)
        .gte('created_at', sevenDaysAgo.toISOString());

      if (activityError) throw activityError;

      return {
        success: true,
        data: {
          totalPatients: patients?.length || 0,
          pendingReviews: pendingReviews?.length || 0,
          aiConsultations: aiConsultations?.length || 0,
          recentActivity: recentActivity?.length || 0
        }
      };
    } catch (error) {
      console.error('Error fetching doctor stats:', error);
      return {
        success: false,
        error: error.message,
        // Return fallback data if database fails
        data: {
          totalPatients: 0,
          pendingReviews: 0,
          aiConsultations: 0,
          recentActivity: 0
        }
      };
    }
  }

  static async getPatientStats(patientId) {
    try {
      // Get total consultations (AI diagnoses)
      const { data: consultations, error: consultationsError } = await supabase
        .from(TABLES.AI_DIAGNOSES)
        .select('*', { count: 'exact' })
        .eq('user_firebase_uid', patientId);

      if (consultationsError) throw consultationsError;

      // Get AI diagnoses count
      const aiDiagnoses = consultations?.length || 0;

      // Get last checkup (most recent medical record)
      const { data: lastCheckup, error: checkupError } = await supabase
        .from('medical_records')
        .select('created_at')
        .eq('patient_firebase_uid', patientId)
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      let daysSinceCheckup = 0;
      if (lastCheckup && !checkupError) {
        const checkupDate = new Date(lastCheckup.created_at);
        const today = new Date();
        daysSinceCheckup = Math.floor((today - checkupDate) / (1000 * 60 * 60 * 24));
      }

      // Calculate health score based on activity and recent checkups
      let healthScore = 85; // Base score
      if (daysSinceCheckup > 90) healthScore -= 10;
      if (aiDiagnoses > 5) healthScore += 5; // Active in monitoring health
      if (daysSinceCheckup === 0) healthScore = 100; // Recent checkup

      return {
        success: true,
        data: {
          totalConsultations: consultations?.length || 0,
          aiDiagnoses: aiDiagnoses,
          lastCheckup: daysSinceCheckup,
          healthScore: Math.max(0, Math.min(100, healthScore))
        }
      };
    } catch (error) {
      console.error('Error fetching patient stats:', error);
      return {
        success: false,
        error: error.message,
        // Return fallback data if database fails
        data: {
          totalConsultations: 0,
          aiDiagnoses: 0,
          lastCheckup: 0,
          healthScore: 85
        }
      };
    }
  }

  // Patient AI History Functions
  static async getPatientList(doctorId) {
    try {
      // Get all patients who have AI diagnoses assigned to this doctor
      const { data, error } = await supabase
        .from(TABLES.AI_DIAGNOSES)
        .select(`
          user_firebase_uid,
          created_at,
          user_profiles!inner(
            firebase_uid,
            first_name,
            last_name,
            email
          )
        `)
        .eq('assigned_doctor_uid', doctorId)
        .order('created_at', { ascending: false });

      if (error) throw error;

      // Group by patient and get latest consultation date
      const patientMap = new Map();
      data?.forEach(record => {
        const uid = record.user_firebase_uid;
        const profile = record.user_profiles;
        
        if (!patientMap.has(uid) || new Date(record.created_at) > new Date(patientMap.get(uid).last_consultation)) {
          patientMap.set(uid, {
            id: uid,
            name: `${profile.first_name} ${profile.last_name}`,
            email: profile.email,
            last_consultation: record.created_at
          });
        }
      });

      return {
        success: true,
        data: Array.from(patientMap.values())
      };
    } catch (error) {
      console.error('Error fetching patient list:', error);
      return {
        success: false,
        error: error.message,
        data: []
      };
    }
  }

  static async getPatientAIHistory(patientId, doctorId = null) {
    try {
      let query = supabase
        .from(TABLES.AI_DIAGNOSES)
        .select(`
          *,
          user_profiles!inner(
            first_name,
            last_name,
            date_of_birth
          )
        `)
        .eq('user_firebase_uid', patientId)
        .order('created_at', { ascending: false });

      // If doctor is specified, only show diagnoses assigned to them
      if (doctorId) {
        query = query.eq('assigned_doctor_uid', doctorId);
      }

      const { data, error } = await query;

      if (error) throw error;

      // Transform data to match expected format
      const transformedData = data?.map(record => ({
        id: record.id,
        patient_id: record.user_firebase_uid,
        timestamp: record.created_at,
        symptoms: record.symptoms,
        age: record.age || this.calculateAge(record.user_profiles?.date_of_birth),
        gender: record.gender,
        diagnosis: record.diagnosis,
        confidence: record.confidence_score,
        prescription: record.prescription,
        recommendations: record.recommendations,
        doctor_review: record.doctor_review_status,
        doctor_notes: record.doctor_notes || '',
        modified_prescription: record.modified_prescription,
        session_type: record.session_type || 'authenticated'
      })) || [];

      return {
        success: true,
        data: transformedData
      };
    } catch (error) {
      console.error('Error fetching AI history:', error);
      return {
        success: false,
        error: error.message,
        data: []
      };
    }
  }

  // Helper function to calculate age from date of birth
  static calculateAge(dateOfBirth) {
    if (!dateOfBirth) return null;
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  }

  // Update doctor review
  static async updateDoctorReview(diagnosisId, reviewData) {
    try {
      const { data, error } = await supabase
        .from(TABLES.AI_DIAGNOSES)
        .update({
          doctor_review_status: reviewData.status,
          doctor_notes: reviewData.notes,
          modified_prescription: reviewData.modifiedPrescription,
          reviewed_at: new Date().toISOString(),
          reviewed_by: auth.currentUser?.uid
        })
        .eq('id', diagnosisId)
        .select()
        .single();

      if (error) throw error;

      return { success: true, data };
    } catch (error) {
      console.error('Error updating doctor review:', error);
      return { success: false, error: error.message };
    }
  }

  // Get all doctors for assignment
  static async getAllDoctors() {
    try {
      const { data, error } = await supabase
        .from('doctor_profiles')
        .select(`
          *,
          user_profiles!inner(
            firebase_uid,
            first_name,
            last_name,
            email
          )
        `)
        .eq('is_verified', true);

      if (error) throw error;

      const doctors = data?.map(doc => ({
        id: doc.user_profiles.firebase_uid,
        name: `Dr. ${doc.user_profiles.first_name} ${doc.user_profiles.last_name}`,
        email: doc.user_profiles.email,
        specialization: doc.specialization,
        license_number: doc.license_number
      })) || [];

      return { success: true, data: doctors };
    } catch (error) {
      console.error('Error fetching doctors:', error);
      return { success: false, error: error.message, data: [] };
    }
  }
}

export default DatabaseService;
// Database Service for MediChain
// Connects to Supabase backend to provide real data instead of mock data

import { supabase, TABLES } from '../config/supabase';
import { auth } from '../config/firebase';
import { API_CONFIG } from '../config/api';

export class DatabaseService {
  
  // Dashboard Statistics
  static async getDoctorStats(doctorId) {
    try {
      // Get pending reviews: Count ALL appointments that haven't been reviewed yet
      // Use backend endpoint to bypass RLS and get accurate count
      let pendingReviews = 0;
      let pendingReviewsError = null;
      try {
        console.log(`🔍 [Pending Reviews] Fetching pending reviews count for doctor: ${doctorId}`);
        
        // Try to get Firebase token for backend API call
        let token = null;
        try {
          const currentUser = auth.currentUser;
          if (currentUser) {
            token = await currentUser.getIdToken();
          } else {
            token = localStorage.getItem('medichain_token') || localStorage.getItem('firebase_id_token');
          }
        } catch (tokenErr) {
          console.warn('⚠️  Could not get auth token, trying fallback:', tokenErr);
          token = localStorage.getItem('medichain_token') || localStorage.getItem('firebase_id_token');
        }
        
        if (token) {
          // Use backend endpoint which uses service_client to bypass RLS
          const response = await fetch(`${API_CONFIG.API_URL}/appointments/pending-reviews-count`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              pendingReviews = data.pending_reviews || 0;
              console.log(`✅ [Pending Reviews] Got count from backend: ${pendingReviews}`);
            } else {
              console.warn('⚠️  Backend returned error:', data.error);
              pendingReviewsError = new Error(data.error || 'Failed to get pending reviews count');
            }
          } else {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            console.error(`❌ [Pending Reviews] Backend error (${response.status}):`, errorData);
            pendingReviewsError = new Error(errorData.error || `HTTP ${response.status}`);
          }
        } else {
          console.warn('⚠️  No auth token available, falling back to direct Supabase query');
          // Fallback to direct Supabase query (may be subject to RLS)
          const appointmentsResult = await supabase
            .from('appointments')
            .select('id')
            .eq('doctor_firebase_uid', doctorId);
          
          if (appointmentsResult.error) {
            pendingReviewsError = appointmentsResult.error;
          } else {
            const appointmentIds = (appointmentsResult.data || []).map(apt => apt.id);
            
            if (appointmentIds.length > 0) {
              const reportsResult = await supabase
                .from('medical_records')
                .select('appointment_id, review_status')
                .in('appointment_id', appointmentIds)
                .eq('doctor_firebase_uid', doctorId);
              
              if (!reportsResult.error && reportsResult.data) {
                const reviewedAppointmentIds = new Set(
                  (reportsResult.data || [])
                    .filter(r => r.review_status === 'reviewed')
                    .map(r => r.appointment_id)
                );
                pendingReviews = appointmentIds.filter(id => !reviewedAppointmentIds.has(id)).length;
              } else {
                pendingReviews = appointmentIds.length;
              }
            }
          }
        }
      } catch (err) {
        console.error('❌ [Pending Reviews] Exception:', err);
        pendingReviewsError = null;
        // Don't throw, just set to 0 on error
        pendingReviews = 0;
      }

      if (pendingReviewsError) {
        console.error(`❌ [Pending Reviews] Error:`, pendingReviewsError);
        // Don't throw, just set to 0
        pendingReviews = 0;
      }
      
      console.log(`✅ [Pending Reviews] Final count: ${pendingReviews}`);

      // Get AI Diagnosis Reviewed count (medical reports with review_status = 'reviewed')
      // Use backend endpoint to bypass RLS and get accurate count
      let aiDiagnosisReviewed = 0;
      let aiDiagnosisError = null;
      try {
        console.log(`🔍 [AI Diagnosis Reviewed] Fetching reviewed count for doctor: ${doctorId}`);
        
        // Try to get Firebase token for backend API call
        let token = null;
        try {
          const currentUser = auth.currentUser;
          if (currentUser) {
            token = await currentUser.getIdToken();
          } else {
            token = localStorage.getItem('medichain_token') || localStorage.getItem('firebase_id_token');
          }
        } catch (tokenErr) {
          console.warn('⚠️  Could not get auth token, trying fallback:', tokenErr);
          token = localStorage.getItem('medichain_token') || localStorage.getItem('firebase_id_token');
        }
        
        if (token) {
          // Use backend endpoint which uses service_client to bypass RLS
          const response = await fetch(`${API_CONFIG.API_URL}/appointments/ai-diagnosis-reviewed-count`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              aiDiagnosisReviewed = data.ai_diagnosis_reviewed || 0;
              console.log(`✅ [AI Diagnosis Reviewed] Got count from backend: ${aiDiagnosisReviewed}`);
            } else {
              console.warn('⚠️  Backend returned error:', data.error);
              aiDiagnosisError = new Error(data.error || 'Failed to get AI diagnosis reviewed count');
            }
          } else {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            console.error(`❌ [AI Diagnosis Reviewed] Backend error (${response.status}):`, errorData);
            aiDiagnosisError = new Error(errorData.error || `HTTP ${response.status}`);
          }
        } else {
          console.warn('⚠️  No auth token available, falling back to direct Supabase query');
          // Fallback to direct Supabase query (may be subject to RLS)
          let result = await supabase
            .from('medical_records')
            .select('id, review_status, diagnosis')
            .eq('doctor_firebase_uid', doctorId);
          
          if (result.error) {
            aiDiagnosisError = result.error;
          } else if (result && result.data) {
            // Filter for reviewed reports: check review_status = 'reviewed' OR (if no review_status column, check if diagnosis exists)
            const reviewedReports = result.data.filter(report => {
              if (report.hasOwnProperty('review_status')) {
                return report.review_status === 'reviewed';
              }
              return report.diagnosis && report.diagnosis.trim() !== '';
            });
            aiDiagnosisReviewed = reviewedReports.length;
          }
        }
      } catch (err) {
        console.error('❌ [AI Diagnosis Reviewed] Exception:', err);
        aiDiagnosisError = null;
        // Don't throw, just set to 0 on error
        aiDiagnosisReviewed = 0;
      }

      if (aiDiagnosisError) {
        console.error(`❌ [AI Diagnosis Reviewed] Error:`, aiDiagnosisError);
        // Don't throw, just set to 0
        aiDiagnosisReviewed = 0;
      }
      
      console.log(`✅ [AI Diagnosis Reviewed] Final count: ${aiDiagnosisReviewed}`);

      // Get today's activity (medical reports with review_status = 'reviewed' created/updated today)
      // Only count reviewed reports, not pending ones
      let todaysActivity = 0;
      let activityError = null;
      try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const todayISO = today.toISOString();
        
        // First try with review_status column
        let result = await supabase
          .from('medical_records')
          .select('id', { count: 'exact' })
          .eq('doctor_firebase_uid', doctorId)
          .eq('review_status', 'reviewed')
          .gte('updated_at', todayISO);
        
        if (result.error) {
          // If review_status column doesn't exist, fallback to checking diagnosis
          if (result.error.code === 'PGRST116' || result.error.message?.includes('column') || result.error.message?.includes('does not exist')) {
            console.log('ℹ️  review_status column not available, using diagnosis check');
            result = await supabase
              .from('medical_records')
              .select('id', { count: 'exact' })
              .eq('doctor_firebase_uid', doctorId)
              .not('diagnosis', 'is', null)
              .neq('diagnosis', '')
              .gte('updated_at', todayISO);
          } else if (result.error.code === 'PGRST116' || result.error.message?.includes('relation') || result.error.message?.includes('does not exist')) {
            console.log('ℹ️  medical_records table not available');
            activityError = null;
          } else {
            activityError = result.error;
          }
        }
        
        if (!activityError && result && !result.error) {
          todaysActivity = result.count || result.data?.length || 0;
        }
      } catch (err) {
        console.log('ℹ️  Could not fetch today\'s activity:', err.message);
        activityError = null;
      }

      if (activityError) throw activityError;

      return {
        success: true,
        data: {
          pendingReviews: pendingReviews,
          aiDiagnosisReviewed: aiDiagnosisReviewed,
          todaysActivity: todaysActivity
        }
      };
    } catch (error) {
      console.error('Error fetching doctor stats:', error);
      return {
        success: false,
        error: error.message,
        // Return fallback data if database fails
        data: {
          pendingReviews: 0,
          aiDiagnosisReviewed: 0,
          todaysActivity: 0
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
      // Note: medical_records table may not exist yet, so handle gracefully
      let lastCheckup = null;
      let checkupError = null;
      try {
        const result = await supabase
          .from('medical_records')
          .select('created_at')
          .eq('patient_firebase_uid', patientId)
          .order('created_at', { ascending: false })
          .limit(1)
          .maybeSingle(); // Use maybeSingle() instead of single() to avoid errors if no records
        
        if (result.error) {
          // If table doesn't exist or RLS blocks, just log and continue
          if (result.error.code === 'PGRST116' || result.error.message?.includes('relation') || result.error.message?.includes('does not exist')) {
            console.log('ℹ️  medical_records table not available or no records found');
            checkupError = null; // Don't treat as error
          } else {
            checkupError = result.error;
          }
        } else {
          lastCheckup = result.data;
        }
      } catch (err) {
        console.log('ℹ️  Could not fetch medical records (table may not exist):', err.message);
        checkupError = null; // Don't treat as error - table may not be set up yet
      }

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

  // Get all patients in the system
  static async getAllPatients() {
    try {
      const { data, error } = await supabase
        .from(TABLES.USER_PROFILES)
        .select('firebase_uid, first_name, last_name, email, created_at, avatar_url')
        .eq('role', 'patient')
        .eq('is_active', true)
        .order('created_at', { ascending: false });

      if (error) throw error;

      const patients = data?.map(patient => ({
        id: patient.firebase_uid,
        name: `${patient.first_name || ''} ${patient.last_name || ''}`.trim(),
        email: patient.email,
        joined: patient.created_at,
        avatar_url: patient.avatar_url
      })) || [];

      return { success: true, data: patients };
    } catch (error) {
      console.error('Error fetching all patients:', error);
      return { success: false, error: error.message, data: [] };
    }
  }
}

export default DatabaseService;
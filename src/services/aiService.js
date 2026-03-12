import axios from 'axios';

// Streamlined AI Diagnosis Service - Version 5.0
const AI_BASE_URL = process.env.REACT_APP_API_URL || 'https://medichainn.onrender.com';

const api = axios.create({
  baseURL: AI_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.error('AI server is not running or unreachable');
      error.isNetworkError = true;
    }
    return Promise.reject(error);
  }
);

export const aiService = {
  getDiagnosis: async (diagnosisData) => {
    try {
      console.log('🩺 Sending diagnosis request:', diagnosisData);
      
      const requestData = {
        symptoms: diagnosisData.symptoms
      };
      
      const response = await api.post('/api/diagnose', requestData);
      const aiData = response.data;
      
      if (!aiData.success || aiData.error) {
        return {
          success: false,
          error: aiData.error || 'AI diagnosis failed',
          message: aiData.message || 'Unknown error occurred'
        };
      }
      
      const diagnosis = aiData.data;
      
      // Debug logging
      console.log('🔍 AI Service Debug:', {
        aiData: aiData,
        diagnosis: diagnosis,
        detected_symptoms: diagnosis.detected_symptoms,
        detailed_results: diagnosis.detailed_results
      });
      
      // SLIDE 1: Detected symptoms from user input
      const symptomsText = diagnosis.detected_symptoms && diagnosis.detected_symptoms.length > 0 
        ? diagnosis.detected_symptoms.join(', ')
        : 'No specific symptoms detected';

      // SLIDE 2: Top 3 conditions with reasons from condition_reason - Sheet1.csv
      let conditionsText = '';
      if (diagnosis.detailed_results && diagnosis.detailed_results.length > 0) {
        conditionsText = diagnosis.detailed_results.map((result, index) => {
          return `${index + 1}. ${result.condition} (${result.confidence})\n   Reason: ${result.reason}`;
        }).join('\n\n');
      } else {
        conditionsText = `1. ${diagnosis.primary_condition} (${diagnosis.primary_confidence})\n   Reason: [No reason data available from CSV]`;
      }

      // SLIDE 3: Recommended actions - condition name and action from action_medication CSV
      let recommendedActionsText = '';
      if (diagnosis.detailed_results && diagnosis.detailed_results.length > 0) {
        recommendedActionsText = diagnosis.detailed_results.map((result, index) => {
          return `${index + 1}. ${result.condition}:\n   ${result.recommended_action}`;
        }).join('\n\n');
      } else {
        recommendedActionsText = `1. ${diagnosis.primary_condition}:\n   [No action data available from CSV]`;
      }

      // SLIDE 4: Medications from action_medication CSV - Enhanced format for better UI
      let medicationsData = [];
      if (diagnosis.detailed_results && diagnosis.detailed_results.length > 0) {
        medicationsData = diagnosis.detailed_results.map((result, index) => ({
          id: index + 1,
          condition: result.condition,
          confidence: result.confidence,
          medicine: result.medication_details?.medicine || result.medication || '[No medicine data in CSV]',
          adult_dose: result.medication_details?.adult_dose || '[No adult dose data in CSV]',
          child_dose: result.medication_details?.child_dose || '[No child dose data in CSV]',
          max_daily_dose: result.medication_details?.max_daily_dose || '[No max dose data in CSV]',
          description: result.medication_details?.description || '[No description data in CSV]',
          notes: result.medication_details?.notes || result.notes || '[No notes data in CSV]'
        }));
      } else {
        medicationsData = [{
          id: 1,
          condition: diagnosis.primary_condition,
          confidence: diagnosis.primary_confidence,
          medicine: '[No medicine data in CSV]',
          adult_dose: '[No adult dose data in CSV]',
          child_dose: '[No child dose data in CSV]',
          max_daily_dose: '[No max dose data in CSV]',
          description: '[No description data in CSV]',
          notes: '[No notes data in CSV]'
        }];
      }

      // Convert medications to text format for legacy support
      const medicationsText = medicationsData.map((med) => {
        return `${med.id}. ${med.condition}:\n   Medicine: ${med.medicine}\n   Adult Dose: ${med.adult_dose}\n   Child Dose: ${med.child_dose}\n   Max Daily: ${med.max_daily_dose}\n   Notes: ${med.notes}`;
      }).join('\n\n');

      // Create formatted response string with slide markers expected by slideshow
      const formatted_response = `**SLIDE_1_SYMPTOMS**
${symptomsText}

**SLIDE_2_CONDITIONS**
${conditionsText}

**SLIDE_3_RECOMMENDED_ACTION**
${recommendedActionsText}

**SLIDE_4_MEDICATIONS**
${medicationsText}`;

      const transformedResponse = {
        success: true,
        data: {
          diagnosis: diagnosis.primary_condition,
          confidence: parseFloat(diagnosis.primary_confidence.replace('%', '')),
          formatted_response: formatted_response,
          medications_data: medicationsData, // Enhanced data for slide 4 UI
          detected_symptoms: diagnosis.detected_symptoms,
          detailed_results: diagnosis.detailed_results, // ✅ CRITICAL: Include detailed_results for slide 2
          prescription: {
            medications: diagnosis.detailed_results[0]?.medicine ? [diagnosis.detailed_results[0].medicine] : ['[No medicine data in CSV]'],
            treatments: diagnosis.detailed_results[0]?.recommended_action ? [diagnosis.detailed_results[0].recommended_action] : ['[No treatment data in CSV]'],
            instructions: diagnosis.detailed_results[0]?.notes || '[No instructions data in CSV]'
          },
          recommendations: [
            diagnosis.detailed_results[0]?.recommended_action || '[No recommendations data in CSV]',
            '[All data should come from CSV files only]',
            '[Follow CSV recommendations only]'
          ],
          ai_model_version: diagnosis.model_version,
          timestamp: diagnosis.timestamp,
          medical_disclaimer: diagnosis.disclaimer
        }
      };
      
      return transformedResponse;
      
    } catch (error) {
      console.error('❌ AI diagnosis error:', error);
      
      if (error.isNetworkError) {
        return {
          success: false,
          error: 'Network Error',
          message: 'AI server is not running. Please ensure the backend is started.'
        };
      }
      
      if (error.response) {
        const errorData = error.response.data;
        return {
          success: false,
          error: errorData.error || 'API Error',
          message: errorData.message || 'Request failed'
        };
      }
      
      return {
        success: false,
        error: 'Unexpected Error',
        message: error.message || 'An unexpected error occurred'
      };
    }
  },

  checkHealth: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('❌ Health check error:', error);
      return {
        status: 'unhealthy',
        ai_ready: false,
        error: error.message
      };
    }
  },

  // Legacy method names for backward compatibility
  diagnose: async (diagnosisData) => {
    return await aiService.getDiagnosis(diagnosisData);
  },

  checkStatus: async () => {
    return await aiService.checkHealth();
  },

  healthCheck: async () => {
    return await aiService.checkHealth();
  }
};

export default aiService;

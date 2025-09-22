import axios from 'axios';

// AI Diagnosis Service - connects to the enhanced AI system
const AI_BASE_URL = process.env.REACT_APP_AI_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: AI_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds timeout for AI processing
});

// Add response interceptor for better error handling
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
  /**
   * Get AI diagnosis based on symptoms
   * @param {Object} diagnosisData - The diagnosis request data
   * @returns {Promise<Object>} Diagnosis response
   */
  getDiagnosis: async (diagnosisData) => {
    try {
      console.log("Sending diagnosis request:", diagnosisData);
      const response = await api.post('/diagnose', diagnosisData);
      console.log("Received diagnosis response:", response.data);
      
      // Transform the AI response to match frontend expectations
      const aiData = response.data;
      
      // Check for error message in response
      if (aiData.error) {
        return {
          success: false,
          error: aiData.error
        };
      }
      
      // Handle both normal diagnosis and unknown case responses
      if (aiData.status === 'unknown_case') {
        return {
          success: true,
          data: {
            diagnosis: 'Professional Consultation Required',
            confidence: 0,
            severity: 'High',
            urgency: 'immediate',
            prescription: aiData.message,
            recommendations: aiData.suggested_actions || [],
            ai_model_version: 'MediChain-AI',
            requires_consultation: true,
            explanation: aiData.reasoning?.ai_limitation || 'This symptom combination requires professional medical evaluation.'
          }
        };
      }
      
      // Handle direct diagnosis response from run_ai_server.py
      if (aiData.diagnosis || aiData.primary_diagnosis) {
        console.log("Handling direct diagnosis format:", aiData);
        
        // Format diagnosis name (replace underscores with spaces and capitalize)
        const rawDiagnosis = aiData.diagnosis || aiData.primary_diagnosis || 'Unknown';
        const formattedDiagnosis = rawDiagnosis.replace(/_/g, ' ')
          .split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ');
        
        return {
          success: true,
          data: {
            diagnosis: formattedDiagnosis,
            confidence: Math.round(aiData.confidence || 0),
            top_predictions: aiData.top_predictions || [],
            differential_diagnoses: aiData.top_3_predictions || aiData.top_predictions || [],
            prescription: {
              medications: ['Consult a doctor for proper medication'],
              treatments: ['Rest and hydration'],
              instructions: 'Follow up with healthcare provider for accurate treatment plan'
            },
            recommendations: [
              'Stay hydrated',
              'Get adequate rest',
              'Monitor symptoms for changes',
              'Contact a healthcare professional if symptoms worsen'
            ],
            ai_model_version: 'MediChain-AI',
            timestamp: new Date().toISOString(),
            severity: 'Moderate',
            urgency: 'normal'
          }
        };
      }
      
      // Handle structured response format
      const analysis = aiData.analysis || {};
      const primaryDiagnosis = analysis.primary_diagnosis || {};
      const recommendations = aiData.recommendations || {};
      
      const transformedData = {
        diagnosis: primaryDiagnosis.condition || aiData.diagnosis || 'Unknown',
        confidence: Math.round((primaryDiagnosis.confidence || aiData.confidence || 0) * 100),
        explanation: primaryDiagnosis.explanation || '',
        prescription: {
          medications: recommendations.medications || ['Based on your symptoms, consult a healthcare provider for appropriate medications'],
          treatments: recommendations.treatments || ['Rest adequately', 'Stay hydrated'],
          instructions: recommendations.lifestyle_advice?.join('; ') || 'Follow up with healthcare provider'
        },
        recommendations: recommendations.lifestyle_advice || [
          'Monitor your symptoms',
          'Contact a healthcare professional if symptoms worsen',
          'Maintain good nutrition and hydration'
        ],
        warnings: recommendations.warnings || [],
        differential_diagnoses: analysis.differential_diagnoses || aiData.top_3_predictions || [],
        ai_model_version: 'MediChain-AI',
        timestamp: aiData.timestamp || new Date().toISOString(),
        medical_disclaimer: aiData.medical_disclaimer || 'This AI diagnosis is for informational purposes only and should not replace professional medical advice.',
        severity: aiData.next_steps?.urgency_level || 'Moderate',
        urgency: aiData.next_steps?.immediate_actions ? 'high' : 'normal'
      };
      
      return {
        success: true,
        data: transformedData
      };
    } catch (error) {
      console.error('AI Diagnosis Error:', error);
      
      if (error.isNetworkError) {
        return {
          success: false,
          error: 'AI server is not available. Please ensure the AI diagnosis server is running on port 5001.',
          isNetworkError: true
        };
      }
      
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get AI diagnosis',
        details: error.response?.data
      };
    }
  },

  /**
   * Provide feedback on a diagnosis
   * @param {Object} feedbackData - The feedback data
   * @returns {Promise<Object>} Feedback response
   */
  provideFeedback: async (feedbackData) => {
    try {
      const response = await api.post('/submit-feedback', feedbackData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('AI Feedback Error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to submit feedback'
      };
    }
  },

  /**
   * Get model information and statistics
   * @returns {Promise<Object>} Model info response
   */
  getModelInfo: async () => {
    try {
      const response = await api.get('/learning-stats');
      const data = response.data;
      
      // Transform the response to match frontend expectations
      const modelInfo = data.model_info || {};
      
      return {
        success: true,
        data: {
          version: modelInfo.name || 'MediChain-AI',
          accuracy: modelInfo.accuracy || '87.5',
          training_samples: modelInfo.total_features || 'N/A',
          last_updated: modelInfo.last_trained || 'Unknown',
          supported_conditions: modelInfo.supported_conditions || 'N/A'
        }
      };
    } catch (error) {
      console.error('AI Model Info Error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to get model information'
      };
    }
  },

  /**
   * Health check for the AI service
   * @returns {Promise<Object>} Health status
   */
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return {
        success: true,
        data: response.data,
        status: 'connected'
      };
    } catch (error) {
      return {
        success: false,
        error: 'AI service unavailable',
        status: 'disconnected'
      };
    }
  },

  /**
   * Start a conversational AI diagnosis session
   * @param {Object} data - Initial symptoms data
   * @returns {Promise<Object>} Conversation response
   */
  startConversation: async (data) => {
    try {
      console.log("Starting AI conversation:", data);
      const response = await axios.post('http://localhost:5000/api/ai/start-conversation', data);
      console.log("Conversation started:", response.data);
      return response.data;
    } catch (error) {
      console.error('Error starting conversation:', error);
      if (error.isNetworkError) {
        throw new Error('AI server is not running. Please start the AI service.');
      }
      throw new Error(error.response?.data?.error || 'Failed to start conversation');
    }
  },

  /**
   * Continue the conversational AI diagnosis
   * @param {Object} data - User response data
   * @returns {Promise<Object>} Conversation response
   */
  continueConversation: async (data) => {
    try {
      console.log("Continuing AI conversation:", data);
      const response = await axios.post('http://localhost:5000/api/ai/continue-conversation', data);
      console.log("Conversation continued:", response.data);
      return response.data;
    } catch (error) {
      console.error('Error continuing conversation:', error);
      if (error.isNetworkError) {
        throw new Error('AI server is not running. Please start the AI service.');
      }
      throw new Error(error.response?.data?.error || 'Failed to continue conversation');
    }
  }
};

export default aiService;

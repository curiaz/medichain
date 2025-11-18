/**
 * Login Debugging Utility
 * Helps diagnose login issues
 */

export const debugLogin = {
  /**
   * Log current API configuration
   */
  logApiConfig() {
    const isLocalhost = typeof window !== 'undefined' && (
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname === ''
    );
    
    const config = {
      NODE_ENV: process.env.NODE_ENV,
      REACT_APP_API_URL: process.env.REACT_APP_API_URL,
      windowLocation: typeof window !== 'undefined' ? window.location.origin : 'N/A',
      hostname: typeof window !== 'undefined' ? window.location.hostname : 'N/A',
      isLocalhost: isLocalhost,
      isProduction: process.env.NODE_ENV === 'production',
      isDevelopment: process.env.NODE_ENV === 'development',
      detectedBackend: isLocalhost ? 'http://localhost:5000' : 'https://medichainn.onrender.com'
    };
    
    console.log('🔍 API Configuration:', config);
    return config;
  },

  /**
   * Test backend connectivity
   */
  async testBackendConnection() {
    try {
      // Detect localhost
      const isLocalhost = typeof window !== 'undefined' && (
        window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname === ''
      );
      
      const API_URL = process.env.REACT_APP_API_URL || 
        (isLocalhost || process.env.NODE_ENV === 'development'
          ? 'http://localhost:5000' 
          : 'https://medichainn.onrender.com');
      
      console.log('🔍 Testing backend connection to:', API_URL);
      
      const response = await fetch(`${API_URL}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json().catch(() => ({}));
      
      console.log('✅ Backend health check:', {
        status: response.status,
        statusText: response.statusText,
        data: data
      });
      
      return {
        success: response.ok,
        status: response.status,
        data: data
      };
    } catch (error) {
      console.error('❌ Backend connection test failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Test CORS preflight
   */
  async testCorsPreflight() {
    try {
      // Detect localhost
      const isLocalhost = typeof window !== 'undefined' && (
        window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname === ''
      );
      
      const API_URL = process.env.REACT_APP_API_URL || 
        (isLocalhost || process.env.NODE_ENV === 'development'
          ? 'http://localhost:5000' 
          : 'https://medichainn.onrender.com');
      
      console.log('🔍 Testing CORS preflight to:', `${API_URL}/api/auth/login`);
      
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'OPTIONS',
        headers: {
          'Origin': window.location.origin,
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
      });
      
      const corsHeaders = {
        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
      };
      
      console.log('✅ CORS preflight response:', {
        status: response.status,
        statusText: response.statusText,
        headers: corsHeaders
      });
      
      return {
        success: response.ok,
        status: response.status,
        headers: corsHeaders
      };
    } catch (error) {
      console.error('❌ CORS preflight test failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Run all diagnostic tests
   */
  async runDiagnostics() {
    console.log('🔍 Starting login diagnostics...');
    console.log('='.repeat(60));
    
    const apiConfig = this.logApiConfig();
    const backendTest = await this.testBackendConnection();
    const corsTest = await this.testCorsPreflight();
    
    console.log('='.repeat(60));
    console.log('📊 Diagnostic Summary:');
    console.log('API Config:', apiConfig);
    console.log('Backend Connection:', backendTest);
    console.log('CORS Preflight:', corsTest);
    console.log('='.repeat(60));
    
    return {
      apiConfig,
      backendTest,
      corsTest
    };
  }
};

// Make it available globally for debugging
if (typeof window !== 'undefined') {
  window.debugLogin = debugLogin;
}


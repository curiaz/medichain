import React, { useState, useEffect } from 'react';
import { sendPasswordResetEmail, onAuthStateChanged } from 'firebase/auth';
import { auth } from '../config/firebase';

const FirebaseDebugTest = () => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('');
  const [logs, setLogs] = useState([]);
  const [firebaseUser, setFirebaseUser] = useState(null);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
    console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
  };

  useEffect(() => {
    // Monitor Firebase auth state
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setFirebaseUser(user);
      if (user) {
        addLog(`Firebase user detected: ${user.email}`, 'success');
      } else {
        addLog('No Firebase user currently signed in', 'info');
      }
    });

    // Test Firebase configuration
    addLog('Firebase configuration check:', 'info');
    addLog(`Project ID: ${auth.app.options.projectId}`, 'info');
    addLog(`Auth Domain: ${auth.app.options.authDomain}`, 'info');
    addLog(`API Key: ${auth.app.options.apiKey ? 'Present' : 'Missing'}`, auth.app.options.apiKey ? 'success' : 'error');

    return () => unsubscribe();
  }, []);

  const testPasswordReset = async () => {
    if (!email) {
      addLog('Please enter an email address', 'error');
      return;
    }

    setStatus('Testing password reset...');
    addLog(`Starting password reset test for: ${email}`, 'info');

    try {
      // Test 1: Check if Firebase is properly initialized
      addLog('Test 1: Checking Firebase initialization...', 'info');
      if (!auth || !auth.app) {
        throw new Error('Firebase Auth not properly initialized');
      }
      addLog('✅ Firebase Auth is initialized', 'success');

      // Test 2: Attempt password reset
      addLog('Test 2: Sending password reset email...', 'info');
      await sendPasswordResetEmail(auth, email, {
        url: window.location.origin + '/login', // Redirect URL after reset
        handleCodeInApp: false
      });
      
      addLog('✅ Password reset email sent successfully!', 'success');
      addLog('📧 Check your inbox (and spam folder) for the reset email', 'info');
      setStatus('Password reset email sent! Check your inbox.');

    } catch (error) {
      addLog(`❌ Password reset failed: ${error.code}`, 'error');
      addLog(`Error message: ${error.message}`, 'error');
      
      // Provide specific debugging info
      switch (error.code) {
        case 'auth/user-not-found':
          addLog('💡 This email is not registered. Try creating an account first.', 'info');
          break;
        case 'auth/invalid-email':
          addLog('💡 The email format is invalid. Please check the email address.', 'info');
          break;
        case 'auth/too-many-requests':
          addLog('💡 Too many attempts. Wait a few minutes and try again.', 'info');
          break;
        case 'auth/network-request-failed':
          addLog('💡 Network error. Check your internet connection.', 'info');
          break;
        default:
          addLog(`💡 Unexpected error code: ${error.code}`, 'info');
      }
      
      setStatus(`Error: ${error.message}`);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div style={{ 
      maxWidth: '800px', 
      margin: '20px auto', 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif' 
    }}>
      <h1>🔧 Firebase Password Reset Debug Tool</h1>
      
      <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '4px' }}>
        <h3>📊 Firebase Status</h3>
        <p><strong>Project ID:</strong> {auth?.app?.options?.projectId || 'Not loaded'}</p>
        <p><strong>Auth Domain:</strong> {auth?.app?.options?.authDomain || 'Not loaded'}</p>
        <p><strong>Current User:</strong> {firebaseUser ? firebaseUser.email : 'None'}</p>
        <p><strong>Auth State:</strong> {auth ? 'Initialized' : 'Not initialized'}</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          Test Email Address:
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter email to test password reset"
          style={{
            width: '100%',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '16px',
            marginBottom: '10px'
          }}
        />
        <button
          onClick={testPasswordReset}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px',
            marginRight: '10px'
          }}
        >
          🧪 Test Password Reset
        </button>
        <button
          onClick={clearLogs}
          style={{
            backgroundColor: '#6c757d',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          🗑️ Clear Logs
        </button>
      </div>

      {status && (
        <div style={{
          padding: '10px',
          backgroundColor: status.includes('Error') ? '#f8d7da' : '#d4edda',
          color: status.includes('Error') ? '#721c24' : '#155724',
          border: `1px solid ${status.includes('Error') ? '#f5c6cb' : '#c3e6cb'}`,
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          {status}
        </div>
      )}

      <div>
        <h3>📝 Debug Logs</h3>
        <div style={{
          backgroundColor: '#000',
          color: '#00ff00',
          padding: '10px',
          borderRadius: '4px',
          fontFamily: 'monospace',
          height: '300px',
          overflowY: 'scroll',
          fontSize: '14px'
        }}>
          {logs.map((log, index) => (
            <div key={index} style={{ 
              color: log.type === 'error' ? '#ff6b6b' : 
                     log.type === 'success' ? '#51cf66' : 
                     log.type === 'info' ? '#74c0fc' : '#00ff00',
              marginBottom: '2px'
            }}>
              [{log.timestamp}] {log.message}
            </div>
          ))}
          {logs.length === 0 && (
            <div style={{ color: '#888' }}>No logs yet. Click "Test Password Reset" to start debugging.</div>
          )}
        </div>
      </div>

      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
        <h4>💡 Debugging Tips:</h4>
        <ul>
          <li>Make sure the email address exists in your Firebase Authentication users</li>
          <li>Check the browser's developer console for additional errors</li>
          <li>Verify your Firebase project settings and API keys</li>
          <li>Check if email/password authentication is enabled in Firebase Console</li>
          <li>Look in your spam folder for the reset email</li>
          <li>Firebase reset emails can take a few minutes to arrive</li>
        </ul>
      </div>
    </div>
  );
};

export default FirebaseDebugTest;
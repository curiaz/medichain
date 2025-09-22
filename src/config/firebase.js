// Firebase Configuration for MediChain
import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';

// Your Firebase config from Firebase Console
// Replace these values with your actual Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyDij3Q998OYB3PkSQpzIkki3wFzSF_OUcM", // You'll need to get this from Firebase Console
  authDomain: "medichain-8773b.firebaseapp.com",
  projectId: "medichain-8773b",
  storageBucket: "medichain-8773b.firebasestorage.app",
  messagingSenderId: "236046401113",
  appId: "1:236046401113:web:a27b992e14f464fac3fb48" // You'll need to get this from Firebase Console
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Cloud Firestore and get a reference to the service
export const db = getFirestore(app);

// Development mode - connect to emulators if needed
if (process.env.NODE_ENV === 'development' && process.env.REACT_APP_USE_FIREBASE_EMULATOR === 'true') {
  try {
    connectAuthEmulator(auth, "http://localhost:9099");
    connectFirestoreEmulator(db, 'localhost', 8080);
  } catch (error) {
    console.log('Firebase emulators already connected or not available');
  }
}

export default app;

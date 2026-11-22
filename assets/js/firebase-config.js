// Firebase Configuration
// Replace these values with your Firebase project config from:
// Firebase Console > Project Settings > Your Apps > Web App > Config

// Project chundu-portfolio-auth (2026-11-22). Replaced authforportpolio, whose
// Auth stayed stuck in PROJECT_SOFT_DELETED after the project was restored.
const firebaseConfig = {
    apiKey: "AIzaSyDo3YehhFpjr7GzE_6ldw9VOKomowQlrUY",
    authDomain: "chundu-portfolio-auth.firebaseapp.com",
    projectId: "chundu-portfolio-auth",
    storageBucket: "chundu-portfolio-auth.firebasestorage.app",
    messagingSenderId: "244406289620",
    appId: "1:244406289620:web:dd1dd34d8e6ebc76ba2741"
};

// Check if Firebase is configured with real credentials
const isFirebaseConfigured = firebaseConfig.apiKey &&
    firebaseConfig.apiKey !== "YOUR_API_KEY" &&
    !firebaseConfig.apiKey.includes("YOUR_");

let auth = null;
let db = null;

if (isFirebaseConfigured && typeof firebase !== 'undefined') {
    try {
        // Initialize Firebase only if properly configured
        firebase.initializeApp(firebaseConfig);
        auth = firebase.auth();
        db = firebase.firestore();
        console.log('Firebase initialized successfully');
    } catch (error) {
        console.warn('Firebase initialization failed:', error.message);
    }
} else {
    console.log('Firebase not configured - authentication features disabled');
}

// Export for use in other files
window.firebaseAuth = auth;
window.firebaseDb = db;
window.isFirebaseConfigured = isFirebaseConfigured;

// Firebase Configuration
// Replace these values with your Firebase project config from:
// Firebase Console > Project Settings > Your Apps > Web App > Config

const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
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

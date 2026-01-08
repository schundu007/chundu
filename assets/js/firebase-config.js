// Firebase Configuration
// Replace these values with your Firebase project config from:
// Firebase Console > Project Settings > Your Apps > Web App > Config

const firebaseConfig = {
    apiKey: "AIzaSyDnKjY9l5L8ph0Fd_Ec0IT1lh6wljMKo0Q",
    authDomain: "authforportpolio.firebaseapp.com",
    projectId: "authforportpolio",
    storageBucket: "authforportpolio.firebasestorage.app",
    messagingSenderId: "110343952224",
    appId: "1:110343952224:web:151e4ae223c3dacfb67005",
    measurementId: "G-KKJG33GF2X"
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

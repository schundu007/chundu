// Authentication Module
// Handles social login, logout, and auth state management

(function() {
    'use strict';

    // Check if Firebase is configured
    if (!window.isFirebaseConfigured) {
        console.log('Auth module: Firebase not configured, authentication disabled');
        // Provide stub functions to prevent errors
        window.showLoginModal = function() {
            console.log('Authentication is not configured');
        };
        window.closeLoginModal = function() {};
        window.signInWithGoogle = function() { console.log('Auth not configured'); };
        window.signInWithFacebook = function() { console.log('Auth not configured'); };
        window.signInWithGitHub = function() { console.log('Auth not configured'); };
        window.signOutUser = function() {};
        window.isAuthenticated = function() { return false; };
        window.getCurrentUser = function() { return null; };
        window.requireAuth = function() { return false; };
        window.toggleUserDropdown = function() {};

        // Hide sign-in buttons when Firebase is not configured
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.nav-auth').forEach(function(el) {
                el.style.display = 'none';
            });
        });
        return;
    }

    // Auth providers
    const googleProvider = new firebase.auth.GoogleAuthProvider();
    const facebookProvider = new firebase.auth.FacebookAuthProvider();
    const githubProvider = new firebase.auth.GithubAuthProvider();

    // Current user state
    let currentUser = null;

    // Login modal HTML
    const loginModalHTML = `
        <div id="login-modal" class="modal-overlay">
            <div class="modal">
                <button class="modal-close" onclick="closeLoginModal()">&times;</button>
                <div class="modal-header">
                    <h2>Welcome</h2>
                    <p id="login-message">Sign in to access all features</p>
                </div>
                <div class="social-login-btns">
                    <button class="social-login-btn google" onclick="signInWithGoogle()">
                        <i class="fab fa-google"></i>
                        Continue with Google
                    </button>
                    <button class="social-login-btn facebook" onclick="signInWithFacebook()">
                        <i class="fab fa-facebook-f"></i>
                        Continue with Facebook
                    </button>
                    <button class="social-login-btn github" onclick="signInWithGitHub()">
                        <i class="fab fa-github"></i>
                        Continue with GitHub
                    </button>
                </div>
                <p style="text-align: center; color: var(--text-muted); font-size: 0.75rem; margin-top: 1.5rem;">
                    By signing in, you agree to our Terms of Service and Privacy Policy
                </p>
            </div>
        </div>
    `;

    // User dropdown HTML
    function getUserDropdownHTML(user) {
        return `
            <div class="nav-user-dropdown" id="user-dropdown">
                <div class="dropdown-header">
                    <img src="${user.photoURL || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(user.displayName || 'User')}" alt="Avatar" class="dropdown-avatar">
                    <div class="dropdown-info">
                        <span class="dropdown-name">${user.displayName || 'User'}</span>
                        <span class="dropdown-email">${user.email}</span>
                    </div>
                </div>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item" onclick="signOutUser()">
                    <i class="fas fa-sign-out-alt"></i>
                    Sign Out
                </button>
            </div>
        `;
    }

    // Initialize auth UI
    function initAuthUI() {
        // Add login modal to body if not exists
        if (!document.getElementById('login-modal')) {
            document.body.insertAdjacentHTML('beforeend', loginModalHTML);
        }

        // Add dropdown styles
        if (!document.getElementById('auth-styles')) {
            const styles = document.createElement('style');
            styles.id = 'auth-styles';
            styles.textContent = `
                .nav-user-dropdown {
                    position: absolute;
                    top: calc(100% + 8px);
                    right: 0;
                    background: var(--bg-secondary);
                    border: 1px solid var(--glass-border);
                    border-radius: var(--radius-lg);
                    min-width: 240px;
                    padding: 0.5rem;
                    box-shadow: var(--shadow-xl);
                    opacity: 0;
                    visibility: hidden;
                    transform: translateY(-10px);
                    transition: var(--transition-normal);
                    z-index: 1001;
                }
                .nav-user-dropdown.active {
                    opacity: 1;
                    visibility: visible;
                    transform: translateY(0);
                }
                .dropdown-header {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 0.75rem;
                }
                .dropdown-avatar {
                    width: 44px;
                    height: 44px;
                    border-radius: 50%;
                    border: 2px solid var(--accent-blue);
                }
                .dropdown-info {
                    display: flex;
                    flex-direction: column;
                }
                .dropdown-name {
                    font-weight: 600;
                    font-size: 0.9rem;
                    color: var(--text-primary);
                }
                .dropdown-email {
                    font-size: 0.75rem;
                    color: var(--text-muted);
                }
                .dropdown-divider {
                    height: 1px;
                    background: var(--glass-border);
                    margin: 0.5rem 0;
                }
                .dropdown-item {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    width: 100%;
                    padding: 0.75rem;
                    background: none;
                    border: none;
                    color: var(--text-secondary);
                    font-size: 0.875rem;
                    cursor: pointer;
                    border-radius: var(--radius-sm);
                    transition: var(--transition-fast);
                }
                .dropdown-item:hover {
                    background: var(--glass-bg);
                    color: var(--accent-blue);
                }
                .dropdown-item i {
                    width: 20px;
                    text-align: center;
                }
                .nav-user-wrapper {
                    position: relative;
                }
            `;
            document.head.appendChild(styles);
        }
    }

    // Update navigation for authenticated/unauthenticated state
    function updateNavForAuth(user) {
        const navAuth = document.querySelector('.nav-auth');
        if (!navAuth) return;

        if (user) {
            navAuth.innerHTML = `
                <div class="nav-user-wrapper">
                    <div class="nav-user" onclick="toggleUserDropdown()">
                        <img src="${user.photoURL || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(user.displayName || 'User')}" alt="Avatar" class="nav-user-avatar">
                    </div>
                    ${getUserDropdownHTML(user)}
                </div>
            `;
        } else {
            navAuth.innerHTML = `
                <button class="btn-signin" onclick="showLoginModal()">Sign In</button>
            `;
        }
    }

    // Show login modal
    window.showLoginModal = function(message) {
        initAuthUI();
        const modal = document.getElementById('login-modal');
        const messageEl = document.getElementById('login-message');
        if (message && messageEl) {
            messageEl.textContent = message;
        }
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    // Close login modal
    window.closeLoginModal = function() {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    // Toggle user dropdown
    window.toggleUserDropdown = function() {
        const dropdown = document.getElementById('user-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('active');
        }
    };

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('user-dropdown');
        const navUser = document.querySelector('.nav-user');
        if (dropdown && navUser && !navUser.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });

    // Sign in with Google
    window.signInWithGoogle = async function() {
        try {
            await auth.signInWithPopup(googleProvider);
            closeLoginModal();
        } catch (error) {
            console.error('Google sign-in error:', error);
            alert('Sign in failed: ' + error.message);
        }
    };

    // Sign in with Facebook
    window.signInWithFacebook = async function() {
        try {
            await auth.signInWithPopup(facebookProvider);
            closeLoginModal();
        } catch (error) {
            console.error('Facebook sign-in error:', error);
            alert('Sign in failed: ' + error.message);
        }
    };

    // Sign in with GitHub
    window.signInWithGitHub = async function() {
        try {
            await auth.signInWithPopup(githubProvider);
            closeLoginModal();
        } catch (error) {
            console.error('GitHub sign-in error:', error);
            alert('Sign in failed: ' + error.message);
        }
    };

    // Sign out
    window.signOutUser = async function() {
        try {
            await auth.signOut();
            const dropdown = document.getElementById('user-dropdown');
            if (dropdown) dropdown.classList.remove('active');
        } catch (error) {
            console.error('Sign out error:', error);
        }
    };

    // Check if user is authenticated
    window.isAuthenticated = function() {
        return !!currentUser;
    };

    // Get current user
    window.getCurrentUser = function() {
        return currentUser;
    };

    // Require auth (show login modal if not authenticated)
    window.requireAuth = function(message) {
        if (!currentUser) {
            showLoginModal(message || 'Please sign in to continue');
            return false;
        }
        return true;
    };

    // Auth state listener
    auth.onAuthStateChanged(function(user) {
        currentUser = user;
        updateNavForAuth(user);

        // Dispatch custom event for other scripts to listen to
        window.dispatchEvent(new CustomEvent('authStateChanged', { detail: { user } }));

        // Update any auth-required elements
        document.querySelectorAll('.auth-required').forEach(el => {
            el.style.display = user ? '' : 'none';
        });

        document.querySelectorAll('.auth-hidden').forEach(el => {
            el.style.display = user ? 'none' : '';
        });
    });

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAuthUI);
    } else {
        initAuthUI();
    }

})();

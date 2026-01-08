// Comments Module
// Handles loading, posting, and managing comments using Firestore

(function() {
    'use strict';

    // Get page ID from URL path
    function getPageId() {
        const path = window.location.pathname;
        // Remove leading/trailing slashes and replace remaining slashes with dashes
        return path.replace(/^\/|\/$/g, '').replace(/\//g, '-') || 'home';
    }

    // Format timestamp
    function formatTime(timestamp) {
        if (!timestamp) return 'Just now';
        const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        // Less than a minute
        if (diff < 60000) return 'Just now';
        // Less than an hour
        if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
        // Less than a day
        if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
        // Less than a week
        if (diff < 604800000) return Math.floor(diff / 86400000) + 'd ago';
        // Default to date
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }

    // Generate avatar URL
    function getAvatarUrl(user) {
        if (user.photoURL) return user.photoURL;
        const name = user.displayName || user.email || 'User';
        return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3b82f6&color=fff`;
    }

    // Create comment HTML
    function createCommentHTML(comment, canDelete) {
        return `
            <div class="comment-item" data-id="${comment.id}">
                <img src="${comment.userPhoto || getAvatarUrl({ displayName: comment.userName })}" alt="${comment.userName}" class="comment-avatar">
                <div class="comment-content">
                    <div class="comment-meta">
                        <span class="comment-author">${comment.userName}</span>
                        <span class="comment-time">${formatTime(comment.createdAt)}</span>
                        ${canDelete ? `<button class="comment-delete" onclick="deleteComment('${comment.id}')" title="Delete comment"><i class="fas fa-trash"></i></button>` : ''}
                    </div>
                    <p class="comment-text">${escapeHtml(comment.text)}</p>
                </div>
            </div>
        `;
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Render comments section
    function renderCommentsSection(container, user) {
        const pageId = getPageId();

        container.innerHTML = `
            <div class="comments-section">
                <div class="comments-header">
                    <h3><i class="fas fa-comments" style="margin-right: 0.5rem; color: var(--accent-blue);"></i>Comments</h3>
                    <span class="comment-count" id="comment-count">0 comments</span>
                </div>

                <div id="comment-form-area">
                    ${user ? `
                        <div class="comment-form">
                            <div class="comment-input-wrapper">
                                <img src="${getAvatarUrl(user)}" alt="Your avatar" class="comment-avatar">
                                <textarea class="comment-input" id="comment-input" placeholder="Share your thoughts..." rows="3"></textarea>
                            </div>
                            <div class="comment-actions">
                                <button class="btn btn-primary" onclick="postComment()">
                                    <i class="fas fa-paper-plane"></i>
                                    Post Comment
                                </button>
                            </div>
                        </div>
                    ` : `
                        <div class="login-prompt">
                            <p>Sign in to join the conversation</p>
                            <button class="btn btn-primary" onclick="showLoginModal('Sign in to post a comment')">
                                <i class="fas fa-sign-in-alt"></i>
                                Sign In
                            </button>
                        </div>
                    `}
                </div>

                <div class="comment-list" id="comment-list">
                    <div class="loading-comments" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                        <i class="fas fa-spinner fa-spin" style="margin-right: 0.5rem;"></i>
                        Loading comments...
                    </div>
                </div>
            </div>
        `;

        // Load comments
        loadComments(pageId);
    }

    // Load comments from Firestore
    async function loadComments(pageId) {
        const commentList = document.getElementById('comment-list');
        const commentCount = document.getElementById('comment-count');
        if (!commentList) return;

        try {
            // Set up real-time listener
            db.collection('comments').doc(pageId).collection('messages')
                .orderBy('createdAt', 'desc')
                .onSnapshot(snapshot => {
                    const comments = [];
                    snapshot.forEach(doc => {
                        comments.push({ id: doc.id, ...doc.data() });
                    });

                    // Update count
                    if (commentCount) {
                        commentCount.textContent = `${comments.length} comment${comments.length !== 1 ? 's' : ''}`;
                    }

                    // Render comments
                    if (comments.length === 0) {
                        commentList.innerHTML = `
                            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                                <i class="fas fa-comments" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                                <p>No comments yet. Be the first to share your thoughts!</p>
                            </div>
                        `;
                    } else {
                        const currentUser = window.getCurrentUser ? window.getCurrentUser() : null;
                        commentList.innerHTML = comments.map(comment =>
                            createCommentHTML(comment, currentUser && currentUser.uid === comment.userId)
                        ).join('');
                    }
                }, error => {
                    console.error('Error loading comments:', error);
                    commentList.innerHTML = `
                        <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
                            <p>Unable to load comments. Please try again later.</p>
                        </div>
                    `;
                });
        } catch (error) {
            console.error('Error setting up comments listener:', error);
        }
    }

    // Post a new comment
    window.postComment = async function() {
        const input = document.getElementById('comment-input');
        if (!input) return;

        const text = input.value.trim();
        if (!text) {
            alert('Please enter a comment');
            return;
        }

        const user = window.getCurrentUser ? window.getCurrentUser() : null;
        if (!user) {
            window.showLoginModal('Sign in to post a comment');
            return;
        }

        const pageId = getPageId();

        try {
            // Disable button while posting
            const btn = input.closest('.comment-form').querySelector('button');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';

            await db.collection('comments').doc(pageId).collection('messages').add({
                userId: user.uid,
                userName: user.displayName || 'Anonymous',
                userPhoto: user.photoURL || null,
                text: text,
                createdAt: firebase.firestore.FieldValue.serverTimestamp()
            });

            // Clear input
            input.value = '';
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane"></i> Post Comment';

        } catch (error) {
            console.error('Error posting comment:', error);
            alert('Failed to post comment. Please try again.');
            const btn = input.closest('.comment-form').querySelector('button');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane"></i> Post Comment';
        }
    };

    // Delete a comment
    window.deleteComment = async function(commentId) {
        if (!confirm('Are you sure you want to delete this comment?')) return;

        const pageId = getPageId();

        try {
            await db.collection('comments').doc(pageId).collection('messages').doc(commentId).delete();
        } catch (error) {
            console.error('Error deleting comment:', error);
            alert('Failed to delete comment. Please try again.');
        }
    };

    // Initialize comments
    window.initComments = function(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Wait for auth state
        const user = window.getCurrentUser ? window.getCurrentUser() : null;
        renderCommentsSection(container, user);

        // Update when auth state changes
        window.addEventListener('authStateChanged', function(e) {
            renderCommentsSection(container, e.detail.user);
        });
    };

    // Auto-initialize if container exists
    document.addEventListener('DOMContentLoaded', function() {
        const container = document.getElementById('comments-container');
        if (container) {
            // Small delay to ensure auth is initialized
            setTimeout(() => window.initComments('comments-container'), 500);
        }
    });

})();

document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".menu-toggle").addEventListener("click", function () {
        document.querySelector(".dropdown-menu").classList.toggle("show");
    });

    // Analytics tracking for interactions
    if (typeof gtag !== 'undefined') {
        // Track navigation clicks
        document.querySelectorAll('nav a').forEach(function(link) {
            link.addEventListener('click', function() {
                gtag('event', 'page_view', {
                    page_title: this.textContent,
                    page_location: this.href
                });
            });
        });

        // Track video interactions
        document.querySelectorAll('video').forEach(function(video) {
            video.addEventListener('play', function() {
                gtag('event', 'video_play', {
                    video_title: this.getAttribute('data-title') || 'Unknown Video'
                });
            });
            
            video.addEventListener('ended', function() {
                gtag('event', 'video_complete', {
                    video_title: this.getAttribute('data-title') || 'Unknown Video'
                });
            });
        });

        // Track contact form submissions
        const contactForm = document.querySelector('#contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', function() {
                gtag('event', 'form_submit', {
                    form_name: 'contact_form'
                });
            });
        }

        // Track external link clicks
        document.querySelectorAll('a[href^="http"]').forEach(function(link) {
            link.addEventListener('click', function() {
                gtag('event', 'click', {
                    event_category: 'outbound',
                    event_label: this.href
                });
            });
        });
    }
});


// Professional Ambient Background — smooth gradient orbs + subtle grid
class AmbientBackground {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.orbs = [];
        this.mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
        this.time = 0;
        this.dpr = Math.min(window.devicePixelRatio || 1, 2);

        this.init();
        this.animate();

        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', (e) => {
            this.mouse.targetX = e.clientX;
            this.mouse.targetY = e.clientY;
        });
    }

    init() {
        this.resize();
        this.createOrbs();
    }

    resize() {
        this.canvas.width = window.innerWidth * this.dpr;
        this.canvas.height = window.innerHeight * this.dpr;
        this.canvas.style.width = window.innerWidth + 'px';
        this.canvas.style.height = window.innerHeight + 'px';
        this.ctx.scale(this.dpr, this.dpr);
        this.width = window.innerWidth;
        this.height = window.innerHeight;
    }

    isLight() {
        return document.documentElement.getAttribute('data-theme') === 'light';
    }

    createOrbs() {
        const isMobile = window.innerWidth < 768;
        this.orbs = [];

        // Large soft gradient orbs — lime/green tones (Nebius-inspired)
        const orbConfigs = isMobile ? [
            { x: 0.25, y: 0.2, r: 220, color: [180, 220, 50], speed: 0.0003 },
            { x: 0.75, y: 0.6, r: 180, color: [120, 180, 40], speed: 0.0004 },
            { x: 0.5, y: 0.85, r: 200, color: [160, 200, 60], speed: 0.00035 },
        ] : [
            { x: 0.2, y: 0.15, r: 400, color: [180, 220, 50], speed: 0.0002, phase: 0 },
            { x: 0.8, y: 0.2, r: 350, color: [140, 200, 40], speed: 0.00025, phase: 1.5 },
            { x: 0.15, y: 0.7, r: 320, color: [160, 210, 55], speed: 0.00022, phase: 3 },
            { x: 0.75, y: 0.75, r: 380, color: [120, 180, 60], speed: 0.00018, phase: 4.5 },
            { x: 0.5, y: 0.45, r: 300, color: [200, 230, 70], speed: 0.0003, phase: 2.2 },
        ];

        orbConfigs.forEach(cfg => {
            this.orbs.push({
                baseX: cfg.x * this.width,
                baseY: cfg.y * this.height,
                x: cfg.x * this.width,
                y: cfg.y * this.height,
                radius: cfg.r,
                color: cfg.color,
                speed: cfg.speed,
                phase: cfg.phase || Math.random() * Math.PI * 2,
                driftX: 30 + Math.random() * 50,
                driftY: 20 + Math.random() * 40,
            });
        });
    }

    drawGrid() {
        const light = this.isLight();
        const opacity = light ? 0.035 : 0.04;
        const gridSize = 80;

        this.ctx.strokeStyle = light
            ? `rgba(148, 163, 184, ${opacity})`
            : `rgba(148, 163, 184, ${opacity})`;
        this.ctx.lineWidth = 0.5;

        // Horizontal lines
        for (let y = 0; y < this.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.width, y);
            this.ctx.stroke();
        }

        // Vertical lines
        for (let x = 0; x < this.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.height);
            this.ctx.stroke();
        }

        // Subtle dot at intersections
        const dotOpacity = light ? 0.05 : 0.06;
        this.ctx.fillStyle = light
            ? `rgba(100, 116, 139, ${dotOpacity})`
            : `rgba(148, 163, 184, ${dotOpacity})`;
        for (let x = 0; x < this.width; x += gridSize) {
            for (let y = 0; y < this.height; y += gridSize) {
                this.ctx.beginPath();
                this.ctx.arc(x, y, 1, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
    }

    drawOrbs() {
        const light = this.isLight();
        const baseOpacity = light ? 0.05 : 0.12;

        this.orbs.forEach(orb => {
            // Slow organic drift using sine waves
            orb.x = orb.baseX + Math.sin(this.time * orb.speed * 1000 + orb.phase) * orb.driftX;
            orb.y = orb.baseY + Math.cos(this.time * orb.speed * 800 + orb.phase * 1.3) * orb.driftY;

            // Subtle mouse parallax — orbs gently shift away from cursor
            const dx = this.mouse.x - orb.x;
            const dy = this.mouse.y - orb.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const maxDist = 600;
            if (dist < maxDist) {
                const force = (1 - dist / maxDist) * 20;
                orb.x -= (dx / dist) * force;
                orb.y -= (dy / dist) * force;
            }

            // Pulsing radius
            const pulse = 1 + Math.sin(this.time * 0.8 + orb.phase) * 0.08;
            const r = orb.radius * pulse;

            // Radial gradient for soft glow
            const gradient = this.ctx.createRadialGradient(orb.x, orb.y, 0, orb.x, orb.y, r);
            const [cr, cg, cb] = orb.color;
            gradient.addColorStop(0, `rgba(${cr}, ${cg}, ${cb}, ${baseOpacity * 1.2})`);
            gradient.addColorStop(0.4, `rgba(${cr}, ${cg}, ${cb}, ${baseOpacity * 0.6})`);
            gradient.addColorStop(1, `rgba(${cr}, ${cg}, ${cb}, 0)`);

            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(orb.x, orb.y, r, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }

    drawTopHighlight() {
        // Subtle bright streak across the top — gives depth
        const light = this.isLight();
        const gradient = this.ctx.createLinearGradient(0, 0, this.width, 0);
        const opacity = light ? 0.04 : 0.06;
        gradient.addColorStop(0, `rgba(180, 220, 50, 0)`);
        gradient.addColorStop(0.3, `rgba(180, 220, 50, ${opacity})`);
        gradient.addColorStop(0.5, `rgba(224, 255, 79, ${opacity * 1.2})`);
        gradient.addColorStop(0.7, `rgba(160, 200, 60, ${opacity})`);
        gradient.addColorStop(1, `rgba(160, 200, 60, 0)`);

        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.width, 2);

        // Soft glow under the line
        const glowGrad = this.ctx.createLinearGradient(0, 0, 0, 120);
        glowGrad.addColorStop(0, `rgba(224, 255, 79, ${opacity * 0.6})`);
        glowGrad.addColorStop(1, 'rgba(224, 255, 79, 0)');
        this.ctx.fillStyle = glowGrad;
        this.ctx.fillRect(0, 0, this.width, 120);
    }

    animate() {
        this.time += 0.016; // ~60fps time step

        // Smooth mouse interpolation
        this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.05;
        this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.05;

        // Reset canvas
        this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Render layers
        this.drawGrid();
        this.drawOrbs();
        this.drawTopHighlight();

        requestAnimationFrame(() => this.animate());
    }

    destroy() {
        // Can be called to stop animation if needed
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('neural-bg');
    if (canvas) {
        new AmbientBackground('neural-bg');
    }
});

// Scroll reveal animation
function initScrollReveal() {
    const reveals = document.querySelectorAll('.reveal');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    reveals.forEach(el => observer.observe(el));
}

document.addEventListener('DOMContentLoaded', initScrollReveal);

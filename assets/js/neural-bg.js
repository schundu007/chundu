// Neural Network Background Animation with Mixed Shapes
class NeuralNetwork {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 180 };
        this.animationId = null;
        this.shapes = ['circle', 'triangle', 'circle', 'diamond', 'circle']; // More circles, fewer others

        this.init();
        this.animate();

        window.addEventListener('resize', () => this.resize());
        window.addEventListener('mousemove', (e) => this.handleMouse(e));
    }

    init() {
        this.resize();
        this.createParticles();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        // Fewer particles - more spread out
        const isMobile = window.innerWidth < 768;
        const divisor = isMobile ? 40000 : 25000; // Reduced density
        const numberOfParticles = Math.floor((this.canvas.width * this.canvas.height) / divisor);
        this.particles = [];

        for (let i = 0; i < numberOfParticles; i++) {
            const shape = this.shapes[Math.floor(Math.random() * this.shapes.length)];
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                size: isMobile ? Math.random() * 4 + 2 : Math.random() * 6 + 3,
                color: this.getRandomColor(),
                shape: shape,
                rotation: Math.random() * Math.PI * 2,
                rotationSpeed: (Math.random() - 0.5) * 0.02,
                pulsePhase: Math.random() * Math.PI * 2,
                elasticity: 0.85 + Math.random() * 0.1
            });
        }
    }

    getRandomColor() {
        const isMobile = window.innerWidth < 768;
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';

        let opacity = isMobile ? (isLight ? 0.5 : 0.4) : (isLight ? 0.7 : 0.6);

        const colors = [
            `rgba(14, 165, 233, ${opacity})`,   // cyan
            `rgba(168, 85, 247, ${opacity})`,   // purple
            `rgba(34, 211, 238, ${opacity})`,   // light cyan
            `rgba(129, 140, 248, ${opacity})`,  // indigo
            `rgba(244, 114, 182, ${opacity * 0.8})`, // pink
            `rgba(52, 211, 153, ${opacity})`,   // emerald
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    handleMouse(e) {
        this.mouse.x = e.clientX;
        this.mouse.y = e.clientY;
    }

    drawCircle(particle, size) {
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, size, 0, Math.PI * 2);
        this.ctx.fill();
    }

    drawTriangle(particle, size) {
        this.ctx.save();
        this.ctx.translate(particle.x, particle.y);
        this.ctx.rotate(particle.rotation);
        this.ctx.beginPath();
        this.ctx.moveTo(0, -size);
        this.ctx.lineTo(size * 0.866, size * 0.5);
        this.ctx.lineTo(-size * 0.866, size * 0.5);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.restore();
    }

    drawDiamond(particle, size) {
        this.ctx.save();
        this.ctx.translate(particle.x, particle.y);
        this.ctx.rotate(particle.rotation);
        this.ctx.beginPath();
        this.ctx.moveTo(0, -size);
        this.ctx.lineTo(size * 0.7, 0);
        this.ctx.lineTo(0, size);
        this.ctx.lineTo(-size * 0.7, 0);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.restore();
    }

    drawParticles() {
        const time = Date.now() * 0.001;

        this.particles.forEach(particle => {
            // Pulsing size effect
            const pulse = 1 + Math.sin(time * 2 + particle.pulsePhase) * 0.15;
            const size = particle.size * pulse;

            this.ctx.fillStyle = particle.color;
            this.ctx.shadowBlur = 8;
            this.ctx.shadowColor = particle.color;

            switch (particle.shape) {
                case 'circle':
                    this.drawCircle(particle, size);
                    break;
                case 'triangle':
                    this.drawTriangle(particle, size);
                    break;
                case 'diamond':
                    this.drawDiamond(particle, size);
                    break;
            }
        });
        this.ctx.shadowBlur = 0;
    }

    drawConnections() {
        const isMobile = window.innerWidth < 768;
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        const maxDistance = isMobile ? 120 : 150;
        const maxOpacity = isMobile ? (isLight ? 0.3 : 0.2) : (isLight ? 0.4 : 0.3);

        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < maxDistance) {
                    const opacity = (1 - distance / maxDistance) * maxOpacity;
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(14, 165, 233, ${opacity})`;
                    this.ctx.lineWidth = isLight ? 0.6 : 0.4;
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }

    updateParticles() {
        this.particles.forEach(particle => {
            // Mouse interaction with elastic bounce
            if (this.mouse.x && this.mouse.y) {
                const dx = particle.x - this.mouse.x;
                const dy = particle.y - this.mouse.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.mouse.radius) {
                    const force = (this.mouse.radius - distance) / this.mouse.radius;
                    // Elastic push away from mouse
                    particle.vx += (dx / distance) * force * 0.03;
                    particle.vy += (dy / distance) * force * 0.03;
                }
            }

            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Update rotation for triangles and diamonds
            particle.rotation += particle.rotationSpeed;

            // Elastic friction (bouncy feel)
            particle.vx *= particle.elasticity;
            particle.vy *= particle.elasticity;

            // Soft return to slower speed
            if (Math.abs(particle.vx) < 0.1) particle.vx += (Math.random() - 0.5) * 0.02;
            if (Math.abs(particle.vy) < 0.1) particle.vy += (Math.random() - 0.5) * 0.02;

            // Elastic boundary bounce
            if (particle.x < 0) {
                particle.x = 0;
                particle.vx *= -particle.elasticity;
            } else if (particle.x > this.canvas.width) {
                particle.x = this.canvas.width;
                particle.vx *= -particle.elasticity;
            }

            if (particle.y < 0) {
                particle.y = 0;
                particle.vy *= -particle.elasticity;
            } else if (particle.y > this.canvas.height) {
                particle.y = this.canvas.height;
                particle.vy *= -particle.elasticity;
            }
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.drawConnections();
        this.drawParticles();
        this.updateParticles();

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    const neuralCanvas = document.getElementById('neural-bg');
    if (neuralCanvas) {
        new NeuralNetwork('neural-bg');
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

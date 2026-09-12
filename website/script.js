// Smooth scrolling to download section
function scrollToDownload() {
    const downloadSection = document.getElementById('download');
    downloadSection.scrollIntoView({ behavior: 'smooth' });
}

// 3D Tilt Effect and Interactive Glow for Bento Cards
document.querySelectorAll('.bento-card').forEach(card => {
    card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Interactive background glow
        card.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.08), rgba(255,255,255,0.02) 50%)`;

        // 3D Tilt (only if it has tilt-card class)
        if (card.classList.contains('tilt-card')) {
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5; // max 5 deg
            const rotateY = ((x - centerX) / centerX) * 5;  // max 5 deg
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        }
    });

    card.addEventListener('mouseleave', () => {
        card.style.background = 'var(--glass-bg)';
        if (card.classList.contains('tilt-card')) {
            card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)`;
        }
    });
});

// Scroll Reveal Animation via Intersection Observer
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
            // Optional: stop observing once revealed
            // revealObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.15
});

document.querySelectorAll('.reveal').forEach(el => {
    revealObserver.observe(el);
});

// --- Custom Cursor Trailer ---
const cursorTrailer = document.getElementById('cursor-trailer');
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let trailerX = mouseX, trailerY = mouseY;

document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

function animateCursor() {
    let distX = mouseX - trailerX;
    let distY = mouseY - trailerY;
    
    // Smooth follow (lerp)
    trailerX += distX * 0.15;
    trailerY += distY * 0.15;
    
    if(cursorTrailer) {
        cursorTrailer.style.transform = `translate(${trailerX}px, ${trailerY}px) translate(-50%, -50%)`;
    }
    requestAnimationFrame(animateCursor);
}
animateCursor();

// --- Interactive Particle Canvas ---
const canvas = document.getElementById('particle-canvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    let w, h;

    function initCanvas() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
        particles = [];
        const numParticles = Math.floor((w * h) / 12000); // Responsive particle count
        for (let i = 0; i < numParticles; i++) {
            particles.push(new Particle());
        }
    }

    class Particle {
        constructor() {
            this.x = Math.random() * w;
            this.y = Math.random() * h;
            this.vx = (Math.random() - 0.5) * 1.5;
            this.vy = (Math.random() - 0.5) * 1.5;
            this.radius = Math.random() * 2 + 1;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > w) this.vx *= -1;
            if (this.y < 0 || this.y > h) this.vy *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0, 240, 255, 0.6)';
            ctx.fill();
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, w, h);
        
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        
        // Connect particles
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 240, 255, ${1 - dist / 120})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
            
            // Connect to mouse
            const mouseDx = particles[i].x - mouseX;
            const mouseDy = particles[i].y - mouseY;
            const mouseDist = Math.sqrt(mouseDx * mouseDx + mouseDy * mouseDy);
            
            if (mouseDist < 180) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(mouseX, mouseY);
                ctx.strokeStyle = `rgba(255, 0, 127, ${1 - mouseDist / 180})`; // Hot pink line to mouse
                ctx.lineWidth = 1.2;
                ctx.stroke();
                
                // Subtle repel
                particles[i].x += mouseDx * 0.015;
                particles[i].y += mouseDy * 0.015;
            }
        }
        
        requestAnimationFrame(animateParticles);
    }

    window.addEventListener('resize', initCanvas);
    initCanvas();
    animateParticles();
}

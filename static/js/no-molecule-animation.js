
/**
 * Nitric Oxide Molecule Animation
 * Provides visual gas particle effects and molecule animations
 */

(function() {
    // Create the global namespace if it doesn't exist
    window.N1O1Loader = window.N1O1Loader || {};
    
    // Gas particle generation
    window.N1O1Loader.generateGasParticles = function() {
        const particles = 25;
        const colors = ['#3b7eb9', '#e05a47', '#6C757D'];
        const container = document.body;
        
        for (let i = 0; i < particles; i++) {
            const particle = document.createElement('div');
            particle.className = 'no-gas-particle';
            
            // Random sizing and positioning
            const size = Math.random() * 8 + 4;
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.backgroundColor = color;
            particle.style.borderRadius = '50%';
            particle.style.position = 'fixed';
            particle.style.pointerEvents = 'none';
            
            // Position near the NO molecule button
            const noButton = document.getElementById('no-molecule-chat-button');
            if (noButton) {
                const rect = noButton.getBoundingClientRect();
                particle.style.right = `${Math.random() * 60 + (rect.right - window.innerWidth + 30)}px`;
                particle.style.bottom = `${Math.random() * 60 + (window.innerHeight - rect.top - 30)}px`;
            } else {
                // Fallback position if button not found
                particle.style.right = `${Math.random() * 60 + 20}px`;
                particle.style.bottom = `${Math.random() * 60 + 20}px`;
            }
            
            particle.style.opacity = Math.random() * 0.7 + 0.3;
            
            // Create animation
            const duration = Math.random() * 2 + 1;
            const direction = Math.random() > 0.5 ? -1 : 1;
            const xMove = direction * (Math.random() * 100 + 50);
            const yMove = direction * (Math.random() * 100 + 50);
            
            particle.style.animation = `gas-particle-float ${duration}s ease-out forwards`;
            particle.style.transform = `translate(0, 0) scale(1)`;
            
            // Add keyframe animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes gas-particle-float {
                    0% {
                        transform: translate(0, 0) scale(0.5);
                        opacity: 0.7;
                    }
                    100% {
                        transform: translate(${xMove}px, ${yMove}px) scale(2);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
            
            // Add particle to document
            container.appendChild(particle);
            
            // Remove after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
                if (style.parentNode) {
                    style.parentNode.removeChild(style);
                }
            }, duration * 1000);
        }
    };
    
    // Pulsating molecule effect
    window.N1O1Loader.startMoleculePulsation = function() {
        const molecule = document.querySelector('.no-molecule-svg');
        if (!molecule) return;
        
        // Create pulsation animation
        setInterval(() => {
            // Subtle random scaling
            const scale = 0.95 + Math.random() * 0.1;
            molecule.style.transform = `scale(${scale})`;
            
            // Randomly adjust opacity of electron clouds
            const clouds = molecule.querySelectorAll('circle:nth-child(4), circle:nth-child(5)');
            clouds.forEach(cloud => {
                cloud.style.opacity = 0.5 + Math.random() * 0.5;
            });
        }, 1500);
    };
    
    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Start molecule pulsation
        window.N1O1Loader.startMoleculePulsation();
        
        // Make the generateGasParticles function available
        console.log("NO gas particle animations initialized");
    });
})();

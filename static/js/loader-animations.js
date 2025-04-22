/**
 * Nitric Oxide Molecule and Cell Biology Loading Animations
 * Author: Dustin Salinas
 * For N1O1 Clinical Trials Platform
 * 
 * This script provides loading animations for the N1O1 Clinical Trials application.
 * It creates a loading overlay with molecular, cellular, and DNA animations.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the loading animations
    initLoadingAnimations();

    // Generate gas particles for NO molecule in chat button
    generateGasParticles();
});

// Initialize loader objects with both uppercase and lowercase versions for compatibility
window.N1O1Loader = window.N1O1Loader || {};
window.n1o1Loader = window.n1o1Loader || {};

function initLoadingAnimations() {
    // Create the loading overlay if it doesn't exist
    if (!document.querySelector('.loading-overlay')) {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';

        const loadingContent = document.createElement('div');
        loadingContent.className = 'loading-content';

        // Create the NO molecule loader
        const moleculeLoader = createNOMoleculeLoader();

        // Create loading message
        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'loading-message';
        loadingMessage.innerHTML = 'Processing Nitric Oxide Dynamics...';

        // Assemble the elements
        loadingContent.appendChild(moleculeLoader);
        loadingContent.appendChild(loadingMessage);
        loadingOverlay.appendChild(loadingContent);

        // Add to body
        document.body.appendChild(loadingOverlay);
    }
}

function createNOMoleculeLoader() {
    const moleculeLoader = document.createElement('div');
    moleculeLoader.className = 'no-molecule-loader';

    const moleculeWrapper = document.createElement('div');
    moleculeWrapper.className = 'no-molecule-wrapper';

    // Create nitrogen atom
    const nitrogen = document.createElement('div');
    nitrogen.className = 'nitrogen';

    // Create oxygen atom
    const oxygen = document.createElement('div');
    oxygen.className = 'oxygen';

    // Create bond
    const bond = document.createElement('div');
    bond.className = 'bond';

    // Assemble the molecule
    moleculeWrapper.appendChild(nitrogen);
    moleculeWrapper.appendChild(oxygen);
    moleculeWrapper.appendChild(bond);
    moleculeLoader.appendChild(moleculeWrapper);

    return moleculeLoader;
}

function generateGasParticles() {
    // Target the NO molecule chat button
    const noMoleculeButton = document.querySelector('.no-molecule-chat-button');

    if (noMoleculeButton) {
        // Create gas particles
        for (let i = 0; i < 8; i++) {
            setTimeout(() => {
                createGasParticle(noMoleculeButton);
            }, i * 500);
        }

        // Continuously create gas particles
        setInterval(() => {
            for (let i = 0; i < 3; i++) {
                setTimeout(() => {
                    createGasParticle(noMoleculeButton);
                }, i * 300);
            }
        }, 4000);
    }
}

function createGasParticle(parent) {
    const particle = document.createElement('div');
    particle.className = 'gas-particle';

    // Random properties for the particle
    const size = Math.random() * 6 + 4;
    const tx = (Math.random() - 0.5) * 120;
    const ty = (Math.random() - 0.5) * 120;
    const duration = Math.random() * 3 + 2;
    const isOxygen = Math.random() > 0.5;

    // Set styles
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    particle.style.backgroundColor = isOxygen ? 'rgba(224, 90, 71, 0.8)' : 'rgba(59, 126, 185, 0.8)';
    particle.style.left = `${Math.random() * 50 + 25}%`;
    particle.style.top = `${Math.random() * 50 + 25}%`;
    particle.style.setProperty('--tx', `${tx}px`);
    particle.style.setProperty('--ty', `${ty}px`);
    particle.style.animationDuration = `${duration}s`;

    // Add to parent
    parent.appendChild(particle);

    // Remove after animation completes
    setTimeout(() => {
        if (particle.parentNode === parent) {
            parent.removeChild(particle);
        }
    }, duration * 1000);
}

// Show loading overlay
function showLoading(message = 'Processing Nitric Oxide Dynamics...') {
    const overlay = document.querySelector('.loading-overlay');
    const loadingMessage = document.querySelector('.loading-message');

    if (overlay && loadingMessage) {
        loadingMessage.textContent = message;
        overlay.classList.add('active');
    }
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');

    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Animation types for cycling
const animationTypes = ['molecule', 'cell', 'dna', 'protein'];
let currentAnimationIndex = 0;

/**
 * Cycle through different animation types
 * @returns {string} The new animation type
 */
function cycleAnimationType() {
    currentAnimationIndex = (currentAnimationIndex + 1) % animationTypes.length;
    return animationTypes[currentAnimationIndex];
}

// Export functions for global use - both uppercase and lowercase for compatibility
window.N1O1Loader = {
    show: showLoading,
    hide: hideLoading,
    cycleAnimationType: cycleAnimationType,
    createGasParticle: createGasParticle,
    generateGasParticles: generateGasParticles
};

// Also assign the same functions to lowercase version for backward compatibility
window.n1o1Loader = window.N1O1Loader;
/**
 * N1O1 Clinical Trials - Onboarding Animation
 * Features a playful research character guide and nitrous oxide liquid-to-gas animation
 */

// Wait for DOM to fully load
document.addEventListener('DOMContentLoaded', () => {
  // Only show onboarding animation if user hasn't seen it before
  if (!localStorage.getItem('n1o1_onboarding_completed')) {
    initOnboardingAnimation();
  }
  
  // Initialize onboarding animation event listeners
  document.getElementById('n1o1-start-onboarding')?.addEventListener('click', initOnboardingAnimation);
});

/**
 * Initialize and display the onboarding animation
 */
function initOnboardingAnimation() {
  // Create the onboarding container and overlay
  createOnboardingElements();
  
  // Start the animation sequence
  startAnimationSequence();
  
  // Mark onboarding as completed for this user
  localStorage.setItem('n1o1_onboarding_completed', 'true');
}

/**
 * Create all DOM elements needed for the onboarding animation
 */
function createOnboardingElements() {
  // Create overlay container
  const overlay = document.createElement('div');
  overlay.className = 'n1o1-onboarding-overlay';
  overlay.id = 'n1o1-onboarding-overlay';
  
  // Create animation container
  const container = document.createElement('div');
  container.className = 'n1o1-onboarding-container';
  container.id = 'n1o1-onboarding-container';
  
  // Create the guide character
  const guide = document.createElement('div');
  guide.className = 'n1o1-guide-character';
  guide.id = 'n1o1-guide-character';
  guide.innerHTML = `
    <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" class="n1o1-guide-svg">
      <!-- Microscope base -->
      <circle cx="60" cy="95" r="20" fill="#2063c9" />
      
      <!-- Character face/head -->
      <circle cx="60" cy="40" r="25" fill="#ef476f" stroke="#2063c9" stroke-width="2" />
      
      <!-- Eyes -->
      <circle cx="50" cy="35" r="5" fill="white" class="n1o1-eye" />
      <circle cx="70" cy="35" r="5" fill="white" class="n1o1-eye" />
      <circle cx="50" cy="35" r="2" fill="#16325c" class="n1o1-pupil" />
      <circle cx="70" cy="35" r="2" fill="#16325c" class="n1o1-pupil" />
      
      <!-- Smile -->
      <path d="M45,45 Q60,55 75,45" fill="none" stroke="#16325c" stroke-width="2" class="n1o1-smile" />
      
      <!-- Microscope tube -->
      <rect x="55" y="55" width="10" height="40" fill="#178bea" />
      
      <!-- Lab coat -->
      <path d="M35,65 Q60,80 85,65 L85,95 Q60,105 35,95 Z" fill="white" stroke="#16325c" stroke-width="1" />
      
      <!-- N1O1 badge -->
      <rect x="55" y="70" width="10" height="5" rx="2" fill="#ef476f" />
    </svg>
  `;
  
  // Create the n2o molecule animation container
  const moleculeContainer = document.createElement('div');
  moleculeContainer.className = 'n1o1-molecule-container';
  moleculeContainer.id = 'n1o1-molecule-container';
  moleculeContainer.innerHTML = `
    <div class="n1o1-liquid-container" id="n1o1-liquid-container">
      <div class="n1o1-liquid" id="n1o1-liquid"></div>
    </div>
    <div class="n1o1-molecules" id="n1o1-molecules"></div>
  `;
  
  // Create the speech bubble
  const speechBubble = document.createElement('div');
  speechBubble.className = 'n1o1-speech-bubble';
  speechBubble.id = 'n1o1-speech-bubble';
  
  // Create the content panel
  const contentPanel = document.createElement('div');
  contentPanel.className = 'n1o1-content-panel';
  contentPanel.id = 'n1o1-content-panel';
  contentPanel.innerHTML = `
    <h2>Welcome to N1O1 Clinical Trials!</h2>
    <p>I'll be your guide to exploring the fascinating world of nitric oxide dynamics.</p>
    <div class="n1o1-buttons">
      <button class="n1o1-button" id="n1o1-next-button">Next</button>
      <button class="n1o1-button n1o1-skip-button" id="n1o1-skip-button">Skip Tour</button>
    </div>
  `;
  
  // Append elements to the DOM
  container.appendChild(guide);
  container.appendChild(moleculeContainer);
  container.appendChild(speechBubble);
  container.appendChild(contentPanel);
  overlay.appendChild(container);
  document.body.appendChild(overlay);
  
  // Add event listeners
  document.getElementById('n1o1-next-button').addEventListener('click', nextOnboardingStep);
  document.getElementById('n1o1-skip-button').addEventListener('click', skipOnboarding);
  
  // Create nitrous oxide molecules
  createMolecules();
}

/**
 * Create nitrous oxide molecule elements
 */
function createMolecules() {
  const moleculesContainer = document.getElementById('n1o1-molecules');
  
  // Clear existing molecules
  moleculesContainer.innerHTML = '';
  
  // Create multiple molecules
  for (let i = 0; i < 15; i++) {
    const molecule = document.createElement('div');
    molecule.className = 'n1o1-molecule';
    molecule.style.left = `${Math.random() * 100}%`;
    molecule.style.animationDelay = `${Math.random() * 2}s`;
    molecule.style.animationDuration = `${2 + Math.random() * 3}s`;
    
    // Use different sizes for some variety
    const scale = 0.8 + Math.random() * 0.4;
    molecule.style.transform = `scale(${scale})`;
    
    // Create molecule structure (N2O) with SVG
    // Enhanced version with scientifically accurate representation
    molecule.innerHTML = `
      <svg width="50" height="24" viewBox="0 0 50 24" xmlns="http://www.w3.org/2000/svg" class="n1o1-molecule-svg">
        <!-- Nitrogen atom 1 (N) -->
        <circle cx="10" cy="12" r="7" fill="#2063c9" class="n1o1-atom n1o1-nitrogen" />
        <text x="10" y="12" text-anchor="middle" dominant-baseline="central" fill="white" font-size="8" font-weight="bold">N</text>
        
        <!-- Nitrogen atom 2 (N) -->
        <circle cx="26" cy="12" r="7" fill="#2063c9" class="n1o1-atom n1o1-nitrogen" />
        <text x="26" y="12" text-anchor="middle" dominant-baseline="central" fill="white" font-size="8" font-weight="bold">N</text>
        
        <!-- Oxygen atom (O) -->
        <circle cx="42" cy="12" r="7" fill="#ef476f" class="n1o1-atom n1o1-oxygen" />
        <text x="42" y="12" text-anchor="middle" dominant-baseline="central" fill="white" font-size="8" font-weight="bold">O</text>
        
        <!-- Bonds -->
        <!-- Triple bond between N atoms (liquid state has shorter bonds) -->
        <line x1="13" y1="10" x2="23" y2="10" stroke="#8ecae6" stroke-width="1.5" class="n1o1-bond n1o1-bond-1-a" />
        <line x1="13" y1="12" x2="23" y2="12" stroke="#8ecae6" stroke-width="1.5" class="n1o1-bond n1o1-bond-1-b" />
        <line x1="13" y1="14" x2="23" y2="14" stroke="#8ecae6" stroke-width="1.5" class="n1o1-bond n1o1-bond-1-c" />
        
        <!-- Double bond between N and O (representing the N=O bond) -->
        <line x1="29" y1="11" x2="39" y2="11" stroke="#ff99ac" stroke-width="1.5" class="n1o1-bond n1o1-bond-2-a" />
        <line x1="29" y1="13" x2="39" y2="13" stroke="#ff99ac" stroke-width="1.5" class="n1o1-bond n1o1-bond-2-b" />
        
        <!-- Electron cloud visualization (for animation) -->
        <ellipse cx="18" cy="12" rx="0" ry="0" fill="rgba(32, 99, 201, 0.2)" class="n1o1-electron-cloud n1o1-cloud-1" />
        <ellipse cx="34" cy="12" rx="0" ry="0" fill="rgba(239, 71, 111, 0.2)" class="n1o1-electron-cloud n1o1-cloud-2" />
      </svg>
    `;
    
    moleculesContainer.appendChild(molecule);
  }
}

/**
 * Start the animation sequence
 */
function startAnimationSequence() {
  const overlay = document.getElementById('n1o1-onboarding-overlay');
  const container = document.getElementById('n1o1-onboarding-container');
  
  // Show the overlay with fade-in
  overlay.style.display = 'flex';
  setTimeout(() => {
    overlay.style.opacity = '1';
  }, 10);
  
  // Animate the guide character entrance
  setTimeout(() => {
    container.classList.add('active');
    document.getElementById('n1o1-guide-character').classList.add('active');
  }, 500);
  
  // Display the speech bubble
  setTimeout(() => {
    document.getElementById('n1o1-speech-bubble').classList.add('active');
    document.getElementById('n1o1-content-panel').classList.add('active');
  }, 1000);
  
  // Start liquid to gas animation
  setTimeout(() => {
    startLiquidToGasAnimation();
  }, 1500);
}

/**
 * Animate liquid to gas transition
 */
function startLiquidToGasAnimation() {
  const liquid = document.getElementById('n1o1-liquid');
  const liquidContainer = document.getElementById('n1o1-liquid-container');
  const molecules = document.getElementById('n1o1-molecules');
  
  // Start with full liquid
  liquid.style.height = '100%';
  
  // Add bubbles dynamically to the liquid
  addBubblesToLiquid(liquidContainer);
  
  // Animate liquid level decreasing
  setTimeout(() => {
    // Add a boiling effect before evaporation
    liquid.classList.add('boiling');
    
    setTimeout(() => {
      // Start evaporating after the boiling effect
      liquid.classList.remove('boiling');
      liquid.classList.add('evaporating');
      
      // Add vapor particles at the top of the container
      addVaporParticles(liquidContainer);
      
      // As liquid decreases, molecules start rising
      setTimeout(() => {
        molecules.classList.add('active');
        
        // Play a light "whoosh" sound effect using the Web Audio API if browser supports it
        playTransformationSound();
        
        // Animate individual molecules with more varied motion
        document.querySelectorAll('.n1o1-molecule').forEach((molecule, index) => {
          // Randomize the delay for a more natural effect
          const delay = 200 + (Math.random() * 300);
          
          setTimeout(() => {
            molecule.classList.add('active');
            
            // Apply random rotation to molecules
            const rotation = Math.random() * 360;
            molecule.style.transform = `rotate(${rotation}deg)`;
            
            // Animate bonds expanding
            const bonds = molecule.querySelectorAll('.n1o1-bond');
            bonds.forEach(bond => {
              bond.classList.add('active');
            });
            
            // Add a pulse effect to atoms
            const atoms = molecule.querySelectorAll('.n1o1-atom');
            atoms.forEach(atom => {
              atom.classList.add('pulsing');
            });
          }, index * delay);
        });
      }, 1000);
    }, 1500);
  }, 500);
}

/**
 * Add bubble elements to the liquid container
 */
function addBubblesToLiquid(container) {
  // Create 10 bubbles
  for (let i = 0; i < 10; i++) {
    const bubble = document.createElement('div');
    bubble.className = 'n1o1-bubble';
    
    // Randomize bubble size
    const size = 5 + (Math.random() * 10);
    bubble.style.width = `${size}px`;
    bubble.style.height = `${size}px`;
    
    // Randomize position
    bubble.style.left = `${Math.random() * 80 + 10}%`;
    bubble.style.bottom = `${Math.random() * 50}%`;
    
    // Randomize animation
    bubble.style.animationDuration = `${1 + Math.random() * 2}s`;
    bubble.style.animationDelay = `${Math.random() * 2}s`;
    
    container.appendChild(bubble);
  }
}

/**
 * Add vapor particle elements above the liquid
 */
function addVaporParticles(container) {
  // Create vapor particles
  for (let i = 0; i < 20; i++) {
    const particle = document.createElement('div');
    particle.className = 'n1o1-vapor-particle';
    
    // Randomize particle size
    const size = 3 + (Math.random() * 5);
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    
    // Randomize position
    particle.style.left = `${Math.random() * 100}%`;
    particle.style.top = `10%`;
    
    // Randomize animation
    particle.style.animationDuration = `${2 + Math.random() * 3}s`;
    particle.style.animationDelay = `${Math.random() * 1}s`;
    
    container.appendChild(particle);
  }
}

/**
 * Play a subtle transformation sound effect
 */
function playTransformationSound() {
  try {
    // Create audio context if supported
    if (window.AudioContext || window.webkitAudioContext) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      const audioCtx = new AudioContext();
      
      // Create an oscillator for the whooshing sound
      const oscillator = audioCtx.createOscillator();
      const gainNode = audioCtx.createGain();
      
      // Set up the oscillator
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(220, audioCtx.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 1.5);
      
      // Set up the gain node for volume control
      gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.2, audioCtx.currentTime + 0.2);
      gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 1.5);
      
      // Connect nodes and start sound
      oscillator.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      
      oscillator.start();
      oscillator.stop(audioCtx.currentTime + 1.5);
    }
  } catch (e) {
    // Ignore any audio errors - sound is non-essential
    console.log('Audio not available for transformation effect');
  }
}

/**
 * Move to the next onboarding step
 */
let currentStep = 0;
const onboardingSteps = [
  {
    title: "Welcome to N1O1 Clinical Trials!",
    content: "I'll be your guide to exploring the fascinating world of nitric oxide dynamics.",
    animation: "welcome"
  },
  {
    title: "Nitrous Oxide Molecular Structure",
    content: "Nitrous oxide (N₂O) consists of two nitrogen atoms bonded to an oxygen atom. This molecular structure gives it unique properties.",
    animation: "welcome"
  },
  {
    title: "Rapid Phase Transition",
    content: "Watch as N₂O rapidly transforms from liquid to gas! This dramatic phase change occurs at -88.5°C under normal pressure.",
    animation: "transform"
  },
  {
    title: "N₂O's Clinical Applications",
    content: "N₂O plays a crucial role as an intravascular signaling molecule, influencing vasodilation and blood flow regulation in the body.",
    animation: "transform"
  },
  {
    title: "Simulate Patient Responses",
    content: "Our platform allows you to create personalized simulations visualizing how nitric oxide affects vascular health through precise modeling.",
    animation: "simulate"
  },
  {
    title: "Data-Driven Insights",
    content: "Track plasma concentrations and physiological responses with interactive visuals for comprehensive analysis of nitric oxide dynamics.",
    animation: "simulate"
  },
  {
    title: "Ready to Begin?",
    content: "Let's start exploring the platform's powerful features to enhance your clinical trials and research!",
    animation: "begin"
  }
];

function nextOnboardingStep() {
  currentStep++;
  
  if (currentStep >= onboardingSteps.length) {
    // End of onboarding
    skipOnboarding();
    return;
  }
  
  // Update content
  const step = onboardingSteps[currentStep];
  const contentPanel = document.getElementById('n1o1-content-panel');
  
  // Animate content change
  contentPanel.classList.remove('active');
  
  setTimeout(() => {
    contentPanel.innerHTML = `
      <h2>${step.title}</h2>
      <p>${step.content}</p>
      <div class="n1o1-buttons">
        <button class="n1o1-button" id="n1o1-next-button">${currentStep === onboardingSteps.length - 1 ? 'Get Started' : 'Next'}</button>
        <button class="n1o1-button n1o1-skip-button" id="n1o1-skip-button">Skip Tour</button>
      </div>
    `;
    
    // Re-add event listeners
    document.getElementById('n1o1-next-button').addEventListener('click', nextOnboardingStep);
    document.getElementById('n1o1-skip-button').addEventListener('click', skipOnboarding);
    
    // Apply animation for this step
    applyStepAnimation(step.animation);
    
    // Show updated content
    contentPanel.classList.add('active');
  }, 300);
}

/**
 * Apply animations specific to each step
 */
function applyStepAnimation(animationType) {
  const guide = document.getElementById('n1o1-guide-character');
  const moleculeContainer = document.getElementById('n1o1-molecule-container');
  
  // Reset animations
  guide.classList.remove('welcome', 'transform', 'simulate', 'begin');
  moleculeContainer.classList.remove('welcome', 'transform', 'simulate', 'begin');
  
  // Apply new animation
  guide.classList.add(animationType);
  moleculeContainer.classList.add(animationType);
  
  if (animationType === 'transform') {
    // Restart the liquid-to-gas animation
    const liquid = document.getElementById('n1o1-liquid');
    const molecules = document.getElementById('n1o1-molecules');
    const liquidContainer = document.getElementById('n1o1-liquid-container');
    
    // Remove existing bubbles and vapor particles
    document.querySelectorAll('.n1o1-bubble, .n1o1-vapor-particle').forEach(element => {
      element.remove();
    });
    
    // Reset liquid state
    liquid.classList.remove('boiling', 'evaporating');
    molecules.classList.remove('active');
    
    document.querySelectorAll('.n1o1-molecule').forEach(molecule => {
      molecule.classList.remove('active');
      molecule.querySelectorAll('.n1o1-bond').forEach(bond => {
        bond.classList.remove('active');
      });
    });
    
    // Reset and restart
    liquid.style.height = '100%';
    setTimeout(() => {
      startLiquidToGasAnimation();
    }, 100);
  } else if (animationType === 'simulate') {
    // Add a simulation-specific animation
    const guide = document.getElementById('n1o1-guide-character');
    guide.classList.add('simulate');
    
    // Add a simulated pulse effect to molecules
    document.querySelectorAll('.n1o1-molecule').forEach(molecule => {
      molecule.style.animationDuration = `${2 + Math.random() * 2}s`;
    });
  } else if (animationType === 'begin') {
    // Final step animation - guide waves goodbye
    const guide = document.getElementById('n1o1-guide-character');
    guide.classList.add('begin');
    
    // Prepare all molecules for the final visual
    document.querySelectorAll('.n1o1-molecule').forEach((molecule, index) => {
      setTimeout(() => {
        molecule.style.opacity = '1';
        molecule.style.transform = 'scale(1)';
      }, index * 50);
    });
  }
}

/**
 * Skip the onboarding animation
 */
function skipOnboarding() {
  const overlay = document.getElementById('n1o1-onboarding-overlay');
  
  // Fade out
  overlay.style.opacity = '0';
  
  // Remove from DOM after animation completes
  setTimeout(() => {
    overlay.remove();
  }, 500);
}
/**
 * Nitric Oxide Molecule and Cell Biology Loading Animations
 * Author: Dustin Salinas
 * For N1O1 Clinical Trials Platform
 * 
 * This script provides loading animations for the N1O1 Clinical Trials application.
 * It creates a loading overlay with molecular, cellular, and DNA animations.
 */

class N1O1Loader {
  constructor() {
    this.loadingMessages = [
      "Calculating nitrite kinetics...",
      "Simulating NO pathways...",
      "Processing molecular interactions...",
      "Analyzing patient data...",
      "Optimizing simulation parameters...",
      "Computing plasma concentrations...",
      "Mapping vascular responses...",
      "Modeling physiological outcomes...",
      "Rendering molecular structures...",
      "Validating simulation results..."
    ];

    this.animationTypes = ['molecule', 'cell', 'dna'];
    this.currentAnimation = 'molecule';
    this.isActive = false;
    this.messageInterval = null;
    this.generatedNucleotides = false;
    
    this.initialize();
  }

  initialize() {
    // Create loading overlay
    if (!document.getElementById('n1o1-loading-overlay')) {
      this.createLoadingElements();
      this.setupEventListeners();
    }
  }

  createLoadingElements() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'n1o1-loading-overlay';
    
    // Create content container
    const content = document.createElement('div');
    content.className = 'loading-content';
    
    // Create molecular animation
    this.createMoleculeAnimation(content);
    
    // Create cell animation
    this.createCellAnimation(content);
    
    // Create DNA animation
    this.createDNAAnimation(content);
    
    // Create loading message
    const message = document.createElement('div');
    message.className = 'loading-message loading-dots';
    message.id = 'loading-message';
    message.textContent = this.getRandomMessage();
    content.appendChild(message);
    
    overlay.appendChild(content);
    document.body.appendChild(overlay);
  }

  createMoleculeAnimation(container) {
    const moleculeLoader = document.createElement('div');
    moleculeLoader.className = 'no-molecule-loader';
    
    const wrapper = document.createElement('div');
    wrapper.className = 'no-molecule-wrapper';
    
    // Create nitrogen atom
    const nitrogen = document.createElement('div');
    nitrogen.className = 'nitrogen';
    wrapper.appendChild(nitrogen);
    
    // Create oxygen atom
    const oxygen = document.createElement('div');
    oxygen.className = 'oxygen';
    wrapper.appendChild(oxygen);
    
    // Create bond
    const bond = document.createElement('div');
    bond.className = 'bond';
    wrapper.appendChild(bond);
    
    // Add gas particles for diffusion effect
    for (let i = 0; i < 8; i++) {
      const particle = document.createElement('div');
      particle.className = 'gas-particle';
      
      // Set random positions
      particle.style.setProperty('--random-x', `${Math.floor(Math.random() * 60) - 30}px`);
      particle.style.setProperty('--random-y', `${Math.floor(Math.random() * 100) - 50}px`);
      
      wrapper.appendChild(particle);
    }
    
    // Create electron orbits
    for (let i = 0; i < 3; i++) {
      const orbit = document.createElement('div');
      orbit.className = 'electron-orbit';
      
      // Create electrons
      const electron = document.createElement('div');
      electron.className = 'electron';
      orbit.appendChild(electron);
      
      wrapper.appendChild(orbit);
    }
    
    moleculeLoader.appendChild(wrapper);
    container.appendChild(moleculeLoader);
  }

  createCellAnimation(container) {
    const cellLoader = document.createElement('div');
    cellLoader.className = 'cell-loader';
    
    // Create cell membrane
    const cell = document.createElement('div');
    cell.className = 'cell';
    
    // Create nucleus
    const nucleus = document.createElement('div');
    nucleus.className = 'nucleus';
    cell.appendChild(nucleus);
    
    // Create organelles
    for (let i = 0; i < 3; i++) {
      const organelle = document.createElement('div');
      organelle.className = 'organelle';
      cell.appendChild(organelle);
    }
    
    // Create vesicles
    for (let i = 0; i < 3; i++) {
      const vesicle = document.createElement('div');
      vesicle.className = 'vesicle';
      cell.appendChild(vesicle);
    }
    
    cellLoader.appendChild(cell);
    container.appendChild(cellLoader);
  }

  createDNAAnimation(container) {
    const dnaLoader = document.createElement('div');
    dnaLoader.className = 'dna-loader';
    
    const dnaStrand = document.createElement('div');
    dnaStrand.className = 'dna-strand';
    
    // Create backbones
    const backboneLeft = document.createElement('div');
    backboneLeft.className = 'backbone-left';
    dnaStrand.appendChild(backboneLeft);
    
    const backboneRight = document.createElement('div');
    backboneRight.className = 'backbone-right';
    dnaStrand.appendChild(backboneRight);
    
    // Create nucleotide pairs
    for (let i = 0; i < 10; i++) {
      const pair = document.createElement('div');
      pair.className = 'nucleotide-pair';
      pair.style.top = (i * 20) + 'px';
      pair.style.transform = `rotateY(${i * 36}deg)`;
      
      const left = document.createElement('div');
      left.className = 'nucleotide-left';
      pair.appendChild(left);
      
      const right = document.createElement('div');
      right.className = 'nucleotide-right';
      pair.appendChild(right);
      
      const basePair = document.createElement('div');
      basePair.className = 'base-pair';
      pair.appendChild(basePair);
      
      dnaStrand.appendChild(pair);
    }
    
    dnaLoader.appendChild(dnaStrand);
    container.appendChild(dnaLoader);
  }

  setupEventListeners() {
    // Add event listener for switching animation types (for future use)
    document.addEventListener('keydown', (e) => {
      if (this.isActive && e.key === 'Tab') {
        e.preventDefault();
        this.cycleAnimationType();
      }
    });
  }

  cycleAnimationType() {
    const overlay = document.getElementById('n1o1-loading-overlay');
    if (!overlay) return;
    
    // Remove current animation class
    overlay.classList.remove(`show-${this.currentAnimation}`);
    
    // Get next animation index
    const currentIndex = this.animationTypes.indexOf(this.currentAnimation);
    const nextIndex = (currentIndex + 1) % this.animationTypes.length;
    this.currentAnimation = this.animationTypes[nextIndex];
    
    // Add next animation class
    if (this.currentAnimation !== 'molecule') {
      overlay.classList.add(`show-${this.currentAnimation}`);
    }
  }

  getRandomMessage() {
    const randomIndex = Math.floor(Math.random() * this.loadingMessages.length);
    return this.loadingMessages[randomIndex];
  }

  startCyclingMessages() {
    const messageElement = document.getElementById('loading-message');
    if (!messageElement) return;
    
    this.messageInterval = setInterval(() => {
      messageElement.textContent = this.getRandomMessage();
    }, 3000);
  }

  stopCyclingMessages() {
    if (this.messageInterval) {
      clearInterval(this.messageInterval);
      this.messageInterval = null;
    }
  }

  show(message = null) {
    const overlay = document.getElementById('n1o1-loading-overlay');
    const messageElement = document.getElementById('loading-message');
    
    if (overlay && messageElement) {
      // Set custom message if provided
      if (message) {
        messageElement.textContent = message;
        this.stopCyclingMessages();
      } else {
        messageElement.textContent = this.getRandomMessage();
        this.startCyclingMessages();
      }
      
      overlay.classList.add('active');
      this.isActive = true;
    }
  }

  hide() {
    const overlay = document.getElementById('n1o1-loading-overlay');
    
    if (overlay) {
      overlay.classList.remove('active');
      this.isActive = false;
      this.stopCyclingMessages();
    }
  }

  setMessage(message) {
    const messageElement = document.getElementById('loading-message');
    
    if (messageElement) {
      messageElement.textContent = message;
      this.stopCyclingMessages();
    }
  }
}

// Initialize loader
const n1o1Loader = new N1O1Loader();

// Export for global use
window.n1o1Loader = n1o1Loader;
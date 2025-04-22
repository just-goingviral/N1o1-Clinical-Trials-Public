/**
 * Loader Animation Demo
 * Shows the different molecular animation types
 */

// Initialize the N1O1 Loader animations
window.n1o1Loader = {
    show: function(message = 'Loading...') {
        const loaderEl = document.getElementById('n1o1-loader');
        if (!loaderEl) {
            // Create loader if it doesn't exist
            const newLoader = document.createElement('div');
            newLoader.id = 'n1o1-loader';
            newLoader.className = 'n1o1-loader-overlay';
            newLoader.innerHTML = `
                <div class="n1o1-loader-content">
                    <div class="n1o1-molecule-animation"></div>
                    <p class="n1o1-loader-message">${message}</p>
                </div>
            `;
            document.body.appendChild(newLoader);
        } else {
            // Update existing loader
            const messageEl = loaderEl.querySelector('.n1o1-loader-message');
            if (messageEl) messageEl.textContent = message;
            loaderEl.style.display = 'flex';
        }
    },
    
    hide: function() {
        const loaderEl = document.getElementById('n1o1-loader');
        if (loaderEl) {
            loaderEl.style.display = 'none';
        }
    },
    
    switchAnimation: function(type) {
        const animationEl = document.querySelector('.n1o1-molecule-animation');
        if (animationEl) {
            animationEl.className = 'n1o1-molecule-animation';
            if (type === 'dna') {
                animationEl.classList.add('dna-animation');
            } else if (type === 'cells') {
                animationEl.classList.add('cells-animation');
            } else {
                // Default to molecule animation
                animationEl.classList.add('molecule-animation');
            }
        }
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Find demo buttons
    const showLoaderBtn = document.getElementById('show-loader-btn');
    const switchAnimBtn = document.getElementById('switch-anim-btn');
    const hideLoaderBtn = document.getElementById('hide-loader-btn');
    
    if (showLoaderBtn) {
        showLoaderBtn.addEventListener('click', function() {
            if (window.n1o1Loader) {
                window.n1o1Loader.show("Processing simulation data...");
            } else {
                alert("Loader not initialized");
            }
        });
    }
    
    if (switchAnimBtn) {
        switchAnimBtn.addEventListener('click', function() {
            if (window.n1o1Loader) {
                window.n1o1Loader.cycleAnimationType();
            } else {
                alert("Loader not initialized");
            }
        });
    }
    
    if (hideLoaderBtn) {
        hideLoaderBtn.addEventListener('click', function() {
            if (window.n1o1Loader) {
                window.n1o1Loader.hide();
            } else {
                alert("Loader not initialized");
            }
        });
    }
    
    // Demo loader on index page automatically if demo section exists
    const loaderDemo = document.getElementById('loader-demo-section');
    if (loaderDemo) {
        // Show loader for 3 seconds after page load
        setTimeout(() => {
            if (window.n1o1Loader) {
                window.n1o1Loader.show("Initializing N1O1 molecular simulation...");
                
                // Cycle through animation types
                setTimeout(() => {
                    window.n1o1Loader.cycleAnimationType();
                    window.n1o1Loader.setMessage("Processing cell signaling pathways...");
                }, 3000);
                
                // Switch to DNA animation
                setTimeout(() => {
                    window.n1o1Loader.cycleAnimationType();
                    window.n1o1Loader.setMessage("Analyzing genetic expression patterns...");
                }, 6000);
                
                // Hide loader
                setTimeout(() => {
                    window.n1o1Loader.hide();
                }, 9000);
            }
        }, 1000);
    }
});
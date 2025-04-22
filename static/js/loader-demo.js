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
    // Check if n1o1Loader exists (it might not be on every page)
    if (typeof window.n1o1Loader === 'undefined') {
        console.log("N1O1 Loader not available on this page");
        return;
    }

    // Initialize animation demo
    const demoBtn = document.getElementById('start-loader-demo');
    if (demoBtn) {
        demoBtn.addEventListener('click', function() {
            // Start with molecules animation
            window.n1o1Loader.switchAnimation('molecules');
            window.n1o1Loader.show("Analyzing nitric oxide molecule dynamics...");

            // Cycle through animation types
            setTimeout(() => {
                window.n1o1Loader.switchAnimation('cells');
                window.n1o1Loader.show("Processing cell signaling pathways...");
            }, 3000);

            // Switch to DNA animation
            setTimeout(() => {
                window.n1o1Loader.switchAnimation('dna');
                window.n1o1Loader.show("Analyzing genetic expression patterns...");
            }, 6000);

            // Hide loader
            setTimeout(() => {
                window.n1o1Loader.hide();
            }, 9000);
        });
    }

    // If there's an automatic demo parameter in URL, run demo
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('demo-loader') && demoBtn) {
        setTimeout(() => demoBtn.click(), 1000);
    }
});
/**
 * Loader Animation Demo
 * Shows the different molecular animation types
 */

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
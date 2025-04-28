/**
 * N1O1 Clinical Trials - Responsive Utilities
 * Provides JavaScript functionality for responsive behavior.
 */

// Execute when DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
  
  // Initialize responsive behaviors
  initResponsiveBehaviors();
  
  // Set up resize event handler
  window.addEventListener('resize', debounce(handleWindowResize, 250));

  // Handle initial orientation
  handleOrientation();
  
  // Set up orientation change listener
  window.addEventListener('orientationchange', handleOrientation);
  
  // Add touch event handlers when needed
  if ('ontouchstart' in window) {
    initTouchBehaviors();
  }
  
  // Initialize mobile menu toggle behavior
  initMobileMenu();
  
  // Initialize mobile-friendly chart behavior
  initMobileCharts();
  
  // Initialize mobile chat behavior (if chat exists)
  initMobileChat();
});

/**
 * Initialize responsive behaviors
 */
function initResponsiveBehaviors() {
  // Add viewport-based classes to body
  updateViewportClasses();
  
  // Enhance tables for mobile
  makeTablesResponsive();
  
  // Add swipe support for tabs/carousels on mobile
  enableSwipeSupport();
  
  // Convert select menus to mobile-friendly versions
  enhanceSelectMenus();
  
  // Add collapsible behavior to long content sections
  makeContentCollapsible();
}

/**
 * Update viewport classes on the body element
 */
function updateViewportClasses() {
  const body = document.body;
  
  // Clear existing viewport classes
  body.classList.remove('viewport-xs', 'viewport-sm', 'viewport-md', 'viewport-lg', 'viewport-xl');
  
  // Add appropriate viewport class
  const width = window.innerWidth;
  
  if (width < 576) {
    body.classList.add('viewport-xs');
  } else if (width < 768) {
    body.classList.add('viewport-sm');
  } else if (width < 992) {
    body.classList.add('viewport-md');
  } else if (width < 1200) {
    body.classList.add('viewport-lg');
  } else {
    body.classList.add('viewport-xl');
  }
  
  // Add orientation class
  body.classList.remove('orientation-portrait', 'orientation-landscape');
  if (window.innerHeight > window.innerWidth) {
    body.classList.add('orientation-portrait');
  } else {
    body.classList.add('orientation-landscape');
  }
  
  // Add touch capability class
  if ('ontouchstart' in window) {
    body.classList.add('touch-device');
  } else {
    body.classList.remove('touch-device');
  }
}

/**
 * Make tables responsive on mobile
 */
function makeTablesResponsive() {
  const tables = document.querySelectorAll('table:not(.table-responsive)');
  
  tables.forEach(table => {
    // Wrap table in responsive container if not already wrapped
    if (!table.parentElement.classList.contains('table-responsive')) {
      const wrapper = document.createElement('div');
      wrapper.className = 'table-responsive';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
    
    // On very small screens, transform tables for vertical reading
    if (window.innerWidth < 576) {
      transformTableForMobile(table);
    }
  });
}

/**
 * Transform standard tables to be more readable on mobile
 */
function transformTableForMobile(table) {
  // Only process once
  if (table.classList.contains('mobile-transformed')) return;
  
  // Add mobile-transformed class to avoid reprocessing
  table.classList.add('mobile-transformed');
  
  // Get header text for data attributes
  const headerCells = table.querySelectorAll('thead th');
  const headerTexts = Array.from(headerCells).map(cell => cell.textContent.trim());
  
  // Update data cells with data-label attribute for CSS content generation
  const rows = table.querySelectorAll('tbody tr');
  
  rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    cells.forEach((cell, index) => {
      if (index < headerTexts.length) {
        cell.setAttribute('data-label', headerTexts[index]);
      }
    });
  });
}

/**
 * Enable swipe support for touch interfaces
 */
function enableSwipeSupport() {
  // Only apply on touch devices
  if (!('ontouchstart' in window)) return;
  
  // Find elements to add swipe support to
  const swipeElements = document.querySelectorAll('.tab-content, .carousel');
  
  swipeElements.forEach(element => {
    let touchStartX = 0;
    let touchEndX = 0;
    
    // Add touch event listeners
    element.addEventListener('touchstart', e => {
      touchStartX = e.changedTouches[0].screenX;
    }, {passive: true});
    
    element.addEventListener('touchend', e => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe(element, touchStartX, touchEndX);
    }, {passive: true});
  });
}

/**
 * Handle swipe gesture logic
 */
function handleSwipe(element, startX, endX) {
  const minSwipeDistance = 50;  // Minimum distance to register as swipe
  const swipeDistance = endX - startX;
  
  // Ignore small movements
  if (Math.abs(swipeDistance) < minSwipeDistance) return;
  
  if (element.classList.contains('tab-content')) {
    // Handle tab navigation swipe
    const activeTab = element.querySelector('.tab-pane.active');
    const tabId = activeTab.getAttribute('id');
    const navTab = document.querySelector(`[data-bs-target="#${tabId}"]`) || 
                   document.querySelector(`[href="#${tabId}"]`);
    
    if (navTab) {
      const navTabs = navTab.parentElement.parentElement.querySelectorAll('.nav-link');
      const tabArray = Array.from(navTabs);
      const currentIndex = tabArray.indexOf(navTab);
      
      if (swipeDistance > 0 && currentIndex > 0) {
        // Swipe right - go to previous tab
        new bootstrap.Tab(tabArray[currentIndex - 1]).show();
      } else if (swipeDistance < 0 && currentIndex < tabArray.length - 1) {
        // Swipe left - go to next tab
        new bootstrap.Tab(tabArray[currentIndex + 1]).show();
      }
    }
  } else if (element.classList.contains('carousel')) {
    // Handle carousel swipe
    const carousel = bootstrap.Carousel.getInstance(element);
    
    if (swipeDistance > 0) {
      // Swipe right - previous slide
      carousel.prev();
    } else {
      // Swipe left - next slide
      carousel.next();
    }
  }
}

/**
 * Enhance select menus for mobile
 */
function enhanceSelectMenus() {
  if (window.innerWidth >= 768) return;
  
  const selects = document.querySelectorAll('select:not(.mobile-enhanced)');
  
  selects.forEach(select => {
    select.classList.add('mobile-enhanced');
    select.classList.add('form-select');
    
    // Increase the font size slightly for better touch
    select.style.fontSize = 'var(--mobile-font-size-base)';
    select.style.paddingTop = '0.5rem';
    select.style.paddingBottom = '0.5rem';
  });
}

/**
 * Make long content sections collapsible on mobile
 */
function makeContentCollapsible() {
  if (window.innerWidth >= 768) return;
  
  const longContents = document.querySelectorAll('.content-section, .card-body');
  
  longContents.forEach(section => {
    // Only process long content (greater than 300px)
    if (section.offsetHeight <= 300) return;
    if (section.classList.contains('has-collapse-toggle')) return;
    
    section.classList.add('has-collapse-toggle');
    
    // Create collapsed state
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'collapse-content';
    
    // Move all children to the wrapper
    Array.from(section.childNodes).forEach(child => {
      contentWrapper.appendChild(child);
    });
    
    // Add wrapper back to the section
    section.appendChild(contentWrapper);
    
    // Add toggle button
    const toggleButton = document.createElement('button');
    toggleButton.className = 'btn btn-sm btn-link expand-collapse-toggle w-100 mt-2';
    toggleButton.innerHTML = 'Show More <i class="fas fa-chevron-down"></i>';
    section.appendChild(toggleButton);
    
    // Set initial state
    contentWrapper.style.maxHeight = '200px';
    contentWrapper.style.overflow = 'hidden';
    
    // Add toggle behavior
    toggleButton.addEventListener('click', function() {
      if (contentWrapper.style.maxHeight === '200px') {
        contentWrapper.style.maxHeight = '100%';
        toggleButton.innerHTML = 'Show Less <i class="fas fa-chevron-up"></i>';
      } else {
        contentWrapper.style.maxHeight = '200px';
        toggleButton.innerHTML = 'Show More <i class="fas fa-chevron-down"></i>';
        // Scroll to the top of the section
        section.scrollIntoView({behavior: 'smooth'});
      }
    });
  });
}

/**
 * Initialize mobile menu behavior
 */
function initMobileMenu() {
  // Enhance navbar-toggler with animation
  const menuTogglers = document.querySelectorAll('.navbar-toggler');
  
  menuTogglers.forEach(toggler => {
    toggler.innerHTML = `
      <div class="toggler-icon">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;
    
    // Add toggle animation class
    toggler.addEventListener('click', function() {
      this.classList.toggle('open');
    });
  });
  
  // Close menu when clicking outside
  document.addEventListener('click', function(event) {
    const navbarCollapse = document.querySelector('.navbar-collapse.show');
    if (navbarCollapse) {
      // Only handle clicks outside the navbar
      if (!navbarCollapse.contains(event.target) && 
          !event.target.classList.contains('navbar-toggler') &&
          !event.target.closest('.navbar-toggler')) {
        
        const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
        if (bsCollapse) {
          bsCollapse.hide();
          // Update toggler icon state
          document.querySelector('.navbar-toggler').classList.remove('open');
        }
      }
    }
  });
}

/**
 * Initialize mobile-optimized charts
 */
function initMobileCharts() {
  if (typeof Chart === 'undefined') return;
  
  // Apply mobile-friendly chart options globally
  if (window.innerWidth < 768) {
    Chart.defaults.font.size = 10;
    Chart.defaults.plugins.legend.display = false;
  }
  
  // Find canvas elements for charts
  const chartCanvases = document.querySelectorAll('canvas[id^="chart"]');
  
  chartCanvases.forEach(canvas => {
    const container = canvas.parentElement;
    if (!container.classList.contains('chart-container')) {
      container.classList.add('chart-container');
    }
  });
}

/**
 * Initialize mobile chat behavior
 */
function initMobileChat() {
  const chatButton = document.querySelector('.chat-button');
  const chatWindow = document.querySelector('.chat-window');
  
  if (!chatButton || !chatWindow) return;
  
  // Adjust chat window position on mobile
  if (window.innerWidth < 768) {
    chatWindow.style.bottom = '0';
    chatWindow.style.right = '0';
    chatWindow.style.width = '100%';
    chatWindow.style.height = '85vh';
    
    // Add chat close button if not present
    if (!chatWindow.querySelector('.chat-close')) {
      const closeButton = document.createElement('button');
      closeButton.className = 'btn btn-sm btn-close chat-close';
      closeButton.innerHTML = '&times;';
      closeButton.style.position = 'absolute';
      closeButton.style.top = '0.5rem';
      closeButton.style.right = '0.5rem';
      
      // Insert at the beginning of the chat header
      const chatHeader = chatWindow.querySelector('.chat-header') || chatWindow.firstChild;
      chatHeader.insertBefore(closeButton, chatHeader.firstChild);
      
      // Add close functionality
      closeButton.addEventListener('click', function() {
        chatWindow.style.display = 'none';
      });
    }
    
    // Update chat button to open the chat
    chatButton.addEventListener('click', function() {
      chatWindow.style.display = 'block';
    });
  }
}

/**
 * Handle orientation change
 */
function handleOrientation() {
  // Update viewport classes on orientation change
  updateViewportClasses();
  
  // Handle specific orientation behaviors
  const isLandscape = window.innerWidth > window.innerHeight;
  
  if (isLandscape) {
    // Landscape-specific adjustments
    adjustLandscapeLayout();
  } else {
    // Portrait-specific adjustments
    adjustPortraitLayout();
  }
}

/**
 * Adjust layout for landscape orientation
 */
function adjustLandscapeLayout() {
  // Optimize chat in landscape
  const chatWindow = document.querySelector('.chat-window');
  if (chatWindow) {
    chatWindow.style.height = '80vh';
  }
  
  // Optimize chart containers
  const chartContainers = document.querySelectorAll('.chart-container');
  chartContainers.forEach(container => {
    container.style.height = '50vh';
  });
}

/**
 * Adjust layout for portrait orientation
 */
function adjustPortraitLayout() {
  // Optimize chat in portrait
  const chatWindow = document.querySelector('.chat-window');
  if (chatWindow) {
    chatWindow.style.height = '85vh';
  }
  
  // Optimize chart containers
  const chartContainers = document.querySelectorAll('.chart-container');
  chartContainers.forEach(container => {
    container.style.height = '60vh';
  });
}

/**
 * Initialize touch-specific behaviors
 */
function initTouchBehaviors() {
  // Apply touch-specific enhancements
  document.body.classList.add('touch-device');
  
  // Add active state for better touch feedback
  const touchTargets = document.querySelectorAll('a, button, .card, .list-group-item');
  
  touchTargets.forEach(element => {
    element.addEventListener('touchstart', function() {
      this.classList.add('touch-active');
    }, {passive: true});
    
    element.addEventListener('touchend', function() {
      this.classList.remove('touch-active');
    }, {passive: true});
  });
}

/**
 * Handle window resize event
 */
function handleWindowResize() {
  // Update viewport classes
  updateViewportClasses();
  
  // Redo responsive tables
  makeTablesResponsive();
  
  // Re-enhance select menus
  enhanceSelectMenus();
  
  // Adjust chart sizes
  const chartContainers = document.querySelectorAll('.chart-container');
  chartContainers.forEach(container => {
    if (window.innerWidth < 768) {
      container.style.height = window.innerHeight > window.innerWidth ? '60vh' : '50vh';
    } else {
      container.style.height = '50vh';
    }
  });
}

/**
 * Debounce function to limit execution frequency
 */
function debounce(func, wait) {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}
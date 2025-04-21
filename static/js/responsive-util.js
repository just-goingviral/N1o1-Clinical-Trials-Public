/**
 * N1O1 Clinical Trials Platform - Responsive Utilities
 * 
 * This file provides helper functions for creating a responsive user experience
 * across different device sizes.
 */

const N1O1Responsive = {
  /**
   * Initialize responsive behavior for the application
   */
  init: function() {
    this.setupMobileMenu();
    this.setupResponsiveCards();
    this.setupResponsiveTables();
    this.setupTouchFriendlyControls();
    this.setupAccessibilitySupport();
    
    // Listen for window resize events to adjust UI elements
    window.addEventListener('resize', this.handleResize.bind(this));
    
    // Initial call to set up the UI based on current viewport
    this.handleResize();
  },
  
  /**
   * Set up the mobile menu toggle behavior
   */
  setupMobileMenu: function() {
    const menuToggle = document.querySelector('.navbar-toggler');
    const mobileMenu = document.querySelector('#navbarMain');
    
    if (menuToggle && mobileMenu) {
      // Ensure the mobile menu closes when a link is clicked
      const navLinks = mobileMenu.querySelectorAll('.nav-link');
      navLinks.forEach(link => {
        link.addEventListener('click', () => {
          if (window.innerWidth < 992) { // Bootstrap's lg breakpoint
            const bsCollapse = new bootstrap.Collapse(mobileMenu);
            bsCollapse.hide();
          }
        });
      });
    }
  },
  
  /**
   * Make cards responsive and touch-friendly
   */
  setupResponsiveCards: function() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
      // Add touch ripple effect for mobile
      card.addEventListener('touchstart', function(e) {
        this.classList.add('touch-active');
      });
      
      card.addEventListener('touchend', function(e) {
        this.classList.remove('touch-active');
      });
    });
  },
  
  /**
   * Make tables responsive on small screens
   */
  setupResponsiveTables: function() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
      // If table isn't already wrapped in a responsive div
      if (!table.parentElement.classList.contains('table-responsive')) {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
      }
    });
  },
  
  /**
   * Enhance controls to be more touch-friendly on mobile
   */
  setupTouchFriendlyControls: function() {
    // Make buttons larger on touch devices
    if ('ontouchstart' in window) {
      const buttons = document.querySelectorAll('.btn');
      buttons.forEach(btn => {
        // For small buttons, make them slightly larger
        if (btn.classList.contains('btn-sm')) {
          btn.classList.remove('btn-sm');
        }
        
        // Increase touch target size with padding
        btn.style.padding = '0.75rem 1rem';
      });
      
      // Add 'Back to Top' button for long pages on mobile
      this.addBackToTopButton();
    }
  },
  
  /**
   * Add 'Back to Top' button for mobile users
   */
  addBackToTopButton: function() {
    // Only add if it doesn't exist yet
    if (!document.getElementById('back-to-top-btn')) {
      const backToTopBtn = document.createElement('button');
      backToTopBtn.id = 'back-to-top-btn';
      backToTopBtn.className = 'btn btn-primary rounded-circle position-fixed';
      backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
      backToTopBtn.style.bottom = '20px';
      backToTopBtn.style.right = '20px';
      backToTopBtn.style.display = 'none'; // Hidden by default
      backToTopBtn.style.zIndex = '1000';
      backToTopBtn.style.width = '50px';
      backToTopBtn.style.height = '50px';
      
      backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      });
      
      document.body.appendChild(backToTopBtn);
      
      // Show/hide based on scroll position
      window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
          backToTopBtn.style.display = 'block';
        } else {
          backToTopBtn.style.display = 'none';
        }
      });
    }
  },
  
  /**
   * Add accessibility enhancements
   */
  setupAccessibilitySupport: function() {
    // Add ARIA labels to elements without proper labeling
    const unlabeledButtons = document.querySelectorAll('button:not([aria-label]):not([title])');
    unlabeledButtons.forEach(btn => {
      if (btn.innerText.trim() === '' && !btn.getAttribute('aria-label')) {
        // Try to determine purpose from icon
        if (btn.querySelector('.fa-plus')) {
          btn.setAttribute('aria-label', 'Add new item');
        } else if (btn.querySelector('.fa-edit')) {
          btn.setAttribute('aria-label', 'Edit item');
        } else if (btn.querySelector('.fa-trash')) {
          btn.setAttribute('aria-label', 'Delete item');
        }
      }
    });
  },
  
  /**
   * Handle window resize events to adjust UI
   */
  handleResize: function() {
    const isMobile = window.innerWidth < 768; // Bootstrap's md breakpoint
    
    // Adjust UI based on viewport width
    if (isMobile) {
      // Mobile-specific adjustments
      this.optimizeForMobile();
    } else {
      // Desktop-specific adjustments
      this.optimizeForDesktop();
    }
  },
  
  /**
   * Optimize UI for mobile devices
   */
  optimizeForMobile: function() {
    // Simplify tables by hiding less important columns
    const tables = document.querySelectorAll('table.responsive-table');
    tables.forEach(table => {
      const lowPriorityColumns = table.querySelectorAll('.low-priority');
      lowPriorityColumns.forEach(col => {
        col.style.display = 'none';
      });
    });
    
    // Adjust container padding
    const containers = document.querySelectorAll('.container');
    containers.forEach(container => {
      container.style.padding = '0.75rem';
    });
    
    // Stack buttons in button groups
    const btnGroups = document.querySelectorAll('.btn-group:not(.mobile-wrap)');
    btnGroups.forEach(group => {
      group.classList.add('d-flex', 'flex-column', 'mobile-wrap');
      const buttons = group.querySelectorAll('.btn');
      buttons.forEach(btn => {
        btn.classList.add('my-1', 'w-100');
        btn.style.borderRadius = '0.25rem';
      });
    });
  },
  
  /**
   * Optimize UI for desktop devices
   */
  optimizeForDesktop: function() {
    // Show all table columns
    const tables = document.querySelectorAll('table.responsive-table');
    tables.forEach(table => {
      const lowPriorityColumns = table.querySelectorAll('.low-priority');
      lowPriorityColumns.forEach(col => {
        col.style.display = '';
      });
    });
    
    // Reset container padding
    const containers = document.querySelectorAll('.container');
    containers.forEach(container => {
      container.style.padding = '';
    });
    
    // Reset button groups
    const btnGroups = document.querySelectorAll('.btn-group.mobile-wrap');
    btnGroups.forEach(group => {
      group.classList.remove('d-flex', 'flex-column', 'mobile-wrap');
      const buttons = group.querySelectorAll('.btn');
      buttons.forEach(btn => {
        btn.classList.remove('my-1', 'w-100');
        btn.style.borderRadius = '';
      });
    });
  }
};

// Initialize responsive behavior when document is ready
document.addEventListener('DOMContentLoaded', function() {
  N1O1Responsive.init();
});
// JobRite.com Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initMobileMenu();
    initParticleAnimation();
    initScrollAnimations();
    initSearchFunctionality();
    initUtilityPages();
});

/**
 * Mobile Menu Toggle - Enhanced for Touch Devices
 */
function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        let isMenuOpen = false;
        
        // Enhanced click handler with touch support
        mobileMenuButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleMenu();
        });
        
        // Touch event handlers for better mobile experience
        mobileMenuButton.addEventListener('touchstart', function(e) {
            e.preventDefault();
            this.style.transform = 'scale(0.95)';
        });
        
        mobileMenuButton.addEventListener('touchend', function(e) {
            e.preventDefault();
            this.style.transform = 'scale(1)';
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (isMenuOpen && !mobileMenu.contains(e.target) && !mobileMenuButton.contains(e.target)) {
                closeMenu();
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isMenuOpen) {
                closeMenu();
                mobileMenuButton.focus();
            }
        });
        
        // Close menu when window is resized to desktop size
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768 && isMenuOpen) {
                closeMenu();
            }
        });
        
        // Add smooth transitions to menu items
        const menuItems = mobileMenu.querySelectorAll('a');
        menuItems.forEach((item, index) => {
            item.style.transitionDelay = `${index * 50}ms`;
            
            // Enhanced touch feedback for menu items
            item.addEventListener('touchstart', function() {
                this.style.backgroundColor = 'rgba(254, 127, 45, 0.1)';
            });
            
            item.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.style.backgroundColor = '';
                }, 150);
            });
        });
        
        function toggleMenu() {
            if (isMenuOpen) {
                closeMenu();
            } else {
                openMenu();
            }
        }
        
        function openMenu() {
            isMenuOpen = true;
            mobileMenu.classList.remove('hidden');
            mobileMenu.classList.add('animate-slide-down');
            
            // Update hamburger icon with animation
            const icon = mobileMenuButton.querySelector('svg');
            icon.style.transform = 'rotate(90deg)';
            icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />';
            
            // Add aria attributes for accessibility
            mobileMenuButton.setAttribute('aria-expanded', 'true');
            mobileMenu.setAttribute('aria-hidden', 'false');
            
            // Focus management
            const firstMenuItem = mobileMenu.querySelector('a');
            if (firstMenuItem) {
                setTimeout(() => firstMenuItem.focus(), 100);
            }
            
            // Prevent body scroll on mobile when menu is open
            if (window.innerWidth < 768) {
                document.body.style.overflow = 'hidden';
            }
        }
        
        function closeMenu() {
            isMenuOpen = false;
            mobileMenu.classList.add('hidden');
            mobileMenu.classList.remove('animate-slide-down');
            
            // Reset hamburger icon
            const icon = mobileMenuButton.querySelector('svg');
            icon.style.transform = 'rotate(0deg)';
            icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />';
            
            // Update aria attributes
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            mobileMenu.setAttribute('aria-hidden', 'true');
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
    }
}

/**
 * Particle Animation System - DISABLED (Using template-based system instead)
 */
function initParticleAnimation() {
    // Disabled - using template-based particle system in home.html for better control
    return;
}
}

/**
 * Scroll Animations
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.category-item, .job-card, .section-title');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Search Functionality
 */
function initSearchFunctionality() {
    const searchForm = document.querySelector('.search-container');
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');
    
    if (searchForm && searchInput && searchButton) {
        // Handle search form submission
        searchButton.addEventListener('click', function(e) {
            e.preventDefault();
            performSearch();
        });
        
        // Handle Enter key in search input
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
        
        // Add search suggestions (placeholder for future implementation)
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length > 2) {
                // Future: Show search suggestions
                console.log('Search query:', query);
            }
        });
    }
    
    function performSearch() {
        const query = searchInput.value.trim();
        if (query) {
            // Add loading state
            searchButton.textContent = 'Searching...';
            searchButton.disabled = true;
            
            // Simulate search (replace with actual search implementation)
            setTimeout(() => {
                console.log('Performing search for:', query);
                // Future: Redirect to search results page
                // window.location.href = `/search/?q=${encodeURIComponent(query)}`;
                
                // Reset button state
                searchButton.textContent = 'Search Jobs';
                searchButton.disabled = false;
            }, 1000);
        }
    }
}

/**
 * Utility Pages Functionality
 */
function initUtilityPages() {
    initSalaryCalculator();
    initCVCreator();
    initFAQInteractions();
}

/**
 * Salary Calculator Functionality
 */
function initSalaryCalculator() {
    const calculateButton = document.querySelector('button[type="button"]');
    const salaryEstimateSection = document.querySelector('.bg-secondary');
    
    if (calculateButton && calculateButton.textContent.includes('Calculate Salary')) {
        calculateButton.addEventListener('click', function() {
            const jobTitle = document.getElementById('job-title')?.value;
            const location = document.getElementById('location')?.value;
            const experience = document.getElementById('experience')?.value;
            const industry = document.getElementById('industry')?.value;
            
            if (!jobTitle || !location || !experience || !industry) {
                alert('Please fill in all fields to calculate salary estimate.');
                return;
            }
            
            // Show loading state
            calculateButton.textContent = 'Calculating...';
            calculateButton.disabled = true;
            
            // Simulate salary calculation
            setTimeout(() => {
                const salaryEstimate = calculateSalaryEstimate(jobTitle, location, experience, industry);
                displaySalaryResults(salaryEstimate);
                
                // Reset button
                calculateButton.textContent = 'Calculate Salary';
                calculateButton.disabled = false;
            }, 1500);
        });
    }
    
    function calculateSalaryEstimate(jobTitle, location, experience, industry) {
        // Mock salary calculation based on inputs
        const baseSalaries = {
            'call-center': 35000,
            'customer-care': 38000,
            'sales': 42000,
            'hr': 48000,
            'it': 55000,
            'logistics': 45000
        };
        
        const experienceMultipliers = {
            '0-1': 1.0,
            '2-3': 1.15,
            '4-5': 1.35,
            '6+': 1.55
        };
        
        const locationMultipliers = {
            'new york': 1.3,
            'california': 1.25,
            'texas': 1.1,
            'florida': 1.05
        };
        
        let baseSalary = baseSalaries[industry] || 40000;
        let experienceMultiplier = experienceMultipliers[experience] || 1.0;
        let locationMultiplier = 1.0;
        
        // Simple location matching
        const locationLower = location.toLowerCase();
        for (const [key, multiplier] of Object.entries(locationMultipliers)) {
            if (locationLower.includes(key)) {
                locationMultiplier = multiplier;
                break;
            }
        }
        
        const estimatedSalary = Math.round(baseSalary * experienceMultiplier * locationMultiplier);
        const minSalary = Math.round(estimatedSalary * 0.85);
        const maxSalary = Math.round(estimatedSalary * 1.15);
        
        return {
            min: minSalary,
            max: maxSalary,
            average: estimatedSalary,
            jobTitle,
            location,
            experience,
            industry
        };
    }
    
    function displaySalaryResults(estimate) {
        if (salaryEstimateSection) {
            salaryEstimateSection.innerHTML = `
                <h3 class="text-lg font-semibold text-primary mb-3">Salary Estimate Results</h3>
                <div class="bg-white rounded-lg p-4 mb-4">
                    <div class="text-center">
                        <div class="text-3xl font-bold text-accent mb-2">
                            $${estimate.min.toLocaleString()} - $${estimate.max.toLocaleString()}
                        </div>
                        <div class="text-lg text-text-secondary">
                            Average: $${estimate.average.toLocaleString()}
                        </div>
                    </div>
                </div>
                <div class="text-sm text-text-secondary space-y-1">
                    <p><strong>Position:</strong> ${estimate.jobTitle}</p>
                    <p><strong>Location:</strong> ${estimate.location}</p>
                    <p><strong>Experience:</strong> ${estimate.experience} years</p>
                    <p class="mt-3 text-xs">
                        <em>* This is an estimated salary range based on market data and may vary by company, specific role requirements, and other factors.</em>
                    </p>
                </div>
            `;
        }
    }
}

/**
 * CV Creator Functionality
 */
function initCVCreator() {
    const generateButton = document.querySelector('button[type="button"]');
    
    if (generateButton && generateButton.textContent.includes('Generate CV')) {
        generateButton.addEventListener('click', function() {
            const formData = collectCVFormData();
            
            if (!validateCVForm(formData)) {
                alert('Please fill in the required fields (Name, Email, Professional Summary).');
                return;
            }
            
            // Show loading state
            generateButton.textContent = 'Generating CV...';
            generateButton.disabled = true;
            
            // Simulate CV generation
            setTimeout(() => {
                displayCVPreview(formData);
                
                // Reset button
                generateButton.textContent = 'Generate CV';
                generateButton.disabled = false;
            }, 2000);
        });
    }
    
    function collectCVFormData() {
        return {
            firstName: document.getElementById('first-name')?.value || '',
            lastName: document.getElementById('last-name')?.value || '',
            email: document.getElementById('email')?.value || '',
            phone: document.getElementById('phone')?.value || '',
            summary: document.getElementById('summary')?.value || '',
            jobTitle: document.getElementById('job-title-exp')?.value || '',
            company: document.getElementById('company')?.value || '',
            jobDescription: document.getElementById('job-description')?.value || '',
            skills: document.getElementById('skills')?.value || ''
        };
    }
    
    function validateCVForm(data) {
        return data.firstName && data.lastName && data.email && data.summary;
    }
    
    function displayCVPreview(data) {
        const previewHTML = `
            <div class="mt-8 bg-white border-2 border-accent rounded-lg p-6">
                <h3 class="text-xl font-semibold text-primary mb-4 text-center">CV Preview</h3>
                <div class="cv-preview bg-gray-50 p-6 rounded-lg">
                    <div class="text-center mb-6">
                        <h1 class="text-2xl font-bold text-primary">${data.firstName} ${data.lastName}</h1>
                        <div class="text-text-secondary mt-2">
                            ${data.email} ${data.phone ? '• ' + data.phone : ''}
                        </div>
                    </div>
                    
                    ${data.summary ? `
                    <div class="mb-6">
                        <h2 class="text-lg font-semibold text-primary border-b border-accent pb-1 mb-3">Professional Summary</h2>
                        <p class="text-text-secondary">${data.summary}</p>
                    </div>
                    ` : ''}
                    
                    ${data.jobTitle && data.company ? `
                    <div class="mb-6">
                        <h2 class="text-lg font-semibold text-primary border-b border-accent pb-1 mb-3">Work Experience</h2>
                        <div class="mb-3">
                            <h3 class="font-semibold">${data.jobTitle}</h3>
                            <div class="text-accent font-medium">${data.company}</div>
                            ${data.jobDescription ? `<p class="text-text-secondary mt-2">${data.jobDescription}</p>` : ''}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${data.skills ? `
                    <div class="mb-6">
                        <h2 class="text-lg font-semibold text-primary border-b border-accent pb-1 mb-3">Skills</h2>
                        <div class="flex flex-wrap gap-2">
                            ${data.skills.split(',').map(skill => 
                                `<span class="bg-accent text-white px-3 py-1 rounded-full text-sm">${skill.trim()}</span>`
                            ).join('')}
                        </div>
                    </div>
                    ` : ''}
                </div>
                
                <div class="text-center mt-6">
                    <button class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-opacity-90 transition-colors duration-200 mr-3">
                        Download PDF
                    </button>
                    <button class="bg-secondary text-primary px-6 py-2 rounded-lg hover:bg-opacity-80 transition-colors duration-200">
                        Edit CV
                    </button>
                </div>
            </div>
        `;
        
        // Insert preview after the form
        const form = document.querySelector('form');
        if (form) {
            // Remove existing preview
            const existingPreview = document.querySelector('.cv-preview-container');
            if (existingPreview) {
                existingPreview.remove();
            }
            
            // Add new preview
            const previewContainer = document.createElement('div');
            previewContainer.className = 'cv-preview-container';
            previewContainer.innerHTML = previewHTML;
            form.parentNode.insertBefore(previewContainer, form.nextSibling);
            
            // Scroll to preview
            previewContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}

/**
 * FAQ Interactions
 */
function initFAQInteractions() {
    const faqItems = document.querySelectorAll('.bg-white.rounded-lg.shadow-md');
    
    faqItems.forEach(item => {
        item.style.cursor = 'pointer';
        item.style.transition = 'all 0.2s ease';
        
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.1)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
        
        // Add click to expand functionality (placeholder)
        item.addEventListener('click', function() {
            const content = this.querySelector('p');
            if (content) {
                content.style.display = content.style.display === 'none' ? 'block' : 'none';
            }
        });
    });
}

/**
 * Smooth Scrolling for Anchor Links
 */
function initSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Category Hover Effects
 */
function initCategoryEffects() {
    const categoryItems = document.querySelectorAll('.category-item');
    
    categoryItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

/**
 * Job Card Interactions
 */
function initJobCardEffects() {
    const jobCards = document.querySelectorAll('.job-card');
    
    jobCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.05)';
        });
    });
}

/**
 * Performance Optimization
 */
function optimizePerformance() {
    // Debounce scroll events
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        scrollTimeout = setTimeout(function() {
            // Handle scroll events here if needed
        }, 16); // ~60fps
    });
    
    // Optimize animations for reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.documentElement.style.setProperty('--animation-duration', '0.01ms');
        
        // Disable particle animations
        const particles = document.querySelectorAll('.particle');
        particles.forEach(particle => {
            particle.style.animation = 'none';
        });
    }
}

/**
 * Error Handling
 */
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Future: Send error reports to monitoring service
});

/**
 * Mobile-specific enhancements
 */
function initMobileEnhancements() {
    // Add touch feedback to interactive elements
    const touchElements = document.querySelectorAll('.touch-feedback, button, .btn, a[href]');
    
    touchElements.forEach(element => {
        // Add touch start feedback
        element.addEventListener('touchstart', function(e) {
            if (!this.classList.contains('no-touch-feedback')) {
                this.style.transform = 'scale(0.98)';
                this.style.opacity = '0.8';
            }
        }, { passive: true });
        
        // Remove touch feedback
        element.addEventListener('touchend', function(e) {
            if (!this.classList.contains('no-touch-feedback')) {
                setTimeout(() => {
                    this.style.transform = '';
                    this.style.opacity = '';
                }, 100);
            }
        }, { passive: true });
        
        // Handle touch cancel
        element.addEventListener('touchcancel', function(e) {
            this.style.transform = '';
            this.style.opacity = '';
        }, { passive: true });
    });
    
    // Improve form input experience on mobile
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        // Prevent zoom on iOS when focusing inputs
        if (window.innerWidth < 768) {
            input.addEventListener('focus', function() {
                if (this.type !== 'file') {
                    this.style.fontSize = '16px';
                }
            });
        }
        
        // Add better visual feedback for form validation
        input.addEventListener('invalid', function() {
            this.classList.add('error');
            this.style.borderColor = '#ef4444';
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('error') && this.validity.valid) {
                this.classList.remove('error');
                this.style.borderColor = '';
            }
        });
    });
    
    // Add swipe gesture support for mobile navigation
    if (window.innerWidth < 768) {
        let startX = 0;
        let startY = 0;
        
        document.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchmove', function(e) {
            if (!startX || !startY) return;
            
            const diffX = startX - e.touches[0].clientX;
            const diffY = startY - e.touches[0].clientY;
            
            // Swipe right to open menu (from left edge)
            if (Math.abs(diffX) > Math.abs(diffY) && diffX < -50 && startX < 50) {
                const mobileMenu = document.getElementById('mobile-menu');
                const mobileMenuButton = document.getElementById('mobile-menu-button');
                
                if (mobileMenu && mobileMenu.classList.contains('hidden')) {
                    mobileMenuButton.click();
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', function() {
            startX = 0;
            startY = 0;
        }, { passive: true });
    }
    
    // Optimize scroll performance on mobile
    let ticking = false;
    
    function updateScrollPosition() {
        // Add scroll-based effects here if needed
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateScrollPosition);
            ticking = true;
        }
    }, { passive: true });
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            // Recalculate layouts after orientation change
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });
    
    // Add pull-to-refresh hint (visual only)
    if ('serviceWorker' in navigator && window.innerWidth < 768) {
        let startY = 0;
        let pullDistance = 0;
        const pullThreshold = 100;
        
        document.addEventListener('touchstart', function(e) {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', function(e) {
            if (startY && window.scrollY === 0) {
                pullDistance = e.touches[0].clientY - startY;
                
                if (pullDistance > 0 && pullDistance < pullThreshold) {
                    // Visual feedback for pull-to-refresh
                    document.body.style.transform = `translateY(${pullDistance * 0.3}px)`;
                    document.body.style.opacity = 1 - (pullDistance / pullThreshold) * 0.2;
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', function() {
            document.body.style.transform = '';
            document.body.style.opacity = '';
            startY = 0;
            pullDistance = 0;
        }, { passive: true });
    }
}

/**
 * Initialize performance optimizations
 */
document.addEventListener('DOMContentLoaded', function() {
    optimizePerformance();
    initSmoothScrolling();
    initCategoryEffects();
    initJobCardEffects();
    initMobileEnhancements();
});

/**
 * Utility Functions
 */
const Utils = {
    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Check if element is in viewport
    isInViewport: function(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// Export utils for use in other scripts
window.JobRiteUtils = Utils;
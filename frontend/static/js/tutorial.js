/**
 * Tutorial Modal Manager
 * Handles the first-time user experience with a step-by-step tutorial
 */

const TUTORIAL_STORAGE_KEY = 'aichemlab_tutorial_seen';

// Check if this is the user's first visit
function checkFirstVisit() {
    const tutorialSeen = localStorage.getItem(TUTORIAL_STORAGE_KEY);
    if (!tutorialSeen) {
        // Show tutorial after a short delay to let the page load
        setTimeout(showTutorial, 800);
    }
}

// Show the tutorial modal
function showTutorial() {
    const modal = document.getElementById('tutorial-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

// Hide the tutorial modal
function hideTutorial() {
    const modal = document.getElementById('tutorial-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Initialize tutorial functionality
function initTutorial() {
    const modal = document.getElementById('tutorial-modal');
    const closeBtn = document.getElementById('tutorial-close');
    const startBtn = document.getElementById('tutorial-start');
    const dontShowCheckbox = document.getElementById('dont-show-again');

    // Close button handler
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            hideTutorial();
            saveTutorialPreference(dontShowCheckbox.checked);
        });
    }

    // Start button handler
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            hideTutorial();
            saveTutorialPreference(dontShowCheckbox.checked);
        });
    }

    // Close on outside click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideTutorial();
                saveTutorialPreference(dontShowCheckbox.checked);
            }
        });
    }

    // Escape key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            hideTutorial();
            saveTutorialPreference(dontShowCheckbox.checked);
        }
    });

    // Check if this is first visit
    checkFirstVisit();
}

// Save user preference to localStorage
function saveTutorialPreference(dontShowAgain) {
    if (dontShowAgain) {
        localStorage.setItem(TUTORIAL_STORAGE_KEY, 'true');
    }
}

// Export function to manually show tutorial (for testing or help button)
window.showTutorialManually = showTutorial;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTutorial);
} else {
    initTutorial();
}
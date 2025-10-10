// Shared state management across all pages
// This file handles saving and loading form values AND prediction results using localStorage

const SharedState = {
    // Save current form values to localStorage
    saveFormInputs: function() {
        const specieSelect = document.getElementById('specie');
        const selectedOption = specieSelect?.options[specieSelect.selectedIndex];
        
        const state = {
            temperature: document.getElementById('temperature')?.value || '27',
            water_ph: document.getElementById('water_ph')?.value || '7.5',
            salinity: document.getElementById('salinity')?.value || '0.5',
            dissolved_oxygen: document.getElementById('dissolved_oxygen')?.value || '6',
            bod: document.getElementById('bod')?.value || '2',
            turbidity: document.getElementById('turbidity')?.value || '10',
            specie_value: specieSelect?.value || '',
            specie_sci: selectedOption?.getAttribute('data-sci') || '',
            specie_common: selectedOption?.getAttribute('data-common') || '',
            specie_desc: selectedOption?.getAttribute('data-desc') || '',
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('xgooa_form_state', JSON.stringify(state));
        console.log('Form state saved:', state);
    },

    // Save prediction results to localStorage
    savePredictionResults: function(geojsonData) {
        if (!geojsonData) return;
        
        const predictionState = {
            geojson: geojsonData,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('xgooa_prediction_results', JSON.stringify(predictionState));
        console.log('Prediction results saved');
    },

    // Load form values from localStorage
    loadFormInputs: function() {
        const saved = localStorage.getItem('xgooa_form_state');
        if (!saved) {
            // Return default values - ALL SLIDERS START AT ZERO
            return {
                temperature: '0',
                water_ph: '0',
                salinity: '0',
                dissolved_oxygen: '0',
                bod: '0',
                turbidity: '0',
                specie_value: '',
                specie_sci: '',
                specie_common: '',
                specie_desc: ''
            };
        }
        return JSON.parse(saved);
    },

    // Load prediction results from localStorage
    loadPredictionResults: function() {
        const saved = localStorage.getItem('xgooa_prediction_results');
        if (!saved) return null;
        
        const data = JSON.parse(saved);
        // Check if data is less than 1 hour old
        const timestamp = new Date(data.timestamp);
        const now = new Date();
        const hoursDiff = (now - timestamp) / (1000 * 60 * 60);
        
        if (hoursDiff > 1) {
            // Data is stale, clear it
            localStorage.removeItem('xgooa_prediction_results');
            return null;
        }
        
        return data.geojson;
    },

    // Apply loaded state to form sliders
    applyFormInputs: function() {
        const state = this.loadFormInputs();
        
        // Apply slider values
        ['temperature', 'water_ph', 'salinity', 'dissolved_oxygen', 'bod', 'turbidity'].forEach(id => {
            const slider = document.getElementById(id);
            const display = document.getElementById(id + '_value');
            if (slider && state[id]) {
                slider.value = state[id];
                if (display) display.textContent = state[id];
            }
        });

        return state;
    },

    // Restore species selection after Select2 is initialized
    restoreSpeciesSelection: function($specieSelect) {
        const state = this.loadFormInputs();
        
        if (!state.specie_value || !state.specie_sci) {
            console.log('No saved species to restore');
            return;
        }

        // Find the option with matching scientific name
        const options = $specieSelect.find('option');
        let matchFound = false;
        
        options.each(function() {
            const $option = $(this);
            if ($option.attr('data-sci') === state.specie_sci) {
                $specieSelect.val($option.val()).trigger('change');
                matchFound = true;
                console.log('Species restored:', state.specie_sci);
                return false; // break the loop
            }
        });

        if (!matchFound) {
            console.log('Could not find matching species option for:', state.specie_sci);
        }
    },

    // Get species scientific name for API call
    getSpeciesName: function() {
        const select = document.getElementById('specie');
        if (!select || !select.selectedOptions || !select.selectedOptions[0]) {
            return '';
        }
        return select.selectedOptions[0].getAttribute('data-sci') || '';
    },

    // Check if we have valid prediction data
    hasPredictionData: function() {
        const results = this.loadPredictionResults();
        const formState = this.loadFormInputs();
        return results !== null && formState.specie_sci !== '';
    },

    // Clear all saved state
    clear: function() {
        localStorage.removeItem('xgooa_form_state');
        localStorage.removeItem('xgooa_prediction_results');
        console.log('All state cleared');
    },

    // Reset form to default values and clear all data
    reset: function() {
        console.log('Starting reset process...');
        
        // Clear localStorage FIRST
        this.clear();
        
        // Reset all sliders to ZERO
        const defaults = {
            temperature: '0',
            water_ph: '0',
            salinity: '0',
            dissolved_oxygen: '0',
            bod: '0',
            turbidity: '0'
        };
        
        // Reset each slider with proper event triggering
        Object.keys(defaults).forEach(id => {
            const slider = document.getElementById(id);
            const display = document.getElementById(id + '_value');
            
            if (slider) {
                // Set the value to ZERO
                slider.value = defaults[id];
                
                // Update display to show ZERO
                if (display) {
                    display.textContent = defaults[id];
                }
                
                // Trigger input event to ensure any listeners are notified
                const inputEvent = new Event('input', { bubbles: true });
                slider.dispatchEvent(inputEvent);
                
                // Trigger change event as well
                const changeEvent = new Event('change', { bubbles: true });
                slider.dispatchEvent(changeEvent);
                
                console.log(`Reset ${id} to ${defaults[id]}`);
            } else {
                console.warn(`Slider not found: ${id}`);
            }
        });
        
        // Reset species dropdown (using jQuery if available)
        const specieSelect = document.getElementById('specie');
        if (specieSelect) {
            if (typeof $ !== 'undefined' && $(specieSelect).data('select2')) {
                $(specieSelect).val(null).trigger('change');
            } else {
                specieSelect.selectedIndex = 0;
            }
        }
        
        // Reset species description
        const noteEl = document.getElementById('species-note');
        if (noteEl) {
            noteEl.innerHTML = '<em class="opacity-75">Select a species to see its description...</em>';
        }
        
        console.log('Form reset to ZERO - complete');
        return true;
    },

    // Show confirmation dialog and reset if confirmed
    confirmAndReset: function() {
        const confirmed = confirm(
            'Are you sure you want to start a new prediction?\n\n' +
            'This will clear all current inputs and results.'
        );
        
        if (confirmed) {
            console.log('User confirmed reset');
            
            // Step 1: Clear localStorage FIRST and wait for it to complete
            this.clear();
            
            // Step 2: Force localStorage to flush by reading it back
            const verifyCleared = localStorage.getItem('xgooa_form_state');
            console.log('Verification - localStorage cleared:', verifyCleared === null);
            
            // Step 3: Reset form visually (sliders, dropdowns, etc.)
            this.resetFormVisuals();
            
            // Step 4: Show success notification
            this.showResetNotification();
            
            // Step 5: Wait longer before reload to ensure everything is processed
            // This gives time for:
            // - localStorage to fully clear
            // - Visual updates to complete
            // - Notification to display
            // - Browser to process all changes
            setTimeout(() => {
                console.log('Reloading page after reset...');
                // Use location.reload() with true to force reload from server
                window.location.reload(true);
            }, 1200); // Increased from 800ms to 1200ms for better reliability
        }
        
        return confirmed;
    },

    // Reset form visuals without clearing localStorage (used internally)
    resetFormVisuals: function() {
        console.log('Resetting form visuals to ZERO...');
        
        // Reset all sliders to ZERO
        const defaults = {
            temperature: '0',
            water_ph: '0',
            salinity: '0',
            dissolved_oxygen: '0',
            bod: '0',
            turbidity: '0'
        };
        
        // Reset each slider with proper event triggering
        Object.keys(defaults).forEach(id => {
            const slider = document.getElementById(id);
            const display = document.getElementById(id + '_value');
            
            if (slider) {
                // Set the value to ZERO
                slider.value = defaults[id];
                
                // Update display to show ZERO
                if (display) {
                    display.textContent = defaults[id];
                }
                
                // Trigger input event to ensure any listeners are notified
                const inputEvent = new Event('input', { bubbles: true });
                slider.dispatchEvent(inputEvent);
                
                // Trigger change event as well
                const changeEvent = new Event('change', { bubbles: true });
                slider.dispatchEvent(changeEvent);
                
                console.log(`Visual reset: ${id} = ${defaults[id]}`);
            }
        });
        
        // Reset species dropdown
        const specieSelect = document.getElementById('specie');
        if (specieSelect) {
            if (typeof $ !== 'undefined' && $(specieSelect).data('select2')) {
                $(specieSelect).val(null).trigger('change');
            } else {
                specieSelect.selectedIndex = 0;
            }
        }
        
        // Reset species description
        const noteEl = document.getElementById('species-note');
        if (noteEl) {
            noteEl.innerHTML = '<em class="opacity-75">Select a species to see its description...</em>';
        }
        
        console.log('Form visuals reset to ZERO - complete');
    },

    // Show temporary success notification
    showResetNotification: function() {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'reset-notification';
        notification.innerHTML = `
            <i class="bi bi-check-circle-fill me-2"></i>
            Form reset successfully! Starting fresh...
        `;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            font-weight: 500;
            animation: slideIn 0.3s ease-out;
        `;
        
        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => notification.remove(), 300);
        }, 500);
    }
};

// Auto-save on form changes
document.addEventListener('DOMContentLoaded', function() {
    // Apply saved form inputs immediately
    SharedState.applyFormInputs();

    // Save on slider change
    ['temperature', 'water_ph', 'salinity', 'dissolved_oxygen', 'bod', 'turbidity'].forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('change', () => SharedState.saveFormInputs());
            slider.addEventListener('input', () => {
                // Update display value in real-time
                const display = document.getElementById(id + '_value');
                if (display) display.textContent = slider.value;
            });
        }
    });

    // Save on species change (will be attached after Select2 init)
    const specieSelect = document.getElementById('specie');
    if (specieSelect) {
        $(specieSelect).on('change', function() {
            SharedState.saveFormInputs();
        });
    }
});

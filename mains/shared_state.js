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
            // Return default values
            return {
                temperature: '27',
                water_ph: '7.5',
                salinity: '0.5',
                dissolved_oxygen: '6',
                bod: '2',
                turbidity: '10',
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

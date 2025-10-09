// Shared state management across all pages
// This file handles saving and loading form values using localStorage

const SharedState = {
    // Save current form values to localStorage
    save: function() {
        const state = {
            temperature: document.getElementById('temperature')?.value || '27',
            water_ph: document.getElementById('water_ph')?.value || '7.5',
            salinity: document.getElementById('salinity')?.value || '0.5',
            dissolved_oxygen: document.getElementById('dissolved_oxygen')?.value || '6',
            bod: document.getElementById('bod')?.value || '2',
            turbidity: document.getElementById('turbidity')?.value || '10',
            specie: document.getElementById('specie')?.value || '',
            specie_sci: document.getElementById('specie')?.options[document.getElementById('specie')?.selectedIndex]?.getAttribute('data-sci') || ''
        };
        localStorage.setItem('xgooa_form_state', JSON.stringify(state));
    },

    // Load form values from localStorage
    load: function() {
        const saved = localStorage.getItem('xgooa_form_state');
        if (!saved) {
            // Set default values
            return {
                temperature: '27',
                water_ph: '7.5',
                salinity: '0.5',
                dissolved_oxygen: '6',
                bod: '2',
                turbidity: '10',
                specie: '',
                specie_sci: ''
            };
        }
        return JSON.parse(saved);
    },

    // Apply loaded state to form
    apply: function() {
        const state = this.load();
        
        // Apply slider values
        ['temperature', 'water_ph', 'salinity', 'dissolved_oxygen', 'bod', 'turbidity'].forEach(id => {
            const slider = document.getElementById(id);
            const display = document.getElementById(id + '_value');
            if (slider && state[id]) {
                slider.value = state[id];
                if (display) display.textContent = state[id];
            }
        });

        // Apply species selection (will be done after Select2 initializes)
        return state;
    },

    // Get species scientific name for API call
    getSpeciesName: function() {
        const select = document.getElementById('specie');
        if (!select || !select.selectedOptions || !select.selectedOptions[0]) {
            return '';
        }
        return select.selectedOptions[0].getAttribute('data-sci') || select.value;
    }
};

// Auto-save on form changes
document.addEventListener('DOMContentLoaded', function() {
    // Save on slider change
    ['temperature', 'water_ph', 'salinity', 'dissolved_oxygen', 'bod', 'turbidity'].forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('change', () => SharedState.save());
        }
    });

    // Save on species change
    const specieSelect = document.getElementById('specie');
    if (specieSelect) {
        specieSelect.addEventListener('change', () => SharedState.save());
    }
});

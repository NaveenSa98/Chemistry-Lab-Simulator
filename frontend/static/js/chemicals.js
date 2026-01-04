/**
 * Chemical Inventory Manager
 * Fetches chemicals from API and dynamically renders categorized inventory
 */

class ChemicalInventory {
    constructor() {
        this.categories = {
            'liquids': { title: '💧 Liquids & Solvents', class: 'liquids' },
            'acids': { title: '🧪 Acids', class: 'acids' },
            'bases': { title: '⚗️ Bases', class: 'bases' },
            'salts': { title: '💎 Salts', class: 'salts' },
            'indicators': { title: '🌈 Indicators', class: 'indicators' },
            'solids': { title: '🧊 Solids', class: 'solids' },
            'gases': { title: '💨 Gases', class: 'gases' },
            'ions': { title: '⚛️ Ions', class: 'ions' }
        };
        this.toggleSetup = false;
        this.documentClickListener = null;
    }

    async loadChemicals() {
        this.setupToggle();
        try {
            const response = await fetch('/api/chemicals');
            const chemicals = await response.json();
            this.cachedChemicals = chemicals; // Cache for back button
            this.renderInventory(chemicals);
        } catch (error) {
            console.error('Error loading chemicals:', error);
            this.showError();
        }
    }

    setupToggle() {
        if (this.toggleSetup) return;

        const btn = document.getElementById('inventory-btn');
        const menu = document.getElementById('inventory-menu');

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.toggle('active');
        });

        // Close when clicking outside
        if (this.documentClickListener) {
            document.removeEventListener('click', this.documentClickListener);
        }

        this.documentClickListener = (e) => {
            if (!menu.contains(e.target) && e.target !== btn) {
                menu.classList.remove('active');
            }
        };

        document.addEventListener('click', this.documentClickListener);
        this.toggleSetup = true;
    }

    renderInventory(chemicals) {
        const menu = document.getElementById('inventory-menu');
        menu.innerHTML = '';

        const categoriesContainer = document.createElement('div');
        categoriesContainer.className = 'categories-grid';

        for (const [key, data] of Object.entries(this.categories)) {
            if (chemicals[key] && chemicals[key].length > 0) {
                const catBtn = document.createElement('div');
                catBtn.className = `category-item ${data.class}`;
                catBtn.innerHTML = `
                    <span class="cat-icon">${data.title.split(' ')[0]}</span>
                    <span class="cat-label">${data.title.split(' ').slice(1).join(' ')}</span>
                `;
                catBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.showChemicalsForCategory(key, data, chemicals[key]);
                });
                categoriesContainer.appendChild(catBtn);
            }
        }

        menu.appendChild(categoriesContainer);
    }

    /**
     * Show chemicals for a selected category
     * Displays each chemical with hover tooltips
     */
    showChemicalsForCategory(categoryKey, categoryData, chemicalList) {
        const menu = document.getElementById('inventory-menu');
        menu.innerHTML = '';

        // Header with Back Button
        const header = document.createElement('div');
        header.className = 'inventory-header-sub';

        const backBtn = document.createElement('button');
        backBtn.className = 'back-btn';
        backBtn.innerHTML = '← Back';
        backBtn.onclick = (e) => {
            e.stopPropagation();
            // Pass the cached chemicals instead of reloading
            const menu = document.getElementById('inventory-menu');
            const response = document.createElement('div'); // Dummy to satisfy loadChemicals if needed
            this.renderInventory(this.cachedChemicals);
        };

        const title = document.createElement('span');
        title.className = `category-title-inline ${categoryData.class}`;
        title.textContent = categoryData.title;

        header.appendChild(backBtn);
        header.appendChild(title);
        menu.appendChild(header);

        // Horizontal Grid for Chemicals
        const horizontalGrid = document.createElement('div');
        horizontalGrid.className = 'horizontal-ingredient-grid';

        chemicalList.forEach(chemical => {
            const item = document.createElement('div');
            item.className = `ingredient ${categoryKey.slice(0, -1)}`;
            item.setAttribute('draggable', 'true');
            item.setAttribute('data-name', chemical.name);
            item.setAttribute('data-tooltip', chemical.formula || 'Formula: N/A');
            item.textContent = chemical.display;

            // Add click handler to show chemical info panel
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                showChemicalInfo(chemical, categoryData);
            });

            horizontalGrid.appendChild(item);
        });

        menu.appendChild(horizontalGrid);
        this.setupDragAndDrop();
    }

    setupDragAndDrop() {
        document.querySelectorAll('.ingredient').forEach(item => {
            item.addEventListener('dragstart', e => {
                e.dataTransfer.setData('name', item.getAttribute('data-name'));
            });
        });
    }

    showError() {
        const menu = document.getElementById('inventory-menu');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-msg';
        errorDiv.textContent = '❌ Error loading chemicals. Please refresh the page.';
        menu.appendChild(errorDiv);
    }
}

/**
 * Display a detailed information panel about a selected chemical
 * Shows formula, category, and other properties to help students learn
 */
function showChemicalInfo(chemical, categoryData) {
    // Remove existing panel if present
    const existingPanel = document.querySelector('.chem-info-panel');
    if (existingPanel) existingPanel.remove();

    // Create new info panel
    const panel = document.createElement('div');
    panel.className = 'chem-info-panel';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '✕';
    closeBtn.addEventListener('click', () => panel.remove());

    const title = document.createElement('h4');
    title.textContent = `📚 ${chemical.name}`;

    const infoContent = document.createElement('div');

    // Create info rows for each property
    const rows = [
        { label: 'Formula', value: chemical.formula || 'N/A' },
        { label: 'Category', value: categoryData.title.split(' ')[1] || 'Unknown' },
        { label: 'Molecular Weight', value: chemical.molecular_weight ? `${chemical.molecular_weight.toFixed(2)} g/mol` : 'N/A' },
        { label: 'IUPAC Name', value: chemical.iupac_name || 'N/A' }
    ];

    rows.forEach(row => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'chem-info-row';

        const label = document.createElement('span');
        label.className = 'chem-info-label';
        label.textContent = row.label;

        const value = document.createElement('span');
        value.className = 'chem-info-value';
        value.textContent = row.value;

        rowDiv.appendChild(label);
        rowDiv.appendChild(value);
        infoContent.appendChild(rowDiv);
    });

    // Add "Add to Beaker" button
    const addBtn = document.createElement('button');
    addBtn.style.cssText = `
        width: 100%;
        margin-top: 12px;
        padding: 8px;
        background: rgba(0, 242, 255, 0.15);
        border: 1px solid var(--accent-color);
        color: #00f2ff;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.3s ease;
    `;
    addBtn.textContent = '➕ Add to Beaker';
    addBtn.addEventListener('click', () => {
        const amount = parseInt(document.getElementById('amount-slider').value);
        if (window.addIngredient) {
            window.addIngredient(chemical.name, amount);
            panel.remove();
        }
    });
    addBtn.addEventListener('mouseover', () => {
        addBtn.style.background = 'rgba(0, 242, 255, 0.25)';
    });
    addBtn.addEventListener('mouseout', () => {
        addBtn.style.background = 'rgba(0, 242, 255, 0.15)';
    });

    panel.appendChild(closeBtn);
    panel.appendChild(title);
    panel.appendChild(infoContent);
    panel.appendChild(addBtn);
    document.body.appendChild(panel);
}

// Initialize and load chemicals when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const inventory = new ChemicalInventory();
    inventory.loadChemicals();
});

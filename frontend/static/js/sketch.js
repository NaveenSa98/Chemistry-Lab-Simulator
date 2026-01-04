let currentVolume = 0; // in ml
const MAX_VOLUME = 500;
let beakerX, beakerY, beakerW, beakerH;
let liquidLevel = 0;
let targetLiquidLevel = 0;
let liquidColor;
let targetLiquidColor;
let ingredientsInBeaker = [];
let particles;
let reactionData = null;
let reactionTimer = 0;
let reactionIntensity = 0;
let temperatureState = 'room';
let concentrationState = 'dilute';
let phaseQueue = [];
let currentPhaseIndex = -1;
let phaseTimer = 0;

function setup() {
    const canvas = createCanvas(800, 600);
    canvas.parent('canvas-container');

    beakerW = 200;
    beakerH = 300;
    beakerX = width / 2 - beakerW / 2;
    beakerY = height / 2 - 180;

    liquidColor = color(255, 255, 255, 30);
    targetLiquidColor = color(255, 255, 255, 30);

    particles = new ParticleSystem();

    // Setup tab switching for results/details
    setupPanelTabs();

    // Condition Controls
    const burnerToggle = document.getElementById('burner-toggle');
    const iceToggle = document.getElementById('ice-toggle');

    burnerToggle.addEventListener('change', () => {
        if (burnerToggle.checked) {
            iceToggle.checked = false;
            temperatureState = 'hot';
        } else {
            temperatureState = 'room';
        }
        updateEnvironment();
    });

    iceToggle.addEventListener('change', () => {
        if (iceToggle.checked) {
            burnerToggle.checked = false;
            temperatureState = 'cold';
        } else {
            temperatureState = 'room';
        }
        updateEnvironment();
    });

    const concToggle = document.getElementById('conc-toggle');
    concToggle.addEventListener('change', () => {
        concentrationState = concToggle.checked ? 'concentrated' : 'dilute';
        updateEnvironment();
    });

    // Quantity Slider Logic
    const amountSlider = document.getElementById('amount-slider');
    const amountVal = document.getElementById('amount-val');
    amountSlider.addEventListener('input', () => {
        amountVal.innerText = amountSlider.value;
    });

    const canvasContainer = document.getElementById('canvas-container');
    canvasContainer.addEventListener('dragover', e => e.preventDefault());
    canvasContainer.addEventListener('drop', e => {
        e.preventDefault();
        const name = e.dataTransfer.getData('name');
        const amount = parseInt(amountSlider.value);
        addIngredient(name, amount);
    });

    // Reset Button
    document.getElementById('reset-btn').addEventListener('click', () => {
        resetBeaker();
    });

    // Initialize Example Reactions
    initExampleReactions();
}

/**
 * Initialize Example Reactions Panel
 * Sets up click handlers for preset reaction buttons
 */
function initExampleReactions() {
    const reactionCards = document.querySelectorAll('.reaction-card');

    reactionCards.forEach(card => {
        const tryBtn = card.querySelector('.try-btn');
        const reactionType = card.getAttribute('data-reaction');

        tryBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            runExampleReaction(reactionType);
        });
    });
}

/**
 * Run a preset example reaction
 * Automatically adds chemicals and sets conditions
 */
async function runExampleReaction(reactionType) {
    // Reset beaker first
    resetBeaker();

    // Reset conditions
    document.getElementById('burner-toggle').checked = false;
    document.getElementById('ice-toggle').checked = false;
    document.getElementById('conc-toggle').checked = false;
    temperatureState = 'room';
    concentrationState = 'dilute';

    // Set amount slider to 50ml for consistency
    const amountSlider = document.getElementById('amount-slider');
    const amountVal = document.getElementById('amount-val');
    amountSlider.value = 50;
    amountVal.innerText = '50';

    // Wait a bit for reset animation
    await sleep(500);

    // Define preset reactions
    const reactions = {
        'neutralization': {
            chemicals: ['Hydrochloric acid', 'Sodium hydroxide'],
            conditions: { heat: false, cold: false, concentrated: false },
            delay: 1000
        },
        'indicator': {
            chemicals: ['Phenolphthalein', 'Sodium hydroxide'],
            conditions: { heat: false, cold: false, concentrated: false },
            delay: 1000
        },
        'bubbling': {
            chemicals: ['Magnesium', 'Hydrochloric acid'],
            conditions: { heat: false, cold: false, concentrated: false },
            delay: 1000
        },
        'precipitate': {
            chemicals: ['Copper sulfate', 'Sodium hydroxide'],
            conditions: { heat: false, cold: false, concentrated: false },
            delay: 1000
        },
        'temperature': {
            chemicals: ['Copper', 'Sulfuric acid'],
            conditions: { heat: true, cold: false, concentrated: true },
            delay: 1000
        },
        'sodium': {
            chemicals: ['Sodium', 'Water'],
            conditions: { heat: false, cold: false, concentrated: false },
            delay: 1000
        }
    };

    const reaction = reactions[reactionType];

    if (!reaction) {
        console.error('Unknown reaction type:', reactionType);
        return;
    }

    // Set conditions
    if (reaction.conditions.heat) {
        document.getElementById('burner-toggle').checked = true;
        temperatureState = 'hot';
    }
    if (reaction.conditions.cold) {
        document.getElementById('ice-toggle').checked = true;
        temperatureState = 'cold';
    }
    if (reaction.conditions.concentrated) {
        document.getElementById('conc-toggle').checked = true;
        concentrationState = 'concentrated';
    }

    // Add chemicals one by one with delay
    for (let i = 0; i < reaction.chemicals.length; i++) {
        const chemical = reaction.chemicals[i];
        await addIngredient(chemical, 50);
        if (i < reaction.chemicals.length - 1) {
            await sleep(reaction.delay);
        }
    }

    // Show success message
    showSuccessBanner(`${reactionType.charAt(0).toUpperCase() + reactionType.slice(1)} reaction started! Watch the beaker.`);
}

/**
 * Show success banner notification
 */
function showSuccessBanner(message) {
    const banner = document.createElement('div');
    banner.className = 'success-banner';
    banner.innerHTML = `✓ ${message}`;
    document.body.appendChild(banner);

    setTimeout(() => {
        banner.remove();
    }, 3000);
}

/**
 * Utility sleep function
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Setup Tab Switching for Results/Details Panels
 * Allows students to switch between reaction results and educational details
 */
function setupPanelTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('[data-tab-content]');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(content => content.style.display = 'none');

            // Add active class to clicked button and show its content
            btn.classList.add('active');
            document.getElementById(tabName + '-panel').style.display = 'block';
        });
    });
}

/**
 * Reset the beaker and clear all data
 * Called when student clicks "Empty Beaker" button
 */
function resetBeaker() {
    ingredientsInBeaker = [];
    currentVolume = 0;
    targetLiquidLevel = 0;
    reactionData = null;
    reactionTimer = 0;
    reactionIntensity = 0;
    targetLiquidColor = color(255, 255, 255, 30);
    particles.stop();

    // Reset UI Panel to idle state
    document.getElementById('status-message').innerText = "Drop chemicals to start an experiment...";
    document.getElementById('status-message').className = 'status-idle';
    document.getElementById('products-section').classList.add('hidden');

    // Reset details tab
    document.getElementById('reaction-equation').innerText = "";
    document.getElementById('reaction-type').innerText = "-";
    document.getElementById('ph-display').innerText = "-";
    document.getElementById('symptoms-display').innerText = "-";
    document.getElementById('concept-display').innerText = "-";
    document.getElementById('ai-explanation').innerText = "Waiting for reaction...";
    document.getElementById('safety-tips').innerText = "Always wear appropriate safety equipment like gloves.";
    document.getElementById('real-world-example').innerText = "-";
}

function draw() {
    clear();

    // Update Timers
    if (reactionTimer > 0) {
        reactionTimer--;
        reactionIntensity = map(reactionTimer, 0, 300, 0, 1);
    } else {
        reactionIntensity = lerp(reactionIntensity, 0, 0.05);
    }

    // Phase Management
    if (phaseQueue.length > 0 && currentPhaseIndex < phaseQueue.length - 1) {
        if (phaseTimer > 0) {
            phaseTimer--;
        } else {
            currentPhaseIndex++;
            applyPhase(phaseQueue[currentPhaseIndex]);
            phaseTimer = 240; // 4 seconds per phase
        }
    }

    // Draw Bench
    stroke(255, 255, 255, 15);
    line(0, beakerY + beakerH, width, beakerY + beakerH);

    // Draw Conditions
    if (temperatureState === 'hot') {
        drawBurner();
    } else if (temperatureState === 'cold') {
        drawIceBath();
    }

    // Heat Haze Effect
    if (reactionData?.animation_triggers?.heat && reactionIntensity > 0) {
        drawHeatHaze();
    }

    // Draw Liquid
    liquidLevel = lerp(liquidLevel, targetLiquidLevel, 0.05);
    liquidColor = lerpColor(liquidColor, targetLiquidColor, 0.05);

    noStroke();
    fill(liquidColor);
    // Beaker shape liquid
    rect(beakerX + 4, beakerY + beakerH - liquidLevel, beakerW - 8, liquidLevel, 0, 0, 10, 10);

    // Frost Effect
    if (temperatureState === 'cold') {
        drawFrost();
    }

    // Run Particles
    if (particles.active && reactionIntensity > 0.1) {
        let pCount = Math.ceil(reactionIntensity * 10);
        for (let i = 0; i < pCount; i++) {
            particles.addParticle(random(beakerX + 20, beakerX + beakerW - 20), beakerY + beakerH - random(10, liquidLevel));
        }
    }
    particles.run();

    // Draw Beaker & Calibration
    drawBeaker();

    // Equation Banner
    if (reactionData && reactionData.equation) {
        drawEquation(reactionData.equation);
    }
}

function drawHeatHaze() {
    push();
    noFill();
    strokeWeight(1);
    for (let i = 0; i < 5; i++) {
        let alpha = reactionIntensity * 50 * (1 - i / 5);
        stroke(255, 255, 255, alpha);
        let offset = sin(frameCount * 0.1 + i) * 5;
        arc(beakerX + beakerW / 2 + offset, beakerY - 20 - i * 15, beakerW * 0.8, 20, 0, PI);
    }
    pop();
}

function drawBeaker() {
    noFill();
    stroke(255, 255, 255, 120);
    strokeWeight(3);
    line(beakerX, beakerY, beakerX, beakerY + beakerH - 10); // L
    line(beakerX + beakerW, beakerY, beakerX + beakerW, beakerY + beakerH - 10); // R
    arc(beakerX + beakerW / 2, beakerY + beakerH - 10, beakerW, 20, 0, PI); // B

    // Markings
    strokeWeight(1);
    textAlign(RIGHT, CENTER);
    textSize(10);
    for (let i = 1; i <= 10; i++) {
        let h = (beakerH / 10) * i;
        let y = beakerY + beakerH - h;
        let ml = i * 50;
        line(beakerX, y, beakerX + 15, y);
        noStroke();
        fill(255, 255, 255, 100);
        text(ml + 'ml', beakerX - 5, y);
        stroke(255, 255, 255, 50);
    }
}

function drawEquation(eq) {
    push();
    textAlign(CENTER, CENTER);
    let alpha = map(reactionIntensity, 0, 1, 100, 255);
    textSize(18);
    let w = textWidth(eq) + 60;
    fill(0, 0, 0, alpha * 0.7);
    noStroke();
    rect(width / 2 - w / 2, beakerY - 80, w, 50, 25);

    fill(0, 255, 255, alpha);
    text(eq, width / 2, beakerY - 55);
    pop();
}

function drawBurner() {
    push();
    let burnerBaseX = beakerX + beakerW / 2;
    // Flame
    noStroke();
    let flameSize = map(sin(frameCount * 0.2), -1, 1, 30, 45);
    fill(255, 120, 0, 200);
    ellipse(burnerBaseX, beakerY + beakerH, 30, flameSize);
    fill(255, 200, 0, 150);
    ellipse(burnerBaseX, beakerY + beakerH, 20, flameSize * 0.7);
    fill(0, 180, 255, 100); // Inner blue
    ellipse(burnerBaseX, beakerY + beakerH, 10, 20);
    pop();
}

function drawIceBath() {
    push();
    fill(0, 200, 255, 40);
    noStroke();
    rect(beakerX - 25, beakerY + beakerH - 40, beakerW + 50, 50, 15);

    // Draw Some Ice Cubes
    fill(255, 255, 255, 180);
    for (let i = 0; i < 6; i++) {
        let ix = beakerX - 15 + i * 40;
        let iy = beakerY + beakerH - 30;
        rect(ix, iy, 15, 15, 3);
        // Highlight on cube
        fill(255, 255, 255, 200);
        rect(ix + 2, iy + 2, 4, 4, 1);
        fill(255, 255, 255, 180);
    }
    pop();
}

function drawFrost() {
    push();
    noStroke();
    fill(255, 255, 255, 40);
    // Beaker shape frost overlay
    rect(beakerX + 4, beakerY + beakerH - liquidLevel, beakerW - 8, liquidLevel, 0, 0, 10, 10);

    // Add some "frost sparks"
    stroke(255, 255, 255, 100);
    strokeWeight(1);
    for (let i = 0; i < 15; i++) {
        let fx = beakerX + noise(i, frameCount * 0.01) * beakerW;
        let fy = (beakerY + beakerH - liquidLevel) + noise(i + 100, frameCount * 0.01) * liquidLevel;
        point(fx, fy);
    }
    pop();
}

/**
 * Add a chemical ingredient to the beaker
 * Fetches the reaction result and updates the UI with student-friendly feedback
 */
async function addIngredient(name, amount) {
    try {
        ingredientsInBeaker.push(name);
        currentVolume += amount;

        let fillPixels = (amount / MAX_VOLUME) * beakerH;
        targetLiquidLevel = Math.min(beakerH - 10, targetLiquidLevel + fillPixels);

        // Get the color of the chemical when added to water
        const colorData = await API.getChemicalColor(name);
        if (colorData && colorData.color) {
            targetLiquidColor = color(colorData.color);
        }

        // Predict what will happen when we mix the chemicals
        const result = await API.react(ingredientsInBeaker, temperatureState, concentrationState);
        if (result) {
            reactionData = result;
            updateUI(result);
            if (result.visual_steps && result.visual_steps.length > 1) {
                startReactionSequence(result.visual_steps);
            } else {
                phaseQueue = []; // Reset queue
                applySymptoms(result);
            }
        }
    } catch (error) {
        showStudentError('Something went wrong while mixing the chemicals. Please try again!');
        // Remove the last ingredient that caused the error
        ingredientsInBeaker.pop();
        currentVolume -= amount;
    }
}

async function updateEnvironment() {
    if (ingredientsInBeaker.length > 0) {
        const result = await API.react(ingredientsInBeaker, temperatureState, concentrationState);
        if (result) {
            reactionData = result;
            updateUI(result);
            if (result.visual_steps && result.visual_steps.length > 1) {
                startReactionSequence(result.visual_steps);
            } else {
                phaseQueue = []; // Reset queue
                applySymptoms(result);
            }
        }
    }
}

function startReactionSequence(steps) {
    phaseQueue = steps;
    currentPhaseIndex = 0;
    applyPhase(phaseQueue[0]);
    phaseTimer = 240;
}

function applyPhase(step) {
    if (step.liquidColor) {
        targetLiquidColor = color(step.liquidColor);
    }

    if (step.equation) {
        document.getElementById('reaction-equation').innerText = step.equation;
    }

    if (step.symptoms) {
        document.getElementById('symptoms-display').innerText = step.symptoms.join(', ');
    }

    applySymptoms(step);
}

/**
 * Update UI with reaction data
 * Shows students what happened in the reaction with clear, educational feedback
 */
function updateUI(data) {
    // Update Results Panel (visible first)
    document.getElementById('reaction-equation').innerText = data.equation || 'No reaction occurred';
    document.getElementById('reaction-type').innerText = data.reaction_type || 'Physical Mixture';
    document.getElementById('ph-display').innerText = (data.ph !== undefined ? data.ph : 'Neutral');
    document.getElementById('symptoms-display').innerText = (data.symptoms && data.symptoms.length > 0)
        ? data.symptoms.join(', ')
        : 'No visible changes';

    // Show the products section with animation
    document.getElementById('products-section').classList.remove('hidden');
    document.getElementById('status-message').className = 'status-active';
    document.getElementById('status-message').innerText = '✓ Reaction detected! Check the results below.';

    // Update Details Panel (for learning)
    document.getElementById('concept-display').innerText = data.concept || 'Chemical Mixture';
    document.getElementById('ai-explanation').innerText = data.explanation || 'This is a simple mixture of chemicals.';
    document.getElementById('safety-tips').innerText = data.safety_tips || 'Always wear safety goggles when handling chemicals.';
    document.getElementById('real-world-example').innerText = data.real_world_example || 'Chemistry is all around us in everyday life!';
}

/**
 * Show student-friendly error messages
 * Converts technical errors into helpful guidance
 */
function showStudentError(message) {
    const banner = document.createElement('div');
    banner.className = 'error-banner';
    banner.innerHTML = `❌ ${message}`;
    document.body.appendChild(banner);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        banner.remove();
    }, 4000);

    console.error(message);
}

function applySymptoms(data) {
    // Stop any existing particle effects
    particles.stop();

    // Reset timers for new reaction
    if (data.reaction_type && data.reaction_type !== 'mixture') {
        reactionTimer = 400; // ~6-7 seconds at 60fps
    } else {
        reactionTimer = 100; // Brief pulse for mixtures
    }

    // Apply liquid color change
    if (data.liquidColor) {
        targetLiquidColor = color(data.liquidColor);
    }

    // Handle animation triggers
    const triggers = data.animation_triggers || {};

    // Activate particle effects based on triggers or particleType
    let pType = data.particleType;
    let pColor = data.particleColor ? color(data.particleColor) : color(255, 255, 255);
    let rgb = [255, 255, 255];
    if (typeof pColor === 'object' && pColor.levels) {
        rgb = [pColor.levels[0], pColor.levels[1], pColor.levels[2]];
    }

    if (triggers.bubbles || pType === 'bubble') {
        particles.setType('bubble', rgb);
    } else if (triggers.precipitate || pType === 'precipitate') {
        particles.setType('precipitate', rgb);
    } else if (triggers.heat) {
        particles.setType('heat', [255, 255, 255]);
    }

    // Fallback for custom particle types
    if (pType && pType !== 'none' && !particles.active) {
        particles.setType(pType, rgb);
    }

    // Handle color change trigger override
    if (triggers.color_change) {
        targetLiquidColor = color(triggers.color_change);
    }
}

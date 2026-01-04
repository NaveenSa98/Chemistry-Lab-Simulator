"""
Hybrid Reaction Engine
Orchestrates rule-based chemistry with AI-powered educational content.

This is the heart of the AI ChemLab simulation. It combines:
1. Deterministic Chemistry Rules (from ChemistryRules)
   - Hardcoded reactions with accurate stoichiometry
   - Visual effects and colors
   - pH values and observable changes

2. LLM Service (from LLMService)
   - AI-generated explanations of what's happening
   - Safety information
   - Real-world applications
   - Chemistry concept labels

The engine processes reactions iteratively - if products can react further,
it calculates the next reaction automatically (cascading reactions).
"""

import logging

# Import backend modules - handle both package and direct execution
try:
    from backend.chemistry_rules import ChemistryRules
    from backend.llm_service import LLMService
except ImportError:
    from chemistry_rules import ChemistryRules
    from llm_service import LLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReactionEngine:
    """
    Main orchestrator for chemistry simulation.

    Combines rule-based chemistry with LLM-generated educational content
    to provide both accurate reactions and engaging explanations.
    """

    def __init__(self):
        """Initialize the reaction engine with chemistry rules and LLM service."""
        self.chemistry_rules = ChemistryRules()  # Database of known reactions
        self.llm_service = LLMService()  # AI service for explanations

    def _should_add_water(self, substances):
        """
        Determine if water should be auto-added for an aqueous reaction.

        NOTE: Water should NOT be auto-added anymore. Users should explicitly add water
        to avoid interfering with reactions like Na + HNO3 (which would otherwise show Na + H2O).

        This method is kept for backwards compatibility but always returns False now.
        Users can add water manually if they need aqueous reactions.

        Args:
            substances (list): List of chemical names (lowercase)

        Returns:
            bool: Always False - users must add water explicitly
        """
        # DISABLED: Auto-water addition was causing issues with reactions like Na + HNO3
        # Users should add water explicitly if they want aqueous reactions
        return False

    def get_initial_color(self, name):
        """
        Get the color a chemical shows when dissolved in water.

        Args:
            name (str): Name of the chemical

        Returns:
            str: Color in hex format (e.g., "#FF0000") or transparent white if unknown

        This helps students see what the beaker looks like when they add
        their first chemical.
        """
        return self.chemistry_rules.initial_colors.get(name.lower(), "#FFFFFF22")

    def predict_reaction(self, ingredients, temperature='room', concentration='dilute'):
        """
        Predict what happens when chemicals are mixed together.

        This is the core of the simulation. It:
        1. Checks if ingredients react according to chemistry rules
        2. Calculates products and visual effects
        3. Checks if products react further (cascading reactions)
        4. Adds AI-generated explanations for each reaction
        5. Returns complete reaction data for visualization

        Args:
            ingredients (list): Names of chemicals being mixed
            temperature (str): 'room', 'hot', or 'cold'
            concentration (str): 'dilute' or 'concentrated'

        Returns:
            dict: Complete reaction prediction with:
            - equation: Chemical equation
            - products: List of products formed
            - reaction_type: Type of reaction (acid-base, redox, etc.)
            - animation_triggers: Visual effects to show
            - explanation: AI-generated explanation
            - safety_tips: Safety information
            - real_world_example: Real-world application
            - And more...

        Example:
            >>> engine = ReactionEngine()
            >>> result = engine.predict_reaction(
            ...     ['sulfuric acid', 'sodium hydroxide'],
            ...     temperature='room',
            ...     concentration='dilute'
            ... )
            >>> print(result['equation'])
            H2SO4 + 2NaOH → Na2SO4 + 2H2O
        """
        if not ingredients:
            return {"error": "No ingredients provided"}

        # Normalize ingredient names for lookup
        current_substances = [i.lower().strip() for i in ingredients]

        # AUTO-ADD WATER FOR AQUEOUS REACTIONS
        # If not already present, add water for most common aqueous reactions
        should_add_water = self._should_add_water(current_substances)
        if should_add_water and "water" not in current_substances:
            current_substances.append("water")
            logger.info(f"Auto-added water for aqueous reaction: {current_substances}")

        reaction_history = []  # Track all reactions that happen
        visual_steps = []  # Animation steps for the frontend
        max_iterations = 5  # Prevent infinite loops from cascading reactions

        logger.info(f"Starting reaction simulation with: {current_substances}")
        
        # CASCADING REACTIONS: Keep checking if products react further
        iteration = 0
        while iteration < max_iterations:
            iteration += 1

            # STEP 1: Check if any of the current substances react with each other
            reaction_data = self.chemistry_rules.predict_reaction(
                current_substances,
                temperature=temperature,
                concentration=concentration
            )

            # No reaction found - exit the loop
            if not reaction_data or reaction_data.get("reaction_type") == "no_reaction":
                break

            # STEP 2: A reaction was found!
            reaction_history.append(reaction_data)

            # STEP 3: Find which specific reactants from our rules matched
            # This helps us know which substances to remove from current_substances
            matched_reactants = []
            for r_key in self.chemistry_rules.reactions.keys():
                if set(r_key).issubset(set(current_substances)):
                    potential_data = self.chemistry_rules.reactions[r_key]
                    # Check if there are condition-specific reaction rules
                    if "conditions" in potential_data:
                        potential_data = potential_data["conditions"].get(
                            f"{temperature}_{concentration}",
                            potential_data["conditions"].get("room_dilute")
                        )

                    if potential_data == reaction_data:
                        matched_reactants = list(r_key)
                        break

            if not matched_reactants:
                break

            # STEP 4: Prepare visual animation step for the frontend
            visual_steps.append({
                "equation": reaction_data.get("equation"),
                "animation_triggers": reaction_data.get("animation_triggers"),
                "liquidColor": reaction_data.get("liquid_color"),
                "particleType": reaction_data.get("particle_type"),
                "particleColor": reaction_data.get("particle_color"),
                "symptoms": reaction_data.get("visual_effects", [])
            })

            # STEP 5: Update the substances list for the next iteration
            # Remove reactants that were consumed
            for r in matched_reactants:
                if r in current_substances:
                    current_substances.remove(r)

            # Add the products formed
            current_substances.extend([p.lower() for p in reaction_data.get("products", [])])
            logger.info(f"Iteration {iteration} result: {current_substances}")

        # STEP 6: Determine primary reaction for UI display
        # If no reactions happened, use default response
        if not reaction_history:
            reaction_data = self.chemistry_rules.get_default_response(ingredients)
        else:
            # Use the LAST (most recent) reaction for primary UI display
            # Earlier reactions are shown in visual_steps animation
            reaction_data = reaction_history[-1]

        # STEP 7: GENERATIVE LAYER - Get AI explanations
        # Pass the full reaction history so AI can explain what happened
        educational_content = self.llm_service.generate_educational_content(
            reaction_data,
            ingredients,
            temperature=temperature,
            concentration=concentration,
            history=[r.get("equation") for r in reaction_history]  # All equations
        )

        # STEP 8: Merge data into final response
        viz = educational_content.get("visual_metadata", {})

        # Combine visual triggers: Hardcoded chemistry rules take priority
        triggers = reaction_data.get("animation_triggers", {})
        final_triggers = {
            "bubbles": triggers.get("bubbles", viz.get("bubbles", False)),
            "precipitate": triggers.get("precipitate", viz.get("precipitate", False)),
            "heat": triggers.get("heat", viz.get("heat", False)),
            "color_change": triggers.get("color_change", viz.get("color_change", None))
        }

        # Determine what particle effect to show
        p_type = reaction_data.get("particle_type", "none")
        if p_type == "none":
            # Auto-select particle type based on triggers
            if final_triggers["bubbles"]:
                p_type = "bubble"  # Gas being released
            elif final_triggers["precipitate"]:
                p_type = "precipitate"  # Solid forming

        # STEP 9: Build final response for frontend
        response = {
            # Chemical equation
            "equation": viz.get("equation") if viz.get("equation") else reaction_data.get("equation", ""),

            # Final list of substances in the beaker
            "products": list(set(current_substances)),

            # pH of the final mixture
            "ph": reaction_data.get("ph_value", 7),

            # Observable changes (color, bubbles, heat, etc.)
            "symptoms": reaction_data.get("visual_effects", []),

            # Type of reaction (acid-base, synthesis, decomposition, etc.)
            "reaction_type": reaction_data.get("reaction_type", "mixture"),

            # Visual triggers for animations
            "animation_triggers": final_triggers,

            # Color the liquid should turn
            "liquidColor": final_triggers["color_change"] or reaction_data.get("liquid_color", "#FFFFFF33"),

            # Type of particles to show (bubbles, precipitate, etc.)
            "particleType": p_type,

            # Color of the particles
            "particleColor": reaction_data.get("particle_color", "#FFFFFF"),

            # Steps for cascading animation
            "visual_steps": visual_steps,

            # AI-GENERATED EDUCATIONAL CONTENT
            "explanation": educational_content.get("explanation", ""),
            "safety_tips": educational_content.get("safety_tips", ""),
            "concept": educational_content.get("concept", ""),
            "real_world_example": educational_content.get("real_world_example", "")
        }

        return response
    
    def get_explanation(self, reaction_data):
        """Legacy method for compatibility."""
        return reaction_data.get("explanation", "No explanation available.")

"""
Rule-based Chemistry Engine
Provides deterministic chemical reaction predictions.
"""

class ChemistryRules:
    def __init__(self):
        self.reactions = self._build_reaction_database()
    
    def _build_initial_colors(self):
        """Standard colors for chemicals when first added to water."""
        return {
            "potassium permanganate": "#800080AA",  # Purple
            "copper sulfate": "#0000FFAA",         # Blue
            "iron(iii) chloride": "#DAA520AA",     # Golden/Yellow
            "cobalt(ii) chloride": "#FF1493AA",    # Pinkish
            "nickel(ii) sulfate": "#00FF00AA",     # Green
            "potassium dichromate": "#FF8C00AA",   # Orange
            "methyl orange": "#FFA500AA",          # Orange
            "bromothymol blue": "#0064FFAA",       # Blue
            "red cabbage extract": "#4B0082AA",    # Purple-ish
            "iodine": "#8B4513AA",                  # Brown
        }

    def _build_reaction_database(self):
        """Database of known chemical reactions with their properties."""
        self.initial_colors = self._build_initial_colors()
        return {
            # Acid-Base Neutralizations
            ("hydrochloric acid", "sodium hydroxide"): {
                "equation": "HCl(aq) + NaOH(aq) → NaCl(aq) + H₂O(l)",
                "products": ["NaCl", "H2O"],
                "ph_value": 7,
                "ph_change": "neutralizes",
                "visual_effects": ["no_visible_change", "heat_released"],
                "reaction_type": "neutralization",
                "animation_triggers": {
                    "bubbles": False,
                    "precipitate": False,
                    "color_change": "#FFFFFF22",
                    "heat": True
                },
                "liquid_color": "#FFFFFF22",
                "particle_type": "none"
            },
            
            # Gas Evolution
            ("acetic acid", "sodium bicarbonate"): {
                "equation": "CH₃COOH(aq) + NaHCO₃(s) → CH₃COONa(aq) + H₂O(l) + CO₂(g)",
                "products": ["CH3COONa", "H2O", "CO2"],
                "ph_value": 8.5,
                "ph_change": "increases",
                "visual_effects": ["rapid_bubbling", "gas_evolution"],
                "reaction_type": "acid_carbonate",
                "animation_triggers": {
                    "bubbles": True,
                    "precipitate": False,
                    "color_change": "#FFFFFF44",
                    "heat": False
                },
                "liquid_color": "#FFFFFF44",
                "particle_type": "bubble",
                "particle_color": "#FFFFFF"
            },
            
            # Specific colorful ones
            ("potassium permanganate", "sodium hydroxide"): {
                "equation": "2KMnO₄(aq) + 2NaOH(aq) → K₂MnO₄(aq) + Na₂MnO₄(aq) + H₂O(l) + O₂(g)",
                "products": ["potassium manganate", "sodium manganate", "oxygen", "water"],
                "ph_value": 13,
                "ph_change": "basic",
                "visual_effects": ["purple_to_green_change"],
                "reaction_type": "redox",
                "animation_triggers": {
                    "bubbles": True,
                    "precipitate": False,
                    "color_change": "#228B22AA", # Turns green
                    "heat": False
                },
                "liquid_color": "#228B22AA",
                "particle_type": "bubble",
                "particle_color": "#FFFFFF"
            },
            
            # Displacement Reactions
            ("copper sulfate", "iron"): {
                "equation": "Fe(s) + CuSO₄(aq) → FeSO₄(aq) + Cu(s)",
                "products": ["iron sulfate", "copper"],
                "ph_value": 5.5,
                "visual_effects": ["blue_color_fading", "reddish_brown_solid_forming"],
                "reaction_type": "single_displacement",
                "animation_triggers": {
                    "bubbles": False,
                    "precipitate": True,
                    "color_change": "#90EE9077", # Pale green (FeSO4)
                    "heat": False
                },
                "liquid_color": "#90EE9077",
                "particle_type": "precipitate",
                "particle_color": "#B87333" # Copper color (reddish-brown)
            },

            ("hydrochloric acid", "zinc"): {
                "equation": "Zn(s) + 2HCl(aq) → ZnCl₂(aq) + H₂(g)",
                "products": ["zinc chloride", "hydrogen"],
                "ph_value": 4,
                "visual_effects": ["vigorous_bubbling", "zinc_dissolving"],
                "reaction_type": "single_displacement",
                "animation_triggers": {
                    "bubbles": True,
                    "precipitate": False,
                    "color_change": "#FFFFFF22",
                    "heat": True
                },
                "liquid_color": "#FFFFFF22",
                "particle_type": "bubble",
                "particle_color": "#FFFFFF"
            },
            
            # Precipitation Reactions
            ("copper sulfate", "sodium hydroxide"): {
                "equation": "CuSO₄(aq) + 2NaOH(aq) → Cu(OH)₂(s) + Na₂SO₄(aq)",
                "products": ["copper hydroxide", "sodium sulfate"],
                "ph_value": 11,
                "ph_change": "increases",
                "visual_effects": ["blue_precipitate"],
                "reaction_type": "precipitation",
                "animation_triggers": {
                    "bubbles": False,
                    "precipitate": True,
                    "color_change": "#0064FFAA",
                    "heat": False
                },
                "liquid_color": "#0064FFAA",
                "particle_type": "precipitate",
                "particle_color": "#00BFFF"
            },
            
            ("lead nitrate", "potassium iodide"): {
                "equation": "Pb(NO₃)₂(aq) + 2KI(aq) → PbI₂(s) + 2KNO₃(aq)",
                "products": ["lead iodide", "potassium nitrate"],
                "ph_value": 7,
                "ph_change": "neutral",
                "visual_effects": ["yellow_precipitate"],
                "reaction_type": "precipitation",
                "animation_triggers": {
                    "bubbles": False,
                    "precipitate": True,
                    "color_change": "#FFD700AA",
                    "heat": False
                },
                "liquid_color": "#FFD700AA",
                "particle_type": "precipitate",
                "particle_color": "#FFD700"
            },
            
            # Transition Metal + Acid (Conditional)
            ("copper", "sulfuric acid"): {
                "conditions": {
                    "hot_concentrated": {
                        "equation": "Cu(s) + 2H₂SO₄(conc) → CuSO₄(aq) + SO₂(g) + 2H₂O(l)",
                        "products": ["copper sulfate", "sulfur dioxide", "water"],
                        "ph_value": 1,
                        "visual_effects": ["blue_color_evolution", "vigorous_bubbling", "gas_evolution"],
                        "reaction_type": "redox",
                        "animation_triggers": {
                            "bubbles": True,
                            "precipitate": False,
                            "heat": True,
                            "color_change": "#0000FFAA",
                            "gas_smoke": True
                        },
                        "liquid_color": "#0000FFAA",
                        "particle_type": "smoke",
                        "particle_color": "#E0E0E0"
                    },
                    "room_dilute": {
                        "equation": "Cu(s) + H₂SO₄(dilute) → No Reaction",
                        "products": ["copper", "sulfuric acid"],
                        "ph_value": 1,
                        "visual_effects": ["no_observable_change"],
                        "reaction_type": "no_reaction",
                        "animation_triggers": {
                            "bubbles": False,
                            "precipitate": False,
                            "heat": False,
                            "gas_smoke": False
                        },
                        "liquid_color": "#FFFFFF11",
                        "particle_type": "none"
                    }
                }
            },
            
            # Indicator Reactions
            ("phenolphthalein", "sodium hydroxide"): {
                "equation": "Phenolphthalein(aq) + NaOH(aq) → Pink Complex(aq)",
                "products": ["pink complex"],
                "ph_value": 10,
                "ph_change": "basic",
                "visual_effects": ["vivid_pink_color"],
                "reaction_type": "indicator",
                "animation_triggers": {
                    "bubbles": False,
                    "precipitate": False,
                    "color_change": "#FF1493AA",
                    "heat": False
                },
                "liquid_color": "#FF1493AA",
                "particle_type": "none"
            },

            # AQUEOUS REACTIONS: Reactions with water
            ("sodium", "water"): {
                "conditions": {
                    "room_dilute": {
                        "equation": "2Na(s) + 2H₂O(l) → 2NaOH(aq) + H₂(g)",
                        "products": ["sodium hydroxide", "hydrogen"],
                        "ph_value": 14,
                        "visual_effects": ["vigorous_reaction", "hydrogen_bubbles", "exothermic"],
                        "reaction_type": "single_displacement",
                        "animation_triggers": {
                            "bubbles": True,
                            "precipitate": False,
                            "color_change": "#FFFFFF22",
                            "heat": True
                        },
                        "liquid_color": "#FFFFFF22",
                        "particle_type": "bubble",
                        "particle_color": "#FFFFFF"
                    },
                    "room_concentrated": {
                        "equation": "2Na(s) + 2H₂O(l) → 2NaOH(aq) + H₂(g)",
                        "products": ["sodium hydroxide", "hydrogen"],
                        "ph_value": 14,
                        "visual_effects": ["violent_reaction", "hydrogen_bubbles", "exothermic"],
                        "reaction_type": "single_displacement",
                        "animation_triggers": {
                            "bubbles": True,
                            "precipitate": False,
                            "color_change": "#FFFFFF22",
                            "heat": True
                        },
                        "liquid_color": "#FFFFFF22",
                        "particle_type": "bubble",
                        "particle_color": "#FFFFFF"
                    }
                }
            },

            # Sodium with nitric acid (concentration dependent)
            ("sodium", "nitric acid"): {
                "conditions": {
                    "room_dilute": {
                        "equation": "8Na + 30HNO₃(dilute) → 8NaNO₃ + 3NH₄NO₃ + 9H₂O",
                        "products": ["sodium nitrate", "ammonium nitrate", "water"],
                        "ph_value": 4,
                        "visual_effects": ["vigorous_reaction", "brown_fumes", "heat_released"],
                        "reaction_type": "redox",
                        "animation_triggers": {
                            "bubbles": True,
                            "precipitate": False,
                            "color_change": "#FFD700AA",
                            "heat": True,
                            "gas_smoke": True
                        },
                        "liquid_color": "#FFD700AA",
                        "particle_type": "smoke",
                        "particle_color": "#8B4513"
                    },
                    "room_concentrated": {
                        "equation": "Na + HNO₃(conc) → NaNO₃ + NO₂(g) + H₂O",
                        "products": ["sodium nitrate", "nitrogen dioxide", "water"],
                        "ph_value": 2,
                        "visual_effects": ["vigorous_reaction", "brown_red_gas", "exothermic"],
                        "reaction_type": "redox",
                        "animation_triggers": {
                            "bubbles": True,
                            "precipitate": False,
                            "color_change": "#8B4513AA",
                            "heat": True,
                            "gas_smoke": True
                        },
                        "liquid_color": "#8B4513AA",
                        "particle_type": "smoke",
                        "particle_color": "#8B4513"
                    },
                    "hot_concentrated": {
                        "equation": "Na + HNO₃(conc) → NaNO₃ + NO₂(g) + H₂O",
                        "products": ["sodium nitrate", "nitrogen dioxide", "water"],
                        "ph_value": 1,
                        "visual_effects": ["violent_reaction", "brown_red_dense_gas"],
                        "reaction_type": "redox",
                        "animation_triggers": {
                            "bubbles": True,
                            "precipitate": False,
                            "color_change": "#654321AA",
                            "heat": True,
                            "gas_smoke": True
                        },
                        "liquid_color": "#654321AA",
                        "particle_type": "smoke",
                        "particle_color": "#8B4513"
                    }
                }
            },

            # Additional gas-producing reactions with proper visualization
            ("magnesium", "hydrochloric acid"): {
                "equation": "Mg(s) + 2HCl(aq) → MgCl₂(aq) + H₂(g)",
                "products": ["magnesium chloride", "hydrogen"],
                "ph_value": 3,
                "visual_effects": ["vigorous_bubbling", "magnesium_dissolving", "gas_evolution"],
                "reaction_type": "single_displacement",
                "animation_triggers": {
                    "bubbles": True,
                    "precipitate": False,
                    "color_change": "#FFFFFF22",
                    "heat": True
                },
                "liquid_color": "#FFFFFF22",
                "particle_type": "bubble",
                "particle_color": "#FFFFFF"
            },

            # Carbonate reactions with proper gas visualization
            ("calcium carbonate", "hydrochloric acid"): {
                "equation": "CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g)",
                "products": ["calcium chloride", "water", "carbon dioxide"],
                "ph_value": 5,
                "visual_effects": ["vigorous_bubbling", "effervescence", "gas_evolution"],
                "reaction_type": "acid_carbonate",
                "animation_triggers": {
                    "bubbles": True,
                    "precipitate": False,
                    "color_change": "#FFFFFF22",
                    "heat": False
                },
                "liquid_color": "#FFFFFF22",
                "particle_type": "bubble",
                "particle_color": "#FFFFFF"
            },
        }
    
    def predict_reaction(self, ingredients, temperature='room', concentration='dilute'):
        """
        Predict reaction based on ingredients and conditions.
        """
        # Normalize ingredient names
        normalized = tuple(sorted([i.lower().strip() for i in ingredients]))
        
        # Check for exact matches
        reaction_entry = None
        if normalized in self.reactions:
            reaction_entry = self.reactions[normalized]
        else:
            # Check for subset matches
            for key in self.reactions.keys():
                if set(key).issubset(set(normalized)):
                    reaction_entry = self.reactions[key]
                    break
        
        if not reaction_entry:
            return None

        # Handle Conditional Reactions
        if "conditions" in reaction_entry:
            cond_key = f"{temperature}_{concentration}"
            return reaction_entry["conditions"].get(cond_key, reaction_entry["conditions"].get("room_dilute"))
        
        return reaction_entry
    
    def get_default_response(self, ingredients):
        """Default response when no specific reaction is found.

        Note: This returns None for animation_triggers to signal that
        the LLM's visual metadata should be used instead of hardcoded values.
        This allows the AI to intelligently detect gas evolution, precipitates,
        and other visual effects for reactions not in the database.
        """
        return {
            "equation": f"Mixture of {', '.join(ingredients)}",
            "products": ingredients,
            "ph_value": 7,
            "ph_change": "neutral",
            "visual_effects": ["mixing_observed"],
            "reaction_type": "mixture",
            "animation_triggers": None,  # Let LLM determine visual effects
            "liquid_color": "#FFFFFF33",
            "particle_type": "none"
        }

"""
Chemical Categorization Service using LLM
Uses Google Gemini 2.0 Flash to categorize chemicals into appropriate categories.
Previously used: Groq LLaMA 3.1 8B
Switched to: Google Gemini 2.0 Flash (better chemistry knowledge, free, integrated with explanations)
"""

import os
import json
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChemicalCategorizer:
    """LLM-based chemical categorization service using Google Gemini 2.0 Flash."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model = "gemini-2.0-flash"
            logger.info("✓ Using Google Gemini 2.0 Flash for chemical categorization")
        else:
            logger.warning("GOOGLE_API_KEY not found. Categorization will use fallback logic.")
            self.client = None
    
    def categorize(self, name, formula, iupac_name=None):
        """
        Categorize a chemical into one of: acids, bases, salts, indicators, solids

        Args:
            name: Common name of the chemical
            formula: Molecular formula
            iupac_name: IUPAC name (optional)

        Returns:
            str: Category (acids, bases, salts, indicators, solids)
        """
        if not self.client:
            return self._fallback_categorize(name, formula)

        prompt = self._build_prompt(name, formula, iupac_name)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(prompt)]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                    system_instruction="You are a chemistry expert. Categorize chemicals accurately. Respond only with valid JSON."
                )
            )

            content = json.loads(response.text)
            category = content.get("category", "salts").lower()
            
            # Validate category
            valid_categories = ['acids', 'bases', 'salts', 'indicators', 'solids', 'gases', 'ions']
            if category not in valid_categories:
                logger.warning(f"Invalid category '{category}' for {name}, using fallback")
                return self._fallback_categorize(name, formula)
            
            logger.info(f"Categorized '{name}' as '{category}'")
            return category
            
        except Exception as e:
            logger.error(f"Error categorizing {name}: {e}")
            return self._fallback_categorize(name, formula)
    
    def _build_prompt(self, name, formula, iupac_name):
        """Build the LLM prompt for categorization."""
        return f"""
Categorize this chemical into ONE of these categories: acids, bases, salts, indicators, solids, gases, ions

Chemical Information:
- Name: {name}
- Formula: {formula}
{f'- IUPAC Name: {iupac_name}' if iupac_name else ''}

Categories:
- acids: Compounds that donate H+ ions (e.g., HCl, H2SO4, acetic acid)
- bases: Compounds that accept H+ or donate OH- ions (e.g., NaOH, NH3, carbonates)
- salts: Ionic compounds formed from neutralization (e.g., NaCl, CuSO4, AgNO3)
- indicators: pH indicators that change color (e.g., phenolphthalein, litmus, methyl orange)
- solids: Pure elemental metals (e.g., Zn, Mg, Fe, Cu, Al)
- gases: Gaseous substances at room temperature (e.g., NH3, Cl2, H2, O2)
- ions: Individual charged species (e.g., CO3^2-, I-, Co2+, NH4+, Cl-)

Respond in JSON format:
{{"category": "acids|bases|salts|indicators|solids|gases|ions", "reasoning": "brief explanation"}}
"""
    
    def _fallback_categorize(self, name, formula):
        """Fallback categorization based on simple rules."""
        name_lower = name.lower()
        formula_lower = formula.lower() if formula else ""
        
        # Check for acids
        if any(acid in name_lower for acid in ['acid', 'vinegar']):
            return 'acids'
        if formula and (formula.startswith('H') and any(x in formula for x in ['Cl', 'SO', 'NO', 'PO', 'CO'])):
            return 'acids'
        
        # Check for bases
        if 'hydroxide' in name_lower or 'ammonia' in name_lower:
            return 'bases'
        if formula and ('OH' in formula or formula == 'NH3'):
            return 'bases'
        if any(base in name_lower for base in ['soda', 'carbonate', 'bicarbonate']):
            return 'bases'
        
        # Check for indicators
        if any(ind in name_lower for ind in ['indicator', 'phenolphthalein', 'litmus', 'methyl', 'bromothymol']):
            return 'indicators'
        
        # Check for pure metals (solids)
        metals = ['zinc', 'magnesium', 'iron', 'copper', 'aluminum', 'sodium', 'calcium', 'zn', 'mg', 'fe', 'cu', 'al', 'na', 'ca']
        if formula and len(formula) <= 3 and formula.isalpha():
            if any(metal == formula_lower for metal in metals):
                return 'solids'
        
        # Check for gases
        gases = ['ammonia', 'chlorine', 'hydrogen', 'oxygen', 'nitrogen', 'methane', 'propane', 'butane', 'nh3', 'cl2', 'h2', 'o2', 'n2', 'ch4']
        if any(gas in name_lower for gas in gases) or any(gas == formula_lower for gas in gases):
            return 'gases'
            
        # Check for ions
        if 'ion' in name_lower or any(c in formula for c in ['+', '-']) if formula else False:
            return 'ions'
            
        # Default to salts
        return 'salts'

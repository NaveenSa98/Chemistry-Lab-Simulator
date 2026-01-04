"""
LLM Service for Educational Content Generation
Uses Google Gemini 2.0 Flash for explanations and safety tips (FREE - 1M tokens/day).
Previously used: Groq LLaMA 3.1 8B, then google.generativeai (deprecated)
Now uses: Google Gemini 2.0 Flash via google.genai SDK (better chemistry accuracy, completely free)
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

class LLMService:
    """
    LLM Service using Google Gemini 2.0 Flash (Free tier: 1M tokens/day).

    Benefits:
    ✓ Latest chemistry knowledge and accuracy
    ✓ Better stoichiometry understanding
    ✓ Understands concentration-dependent reactions
    ✓ Free tier is generous (1M tokens/day)
    ✓ Better safety information generation
    ✓ Uses stable google.genai SDK (replaces deprecated google.generativeai)
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-2.0-flash'
            logger.info("✓ Using Google Gemini 2.0 Flash (FREE tier)")
        else:
            logger.warning("❌ GOOGLE_API_KEY not found. LLM features will be disabled.")
            self.client = None
            self.model_name = None

    def generate_educational_content(self, reaction_data, ingredients, temperature='room', concentration='dilute', history=None):
        """
        Generate educational explanation considering reaction history.
        Uses Google Gemini 2.0 Flash for better chemistry accuracy.
        """
        if not self.client:
            logger.warning("LLM client not available, using fallback content")
            return self._get_fallback_content(reaction_data)

        prompt = self._build_prompt(reaction_data, ingredients, temperature, concentration, history)

        try:
            # Google Gemini API call using google.genai SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=600
                )
            )

            # Parse JSON from response
            response_text = response.text

            # Try to extract JSON from response
            try:
                # Find JSON in response (sometimes model adds extra text)
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    content = json.loads(json_match.group())
                else:
                    content = json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Gemini response as JSON: {response_text}")
                return self._get_fallback_content(reaction_data)

            return {
                "explanation": content.get("explanation", ""),
                "safety_tips": content.get("safety_tips", ""),
                "concept": content.get("concept", ""),
                "real_world_example": content.get("real_world_example", ""),
                "visual_metadata": {
                    "bubbles": content.get("bubbles", False),
                    "precipitate": content.get("precipitate", False),
                    "heat": content.get("heat", False),
                    "color_change": content.get("color_change", None),
                    "equation": content.get("equation", "")
                }
            }

        except Exception as e:
            logger.error(f"Error calling Google Gemini API: {e}")
            logger.error(f"Details: {str(e)}")
            return self._get_fallback_content(reaction_data)
    
    def _build_prompt(self, reaction_data, ingredients, temperature='room', concentration='dilute', history=None):
        """
        Build improved prompt for Google Gemini 2.0 Flash with chemistry-specific instructions.

        Gemini 2.0 Flash has superior chemistry knowledge, allowing detailed instructions.
        """
        history_text = ""
        if history and len(history) > 1:
            history_text = f"\n- Step-by-step Reaction History: {' -> '.join(history)}"

        return f"""You are an expert chemistry education assistant. Provide comprehensive, detailed explanations suitable for high school and early college students.

REACTION DATA:
- Initial Ingredients: {', '.join(ingredients)}
- Chemical Equation: {reaction_data.get('equation', 'Unknown')}
- Reaction Type: {reaction_data.get('reaction_type', 'Unknown')}
- Conditions: Temperature = {temperature}, Concentration = {concentration}{history_text}
- Observable Effects: {', '.join(reaction_data.get('visual_effects', []))}
- Final pH: {reaction_data.get('ph_value', 7)}

INSTRUCTION - Provide DETAILED Chemistry Education:
Explain this reaction with sufficient depth and detail. Include:
- What is happening at the molecular level
- Why the reactants combine in this way
- The role of concentration and temperature
- What students should observe and why
- How this relates to broader chemistry concepts

RESPOND WITH VALID JSON ONLY (no extra text before or after):
{{
  "explanation": "Comprehensive explanation (4-6 sentences). Start with WHAT happens, then WHY at the molecular/ionic level, then discuss conditions and observable changes. Make it educational and detailed for students learning this concept.",
  "safety_tips": "Specific, practical safety precautions for these chemicals (2-3 sentences). Explain what hazards exist and what protective measures are needed.",
  "concept": "The chemistry concept name and a detailed description (2-3 sentences). Explain what type of reaction this is, why it's classified that way, and what makes it significant. Example format: 'Redox Reaction - A reaction involving transfer of electrons between reactants, where one substance is oxidized and another is reduced, causing change in oxidation states.'",
  "real_world_example": "A detailed practical application (2-3 sentences). Explain how and why this reaction is used in industry, medicine, or everyday life, and what makes it important.",
  "bubbles": true or false (gas evolution),
  "precipitate": true or false (solid formation),
  "heat": true or false (exothermic process),
  "color_change": "hex color like #FF0000 or null",
  "equation": "the balanced chemical equation"
}}

QUALITY REQUIREMENTS:
- Be thorough and educational, not superficial
- Use correct chemistry terminology
- Explain the WHY, not just the WHAT
- Make concepts accessible to students while maintaining accuracy
- Include relevant details about molecular interactions"""
    
    def _get_fallback_content(self, reaction_data):
        """Fallback content when LLM is unavailable - provides detailed explanations."""
        reaction_type = reaction_data.get('reaction_type', 'mixture')

        fallback_map = {
            "neutralization": {
                "explanation": "In a neutralization reaction, an acid (H+ donor) reacts with a base (OH- donor) to form salt and water. The H+ ions from the acid combine with OH- ions from the base, producing water and ionic salts. The solution becomes less acidic or basic, approaching neutral pH 7, and typically releases heat energy (exothermic). This is a fundamental acid-base reaction in chemistry.",
                "safety_tips": "Always add acid to base slowly (never the reverse) to prevent violent reactions and splashing. Wear goggles and gloves. If you spill acid or base, neutralize with the opposite substance before cleanup. Use proper ventilation.",
                "concept": "Acid-Base Neutralization Reaction - An exothermic reaction where hydrogen ions (H+) from an acid combine with hydroxide ions (OH-) from a base to form water and a salt. This balances pH and is essential in chemistry and industry.",
                "real_world_example": "Antacids (like calcium carbonate or sodium bicarbonate) neutralize excess stomach acid to relieve heartburn. Industrial acid-base neutralization is used in water treatment to adjust pH levels in drinking water and wastewater."
            },
            "single_displacement": {
                "explanation": "In a displacement reaction, a more reactive element replaces a less reactive element in a compound. The reactivity of metals follows a predictable order - more reactive metals can displace less reactive metals from their salts or acids. This occurs because the more reactive metal has a stronger tendency to lose electrons and form positive ions, driving the reaction forward.",
                "safety_tips": "Handle reactive metals carefully as they can react violently with water or acid. Never touch reactive metals with bare hands. Dispose of metal salts and unreacted metals according to chemical waste guidelines. Work in a well-ventilated area or fume hood.",
                "concept": "Single Displacement (Substitution) Reaction - A reaction where a more reactive element displaces a less reactive element from a compound, based on relative reactivity. This demonstrates the electrochemical series and electron transfer principles in redox reactions.",
                "real_world_example": "The extraction of pure metals from ores uses displacement principles - for example, carbon displaces metals from their oxides in industrial smelting. Galvanizing (coating steel with zinc) protects against rust through displacement chemistry. Cathodic protection in pipelines uses similar displacement principles."
            },
            "precipitation": {
                "explanation": "A precipitation reaction occurs when two soluble ionic compounds combine to form an insoluble solid (precipitate) that separates from the solution. The insoluble product forms because the ions have reduced solubility when combined, exceeding the solubility product constant. The precipitate settles out as a distinct solid phase, while the solution retains dissolved ions.",
                "safety_tips": "Avoid skin contact with precipitates as some are toxic. Use appropriate gloves and eye protection. Some precipitates (like barium sulfate) are harmless, while others require careful disposal. Always wash hands after handling and dispose of chemical waste in designated containers.",
                "concept": "Precipitation Reaction - A reaction between soluble ionic compounds that produces an insoluble solid (precipitate) when ions combine. The driving force is the formation of a compound with low solubility, and these reactions are essential for analytical chemistry and industrial processes.",
                "real_world_example": "Water treatment plants use precipitation reactions to remove hardness (calcium and magnesium ions) and contaminating ions. In analytical chemistry, precipitation is used to identify and quantify specific ions. Photography and pharmaceutical manufacturing rely on precipitation for product purification."
            },
            "redox": {
                "explanation": "A redox (reduction-oxidation) reaction involves the transfer of electrons between reactants. One reactant is oxidized (loses electrons) while another is reduced (gains electrons). Oxidation states change as electrons transfer, and the number of electrons lost must equal the number gained. These reactions release or absorb energy depending on whether bonds are broken or formed.",
                "safety_tips": "Many redox reactions are vigorous and can release significant heat or gases. Ensure proper ventilation, use appropriate glassware, and never mix incompatible oxidizing and reducing agents. Always follow proper chemical handling procedures and safety guidelines.",
                "concept": "Redox (Oxidation-Reduction) Reaction - A reaction where electrons are transferred from one reactant (reducing agent) to another (oxidizing agent), causing changes in oxidation states. These reactions are fundamental to chemistry, including combustion, corrosion, and photosynthesis.",
                "real_world_example": "Combustion reactions are redox reactions that power engines and generate electricity. Cellular respiration (oxidizing glucose) provides energy for all living organisms. Batteries and fuel cells operate through controlled redox reactions to generate electrical energy."
            }
        }

        return fallback_map.get(reaction_type, {
            "explanation": "These substances are being mixed together. Observe any changes in color, temperature, physical state, or other properties. Even if no obvious reaction occurs, molecular interactions may be happening at the particulate level that aren't easily visible.",
            "safety_tips": "Always wear appropriate personal protective equipment (goggles, gloves, lab coat). Work in a well-ventilated area. Read safety data sheets for all chemicals before handling. Know the location of emergency equipment.",
            "concept": "Chemical Mixture or Interaction - A combination of substances that may or may not undergo observable chemical changes. Understanding interactions between substances is fundamental to chemistry.",
            "real_world_example": "Understanding how different chemicals interact is essential in pharmacy, food science, environmental remediation, and countless industrial processes where controlled mixing produces desired products."
        })

"""
Utility to format chemical formulas from Hill System (alphabetical) notation 
to common laboratory chemical notation.
"""

COMMON_MAP = {
    "ClH": "HCl",
    "H2O4S": "H2SO4",
    "H4N2": "N2H4",
    "H3N": "NH3",
    "H4O2S": "H2SO4", # Some variants
    "HNaO": "NaOH",
    "HKO": "KOH",
    "H3O4P": "H3PO4",
    "H2O": "H2O",
    "H2O2": "H2O2",
    "CH4": "CH4",
    "CH2O2": "HCOOH", # Formic acid
    "C2H4O2": "CH3COOH", # Acetic acid
    "C6H8O7": "C6H8O7", # Citric acid (stay same but often represented differently)
    "ClNa": "NaCl",
    "IK": "KI",
    "ClK": "KCl",
    "O2S": "SO2",
    "O3S": "SO3",
}

def format_formula(formula, name=""):
    """
    Converts a Hill System formula to a common representation.
    If name is provided, can be used for more specific mapping.
    """
    if not formula:
        return name or "Unknown"
        
    # Check specific map
    if formula in COMMON_MAP:
        return COMMON_MAP[formula]
        
    # Handle simple acids (binary) - Hill puts H first unless C is present
    # But for HCl, Hill puts Cl first (ClH).
    # If it ends in H and doesn't contain C, it might be an acid Hill-flipped.
    if formula.endswith('H') and 'C' not in formula:
        # e.g., ClH -> HCl, FH -> HF, BrH -> HBr
        return 'H' + formula[:-1]
        
    return formula

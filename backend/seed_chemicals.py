"""
Hardcoded & Dynamic Seed Script
Seeds 20 specific chemicals per category and discovers others.
"""

import logging
import sys
from database import Database
from pubchem_service import PubChemService
from chemical_categorizer import ChemicalCategorizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of 20 hardcoded chemicals per category (to ensure a core library)
CORE_CHEMICALS = {
    "liquids": [
        "Water"  # Essential solvent - add first so users can manually add water to beaker
    ],
    "acids": [
        "Hydrochloric acid", "Sulfuric acid", "Nitric acid", "Acetic acid",
        "Citric acid", "Phosphoric acid", "Formic acid", "Carbonic acid",
        "Boric acid", "Oxalic acid", "Hydrofluoric acid", "Benzoic acid",
        "Tartaric acid", "Malic acid", "Lactic acid", "Salicylic acid",
        "Perchloric acid", "Chromic acid", "Hydroiodic acid", "Hydrobromic acid"
    ],
    "bases": [
        "Sodium hydroxide", "Potassium hydroxide", "Calcium hydroxide",
        "Sodium carbonate", "Sodium bicarbonate", "Magnesium hydroxide", "Ammonium hydroxide",
        "Barium hydroxide", "Lithium hydroxide", "Strontium hydroxide", "Cesium hydroxide", 
        "Aluminum hydroxide", "Hydrazine", "Pyridine", "Methylamine", "Sodium aluminate", 
        "Potassium carbonate", "Lithium carbonate", "Calcium oxide"
    ],
    "gases": [
        "Ammonia", "Chlorine", "Hydrogen", "Oxygen", "Nitrogen", 
        "Carbon dioxide", "Helium", "Neon", "Argon", "Methane",
        "Ethane", "Propane", "Butane", "Nitrous oxide", "Nitrogen dioxide",
        "Sulfur dioxide", "Hydrogen sulfide", "Acetylene", "Ethylene", "Carbon monoxide"
    ],
    "salts": [
        "Sodium chloride", "Potassium chloride", "Calcium chloride", "Copper sulfate",
        "Silver nitrate", "Lead nitrate", "Potassium iodide", "Potassium permanganate",
        "Barium chloride", "Sodium sulfate", "Ammonium chloride", "Iron(III) chloride",
        "Zinc sulfate", "Magnesium sulfate", "Cobalt(II) chloride", "Nickel(II) sulfate",
        "Potassium dichromate", "Sodium thiosulfate", "Ammonium nitrate", "Lead(II) acetate"
    ],
    "indicators": [
        "Phenolphthalein", "Bromothymol blue", "Methyl orange", "Methyl red", 
        "Bromocresol green", "Thymol blue", "Phenol red", "Alizarin yellow R",
        "Congo red", "Crystal violet", "Eriochrome Black T", "Murexide",
        "Bromophenol blue", "Indigo carmine", "Neutral red", "Cresol red",
        "Alizarin red S", "Bromocresol purple", "Thymolphthalein", "Malachite green"
    ],
    "solids": [
        "Zinc", "Magnesium", "Iron", "Copper", "Aluminum", "Sodium", "Calcium",
        "Potassium", "Lithium", "Lead", "Tin", "Silver", "Gold", "Platinum",
        "Sulfur", "Carbon", "Iodine", "Silicon", "Phosphorus", "Nickel"
    ],
    "ions": [
        "Carbonate ion", "Iodide ion", "Cobalt(II) ion", "Sulfate ion", "Ammonium ion",
        "Chloride ion", "Nitrate ion", "Phosphate ion", "Sodium ion", "Potassium ion",
        "Calcium ion", "Magnesium ion", "Iron(III) ion", "Copper(II) ion", "Zinc ion",
        "Hydroxide ion", "Nitrite ion", "Sulfite ion", "Bromide ion", "Fluoride ion"
    ]
}

def seed_database():
    db = Database()
    pubchem = PubChemService()
    
    # Create tables if they don't exist
    db.create_tables()
    
    logger.info("="*60)
    logger.info("SEEDING DATABASE: 20 HARDCODED + DYNAMIC DISCOVERY")
    logger.info("="*60)
    
    total_added = 0
    total_skipped = 0
    
    for category, name_list in CORE_CHEMICALS.items():
        logger.info(f"\n🌱 Seeding {category.upper()}...")
        
        # 1. Add Hardcoded 20
        for name in name_list:
            try:
                chem_data = pubchem.get_chemical_by_name(name)
                if not chem_data:
                    continue
                
                if db.chemical_exists(chem_data['cid']):
                    total_skipped += 1
                    continue
                
                db.add_chemical(
                    cid=chem_data['cid'],
                    name=chem_data['name'],
                    formula=chem_data['formula'],
                    molecular_weight=chem_data.get('molecular_weight'),
                    category=category,
                    iupac_name=chem_data.get('iupac_name'),
                    smiles=chem_data.get('smiles')
                )
                logger.info(f"  ✓ Added Hardcoded: {name}")
                total_added += 1
            except Exception as e:
                logger.error(f"  ✗ Error seeding {name}: {e}")

        # 2. Dynamic discovery for the category (to add "others")
        try:
            discovered_cids = pubchem.discover_chemicals_by_category_keywords(category, max_per_keyword=2)
            for cid in discovered_cids:
                if db.chemical_exists(cid):
                    continue
                
                chem_data = pubchem.get_chemical_by_cid(cid)
                if not chem_data:
                    continue
                
                db.add_chemical(
                    cid=chem_data['cid'],
                    name=chem_data['name'],
                    formula=chem_data['formula'],
                    molecular_weight=chem_data.get('molecular_weight'),
                    category=category,
                    iupac_name=chem_data.get('iupac_name'),
                    smiles=chem_data.get('smiles')
                )
                logger.info(f"  ✓ Added Discovered: {chem_data['name']}")
                total_added += 1
        except Exception as e:
            logger.error(f"Error discovering {category}: {e}")

    logger.info("\n" + "="*60)
    logger.info("SEEDING COMPLETE!")
    logger.info(f"  ✓ Total Added: {total_added}")
    logger.info(f"  ⊘ Total Skipped/Duplicates: {total_skipped}")
    logger.info("="*60)

if __name__ == "__main__":
    seed_database()

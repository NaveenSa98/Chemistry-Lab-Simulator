"""
PubChem API Service using PubChemPy Wrapper
Programmatic access to PubChem names, formulas, and properties.
Supports bulk operations and high-level chemical data retrieval.
"""

import pubchempy as pcp
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress noisy pubchempy logging
logging.getLogger('pubchempy').setLevel(logging.WARNING)

class PubChemService:
    """Service for interacting with PubChem API using PubChemPy wrapper with raw REST fallback."""
    
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    RATE_LIMIT_DELAY = 0.2  # Safety delay between requests
    
    def __init__(self):
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Internal rate limiting to be polite to PubChem API."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        self.last_request_time = time.time()
    
    def get_chemical_by_name(self, name):
        """Fetch chemical data using PubChemPy with fallback to raw PUG REST."""
        self._rate_limit()
        
        # 1. Try PubChemPy Wrapper
        try:
            compounds = pcp.get_compounds(name, 'name')
            if compounds:
                comp = compounds[0]
                return {
                    'cid': comp.cid,
                    'name': comp.synonyms[0] if comp.synonyms else name,
                    'formula': comp.molecular_formula,
                    'molecular_weight': comp.molecular_weight,
                    'iupac_name': comp.iupac_name,
                    'smiles': comp.smiles
                }
        except Exception as e:
            logger.warning(f"PubChemPy wrapper failed for {name}, trying raw API: {e}")

        # 2. Fallback to Raw PUG REST API
        return self._fetch_raw_pug_rest(name, 'name')

    def _fetch_raw_pug_rest(self, identifier, identifier_type='name'):
        """Direct PUG REST API call as fallback."""
        try:
            props = "MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES"
            url = f"{self.BASE_URL}/compound/{identifier_type}/{identifier}/property/{props}/JSON"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'PropertyTable' in data and 'Properties' in data['PropertyTable']:
                    p = data['PropertyTable']['Properties'][0]
                    return {
                        'cid': p.get('CID'),
                        'name': str(identifier),
                        'formula': p.get('MolecularFormula'),
                        'molecular_weight': p.get('MolecularWeight'),
                        'iupac_name': p.get('IUPACName'),
                        'smiles': p.get('CanonicalSMILES')
                    }
            return None
        except Exception as e:
            logger.error(f"Raw PUG REST fallback failed: {e}")
            return None

    def get_chemical_by_cid(self, cid):
        """Fetch chemical data by PubChem Compound ID."""
        self._rate_limit()
        try:
            compounds = pcp.get_compounds(cid, 'cid')
            if compounds:
                comp = compounds[0]
                return {
                    'cid': comp.cid,
                    'name': comp.synonyms[0] if comp.synonyms else f"CID_{cid}",
                    'formula': comp.molecular_formula,
                    'molecular_weight': comp.molecular_weight,
                    'iupac_name': comp.iupac_name,
                    'smiles': comp.smiles
                }
            return None
        except pcp.PubChemHTTPError as e:
            if "404" in str(e):
                logger.warning(f"CID {cid} not found in PubChem (404)")
            else:
                logger.error(f"PubChem HTTP error fetching CID {cid}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching CID {cid}: {e}")
            return None

    def search_chemicals_by_keyword(self, keyword, max_results=20):
        """Search for chemicals by keyword and return list of CIDs."""
        self._rate_limit()
        try:
            # get_cids handles the name-to-CID conversion
            cids = pcp.get_cids(keyword, 'name')
            return cids[:max_results] if cids else []
        except pcp.PubChemHTTPError as e:
            if "404" in str(e):
                logger.debug(f"Keyword '{keyword}' produced 404 search result")
            return []
        except Exception as e:
            logger.warning(f"PubChemPy search error for '{keyword}': {e}")
            return []

    def get_chemicals_by_formula(self, formula, max_results=10):
        """Get chemicals by molecular formula."""
        self._rate_limit()
        try:
            compounds = pcp.get_compounds(formula, 'formula')
            return [c.cid for c in compounds[:max_results]] if compounds else []
        except Exception as e:
            logger.error(f"PubChemPy formula search error for '{formula}': {e}")
            return []

    def get_compounds_bulk(self, identifiers, identifier_type='name'):
        """
        Fetch multiple compounds in a single operation.
        identifiers: list of names, CIDs, or SMILES
        """
        self._rate_limit()
        try:
            compounds = pcp.get_compounds(identifiers, identifier_type)
            results = []
            for comp in compounds:
                results.append({
                    'cid': comp.cid,
                    'name': comp.synonyms[0] if comp.synonyms else f"ID_{comp.cid}",
                    'formula': comp.molecular_formula,
                    'molecular_weight': comp.molecular_weight,
                    'iupac_name': comp.iupac_name,
                    'smiles': comp.smiles
                })
            return results
        except pcp.PubChemHTTPError as e:
            logger.error(f"PubChem bulk HTTP error: {e}")
            return []
        except Exception as e:
            logger.error(f"PubChemPy bulk error: {e}")
            return []

    def discover_chemicals_by_category_keywords(self, category, max_per_keyword=10):
        """Discover chemicals using high-level category keywords for expansion."""
        # Use broader terms to find NEW chemicals not in the core 100
        category_keywords = {
            'acids': ['Butyric acid', 'Lactic acid', 'Oxalic acid', 'Benzoic acid', 'Propionic acid'],
            'bases': ['Pyridine', 'Hydrazine', 'Methylamine', 'Ethanolamine', 'Piperidine'],
            'salts': ['Ammonium carbonate', 'Magnesium chloride', 'Calcium nitrate', 'Barium sulfate', 'Sodium sulfite'],
            'indicators': ['Methyl red', 'Phenol red', 'Alizarin yellow', 'Cresol purple', 'Neutral red'],
            'solids': ['Antimony', 'Bismuth', 'Chromium', 'Cobalt', 'Nickel'],
            'gases': ['Ammonia', 'Chlorine', 'Hydrogen sulfide', 'Nitrogen dioxide', 'Sulfur dioxide'],
            'ions': ['Carbonate ion', 'Iodide ion', 'Cobalt(II) ion', 'Sulfate ion', 'Ammonium ion']
        }
        
        keywords = category_keywords.get(category, [])
        all_cids = set()
        
        for kw in keywords:
            logger.info(f"    Searching for expansion: '{kw}'...")
            cids = self.search_chemicals_by_keyword(kw, max_results=max_per_keyword)
            if cids:
                all_cids.update(cids)
        
        return list(all_cids)

"""
AI ChemLab Backend - Flask Application
Educational chemistry simulator with AI-powered explanations.

This backend provides REST API endpoints for:
- Chemical inventory management
- Reaction prediction and simulation
- Educational explanations via AI
- Chemical data from PubChem database
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Import backend modules - handle both package and direct execution
try:
    # When run as a package (production with gunicorn)
    from backend.reaction_engine import ReactionEngine
    from backend.database import Database
    from backend.pubchem_service import PubChemService
    from backend.chemical_categorizer import ChemicalCategorizer
except ImportError:
    # When run directly from backend directory (local development)
    from reaction_engine import ReactionEngine
    from database import Database
    from pubchem_service import PubChemService
    from chemical_categorizer import ChemicalCategorizer

# Initialize Flask app with frontend assets paths
app = Flask(__name__,
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend requests

# Initialize core services
engine = ReactionEngine()  # Handles reaction predictions
db = Database()  # PostgreSQL database
pubchem = PubChemService()  # PubChem API integration
categorizer = ChemicalCategorizer()  # AI-based chemical categorization

# Create database tables on startup
try:
    db.create_tables()
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chemicals', methods=['GET'])
def get_chemicals():
    """
    Get all chemicals from database organized by category.

    Returns:
        JSON: Dictionary with keys for each category (acids, bases, salts, etc.)
              Each category contains a list of chemical objects with:
              - id: Database ID
              - name: Chemical name
              - formula: Chemical formula
              - molecular_weight: Weight in g/mol
              - category: Chemical classification
              - iupac_name: IUPAC name
              - smiles: SMILES notation
    """
    try:
        chemicals = db.get_all_chemicals()
        return jsonify(chemicals)
    except Exception as e:
        print(f"Error fetching chemicals: {e}")
        # Return empty categories if database is not available
        # This allows the frontend to still work with user-provided chemicals
        return jsonify({
            'liquids': [],
            'acids': [],
            'bases': [],
            'salts': [],
            'indicators': [],
            'solids': [],
            'gases': [],
            'ions': []
        })

@app.route('/api/admin/add-chemical', methods=['POST'])
def add_chemical():
    """
    Admin endpoint to add a chemical to the database.

    Request Body:
        {"name": "Aspirin"} - Search by chemical name
        or
        {"cid": 2244} - Search by PubChem CID (Compound ID)

    Returns:
        201: Chemical successfully added
        200: Chemical already exists in database
        400: Invalid request (missing name or cid)
        404: Chemical not found in PubChem database
        500: Server error during processing

    The function:
    1. Fetches chemical data from PubChem API
    2. Checks if it already exists in the database
    3. Auto-categorizes the chemical using AI (acids, bases, salts, etc.)
    4. Stores it in PostgreSQL for future use
    """
    data = request.json

    try:
        # Fetch from PubChem by CID or name
        if 'cid' in data:
            chem_data = pubchem.get_chemical_by_cid(data['cid'])
        elif 'name' in data:
            chem_data = pubchem.get_chemical_by_name(data['name'])
        else:
            return jsonify({
                "error": "Please provide either a chemical name or PubChem ID"
            }), 400

        if not chem_data:
            return jsonify({
                "error": "Chemical not found. Try searching with a different name or CID."
            }), 404

        # Check if already exists in database
        if db.chemical_exists(chem_data['cid']):
            return jsonify({
                "message": "This chemical is already in the database",
                "chemical": chem_data
            }), 200

        # Auto-categorize using LLM AI
        category = categorizer.categorize(
            chem_data['name'],
            chem_data['formula'],
            chem_data.get('iupac_name')
        )

        # Add to database
        result = db.add_chemical(
            cid=chem_data['cid'],
            name=chem_data['name'],
            formula=chem_data['formula'],
            molecular_weight=chem_data.get('molecular_weight'),
            category=category,
            iupac_name=chem_data.get('iupac_name'),
            smiles=chem_data.get('smiles')
        )

        return jsonify({
            "message": "Chemical added successfully!",
            "chemical": result
        }), 201

    except Exception as e:
        print(f"Error adding chemical: {str(e)}")
        return jsonify({
            "error": "Unable to add chemical. Please try again later."
        }), 500

@app.route('/api/admin/search', methods=['GET'])
def search_chemicals():
    """
    Search PubChem database for chemicals by keyword.

    Query Parameters:
        keyword (required): Chemical name to search (e.g., "aspirin", "sulfuric acid")
        max_results (optional): Maximum results to return (default: 20, max: 100)

    Returns:
        JSON with:
        - results: Array of matching chemicals (limited to 10)
        - total_found: Total number of matches in PubChem

    Example: /api/admin/search?keyword=aspirin&max_results=20
    """
    keyword = request.args.get('keyword')
    max_results = int(request.args.get('max_results', 20))

    if not keyword:
        return jsonify({
            "error": "Please enter a chemical name to search for"
        }), 400

    try:
        # Search PubChem for matching chemicals
        cids = pubchem.search_chemicals_by_keyword(keyword, max_results)

        # Fetch details for each matching chemical
        chemicals = []
        for cid in cids[:10]:  # Limit to 10 to avoid API rate limits
            chem_data = pubchem.get_chemical_by_cid(cid)
            if chem_data:
                chemicals.append(chem_data)

        return jsonify({
            "results": chemicals,
            "total_found": len(cids)
        })

    except Exception as e:
        print(f"Error searching chemicals: {str(e)}")
        return jsonify({
            "error": "Could not search the database. Please try again."
        }), 500

@app.route('/api/admin/discover/<category>', methods=['POST'])
def discover_category(category):
    """
    Auto-discover and add chemicals for a specific category.

    URL Parameters:
        category: One of ['liquids', 'acids', 'bases', 'salts', 'indicators', 'solids', 'gases', 'ions']

    Returns:
        JSON with discovery results:
        - message: Summary of the operation
        - added: Number of chemicals successfully added
        - skipped: Number of chemicals already in database
        - errors: List of any errors encountered

    This endpoint:
    1. Searches PubChem for representative chemicals in the category
    2. Fetches detailed data for each found chemical
    3. Adds new ones to the database (skips duplicates)
    4. Returns statistics on the operation

    Example: POST /api/admin/discover/acids
    """
    valid_categories = ['liquids', 'acids', 'bases', 'salts', 'indicators', 'solids', 'gases', 'ions']
    if category not in valid_categories:
        return jsonify({
            "error": f"Invalid category. Please use one of: {', '.join(valid_categories)}"
        }), 400

    try:
        # Discover chemicals in this category from PubChem
        cids = pubchem.discover_chemicals_by_category_keywords(category, max_per_keyword=3)

        added_count = 0
        skipped_count = 0
        errors = []

        # Process each discovered chemical
        for cid in cids[:20]:  # Limit to 20 per discovery to avoid overwhelming the system
            try:
                # Skip if already in database
                if db.chemical_exists(cid):
                    skipped_count += 1
                    continue

                # Fetch chemical data from PubChem
                chem_data = pubchem.get_chemical_by_cid(cid)
                if not chem_data:
                    continue

                # Add to database (category is known)
                db.add_chemical(
                    cid=chem_data['cid'],
                    name=chem_data['name'],
                    formula=chem_data['formula'],
                    molecular_weight=chem_data.get('molecular_weight'),
                    category=category,
                    iupac_name=chem_data.get('iupac_name'),
                    smiles=chem_data.get('smiles')
                )
                added_count += 1

            except Exception as e:
                errors.append(f"CID {cid}: {str(e)}")

        return jsonify({
            "message": f"Discovery complete for {category}!",
            "added": added_count,
            "skipped": skipped_count,
            "errors": errors
        })

    except Exception as e:
        print(f"Error discovering chemicals: {str(e)}")
        return jsonify({
            "error": "Could not discover chemicals. Please try again later."
        }), 500

@app.route('/api/chemical-color/<name>', methods=['GET'])
def get_chemical_color(name):
    """
    Get the color of a chemical when mixed with water.

    URL Parameters:
        name: Name of the chemical (e.g., "potassium permanganate")

    Returns:
        JSON with:
        - color: RGB color string (e.g., "#FF0000") or color name

    This helps students visualize what the mixture looks like in the beaker.
    """
    try:
        color = engine.get_initial_color(name)
        return jsonify({"color": color})
    except Exception as e:
        print(f"Error getting chemical color: {str(e)}")
        return jsonify({"color": "#ffffff"}), 200  # Default to white if color not found


@app.route('/api/react', methods=['POST'])
def react():
    """
    Predict what happens when chemicals are mixed together.

    Request Body:
        {
            "ingredients": ["Sulfuric acid", "Sodium hydroxide"],
            "temperature": "hot" | "room" | "cold",
            "concentration": "concentrated" | "dilute"
        }

    Returns:
        JSON with reaction prediction:
        - equation: Chemical equation (e.g., "H2SO4 + 2NaOH → Na2SO4 + 2H2O")
        - reaction_type: Type of reaction (acid-base, redox, synthesis, etc.)
        - products: List of products formed
        - ph: pH of the resulting mixture
        - symptoms: Observable changes (color change, bubbling, heat, etc.)
        - animation_triggers: Visual effects for the beaker
        - particleType: Particle effect to show (bubble, precipitate, etc.)
        - particleColor: Color of particles
        - liquidColor: Color of the liquid in the beaker
        - explanation: AI-generated educational explanation
        - safety_tips: Safety information for students
        - real_world_example: Real-world application of this reaction
        - concept: Chemistry concept being demonstrated

    This is the core of the simulation - it combines:
    1. Rule-based reactions (stored database of known reactions)
    2. AI explanations (generated via Google Gemini 2.0 Flash)
    3. Visual feedback (colors, particles, animations)
    """
    try:
        data = request.json
        ingredients = data.get('ingredients', [])
        temp = data.get('temperature', 'room')
        conc = data.get('concentration', 'dilute')

        if not ingredients:
            return jsonify({
                "error": "Please add some chemicals first!"
            }), 400

        # Predict the reaction outcome
        result = engine.predict_reaction(ingredients, temperature=temp, concentration=conc)
        return jsonify(result)

    except Exception as e:
        print(f"Error predicting reaction: {str(e)}")
        return jsonify({
            "error": "Could not predict the reaction. Please try again."
        }), 500


@app.route('/api/explain', methods=['POST'])
def explain():
    """
    Get an explanation for a reaction (legacy endpoint).

    Request Body:
        {
            "reaction_data": { reaction object from /api/react }
        }

    Returns:
        JSON with:
        - explanation: Detailed text explanation of the reaction
    """
    try:
        data = request.json
        reaction_data = data.get('reaction_data', {})
        explanation = engine.get_explanation(reaction_data)
        return jsonify({"explanation": explanation})
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")
        return jsonify({
            "explanation": "Could not generate explanation. Please try again."
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

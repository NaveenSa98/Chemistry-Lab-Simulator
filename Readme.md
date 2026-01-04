# AI ChemLab - Virtual Chemistry Laboratory Simulator

An interactive, AI-powered virtual chemistry laboratory that allows students to safely perform chemistry experiments online. Mix chemicals, observe realistic reactions, and learn with AI-generated explanations.

## Features

### Interactive Laboratory Experience

- **Visual Beaker Simulation**: Real-time p5.js-powered animations showing color changes, bubbling, precipitates, and other reaction effects
- **Drag-and-Drop Interface**: Intuitive chemical selection and mixing
- **Chemical Inventory**: Comprehensive database of chemicals organized by category (acids, bases, salts, indicators, liquids, solids, gases, ions)
- **Reaction Controls**: Adjust temperature (Bunsen burner/ice bath), concentration, and chemical amounts

### Intelligent Reaction Prediction

- **Rule-Based Chemistry Engine**: Accurate stoichiometric calculations and reaction predictions
- **Cascading Reactions**: Automatically detects and simulates multi-step reactions
- **PubChem Integration**: Real chemical data including molecular formulas, IUPAC names, and molecular weights
- **AI-Powered Explanations**: Google Gemini 2.0 Flash generates detailed educational content

### Educational Content

- **Concept Labels**: Identifies chemistry concepts (acid-base reactions, redox, precipitation, etc.)
- **Safety Information**: Real-world safety tips for each reaction
- **Observable Changes**: Color changes, pH levels, gas evolution, precipitate formation
- **Real-World Applications**: Connects experiments to practical applications
- **Example Reactions**: Pre-configured experiments for beginners

### Technical Capabilities

- **PostgreSQL Database**: Persistent chemical storage with SQLAlchemy ORM
- **RESTful API**: Clean Flask-based backend for all operations
- **Responsive Design**: Works on desktop and tablet devices
- **Auto-Discovery**: AI-powered chemical categorization using LLM

## Tech Stack

### Frontend

- **HTML5/CSS3**: Modern, responsive UI with glassmorphism design
- **JavaScript (ES6+)**: Vanilla JS for interactions and API calls
- **p5.js**: Canvas-based animations and particle systems
- **Google Fonts (Outfit)**: Clean, modern typography

### Backend

- **Flask**: Lightweight Python web framework
- **Flask-CORS**: Cross-origin resource sharing support
- **SQLAlchemy**: Database ORM for PostgreSQL
- **Gunicorn**: Production WSGI server

### APIs & Services

- **PubChem API**: Chemical data and compound information
- **Google Gemini 2.0 Flash**: AI-powered educational explanations
- **PubChemPy**: Python wrapper for PubChem integration

### Database

- **PostgreSQL**: Production database for chemical storage
- **Render PostgreSQL**: Managed database hosting

## Live Demo

[(https://chemistry-lab-simulator.onrender.com/)]

## Screenshots

[Add screenshots of your application here showing the beaker interface, chemical inventory, and reaction results]

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Google AI API key ([Get one here](https://makersuite.google.com/app/apikey))

### Local Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/Chemistry-Lab-Simulator.git
cd Chemistry-Lab-Simulator
```

1. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Set up environment variables**

   Create a `.env` file in the root directory:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:

   ```env
   # Google AI API Key (required for AI-powered explanations)
   GOOGLE_API_KEY=your_google_api_key_here

   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/chemlab
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=chemlab
   DB_USER=postgres
   DB_PASSWORD=your_password_here
   ```

1. **Set up PostgreSQL database**

```bash
# Create database
createdb chemlab

# Or using psql
psql -U postgres
CREATE DATABASE chemlab;
\q
```

1. **Initialize the database**

```bash
python backend/database.py  # Creates tables
python backend/seed_chemicals.py  # (Optional) Seeds initial chemicals
```

1. **Run the development server**

```bash
python backend/app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```text
Chemistry-Lab-Simulator/
├── backend/
│   ├── app.py                    # Flask application and API routes
│   ├── database.py               # Database models and configuration
│   ├── reaction_engine.py        # Hybrid reaction prediction engine
│   ├── chemistry_rules.py        # Rule-based reaction database
│   ├── llm_service.py           # Google Gemini AI integration
│   ├── pubchem_service.py       # PubChem API wrapper
│   ├── chemical_categorizer.py  # AI-powered chemical classification
│   ├── formula_formatter.py     # Chemical formula formatting
│   └── seed_chemicals.py        # Database seeding script
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Main stylesheet
│   │   └── js/
│   │       ├── sketch.js        # p5.js beaker visualization
│   │       ├── api.js           # Backend API communication
│   │       ├── chemicals.js     # Chemical inventory UI
│   │       ├── particles.js     # Particle system for effects
│   │       └── tutorial.js      # Tutorial modal logic
│   └── templates/
│       └── index.html           # Main HTML template
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── Procfile                     # Render deployment config
├── render.yaml                  # Render infrastructure as code
├── LICENSE                      # MIT License
└── Readme.md                    # This file
```

## Usage Guide

### For Students

1. **Select Chemicals**: Click "Chemical Inventory" to browse available chemicals
1. **Add to Beaker**: Drag chemicals or click "Add to Beaker"
1. **Adjust Amount**: Use the slider to control volume (10-100ml)
1. **Set Conditions**:
   - Toggle Bunsen Burner for heat
   - Toggle Ice Bath for cold
   - Toggle Concentrated for higher concentration
1. **Observe Results**: Watch animations in the beaker
1. **Learn**: Check the Results and Details tabs for explanations

### Example Reactions to Try

- **Acid-Base Neutralization**: HCl + NaOH → NaCl + H₂O
- **Color Change with Indicator**: Phenolphthalein + NaOH (turns pink)
- **Gas Evolution**: Magnesium + HCl → MgCl₂ + H₂ (bubbling)
- **Precipitate Formation**: CuSO₄ + NaOH → Cu(OH)₂ (blue solid)
- **Temperature-Dependent**: Cu + H₂SO₄ (requires heat)
- **Vigorous Reaction**: Na + H₂O → NaOH + H₂ (violent)

## Deployment

### Render Deployment

This project is configured for one-click deployment on Render.

1. **Fork this repository**

1. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

1. **Add environment variables**
   - `GOOGLE_API_KEY`: Your Google AI API key
   - `DATABASE_URL`: Auto-configured by Render PostgreSQL

1. **Deploy**
   - Render will automatically:
     - Create a PostgreSQL database
     - Install dependencies
     - Start the Flask application with Gunicorn

### Manual Deployment

For other platforms:

1. Set up a PostgreSQL database
1. Set environment variables
1. Install dependencies: `pip install -r requirements.txt`
1. Run with Gunicorn: `gunicorn --bind 0.0.0.0:$PORT backend.app:app`

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue with details and steps to reproduce
1. **Suggest Features**: Share ideas for new reactions or features
1. **Add Reactions**: Contribute to [chemistry_rules.py](backend/chemistry_rules.py)
1. **Improve UI**: Enhance the frontend design and user experience
1. **Documentation**: Help improve this README or add code comments

### Development Workflow

1. Fork the repository
1. Create a feature branch: `git checkout -b feature/amazing-feature`
1. Make your changes
1. Test thoroughly
1. Commit: `git commit -m 'Add amazing feature'`
1. Push: `git push origin feature/amazing-feature`
1. Open a Pull Request

## Known Issues

- Some complex organic reactions are not yet supported
- Mobile touch interactions need optimization
- Very fast reaction sequences may skip intermediate steps

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Naveen Samaranayake

## Acknowledgments

- **PubChem**: For providing comprehensive chemical data
- **Google AI**: For Gemini 2.0 Flash API
- **p5.js Community**: For the amazing creative coding library
- **Chemistry Education Community**: For feedback and testing

## Support

If you find this project helpful, please consider:

- Giving it a star on GitHub
- Sharing it with students and educators
- Contributing to the codebase
- Reporting issues and suggesting improvements

**Note**: This is an educational tool. While reactions are based on real chemistry, always consult with qualified professionals before performing any real-world chemistry experiments. Safety first!

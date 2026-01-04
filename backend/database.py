"""
Database configuration and models for chemical storage.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

from formula_formatter import format_formula

Base = declarative_base()

class Chemical(Base):
    """Chemical model for storing PubChem data."""
    __tablename__ = 'chemicals'
    
    id = Column(Integer, primary_key=True)
    cid = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    formula = Column(String(100))
    molecular_weight = Column(Float)
    category = Column(String(50))  # liquids, acids, bases, salts, indicators, solids, gases, ions
    iupac_name = Column(Text)
    smiles = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'cid': self.cid,
            'name': self.name,
            'formula': self.formula,
            'molecular_weight': self.molecular_weight,
            'category': self.category,
            'iupac_name': self.iupac_name,
            'smiles': self.smiles,
            'display': format_formula(self.formula, self.name)
        }

class Database:
    """Database connection and operations manager."""
    
    def __init__(self):
        # Use environment variable or default to local PostgreSQL
        db_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.Session()
    
    def add_chemical(self, cid, name, formula, molecular_weight, category, iupac_name=None, smiles=None):
        """Add a chemical to the database."""
        session = self.get_session()
        try:
            chemical = Chemical(
                cid=cid,
                name=name,
                formula=formula,
                molecular_weight=molecular_weight,
                category=category,
                iupac_name=iupac_name,
                smiles=smiles
            )
            session.add(chemical)
            session.commit()
            return chemical.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_chemicals(self):
        """Get all chemicals grouped by category."""
        session = self.get_session()
        try:
            chemicals = session.query(Chemical).all()

            # Group by category
            grouped = {
                'liquids': [],
                'acids': [],
                'bases': [],
                'salts': [],
                'indicators': [],
                'solids': [],
                'gases': [],
                'ions': []
            }

            for chem in chemicals:
                if chem.category in grouped:
                    grouped[chem.category].append(chem.to_dict())

            return grouped
        finally:
            session.close()
    
    def get_chemical_by_cid(self, cid):
        """Get a chemical by PubChem CID."""
        session = self.get_session()
        try:
            return session.query(Chemical).filter_by(cid=cid).first()
        finally:
            session.close()
    
    def chemical_exists(self, cid):
        """Check if a chemical already exists in database."""
        return self.get_chemical_by_cid(cid) is not None

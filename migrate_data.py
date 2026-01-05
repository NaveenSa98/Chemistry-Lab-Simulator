"""
Script to migrate chemicals from local database to Railway database.
Run this script locally to copy all chemicals to Railway.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Chemical, Base
import os

def migrate_chemicals(source_url, target_url):
    """Migrate chemicals from source to target database."""

    # Connect to source (local) database
    source_engine = create_engine(source_url)
    SourceSession = sessionmaker(bind=source_engine)
    source_session = SourceSession()

    # Connect to target (Railway) database
    target_engine = create_engine(target_url)
    TargetSession = sessionmaker(bind=target_engine)
    target_session = TargetSession()

    try:
        # Create tables in target if they don't exist
        Base.metadata.create_all(target_engine)

        # Get all chemicals from source
        chemicals = source_session.query(Chemical).all()

        print(f"Found {len(chemicals)} chemicals to migrate")

        migrated = 0
        skipped = 0

        for chem in chemicals:
            try:
                # Check if chemical already exists in target
                existing = target_session.query(Chemical).filter_by(cid=chem.cid).first()

                if existing:
                    print(f"Skipping {chem.name} (already exists)")
                    skipped += 1
                    continue

                # Create new chemical in target database
                new_chem = Chemical(
                    cid=chem.cid,
                    name=chem.name,
                    formula=chem.formula,
                    molecular_weight=chem.molecular_weight,
                    category=chem.category,
                    iupac_name=chem.iupac_name,
                    smiles=chem.smiles
                )

                target_session.add(new_chem)
                target_session.commit()

                print(f"✓ Migrated: {chem.name}")
                migrated += 1

            except Exception as e:
                print(f"✗ Error migrating {chem.name}: {e}")
                target_session.rollback()

        print(f"\n✓ Migration complete!")
        print(f"  - Migrated: {migrated}")
        print(f"  - Skipped: {skipped}")
        print(f"  - Total: {len(chemicals)}")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
    finally:
        source_session.close()
        target_session.close()

if __name__ == "__main__":
    # Local database URL
    LOCAL_DB = "postgresql://postgres:1234@localhost:5432/chemlab"

    # Railway database URL - GET THIS FROM RAILWAY DASHBOARD
    print("=" * 60)
    print("CHEMISTRY LAB SIMULATOR - DATABASE MIGRATION")
    print("=" * 60)
    print("\nTo get your Railway database URL:")
    print("1. Go to Railway dashboard")
    print("2. Click on your PostgreSQL service")
    print("3. Go to 'Variables' tab")
    print("4. Copy the DATABASE_URL value")
    print("\nPaste it below:")
    print("=" * 60)

    railway_db = input("\nRailway DATABASE_URL: ").strip()

    if not railway_db:
        print("✗ No URL provided. Exiting.")
        exit(1)

    print(f"\n⚡ Starting migration...")
    print(f"  FROM: {LOCAL_DB}")
    print(f"  TO: {railway_db[:30]}...")
    print()

    confirm = input("Continue? (yes/no): ").strip().lower()

    if confirm == 'yes':
        migrate_chemicals(LOCAL_DB, railway_db)
    else:
        print("✗ Migration cancelled.")

#!/usr/bin/env python3
"""
Setup script for the TechCorp KG-RAG Demo

This script helps set up the demo environment by checking dependencies
and downloading required models.
"""

import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def download_spacy_model():
    """Download spaCy English model."""
    print("🔤 Downloading spaCy English model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ spaCy model downloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download spaCy model: {e}")
        print("You can try manually: python -m spacy download en_core_web_sm")
        return False

def create_directories():
    """Create necessary directories."""
    print("📁 Creating necessary directories...")
    
    directories = [
        "data/raw",
        "data/processed", 
        "data/rdf",
        "data/ontology",
        "data/graphdb"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully")

def verify_sample_data():
    """Verify that sample data files exist."""
    print("📄 Verifying sample data files...")
    
    required_files = [
        "data/raw/sample_documents.json",
        "data/ontology/techcorp_ontology.ttl"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist

def run_basic_test():
    """Run a basic test to verify the setup."""
    print("🧪 Running basic setup test...")
    
    try:
        # Test imports
        import rdflib
        import spacy
        print("✅ Core libraries import successfully")
        
        # Test spaCy model
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("TechCorp is a technology company.")
        print(f"✅ spaCy model works (found {len(doc.ents)} entities)")
        
        # Test RDFLib
        g = rdflib.Graph()
        g.parse(data="<s> <p> <o> .", format="turtle")
        print(f"✅ RDFLib works (parsed {len(g)} triples)")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🔧 TechCorp KG-RAG Demo Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Download spaCy model
    if not download_spacy_model():
        success = False
    
    # Verify sample data
    if not verify_sample_data():
        print("⚠️  Some sample data files are missing, but the demo should still work")
    
    # Run basic test
    if success and not run_basic_test():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Setup completed successfully!")
        print("\nYou can now run the demo with:")
        print("   python demo.py")
        print("\nOr get help with:")
        print("   python demo.py --help")
    else:
        print("❌ Setup completed with some issues")
        print("Please check the error messages above and resolve any problems")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

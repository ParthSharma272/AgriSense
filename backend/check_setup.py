#!/usr/bin/env python3
"""
Quick test script to verify AgriSense installation
"""
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 or higher required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if key dependencies are installed"""
    required = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pandas', 'Pandas'),
        ('sentence_transformers', 'Sentence Transformers'),
        ('chromadb', 'ChromaDB'),
        ('huggingface_hub', 'Hugging Face Hub'),
    ]
    
    all_installed = True
    for module, name in required:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"❌ {name} not installed")
            all_installed = False
    
    return all_installed


def check_env_file():
    """Check if .env file exists"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print("✓ .env file exists")
        
        # Check for HF token
        with open(env_file) as f:
            content = f.read()
            if 'HF_API_TOKEN=' in content and 'your_' not in content:
                print("✓ HF_API_TOKEN appears to be set")
            else:
                print("⚠ HF_API_TOKEN may not be configured")
                return False
        return True
    else:
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        return False


def check_directories():
    """Check if required directories exist"""
    dirs = ['data', 'chroma_db', 'cache']
    all_exist = True
    
    for dir_name in dirs:
        dir_path = Path(__file__).parent / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"⚠ {dir_name}/ directory missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all checks"""
    print("=" * 50)
    print("AgriSense 2.0 - Installation Check")
    print("=" * 50)
    print()
    
    print("Checking Python version...")
    python_ok = check_python_version()
    print()
    
    print("Checking Python dependencies...")
    deps_ok = check_dependencies()
    print()
    
    print("Checking configuration...")
    env_ok = check_env_file()
    print()
    
    print("Checking directories...")
    dirs_ok = check_directories()
    print()
    
    print("=" * 50)
    if python_ok and deps_ok and env_ok and dirs_ok:
        print("✓ All checks passed!")
        print()
        print("You're ready to run AgriSense:")
        print("  uvicorn main:app --reload")
    else:
        print("⚠ Some checks failed")
        print()
        print("Please fix the issues above, then:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create .env file: cp .env.example .env")
        print("3. Run initialization: python init_agrisense.py")
    print("=" * 50)


if __name__ == "__main__":
    main()

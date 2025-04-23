
#!/usr/bin/env python
"""
Quick pre-deployment test for N1O1 Clinical Trials
"""
import importlib
import sys
import os

def test_critical_modules():
    """Test if critical modules can be imported"""
    print("Testing critical imports...")
    
    critical_modules = [
        "flask", 
        "openai", 
        "sqlalchemy", 
        "flask_sqlalchemy", 
        "dotenv",
        "matplotlib", 
        "numpy",
        "routes.chat_routes",
        "routes.consent_routes",
        "patient_education",
        "eligibility"
    ]
    
    all_passed = True
    for module in critical_modules:
        try:
            if module.startswith("routes."):
                # For relative imports
                module_name = module.split(".")
                if len(module_name) > 1:
                    try:
                        from routes import chat_routes, consent_routes
                        print(f"✅ Successfully imported {module}")
                    except ImportError as e:
                        print(f"❌ Failed to import {module}: {str(e)}")
                        all_passed = False
            else:
                # Standard imports
                importlib.import_module(module)
                print(f"✅ Successfully imported {module}")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {str(e)}")
            all_passed = False
    
    return all_passed

def check_app():
    """Test if main Flask app can initialize"""
    print("\nTesting Flask app initialization...")
    
    try:
        from main import app
        print("✅ Successfully initialized Flask app")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Flask app: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("N1O1 CLINICAL TRIALS PRE-DEPLOYMENT TEST")
    print("========================================")
    
    modules_ok = test_critical_modules()
    app_ok = check_app()
    
    if modules_ok and app_ok:
        print("\n✅ All tests passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test setup script for Angel One MCP Server and Client

This script helps verify that your environment is properly configured
and all dependencies are working correctly.
"""

import os
import sys
import yaml
from dotenv import load_dotenv

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    load_dotenv()
    
    required_vars = [
        "ANGEL_ONE_API_KEY",
        "ANGEL_ONE_CLIENT_CODE", 
        "ANGEL_ONE_PASSWORD",
        "ANGEL_ONE_TOTP_SECRET",
        "GEMINI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"   ✅ {var}: {'*' * 8} (configured)")
    
    if missing_vars:
        print(f"   ❌ Missing variables: {missing_vars}")
        return False
    
    print("   ✅ All environment variables configured!")
    return True

def test_dependencies():
    """Test if all required Python packages are installed"""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        ("mcp", "Model Context Protocol SDK"),
        ("SmartApi", "Angel One Smart API"),
        ("pyotp", "TOTP authentication"),
        ("google.generativeai", "Google Gemini API"),
        ("yaml", "Configuration file management"),
        ("dotenv", "Environment variable management"),
        ("httpx", "HTTP client")
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}: {description}")
        except ImportError:
            print(f"   ❌ {package}: {description} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   📋 To install missing packages, run:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("   ✅ All dependencies installed!")
    return True

def test_angel_one_connection():
    """Test basic Angel One API connection (without authentication)"""
    print("\n🔗 Testing Angel One API Connection...")
    
    try:
        from SmartApi.smartConnect import SmartConnect
        
        api_key = os.getenv("ANGEL_ONE_API_KEY")
        if not api_key:
            print("   ⚠️  Cannot test - ANGEL_ONE_API_KEY not set")
            return False
        
        # Just test if we can create the SmartConnect instance
        smart_api = SmartConnect(api_key=api_key)
        print("   ✅ SmartConnect instance created successfully")
        
        print("   ℹ️  Note: Full authentication test requires TOTP and will be done during actual usage")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating SmartConnect instance: {e}")
        return False

def test_gemini_connection():
    """Test basic Gemini API connection"""
    print("\n🤖 Testing Gemini API Connection...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("   ⚠️  Cannot test - GEMINI_API_KEY not set")
            return False
        
        # Just test if we can configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("   ✅ Gemini client created successfully")
        
        print("   ℹ️  Note: Full API test will be done during actual usage")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating Gemini client: {e}")
        return False

def test_configuration():
    """Test configuration file loading"""
    print("\n⚙️  Testing Configuration...")
    
    try:
        if not os.path.exists('config.yaml'):
            print("   ⚠️  config.yaml not found - using defaults")
            return True
        
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check essential config sections
        required_sections = ['ai', 'trading']
        for section in required_sections:
            if section in config:
                print(f"   ✅ {section} configuration found")
            else:
                print(f"   ⚠️  {section} configuration missing - using defaults")
        
        # Check AI model setting
        if 'ai' in config and 'model' in config['ai']:
            print(f"   ✅ AI model: {config['ai']['model']}")
        
        # Check trading settings
        if 'trading' in config:
            dry_run = config['trading'].get('dry_run_mode', True)
            max_qty = config['trading'].get('max_order_quantity', 10000)
            print(f"   ✅ Dry run mode: {dry_run}")
            print(f"   ✅ Max order quantity: {max_qty}")
        
        print("   ✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading configuration: {e}")
        return False

def test_file_structure():
    """Test if all required files are present"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        ("angel_one_mcp_server.py", "MCP Server"),
        ("angel_one_mcp_client.py", "MCP Client"), 
        ("requirements.txt", "Dependencies list"),
        ("config.yaml", "Configuration file"),
        (".env", "Environment variables (should be created by you)")
    ]
    
    missing_files = []
    
    for filename, description in required_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}: {description}")
        else:
            print(f"   ❌ {filename}: {description} - NOT FOUND")
            missing_files.append(filename)
    
    if missing_files:
        if ".env" in missing_files:
            print("\n   📝 To create .env file, copy from config_template.txt:")
            print("   cp config_template.txt .env")
            print("\n   Then edit the .env file with your actual credentials.")
            print("   Non-secret configurations are in config.yaml")
        return False
    
    print("   ✅ All required files present!")
    return True

def main():
    """Run all tests"""
    print("🧪 Angel One MCP Setup Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_configuration,
        test_environment_variables,
        test_dependencies,
        test_angel_one_connection,
        test_gemini_connection
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n✅ Your setup is ready!")
        print("\n🚀 To start the trading assistant:")
        print("   1. Activate virtual environment: source venv/bin/activate")
        print("   2. Run: python angel_one_mcp_client.py angel_one_mcp_server.py")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\n❌ Please fix the issues above before proceeding")
        
        if not results[1]:  # Environment variables test failed
            print("\n🔧 Next steps:")
            print("1. Create .env file with your credentials")
            print("2. Get Angel One API access: https://smartapi.angelone.in/")
            print("3. Get Anthropic API key: https://console.anthropic.com/settings/keys")
        
        if not results[2]:  # Dependencies test failed
            print("\n📦 Install missing dependencies:")
            print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main() 
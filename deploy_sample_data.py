#!/usr/bin/env python3
"""
Deploy sample data script for Railway
This script should be run on Railway to populate the production database
"""

import json
import os
import sys
from datetime import datetime, date

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Railway will have these environment variables set
RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT')

def main():
    """Main deployment function"""
    
    print("🚀 TrueTank Sample Data Deployment")
    print("=" * 50)
    
    if RAILWAY_ENVIRONMENT:
        print(f"🌐 Environment: {RAILWAY_ENVIRONMENT}")
    else:
        print("⚠️  Warning: RAILWAY_ENVIRONMENT not detected (running locally?)")
    
    # Look for the most recent sample data export
    sample_files = [f for f in os.listdir('.') if f.startswith('sample_data_export_') and f.endswith('.json')]
    
    if not sample_files:
        print("❌ No sample data export files found!")
        print("   Please ensure sample_data_export_*.json is deployed with your app")
        return False
    
    # Use the most recent file
    latest_file = sorted(sample_files)[-1]
    print(f"📁 Using data file: {latest_file}")
    
    # Import the sample data
    from import_sample_data import import_data
    
    success = import_data(latest_file)
    
    if success:
        print("\n✅ Sample data deployment completed!")
        print("🎯 Your Railway database now has:")
        print("   • 4 Locations (Pewee Valley, KY area)")
        print("   • 4 Team Members (with certifications)")
        print("   • 4 Trucks (fully equipped)")
        print("   • 25 Customers (Kentucky area)")
        print("   • 18 Septic Systems (realistic data)")
        print("   • 39 Tickets (today/tomorrow schedule)")
        print("\n🌐 Ready for testing on Railway!")
    else:
        print("\n❌ Sample data deployment failed!")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
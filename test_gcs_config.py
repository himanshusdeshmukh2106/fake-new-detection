#!/usr/bin/env python3
"""
Test GCS Authentication Configuration
This script tests if your GCS credentials are properly configured.
"""

import sys
import os
sys.path.append('.')

from factcheck.utils.api_config import load_api_config
from factcheck.utils.utils import load_yaml

def test_gcs_config():
    """Test GCS configuration"""
    
    print("🧪 Testing GCS Configuration")
    print("=" * 50)
    
    # Load API config
    try:
        api_config = load_yaml("api_config.yaml")
        merged_config = load_api_config(api_config)
        print("✅ API config loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load API config: {e}")
        return
    
    # Check required GCS settings
    gcs_bucket = merged_config.get('GCS_BUCKET_NAME')
    gcs_url = merged_config.get('GCS_BASE_URL')
    credentials = merged_config.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    print(f"\n📋 Configuration Summary:")
    print(f"  • Bucket Name: {gcs_bucket}")
    print(f"  • Base URL: {gcs_url}")
    print(f"  • Credentials: {credentials[:50] + '...' if credentials and len(credentials) > 50 else credentials}")
    
    # Test credentials format
    if credentials:
        if credentials.startswith('{') and credentials.endswith('}'):
            print("  • Format: Inline JSON credentials")
            try:
                import json
                creds_dict = json.loads(credentials)
                project_id = creds_dict.get('project_id', 'Unknown')
                client_email = creds_dict.get('client_email', 'Unknown')
                print(f"  • Project ID: {project_id}")
                print(f"  • Service Account: {client_email}")
                print("✅ Inline JSON credentials are valid")
            except Exception as e:
                print(f"❌ Invalid JSON credentials: {e}")
        elif os.path.exists(credentials):
            print("  • Format: JSON file path")
            print("✅ Credentials file exists")
        else:
            print(f"❌ Credentials file not found: {credentials}")
    else:
        print("  • No credentials configured - will use Application Default Credentials")
    
    print(f"\n🚨 Important Setup Steps:")
    print(f"1. Create GCS bucket named: {gcs_bucket}")
    print(f"2. Grant service account 'Storage Object Admin' role")
    print(f"3. Make bucket publicly readable (optional)")
    print(f"4. Test by uploading an image via the web interface")
    
    print(f"\n💡 If GCS fails, the system will automatically fallback to local files.")

if __name__ == "__main__":
    test_gcs_config()
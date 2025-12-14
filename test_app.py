"""
Test script to verify all routes work correctly
"""

from app import app
import sys

def test_routes():
    """Test all Flask routes"""
    
    print("🧪 Testing Flask Application Routes...")
    print("=" * 50)
    
    with app.test_client() as client:
        routes_to_test = [
            ('/', 'Home Page'),
            ('/lost', 'Lost Items Page'),
            ('/found', 'Found Items Page'),
            ('/report/lost', 'Report Lost Page'),
            ('/report/found', 'Report Found Page'),
            ('/admin', 'Admin Dashboard'),
        ]
        
        for route, description in routes_to_test:
            try:
                response = client.get(route)
                if response.status_code == 200:
                    print(f"✅ {description}: OK")
                else:
                    print(f"❌ {description}: ERROR (Status {response.status_code})")
            except Exception as e:
                print(f"❌ {description}: ERROR - {str(e)}")
        
        # Test item detail pages with sample data
        print("\n📝 Testing item detail pages...")
        try:
            response = client.get('/item/lost/1')
            if response.status_code == 200:
                print("✅ Lost Item Detail: OK")
            else:
                print(f"❌ Lost Item Detail: ERROR (Status {response.status_code})")
        except Exception as e:
            print(f"❌ Lost Item Detail: ERROR - {str(e)}")
        
        try:
            response = client.get('/item/found/1')
            if response.status_code == 200:
                print("✅ Found Item Detail: OK")
            else:
                print(f"❌ Found Item Detail: ERROR (Status {response.status_code})")
        except Exception as e:
            print(f"❌ Found Item Detail: ERROR - {str(e)}")
        
        # Test claim pages
        print("\n🏆 Testing claim pages...")
        try:
            response = client.get('/claim/lost/1')
            if response.status_code == 200:
                print("✅ Claim Lost Item: OK")
            else:
                print(f"❌ Claim Lost Item: ERROR (Status {response.status_code})")
        except Exception as e:
            print(f"❌ Claim Lost Item: ERROR - {str(e)}")
        
        try:
            response = client.get('/claim/found/1')
            if response.status_code == 200:
                print("✅ Claim Found Item: OK")
            else:
                print(f"❌ Claim Found Item: ERROR (Status {response.status_code})")
        except Exception as e:
            print(f"❌ Claim Found Item: ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Route testing completed!")
    print("🚀 If all tests pass, you can run: python run_app.py")

if __name__ == "__main__":
    test_routes()
#!/usr/bin/env python3
"""
Test script to verify achievement API endpoints
"""

import requests
import json

def test_achievement_api():
    base_url = "http://127.0.0.1:5000"
    
    print("Testing Achievement API Endpoints")
    print("="*50)
    
    # First login as demo user
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    session = requests.Session()
    
    try:
        print("\n1. Testing login...")
        login_response = session.post(f"{base_url}/api/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            
            print("\n2. Testing achievements endpoint...")
            achievements_response = session.get(f"{base_url}/api/achievements")
            print(f"Achievements status: {achievements_response.status_code}")
            
            if achievements_response.status_code == 200:
                achievements = achievements_response.json()
                print(f"✅ Got {len(achievements)} achievements")
                
                # Print first few achievements
                for i, achv in enumerate(achievements[:3]):
                    print(f"  - {achv['name']}: {achv['description']} ({'Unlocked' if achv['unlocked'] else 'Locked'})")
                
            print("\n3. Testing achievement stats...")
            stats_response = session.get(f"{base_url}/api/achievements/stats")
            print(f"Stats status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ Achievement stats:")
                print(f"  - Total: {stats['total_achievements']}")
                print(f"  - Unlocked: {stats['unlocked_achievements']}")
                print(f"  - Completion: {stats['completion_percentage']}%")
                print(f"  - Points: {stats['total_points']}")
                
            print("\n4. Testing activity logging...")
            activity_data = {
                "activity_type": "chapter_read",
                "activity_data": {
                    "story_id": 1,
                    "chapter_num": 1,
                    "title": "Test Chapter"
                }
            }
            
            activity_response = session.post(f"{base_url}/api/log_activity", json=activity_data)
            print(f"Activity log status: {activity_response.status_code}")
            
            if activity_response.status_code == 200:
                activity_result = activity_response.json()
                print(f"✅ Activity logged successfully")
                if activity_result.get('new_achievements'):
                    print(f"🏆 New achievements unlocked: {len(activity_result['new_achievements'])}")
                    for achv in activity_result['new_achievements']:
                        print(f"  - {achv['name']}: {achv['description']}")
                else:
                    print("  - No new achievements unlocked")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Flask app is running on port 5000.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_achievement_api()

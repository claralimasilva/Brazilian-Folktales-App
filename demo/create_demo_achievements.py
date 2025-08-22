#!/usr/bin/env python3
"""
Test script to add some demo achievements and test ranking
"""

import sqlite3
from database import get_db_connection, log_user_activity, get_global_ranking, get_user_rank

def create_demo_achievements():
    """Create some demo achievements for testing ranking"""
    print("Creating demo achievements for testing...")
    
    # Create some demo achievements for demo user (user_id should be 2)
    activities = [
        ('chapter_read', {'story_id': 1, 'chapter_num': 1}),
        ('chapter_read', {'story_id': 1, 'chapter_num': 2}),
        ('quiz_completed', {'story_id': 1, 'chapter_num': 1, 'score': 5, 'total': 5, 'percentage': 100}),
        ('quiz_completed', {'story_id': 1, 'chapter_num': 2, 'score': 4, 'total': 5, 'percentage': 80}),
    ]
    
    user_id = 2  # demo user
    
    for activity_type, activity_data in activities:
        print(f"Logging activity: {activity_type}")
        new_achievements = log_user_activity(user_id, activity_type, activity_data)
        if new_achievements:
            print(f"  🏆 New achievements: {[a['name'] for a in new_achievements]}")
        else:
            print("  - No new achievements")
    
    print("\nDemo achievements created!")

def test_ranking_functions():
    """Test ranking functions"""
    print("\nTesting ranking functions...")
    
    # Test global ranking
    print("\n--- Global Ranking ---")
    ranking = get_global_ranking(10)
    for user in ranking:
        print(f"#{user['rank']} - {user['username']}: {user['total_points']} pts ({user['achievements_count']} achievements)")
    
    # Test user rank
    print("\n--- Demo User Rank ---")
    user_rank = get_user_rank(2)  # demo user
    if user_rank:
        print(f"#{user_rank['rank']} - {user_rank['username']}: {user_rank['total_points']} pts ({user_rank['achievements_count']} achievements)")
    else:
        print("Demo user not found in ranking")

if __name__ == "__main__":
    create_demo_achievements()
    test_ranking_functions()
    print("\nDemo completed! Check the web interface ranking page.")

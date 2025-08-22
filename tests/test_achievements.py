#!/usr/bin/env python3
"""
Test script to verify achievement system setup
"""

import sqlite3
import json
from database import get_db_connection, init_database

def test_achievements_db():
    print("Testing Achievement Database Setup")
    print("="*50)
    
    # Initialize database to make sure all tables exist
    init_database()
    
    conn = get_db_connection()
    
    # Check if achievements table exists and has data
    achievements = conn.execute('SELECT * FROM achievements ORDER BY category, points').fetchall()
    print(f"\nTotal achievements in database: {len(achievements)}")
    
    if achievements:
        print("\nAchievements by category:")
        categories = {}
        for achievement in achievements:
            category = achievement['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(achievement)
        
        for category, achvs in categories.items():
            print(f"\n{category.upper()} ({len(achvs)} achievements):")
            for achv in achvs:
                print(f"  - {achv['name']} ({achv['points']} pts): {achv['description']}")
                print(f"    Requirement: {achv['requirement_type']} >= {achv['requirement_value']}")
    
    # Check other tables
    print(f"\nUser achievements count: {conn.execute('SELECT COUNT(*) FROM user_achievements').fetchone()[0]}")
    print(f"Activity log count: {conn.execute('SELECT COUNT(*) FROM activity_log').fetchone()[0]}")
    
    # Check users table
    users = conn.execute('SELECT username, user_type FROM users').fetchall()
    print(f"\nRegistered users: {len(users)}")
    for user in users:
        print(f"  - {user['username']} ({user['user_type']})")
    
    conn.close()
    print("\nDatabase test completed successfully!")

if __name__ == "__main__":
    test_achievements_db()

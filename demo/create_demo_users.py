#!/usr/bin/env python3
"""
Create more demo users and achievements for testing ranking
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection, create_user
import hashlib

def create_demo_users_and_achievements():
    """Create demo users with different achievement levels"""
    conn = get_db_connection()
    
    # Create some demo users
    demo_users = [
        ('alice', 'alice123', [('first_quiz', 50), ('perfect_score', 100), ('first_story', 50)]),
        ('bob', 'bob123', [('first_quiz', 50), ('quiz_master', 300)]),
        ('carol', 'carol123', [('perfect_score', 100), ('first_story', 50), ('daily_learner', 100), ('first_quiz', 50)]),
        ('david', 'david123', [('first_story', 50)]),
        ('eve', 'eve123', [('first_quiz', 50), ('perfect_score', 100), ('quiz_master', 300), ('daily_learner', 100), ('word_collector', 200)])
    ]
    
    for username, password, achievements in demo_users:
        # Check if user already exists
        existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing:
            user_id = existing['id']
            print(f"User {username} already exists (ID: {user_id})")
        else:
            # Create user
            success, message = create_user(username, password, 'regular')
            if success:
                # Get the newly created user ID
                new_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
                user_id = new_user['id']
                print(f"Created user {username} (ID: {user_id})")
            else:
                print(f"Failed to create user {username}: {message}")
                continue
        
        # Add achievements
        for achievement_key, points in achievements:
            # Get achievement ID
            achievement = conn.execute('''
                SELECT id, name FROM achievements WHERE achievement_key = ?
            ''', (achievement_key,)).fetchone()
            
            if not achievement:
                print(f"  ❌ Achievement {achievement_key} not found")
                continue
            
            # Check if already unlocked
            existing_achievement = conn.execute('''
                SELECT id FROM user_achievements 
                WHERE user_id = ? AND achievement_id = ?
            ''', (user_id, achievement['id'])).fetchone()
            
            if not existing_achievement:
                conn.execute('''
                    INSERT INTO user_achievements (user_id, achievement_id, progress)
                    VALUES (?, ?, ?)
                ''', (user_id, achievement['id'], 100))
                print(f"  ✅ Unlocked: {achievement['name']} (+{points} pts)")
            else:
                print(f"  ⚠️  Already has: {achievement['name']}")
    
    conn.commit()
    conn.close()
    
    print("\nDemo users and achievements created!")
    
    # Show ranking
    from database import get_global_ranking
    ranking = get_global_ranking(10)
    
    print("\n--- Current Global Ranking ---")
    for user in ranking:
        print(f"#{user['rank']} - {user['username']}: {user['total_points']} pts ({user['achievements_count']} achievements)")

if __name__ == "__main__":
    create_demo_users_and_achievements()

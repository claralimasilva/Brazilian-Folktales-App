#!/usr/bin/env python3
"""
Manually unlock some achievements for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def manually_unlock_achievements():
    """Manually unlock some achievements for demo user"""
    conn = get_db_connection()
    
    # Get demo user ID
    demo_user = conn.execute('SELECT id FROM users WHERE username = ?', ('demo',)).fetchone()
    if not demo_user:
        print("Demo user not found!")
        return
    
    user_id = demo_user['id']
    
    # Get some achievements to unlock
    achievements = conn.execute('''
        SELECT id, name, description, points 
        FROM achievements 
        WHERE achievement_key IN ('quiz_beginner', 'perfect_score', 'first_reader')
    ''').fetchall()
    
    print(f"Unlocking achievements for user {user_id}...")
    
    for achievement in achievements:
        # Check if already unlocked
        existing = conn.execute('''
            SELECT id FROM user_achievements 
            WHERE user_id = ? AND achievement_id = ?
        ''', (user_id, achievement['id'])).fetchone()
        
        if not existing:
            conn.execute('''
                INSERT INTO user_achievements (user_id, achievement_id, progress)
                VALUES (?, ?, ?)
            ''', (user_id, achievement['id'], 100))
            
            print(f"✅ Unlocked: {achievement['name']} (+{achievement['points']} pts)")
        else:
            print(f"⚠️  Already unlocked: {achievement['name']}")
    
    conn.commit()
    
    # Check total points
    total_points = conn.execute('''
        SELECT COALESCE(SUM(a.points), 0) as total
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = ?
    ''', (user_id,)).fetchone()['total']
    
    conn.close()
    
    print(f"\nDemo user now has {total_points} total achievement points!")

if __name__ == "__main__":
    manually_unlock_achievements()

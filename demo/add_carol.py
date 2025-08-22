#!/usr/bin/env python3
"""
Add achievements to Carol
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def add_carol_achievements():
    conn = get_db_connection()
    
    # Get Carol's user ID
    carol = conn.execute('SELECT id FROM users WHERE username = ?', ('carol',)).fetchone()
    if not carol:
        print("Carol not found!")
        return
    
    user_id = carol['id']
    achievements_to_add = ['perfect_score', 'first_story', 'daily_learner', 'first_quiz']
    
    for achievement_key in achievements_to_add:
        achievement = conn.execute('SELECT id, name, points FROM achievements WHERE achievement_key = ?', (achievement_key,)).fetchone()
        if achievement:
            existing = conn.execute('SELECT id FROM user_achievements WHERE user_id = ? AND achievement_id = ?', (user_id, achievement['id'])).fetchone()
            if not existing:
                conn.execute('INSERT INTO user_achievements (user_id, achievement_id, progress) VALUES (?, ?, ?)', (user_id, achievement['id'], 100))
                print(f"✅ Carol unlocked: {achievement['name']} (+{achievement['points']} pts)")
    
    conn.commit()
    conn.close()
    print("Carol's achievements added!")

if __name__ == "__main__":
    add_carol_achievements()

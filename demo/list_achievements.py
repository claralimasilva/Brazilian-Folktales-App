#!/usr/bin/env python3
"""
Check achievement keys in database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def list_achievements():
    conn = get_db_connection()
    achievements = conn.execute('SELECT achievement_key, name, points FROM achievements ORDER BY category, points').fetchall()
    
    print("Available achievements:")
    for achievement in achievements:
        print(f"  {achievement['achievement_key']}: {achievement['name']} ({achievement['points']} pts)")
    
    conn.close()

if __name__ == "__main__":
    list_achievements()

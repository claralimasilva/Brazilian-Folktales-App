#!/usr/bin/env python3
"""
Show final ranking
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_global_ranking

def show_ranking():
    ranking = get_global_ranking(10)
    print("--- FINAL GLOBAL RANKING ---")
    for user in ranking:
        print(f"#{user['rank']} - {user['username']}: {user['total_points']} pts ({user['achievements_count']} achievements)")

if __name__ == "__main__":
    show_ranking()

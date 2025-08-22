import sqlite3
import hashlib
import os
from datetime import datetime
from pathlib import Path

# Use proper path configuration
DATABASE_DIR = Path(__file__).parent / "data"
DATABASE_FILE = DATABASE_DIR / 'folktale_users.db'

# Ensure data directory exists
DATABASE_DIR.mkdir(exist_ok=True)

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(str(DATABASE_FILE))
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """Initialize database with tables and default admin user"""
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL DEFAULT 'regular',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create user_progress table for learning statistics
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            story_id TEXT,
            chapter INTEGER DEFAULT 1,
            completed_chapters TEXT DEFAULT '[]',
            quiz_scores TEXT DEFAULT '[]',
            vocabulary_learned TEXT DEFAULT '[]',
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create sessions table for better session management
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create achievements table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achievement_key TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT DEFAULT '🏆',
            category TEXT DEFAULT 'general',
            points INTEGER DEFAULT 100,
            requirement_type TEXT NOT NULL,
            requirement_value INTEGER DEFAULT 1,
            is_hidden BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_achievements table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id INTEGER NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            progress INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (achievement_id) REFERENCES achievements (id),
            UNIQUE(user_id, achievement_id)
        )
    ''')
    
    # Create activity_log table for tracking user actions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            activity_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if admin user exists, if not create one
    admin_exists = conn.execute(
        'SELECT COUNT(*) as count FROM users WHERE user_type = "admin"'
    ).fetchone()
    
    if admin_exists['count'] == 0:
        # Create default admin user (this should be changed in production)
        admin_password = hash_password('admin_secure_2024!')
        conn.execute(
            'INSERT INTO users (username, password_hash, user_type) VALUES (?, ?, ?)',
            ('admin', admin_password, 'admin')
        )
        print("Default admin user created: admin / admin_secure_2024!")
        print("Please change this password immediately in production!")
    
    # Initialize default achievements if none exist
    achievements_exist = conn.execute(
        'SELECT COUNT(*) as count FROM achievements'
    ).fetchone()
    
    if achievements_exist['count'] == 0:
        init_default_achievements(conn)
    
    conn.commit()
    conn.close()

def init_default_achievements(conn):
    """Initialize default achievements"""
    default_achievements = [
        # Reading Achievements
        ('first_story', 'First Reader', 'Complete your first story', '📖', 'reading', 50, 'stories_completed', 1, 0),
        ('story_master', 'Story Master', 'Complete 5 different stories', '📚', 'reading', 250, 'stories_completed', 5, 0),
        ('bookworm', 'Bookworm', 'Complete 10 different stories', '🐛', 'reading', 500, 'stories_completed', 10, 0),
        ('chapter_explorer', 'Chapter Explorer', 'Read 25 chapters', '🗺️', 'reading', 200, 'chapters_read', 25, 0),
        ('marathon_reader', 'Marathon Reader', 'Read 100 chapters', '🏃‍♂️', 'reading', 750, 'chapters_read', 100, 0),
        
        # Quiz Achievements  
        ('first_quiz', 'Quiz Beginner', 'Complete your first quiz', '🎯', 'quiz', 50, 'quizzes_completed', 1, 0),
        ('quiz_master', 'Quiz Master', 'Complete 20 quizzes', '🏆', 'quiz', 300, 'quizzes_completed', 20, 0),
        ('perfect_score', 'Perfect Score', 'Get 100% on a quiz', '⭐', 'quiz', 100, 'perfect_quizzes', 1, 0),
        ('perfectionist', 'Perfectionist', 'Get 100% on 10 quizzes', '💎', 'quiz', 500, 'perfect_quizzes', 10, 0),
        ('quick_thinker', 'Quick Thinker', 'Complete a quiz in under 30 seconds', '⚡', 'quiz', 150, 'quick_quiz', 1, 0),
        
        # Learning Streak Achievements
        ('daily_learner', 'Daily Learner', 'Study for 3 consecutive days', '📅', 'streak', 100, 'daily_streak', 3, 0),
        ('weekly_warrior', 'Weekly Warrior', 'Study for 7 consecutive days', '🔥', 'streak', 300, 'daily_streak', 7, 0),
        ('monthly_master', 'Monthly Master', 'Study for 30 consecutive days', '👑', 'streak', 1000, 'daily_streak', 30, 0),
        
        # Vocabulary Achievements
        ('word_collector', 'Word Collector', 'Learn 50 new words', '📝', 'vocabulary', 200, 'words_learned', 50, 0),
        ('vocabulary_master', 'Vocabulary Master', 'Learn 200 new words', '📖', 'vocabulary', 600, 'words_learned', 200, 0),
        ('linguist', 'Linguist', 'Learn 500 new words', '🌍', 'vocabulary', 1500, 'words_learned', 500, 0),
        
        # Special Achievements
        ('early_bird', 'Early Bird', 'Study before 8 AM', '🌅', 'special', 100, 'early_study', 1, 0),
        ('night_owl', 'Night Owl', 'Study after 10 PM', '🦉', 'special', 100, 'night_study', 1, 0),
        ('completionist', 'Completionist', 'Complete all available stories', '🏁', 'special', 2000, 'all_stories_completed', 1, 1),
        ('speed_reader', 'Speed Reader', 'Read 10 chapters in one day', '💨', 'special', 300, 'chapters_in_day', 10, 0),
        
        # Audio Achievements
        ('audio_learner', 'Audio Learner', 'Use audio feature 10 times', '🎧', 'audio', 150, 'audio_used', 10, 0),
        ('listening_expert', 'Listening Expert', 'Use audio feature 50 times', '🔊', 'audio', 400, 'audio_used', 50, 0),
        
        # Exploration Achievements
        ('theme_explorer', 'Theme Explorer', 'Try all available themes', '🎨', 'exploration', 100, 'themes_used', 4, 0),
        ('cursor_collector', 'Cursor Collector', 'Try all cursor styles', '🖱️', 'exploration', 75, 'cursors_used', 5, 0),
    ]
    
    for achievement in default_achievements:
        conn.execute('''
            INSERT INTO achievements 
            (achievement_key, name, description, icon, category, points, requirement_type, requirement_value, is_hidden)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', achievement)
    
    print(f"Initialized {len(default_achievements)} default achievements!")

def create_user(username, password, user_type='regular'):
    """Create a new user"""
    conn = get_db_connection()
    try:
        password_hash = hash_password(password)
        conn.execute(
            'INSERT INTO users (username, password_hash, user_type) VALUES (?, ?, ?)',
            (username, password_hash, user_type)
        )
        conn.commit()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, f"Error creating user: {str(e)}"
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate user and return user data"""
    conn = get_db_connection()
    try:
        password_hash = hash_password(password)
        user = conn.execute(
            'SELECT id, username, user_type, is_active FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        ).fetchone()
        
        if user and user['is_active']:
            # Update last login
            conn.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.now(), user['id'])
            )
            conn.commit()
            
            return True, {
                'id': user['id'],
                'username': user['username'],
                'user_type': user['user_type'],
                'is_admin': user['user_type'] == 'admin'
            }
        else:
            return False, None
    except Exception as e:
        print(f"Authentication error: {e}")
        return False, None
    finally:
        conn.close()

def get_user_by_id(user_id):
    """Get user information by ID"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            'SELECT id, username, user_type, created_at, last_login FROM users WHERE id = ? AND is_active = 1',
            (user_id,)
        ).fetchone()
        
        if user:
            return {
                'id': user['id'],
                'username': user['username'],
                'user_type': user['user_type'],
                'is_admin': user['user_type'] == 'admin',
                'created_at': user['created_at'],
                'last_login': user['last_login']
            }
        return None
    finally:
        conn.close()

def get_all_users():
    """Get all users (admin only)"""
    conn = get_db_connection()
    try:
        users = conn.execute(
            'SELECT id, username, user_type, created_at, last_login, is_active FROM users ORDER BY created_at DESC'
        ).fetchall()
        
        return [dict(user) for user in users]
    finally:
        conn.close()

def update_user_password(user_id, new_password):
    """Update user password"""
    conn = get_db_connection()
    try:
        password_hash = hash_password(new_password)
        conn.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (password_hash, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False
    finally:
        conn.close()

def deactivate_user(user_id):
    """Deactivate user account"""
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE users SET is_active = 0 WHERE id = ?',
            (user_id,)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deactivating user: {e}")
        return False
    finally:
        conn.close()

def save_user_progress(user_id, story_id, chapter, completed_chapters, quiz_scores, vocabulary_learned):
    """Save or update user progress"""
    conn = get_db_connection()
    try:
        # Check if progress exists
        existing = conn.execute(
            'SELECT id FROM user_progress WHERE user_id = ? AND story_id = ?',
            (user_id, story_id)
        ).fetchone()
        
        if existing:
            # Update existing progress
            conn.execute(
                '''UPDATE user_progress 
                   SET chapter = ?, completed_chapters = ?, quiz_scores = ?, 
                       vocabulary_learned = ?, last_accessed = ?
                   WHERE user_id = ? AND story_id = ?''',
                (chapter, str(completed_chapters), str(quiz_scores), 
                 str(vocabulary_learned), datetime.now(), user_id, story_id)
            )
        else:
            # Insert new progress
            conn.execute(
                '''INSERT INTO user_progress 
                   (user_id, story_id, chapter, completed_chapters, quiz_scores, vocabulary_learned)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, story_id, chapter, str(completed_chapters), 
                 str(quiz_scores), str(vocabulary_learned))
            )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving progress: {e}")
        return False
    finally:
        conn.close()

def get_user_progress(user_id, story_id=None):
    """Get user progress for specific story or all stories"""
    conn = get_db_connection()
    try:
        if story_id:
            progress = conn.execute(
                'SELECT * FROM user_progress WHERE user_id = ? AND story_id = ?',
                (user_id, story_id)
            ).fetchone()
            return dict(progress) if progress else None
        else:
            progress = conn.execute(
                'SELECT * FROM user_progress WHERE user_id = ?',
                (user_id,)
            ).fetchall()
            return [dict(p) for p in progress]
    finally:
        conn.close()

# Initialize database when module is imported
if __name__ == "__main__":
    init_database()

# Achievement Functions
def log_user_activity(user_id, activity_type, activity_data=None):
    """Log user activity for achievement tracking"""
    conn = get_db_connection()
    import json
    
    data_json = json.dumps(activity_data) if activity_data else None
    
    conn.execute('''
        INSERT INTO activity_log (user_id, activity_type, activity_data)
        VALUES (?, ?, ?)
    ''', (user_id, activity_type, data_json))
    
    conn.commit()
    conn.close()
    
    # Check for new achievements after logging activity
    return check_achievements(user_id, activity_type, activity_data)

def check_achievements(user_id, activity_type, activity_data=None):
    """Check if user has unlocked any new achievements"""
    conn = get_db_connection()
    
    # Get user's current achievements
    unlocked = set()
    user_achievements = conn.execute('''
        SELECT a.achievement_key 
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = ?
    ''', (user_id,)).fetchall()
    
    for ua in user_achievements:
        unlocked.add(ua['achievement_key'])
    
    # Get all achievements that could be unlocked
    achievements = conn.execute('''
        SELECT * FROM achievements WHERE achievement_key NOT IN (
            SELECT a.achievement_key 
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.id
            WHERE ua.user_id = ?
        )
    ''', (user_id,)).fetchall()
    
    newly_unlocked = []
    
    for achievement in achievements:
        if should_unlock_achievement(conn, user_id, achievement):
            # Unlock the achievement
            conn.execute('''
                INSERT INTO user_achievements (user_id, achievement_id, progress)
                VALUES (?, ?, ?)
            ''', (user_id, achievement['id'], achievement['requirement_value']))
            
            newly_unlocked.append({
                'key': achievement['achievement_key'],
                'name': achievement['name'],
                'description': achievement['description'],
                'icon': achievement['icon'],
                'points': achievement['points']
            })
    
    conn.commit()
    conn.close()
    
    return newly_unlocked

def should_unlock_achievement(conn, user_id, achievement):
    """Check if a specific achievement should be unlocked"""
    req_type = achievement['requirement_type']
    req_value = achievement['requirement_value']
    
    if req_type == 'stories_completed':
        count = conn.execute('''
            SELECT COUNT(DISTINCT story_id) as count
            FROM user_progress 
            WHERE user_id = ? AND completed_chapters != '[]'
        ''', (user_id,)).fetchone()
        return count['count'] >= req_value
        
    elif req_type == 'chapters_read':
        # Count total chapters read by looking at completed_chapters JSON
        import json
        progress_records = conn.execute('''
            SELECT completed_chapters FROM user_progress WHERE user_id = ?
        ''', (user_id,)).fetchall()
        
        total = 0
        for record in progress_records:
            if record['completed_chapters']:
                try:
                    chapters = json.loads(record['completed_chapters'])
                    total += len(chapters)
                except:
                    continue
        
        return total >= req_value
        
    elif req_type == 'quizzes_completed':
        # Count total quiz attempts
        import json
        progress_records = conn.execute('''
            SELECT quiz_scores FROM user_progress WHERE user_id = ?
        ''', (user_id,)).fetchall()
        
        total = 0
        for record in progress_records:
            if record['quiz_scores']:
                try:
                    scores = json.loads(record['quiz_scores'])
                    total += len(scores)
                except:
                    continue
        
        return total >= req_value
        
    elif req_type == 'perfect_quizzes':
        # Count perfect quiz scores (100%)
        import json
        count = 0
        progress_records = conn.execute('''
            SELECT quiz_scores FROM user_progress WHERE user_id = ?
        ''', (user_id,)).fetchall()
        
        for record in progress_records:
            if record['quiz_scores']:
                try:
                    scores = json.loads(record['quiz_scores'])
                    count += sum(1 for score in scores if score >= 100)
                except:
                    continue
        
        return count >= req_value
        
    elif req_type == 'words_learned':
        # Count unique vocabulary words learned
        import json
        total = 0
        progress_records = conn.execute('''
            SELECT vocabulary_learned FROM user_progress WHERE user_id = ?
        ''', (user_id,)).fetchall()
        
        for record in progress_records:
            if record['vocabulary_learned']:
                try:
                    words = json.loads(record['vocabulary_learned'])
                    total += len(words)
                except:
                    continue
        
        return total >= req_value
        
    elif req_type == 'daily_streak':
        # Check consecutive days of activity
        from datetime import datetime, timedelta
        
        activities = conn.execute('''
            SELECT DATE(timestamp) as activity_date
            FROM activity_log 
            WHERE user_id = ? 
            GROUP BY DATE(timestamp)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, req_value + 5)).fetchall()
        
        if not activities:
            return False
            
        # Calculate consecutive days
        current_streak = 1
        if len(activities) < req_value:
            return False
            
        for i in range(1, len(activities)):
            prev_date = datetime.strptime(activities[i-1]['activity_date'], '%Y-%m-%d').date()
            curr_date = datetime.strptime(activities[i]['activity_date'], '%Y-%m-%d').date()
            
            if (prev_date - curr_date).days == 1:
                current_streak += 1
                if current_streak >= req_value:
                    return True
            else:
                break
                
        return current_streak >= req_value
    
    # Add more achievement types as needed
    return False

def get_user_achievements(user_id):
    """Get all achievements for a user"""
    conn = get_db_connection()
    
    unlocked = conn.execute('''
        SELECT a.*, ua.unlocked_at, ua.progress
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = ?
        ORDER BY ua.unlocked_at DESC
    ''', (user_id,)).fetchall()
    
    all_achievements = conn.execute('''
        SELECT * FROM achievements 
        WHERE is_hidden = 0
        ORDER BY category, points
    ''').fetchall()
    
    conn.close()
    
    # Convert to dictionaries and add unlock status
    unlocked_dict = {a['achievement_key']: dict(a) for a in unlocked}
    
    result = []
    for achievement in all_achievements:
        achievement_dict = dict(achievement)
        achievement_dict['unlocked'] = achievement['achievement_key'] in unlocked_dict
        if achievement_dict['unlocked']:
            achievement_dict['unlocked_at'] = unlocked_dict[achievement['achievement_key']]['unlocked_at']
        result.append(achievement_dict)
    
    return result

def get_user_achievement_stats(user_id):
    """Get achievement statistics for a user"""
    conn = get_db_connection()
    
    total_achievements = conn.execute('''
        SELECT COUNT(*) as count FROM achievements WHERE is_hidden = 0
    ''').fetchone()['count']
    
    unlocked_achievements = conn.execute('''
        SELECT COUNT(*) as count 
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = ? AND a.is_hidden = 0
    ''', (user_id,)).fetchone()['count']
    
    total_points = conn.execute('''
        SELECT COALESCE(SUM(a.points), 0) as total
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = ?
    ''', (user_id,)).fetchone()['total']
    
    conn.close()
    
    return {
        'total_achievements': total_achievements,
        'unlocked_achievements': unlocked_achievements,
        'completion_percentage': round((unlocked_achievements / total_achievements) * 100, 1) if total_achievements > 0 else 0,
        'total_points': total_points
    }

def get_global_ranking(limit=50):
    """Get global ranking of users by achievement points"""
    conn = get_db_connection()
    
    ranking = conn.execute('''
        SELECT 
            u.id,
            u.username,
            COALESCE(SUM(a.points), 0) as total_points,
            COUNT(ua.achievement_id) as achievements_count,
            MAX(ua.unlocked_at) as last_achievement
        FROM users u
        LEFT JOIN user_achievements ua ON u.id = ua.user_id
        LEFT JOIN achievements a ON ua.achievement_id = a.id
        WHERE u.user_type = 'regular'
        GROUP BY u.id, u.username
        ORDER BY total_points DESC, achievements_count DESC, last_achievement DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries with rank
    result = []
    for i, user in enumerate(ranking):
        result.append({
            'rank': i + 1,
            'user_id': user['id'],
            'username': user['username'],
            'total_points': user['total_points'],
            'achievements_count': user['achievements_count'],
            'last_achievement': user['last_achievement']
        })
    
    return result

def get_user_rank(user_id):
    """Get specific user's rank in global ranking"""
    conn = get_db_connection()
    
    # Get user's points and achievements
    user_stats = conn.execute('''
        SELECT 
            u.username,
            COALESCE(SUM(a.points), 0) as total_points,
            COUNT(ua.achievement_id) as achievements_count,
            MAX(ua.unlocked_at) as last_achievement
        FROM users u
        LEFT JOIN user_achievements ua ON u.id = ua.user_id
        LEFT JOIN achievements a ON ua.achievement_id = a.id
        WHERE u.id = ? AND u.user_type = 'regular'
        GROUP BY u.id, u.username
    ''', (user_id,)).fetchone()
    
    if not user_stats:
        conn.close()
        return None
    
    # Count how many users have better scores
    better_users = conn.execute('''
        SELECT COUNT(*) as count
        FROM (
            SELECT 
                u.id,
                COALESCE(SUM(a.points), 0) as total_points,
                COUNT(ua.achievement_id) as achievements_count,
                MAX(ua.unlocked_at) as last_achievement
            FROM users u
            LEFT JOIN user_achievements ua ON u.id = ua.user_id
            LEFT JOIN achievements a ON ua.achievement_id = a.id
            WHERE u.user_type = 'regular'
            GROUP BY u.id
        ) ranked
        WHERE 
            ranked.total_points > ? OR 
            (ranked.total_points = ? AND ranked.achievements_count > ?) OR
            (ranked.total_points = ? AND ranked.achievements_count = ? AND ranked.last_achievement > ?)
    ''', (
        user_stats['total_points'],
        user_stats['total_points'], user_stats['achievements_count'],
        user_stats['total_points'], user_stats['achievements_count'], user_stats['last_achievement']
    )).fetchone()
    
    conn.close()
    
    rank = better_users['count'] + 1
    
    return {
        'rank': rank,
        'username': user_stats['username'],
        'total_points': user_stats['total_points'],
        'achievements_count': user_stats['achievements_count'],
        'last_achievement': user_stats['last_achievement']
    }

def get_category_rankings():
    """Get rankings by achievement categories"""
    conn = get_db_connection()
    
    categories = ['reading', 'quiz', 'streak', 'vocabulary', 'special', 'audio', 'exploration']
    rankings = {}
    
    for category in categories:
        category_ranking = conn.execute('''
            SELECT 
                u.id,
                u.username,
                COALESCE(SUM(a.points), 0) as category_points,
                COUNT(ua.achievement_id) as category_achievements
            FROM users u
            LEFT JOIN user_achievements ua ON u.id = ua.user_id
            LEFT JOIN achievements a ON ua.achievement_id = a.id AND a.category = ?
            WHERE u.user_type = 'regular'
            GROUP BY u.id, u.username
            HAVING category_points > 0
            ORDER BY category_points DESC, category_achievements DESC
            LIMIT 10
        ''', (category,)).fetchall()
        
        rankings[category] = [
            {
                'rank': i + 1,
                'user_id': user['id'],
                'username': user['username'],
                'points': user['category_points'],
                'achievements': user['category_achievements']
            }
            for i, user in enumerate(category_ranking)
        ]
    
    conn.close()
    return rankings

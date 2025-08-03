#!/usr/bin/env python3
"""
Database operations for Telegram Anonymous Chat Bot
"""
import sqlite3
import time
import random
import logging
from typing import Optional, List, Dict, Tuple, Any
from config import DB_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager with connection handling and operations"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            c = conn.cursor()
            
            # User profiles table
            c.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                gender TEXT,
                age INTEGER,
                bio TEXT,
                photo_id TEXT,
                language TEXT,
                pro_expires_at INTEGER,
                is_banned INTEGER DEFAULT 0,
                banned_until INTEGER DEFAULT 0,
                hobbies TEXT,
                points INTEGER DEFAULT 0
            )''')
            
            # Reports table
            c.execute('''CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER,
                reported_id INTEGER,
                reason TEXT,
                timestamp INTEGER
            )''')
            
            # Block list table
            c.execute('''CREATE TABLE IF NOT EXISTS block_list (
                user_id INTEGER,
                blocked_id INTEGER,
                PRIMARY KEY(user_id, blocked_id)
            )''')
            
            # Chat queue table
            c.execute('''CREATE TABLE IF NOT EXISTS chat_queue (
                user_id INTEGER PRIMARY KEY,
                gender_pref TEXT,
                hobby_pref TEXT,
                age_min INTEGER,
                age_max INTEGER,
                is_pro INTEGER DEFAULT 0,
                queued_at INTEGER DEFAULT 0
            )''')
            
            # Chat sessions table
            c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                partner_id INTEGER,
                started_at INTEGER,
                secret_mode INTEGER DEFAULT 0
            )''')
            
            # Group chat table
            c.execute('''CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                members TEXT,
                started_at INTEGER
            )''')
            
            # Quiz winners table
            c.execute('''CREATE TABLE IF NOT EXISTS quiz_winners (
                quiz_id INTEGER,
                user_id INTEGER,
                prize TEXT,
                timestamp INTEGER DEFAULT 0
            )''')
            
            # Feedback table
            c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                partner_id INTEGER,
                rating INTEGER,
                comment TEXT,
                timestamp INTEGER
            )''')
            
            # Polls table
            c.execute('''CREATE TABLE IF NOT EXISTS polls (
                poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                options TEXT,
                responses TEXT,
                created_at INTEGER
            )''')
            
            conn.commit()
        logger.info("Database initialized successfully.")

# Initialize database manager
db_manager = DatabaseManager()

# ========== User Profile Operations ==========

def create_or_update_user(user_id: int, username: str = None) -> None:
    """Create new user or update existing username"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM user_profiles WHERE user_id=?", (user_id,))
        if not c.fetchone():
            # Give new users 1200 points so they can test Pro redemption
            c.execute("INSERT INTO user_profiles (user_id, username, points) VALUES (?,?,?)", 
                     (user_id, username, 1200))
        else:
            c.execute("UPDATE user_profiles SET username=? WHERE user_id=?", 
                     (username, user_id))
        conn.commit()

def get_user_profile(user_id: int) -> Dict[str, Any]:
    """Get user profile data"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("""SELECT gender, age, bio, photo_id, hobbies, points, language, pro_expires_at 
                     FROM user_profiles WHERE user_id=?""", (user_id,))
        row = c.fetchone()
        if row:
            data = dict(zip(["gender", "age", "bio", "photo_id", "hobbies", "points", "language", "pro_expires_at"], row))
            data["hobbies"] = data["hobbies"].split(",") if data["hobbies"] else []
            return data
        return {}

def update_user_profile(user_id: int, **kwargs) -> None:
    """Update user profile fields"""
    if not kwargs:
        return
    
    # Handle hobbies list conversion
    if 'hobbies' in kwargs and isinstance(kwargs['hobbies'], list):
        kwargs['hobbies'] = ",".join(kwargs['hobbies'])
    
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        fields = ", ".join([f"{k}=?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        c.execute(f"UPDATE user_profiles SET {fields} WHERE user_id=?", values)
        conn.commit()

def is_profile_complete(user_id: int) -> bool:
    """Check if user profile is complete"""
    profile = get_user_profile(user_id)
    required_fields = ["gender", "age", "bio", "photo_id"]
    return all(profile.get(field) for field in required_fields)

def is_user_pro(user_id: int) -> bool:
    """Check if user has active Pro subscription"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT pro_expires_at FROM user_profiles WHERE user_id=?", (user_id,))
        row = c.fetchone()
        return bool(row and row[0] and row[0] > int(time.time()))

def get_user_ban_status(user_id: int) -> Tuple[bool, int]:
    """Get user ban status and ban expiry"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT is_banned, banned_until FROM user_profiles WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if row:
            return bool(row[0]), row[1]
        return False, 0

def ban_user(user_id: int, banned_until: int) -> None:
    """Ban user until specified timestamp"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE user_profiles SET is_banned=1, banned_until=? WHERE user_id=?", 
                 (banned_until, user_id))
        conn.commit()

def unban_user(user_id: int) -> None:
    """Unban user"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE user_profiles SET is_banned=0, banned_until=0 WHERE user_id=?", (user_id,))
        conn.commit()

# ========== Chat Operations ==========

def add_to_queue(user_id: int, gender_pref: str = None, hobby_pref: str = None, 
                age_min: int = None, age_max: int = None, is_pro: bool = False) -> None:
    """Add user to chat queue"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        queued_at = int(time.time())
        c.execute("""INSERT OR REPLACE INTO chat_queue 
                     (user_id, gender_pref, hobby_pref, age_min, age_max, is_pro, queued_at) 
                     VALUES (?,?,?,?,?,?,?)""", 
                 (user_id, gender_pref, hobby_pref, age_min, age_max, int(is_pro), queued_at))
        conn.commit()

def remove_from_queue(user_id: int) -> None:
    """Remove user from chat queue"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM chat_queue WHERE user_id=?", (user_id,))
        conn.commit()

def find_partner(user_id: int, gender_pref: str = None, hobby_pref: str = None, 
                age_min: int = None, age_max: int = None) -> Optional[int]:
    """Find available chat partner with improved logic"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        
        # Get user's blocked list
        c.execute("SELECT blocked_id FROM block_list WHERE user_id=?", (user_id,))
        blocked_ids = [row[0] for row in c.fetchall()]
        
        # Base query for available users - simplified for basic mode
        base_query = """
            SELECT u.user_id, u.gender, u.age, u.hobbies 
            FROM user_profiles u 
            WHERE u.user_id != ? 
            AND u.is_banned = 0 
            AND u.user_id NOT IN (SELECT user_id FROM sessions)
        """
        params = [user_id]
        
        # Add filters based on preferences (only if user has data)
        if gender_pref and gender_pref != "Any":
            base_query += " AND (u.gender = ? OR u.gender IS NULL)"
            params.append(gender_pref)
        
        if age_min is not None and age_max is not None:
            base_query += " AND (u.age BETWEEN ? AND ? OR u.age IS NULL)"
            params.extend([age_min, age_max])
        
        # Note: Removed strict profile completion requirement
        # Users can chat even without complete profile
        
        c.execute(base_query, params)
        candidates = c.fetchall()
        
        # Filter out blocked users
        available_candidates = []
        for candidate in candidates:
            candidate_id = candidate[0]
            if candidate_id not in blocked_ids and not is_user_blocked_by(candidate_id, user_id):
                available_candidates.append(candidate)
        
        if not available_candidates:
            return None
        
        # Priority matching
        if hobby_pref and hobby_pref != "Any":
            # First try to match hobby preference
            for candidate in available_candidates:
                candidate_id, gender, age, hobbies_str = candidate
                hobbies = hobbies_str.split(",") if hobbies_str else []
                if hobby_pref in hobbies:
                    return candidate_id
        
        # If no hobby match or no hobby preference, return first available
        return available_candidates[0][0] if available_candidates else None

def create_chat_session(user_id: int, partner_id: int, secret_mode: bool = False) -> None:
    """Create chat session between two users"""
    now = int(time.time())
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        # Create session for both users
        c.execute("""INSERT OR REPLACE INTO sessions 
                     (user_id, partner_id, started_at, secret_mode) VALUES (?,?,?,?)""", 
                 (user_id, partner_id, now, int(secret_mode)))
        c.execute("""INSERT OR REPLACE INTO sessions 
                     (user_id, partner_id, started_at, secret_mode) VALUES (?,?,?,?)""", 
                 (partner_id, user_id, now, int(secret_mode)))
        
        # Remove both users from queue
        c.execute("DELETE FROM chat_queue WHERE user_id IN (?, ?)", (user_id, partner_id))
        conn.commit()

def get_chat_partner(user_id: int) -> Optional[int]:
    """Get current chat partner ID"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
        row = c.fetchone()
        return row[0] if row else None

def end_chat_session(user_id: int) -> Optional[int]:
    """End chat session and return partner ID"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if row:
            partner_id = row[0]
            c.execute("DELETE FROM sessions WHERE user_id IN (?, ?)", (user_id, partner_id))
            conn.commit()
            return partner_id
    return None

def is_in_chat(user_id: int) -> bool:
    """Check if user is currently in a chat session"""
    return get_chat_partner(user_id) is not None

def set_secret_mode(user_id: int, secret_mode: bool = True) -> None:
    """Set secret mode for user's current session"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE sessions SET secret_mode=? WHERE user_id=?", (int(secret_mode), user_id))
        conn.commit()

def is_secret_mode(user_id: int) -> bool:
    """Check if user's current session is in secret mode"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT secret_mode FROM sessions WHERE user_id=?", (user_id,))
        row = c.fetchone()
        return bool(row and row[0])

# ========== Block and Report Operations ==========

def block_user(user_id: int, blocked_id: int) -> None:
    """Block a user"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO block_list (user_id, blocked_id) VALUES (?,?)", 
                 (user_id, blocked_id))
        conn.commit()

def unblock_user(user_id: int, blocked_id: int) -> None:
    """Unblock a user"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM block_list WHERE user_id=? AND blocked_id=?", (user_id, blocked_id))
        conn.commit()

def is_user_blocked_by(user_id: int, target_id: int) -> bool:
    """Check if user is blocked by target"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM block_list WHERE user_id=? AND blocked_id=?", (target_id, user_id))
        return c.fetchone() is not None

def add_report(reporter_id: int, reported_id: int, reason: str) -> None:
    """Add a report"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        timestamp = int(time.time())
        c.execute("INSERT INTO reports (reporter_id, reported_id, reason, timestamp) VALUES (?,?,?,?)",
                 (reporter_id, reported_id, reason, timestamp))
        conn.commit()

def get_user_reports(user_id: int, days: int = 7) -> List[Tuple]:
    """Get reports for a user in the last N days"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        since_timestamp = int(time.time()) - (days * 86400)
        c.execute("SELECT * FROM reports WHERE reported_id=? AND timestamp > ?", 
                 (user_id, since_timestamp))
        return c.fetchall()

# ========== Statistics and Leaderboard ==========

def get_user_stats() -> Dict[str, int]:
    """Get general user statistics"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM user_profiles")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM sessions")
        active_chats = c.fetchone()[0] // 2  # Divide by 2 since each chat has 2 entries
        
        c.execute("SELECT COUNT(*) FROM reports WHERE timestamp > ?", (int(time.time()) - 86400,))
        reports_24h = c.fetchone()[0]
        
        return {
            "total_users": total_users,
            "active_chats": active_chats,
            "reports_24h": reports_24h
        }

def get_top_users(limit: int = 5) -> List[Tuple[int, int]]:
    """Get top users by points"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, points FROM user_profiles ORDER BY points DESC LIMIT ?", (limit,))
        return c.fetchall()

def add_user_points(user_id: int, points: int) -> None:
    """Add points to user"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE user_profiles SET points = points + ? WHERE user_id=?", (points, user_id))
        conn.commit()

# ========== Utility Functions ==========

def mask_username(username: str) -> str:
    """Mask username for privacy"""
    if not username:
        return "User" + "".join(random.choices("0123456789", k=4))
    if len(username) <= 4:
        return username[0] + "**" + username[-1] if len(username) > 1 else username
    return username[:2] + "*" * (len(username) - 3) + username[-1]

def cleanup_expired_queues(max_age_minutes: int = 30) -> None:
    """Clean up old queue entries"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        cutoff_time = int(time.time()) - (max_age_minutes * 60)
        c.execute("DELETE FROM chat_queue WHERE queued_at < ?", (cutoff_time,))
        conn.commit()

def get_queue_stats() -> Dict[str, int]:
    """Get queue statistics"""
    with db_manager.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM chat_queue")
        total_in_queue = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM chat_queue WHERE is_pro = 1")
        pro_in_queue = c.fetchone()[0]
        
        return {
            "total_in_queue": total_in_queue,
            "pro_in_queue": pro_in_queue,
            "regular_in_queue": total_in_queue - pro_in_queue
        }
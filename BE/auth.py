import json
import hashlib
import uuid
import jwt
import requests
import os
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps

# GitHub Gist Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable not set. Please add it to Vercel secrets.")
GITHUB_USERNAME = 'Kenbachkhoa1234'
GIST_FILENAME = 'chess_users.json'

JWT_SECRET = os.environ.get('JWT_SECRET', 'chess-game-secret-key-2024')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRATION = 24 * 60 * 60


class AuthManager:
    def __init__(self):
        self.users = {}
        self.gist_id = None
        self.init_gist()
    
    def init_gist(self):
        """Initialize Gist or load existing users from Gist"""
        try:
            self.gist_id = self.find_gist()
            if self.gist_id:
                self.load_from_gist()
            else:
                self.create_gist()
        except Exception as e:
            print(f"Gist initialization error: {e}")
            self.create_demo_users()
    
    def find_gist(self):
        """Find existing chess_users.json gist"""
        try:
            headers = {'Authorization': f'token {GITHUB_TOKEN}'}
            resp = requests.get(f'https://api.github.com/users/{GITHUB_USERNAME}/gists', 
                              headers=headers, timeout=5)
            if resp.status_code == 200:
                for gist in resp.json():
                    if GIST_FILENAME in gist.get('files', {}):
                        return gist['id']
        except Exception as e:
            print(f"Find gist error: {e}")
        return None
    
    def create_gist(self):
        """Create new gist with initial users"""
        try:
            demo_data = {
                "demo@example.com": {
                    "username": "demo",
                    "email": "demo@example.com",
                    "password_hash": self.hash_password("demo123"),
                    "elo": 1600,
                    "wins": 0,
                    "losses": 0,
                    "user_id": str(uuid.uuid4())
                }
            }
            
            payload = {
                'description': 'Chess Game Users Database',
                'public': False,
                'files': {
                    GIST_FILENAME: {
                        'content': json.dumps(demo_data, indent=2)
                    }
                }
            }
            
            headers = {'Authorization': f'token {GITHUB_TOKEN}'}
            resp = requests.post('https://api.github.com/gists', 
                               json=payload, 
                               headers=headers, 
                               timeout=10)
            
            if resp.status_code == 201:
                gist = resp.json()
                self.gist_id = gist['id']
                self.users = demo_data
                print(f"✓ Created gist: {self.gist_id}")
            else:
                print(f"Failed to create gist: {resp.status_code}")
                self.create_demo_users()
        except Exception as e:
            print(f"Create gist error: {e}")
            self.create_demo_users()
    
    def load_from_gist(self):
        """Load users from GitHub Gist"""
        try:
            headers = {'Authorization': f'token {GITHUB_TOKEN}'}
            resp = requests.get(f'https://api.github.com/gists/{self.gist_id}', 
                              headers=headers, timeout=5)
            
            if resp.status_code == 200:
                gist = resp.json()
                content = gist['files'][GIST_FILENAME]['content']
                self.users = json.loads(content)
                print(f"✓ Loaded {len(self.users)} users from gist")
            else:
                print(f"Failed to load gist: {resp.status_code}")
                self.create_demo_users()
        except Exception as e:
            print(f"Load from gist error: {e}")
            self.create_demo_users()
    
    def save_to_gist(self):
        """Save users to GitHub Gist"""
        try:
            if not self.gist_id:
                return False
            
            payload = {
                'files': {
                    GIST_FILENAME: {
                        'content': json.dumps(self.users, indent=2)
                    }
                }
            }
            
            headers = {'Authorization': f'token {GITHUB_TOKEN}'}
            resp = requests.patch(f'https://api.github.com/gists/{self.gist_id}', 
                                json=payload, 
                                headers=headers, 
                                timeout=10)
            
            return resp.status_code == 200
        except Exception as e:
            print(f"Save to gist error: {e}")
            return False
    
    def create_demo_users(self):
        """Create demo users if gist fails"""
        self.users = {
            "demo@example.com": {
                "username": "demo",
                "email": "demo@example.com",
                "password_hash": self.hash_password("demo123"),
                "elo": 1600,
                "wins": 0,
                "losses": 0,
                "user_id": str(uuid.uuid4())
            }
        }
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, email, password, elo=1600):
        """Register new user"""
        if email in self.users:
            return False, "Email already registered"
        
        user = {
            "username": username,
            "email": email,
            "password_hash": self.hash_password(password),
            "elo": elo,
            "wins": 0,
            "losses": 0,
            "user_id": str(uuid.uuid4())
        }
        
        self.users[email] = user
        self.save_to_gist()
        return True, "Registration successful"
    
    def login(self, email, password):
        """Login user and return JWT token"""
        if email not in self.users:
            return False, "User not found", None
        
        user = self.users[email]
        if user['password_hash'] != self.hash_password(password):
            return False, "Invalid password", None
        
        # Generate JWT token
        payload = {
            'user_id': user['user_id'],
            'email': email,
            'username': user['username'],
            'elo': user['elo'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return True, "Login successful", token
    
    def get_user(self, email):
        """Get user by email"""
        return self.users.get(email)
    
    def update_user(self, email, **kwargs):
        """Update user data"""
        if email not in self.users:
            return False
        
        self.users[email].update(kwargs)
        self.save_to_gist()
        return True
    
    def get_leaderboard(self, limit=10):
        """Get top players by ELO"""
        sorted_users = sorted(
            self.users.values(),
            key=lambda x: x['elo'],
            reverse=True
        )
        return [
            {
                'username': user['username'],
                'elo': user['elo'],
                'wins': user['wins'],
                'losses': user['losses']
            }
            for user in sorted_users[:limit]
        ]


# Global auth manager instance
auth_manager = AuthManager()


def token_required(f):
    """Decorator to verify JWT token"""
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

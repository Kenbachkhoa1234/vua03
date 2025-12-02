import json
import os
import hashlib
import uuid
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# ===== AUTHENTICATION MODULE WITH IN-MEMORY DATABASE =====
# Sử dụng in-memory database vì Vercel không cho phép ghi file

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-chess-game-2024')
TOKEN_EXPIRATION = 24 * 60 * 60  # 24 hours

# In-memory database
USERS_DB = {}

class AuthManager:
    def __init__(self):
        self.users = USERS_DB
        self.load_demo_users()
    
    def load_demo_users(self):
        """Load demo users cho testing"""
        if not self.users:
            self.register('demo', 'demo@example.com', 'demo123', 1200)
            self.register('admin', 'admin@example.com', 'admin123', 1500)
    
    def hash_password(self, password):
        """Hash mật khẩu với SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, user_id, username):
        """Tạo JWT token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    
    def verify_token(self, token):
        """Xác thực JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register(self, username, email, password, elo=1000):
        """Đăng ký user mới"""
        # Kiểm tra user đã tồn tại
        if email in self.users:
            return {'success': False, 'message': 'Email đã được sử dụng'}
        
        # Kiểm tra username đã tồn tại
        for user in self.users.values():
            if user.get('username') == username:
                return {'success': False, 'message': 'Tên người dùng đã tồn tại'}
        
        # Kiểm tra độ dài password
        if len(password) < 6:
            return {'success': False, 'message': 'Mật khẩu phải có ít nhất 6 ký tự'}
        
        # Tạo user mới
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(password)
        
        self.users[email] = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'password': hashed_password,
            'elo': elo,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        return {
            'success': True,
            'message': 'Tạo tài khoản thành công',
            'user_id': user_id
        }
    
    def login(self, email, password):
        """Đăng nhập"""
        # Kiểm tra email tồn tại
        if email not in self.users:
            return {'success': False, 'message': 'Email hoặc mật khẩu không đúng'}
        
        user = self.users[email]
        hashed_password = self.hash_password(password)
        
        # Kiểm tra mật khẩu
        if user['password'] != hashed_password:
            return {'success': False, 'message': 'Email hoặc mật khẩu không đúng'}
        
        # Tạo token
        token = self.generate_token(user['user_id'], user['username'])
        
        # Cập nhật last_login
        user['last_login'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'message': 'Đăng nhập thành công',
            'token': token,
            'user_id': user['user_id'],
            'username': user['username'],
            'elo': user['elo']
        }
    
    def get_user(self, user_id):
        """Lấy thông tin user theo user_id"""
        for user in self.users.values():
            if user.get('user_id') == user_id:
                # Không trả về password
                user_data = user.copy()
                del user_data['password']
                return user_data
        return None
    
    def update_user(self, user_id, **kwargs):
        """Cập nhật thông tin user"""
        for user in self.users.values():
            if user.get('user_id') == user_id:
                for key, value in kwargs.items():
                    if key != 'password' and key != 'user_id':
                        user[key] = value
                return True
        return False
    
    def get_leaderboard(self, limit=100):
        """Lấy bảng xếp hạng"""
        users_list = []
        for user in self.users.values():
            users_list.append({
                'username': user['username'],
                'elo': user['elo'],
                'wins': user['wins'],
                'losses': user['losses'],
                'draws': user['draws']
            })
        
        # Sắp xếp theo ELO giảm dần
        users_list.sort(key=lambda x: x['elo'], reverse=True)
        return users_list[:limit]

# Initialize auth manager
auth_manager = AuthManager()

# ===== DECORATORS =====

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Lấy token từ header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Token không hợp lệ'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token bị thiếu'}), 401
        
        # Xác thực token
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Token không hợp lệ hoặc đã hết hạn'}), 401
        
        # Truyền user_id vào function
        request.user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated

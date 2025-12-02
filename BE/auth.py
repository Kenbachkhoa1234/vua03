import os
import hashlib
import uuid
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Try to import Supabase, fallback to demo mode if not available
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    print("Warning: supabase package not installed. Using demo mode.")

# ===== SUPABASE AUTHENTICATION MODULE =====

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-chess-game-2024')
TOKEN_EXPIRATION = 24 * 60 * 60  # 24 hours

# Initialize Supabase client
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

supabase = None
if HAS_SUPABASE and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Connected to Supabase")
    except Exception as e:
        print(f"Warning: Supabase connection failed: {e}")

# Fallback demo database
DEMO_USERS = {}

class AuthManager:
    def __init__(self):
        self.supabase = supabase
        self.use_db = supabase is not None
        if not self.use_db:
            self.load_demo_users()
    
    def load_demo_users(self):
        """Load demo users cho testing (khi không có Supabase)"""
        if not DEMO_USERS:
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
        try:
            if self.use_db:
                # Use Supabase
                # Kiểm tra email đã tồn tại
                response = self.supabase.table('users').select('id').eq('email', email).execute()
                if response.data and len(response.data) > 0:
                    return {'success': False, 'message': 'Email đã được sử dụng'}
                
                # Kiểm tra username đã tồn tại
                response = self.supabase.table('users').select('id').eq('username', username).execute()
                if response.data and len(response.data) > 0:
                    return {'success': False, 'message': 'Tên người dùng đã tồn tại'}
                
                # Kiểm tra độ dài password
                if len(password) < 6:
                    return {'success': False, 'message': 'Mật khẩu phải có ít nhất 6 ký tự'}
                
                # Tạo user mới
                user_id = str(uuid.uuid4())
                hashed_password = self.hash_password(password)
                
                new_user = {
                    'id': user_id,
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
                
                response = self.supabase.table('users').insert(new_user).execute()
                
                if response.data:
                    return {
                        'success': True,
                        'message': 'Tạo tài khoản thành công',
                        'user_id': user_id
                    }
                else:
                    return {'success': False, 'message': 'Lỗi tạo tài khoản'}
            else:
                # Use demo mode
                if email in DEMO_USERS:
                    return {'success': False, 'message': 'Email đã được sử dụng'}
                
                for user in DEMO_USERS.values():
                    if user.get('username') == username:
                        return {'success': False, 'message': 'Tên người dùng đã tồn tại'}
                
                if len(password) < 6:
                    return {'success': False, 'message': 'Mật khẩu phải có ít nhất 6 ký tự'}
                
                user_id = str(uuid.uuid4())
                hashed_password = self.hash_password(password)
                
                DEMO_USERS[email] = {
                    'id': user_id,
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
        except Exception as e:
            print(f"Register error: {e}")
            return {'success': False, 'message': f'Lỗi: {str(e)}'}
    
    def login(self, email, password):
        """Đăng nhập"""
        try:
            if self.use_db:
                # Use Supabase
                response = self.supabase.table('users').select('*').eq('email', email).execute()
                
                if not response.data or len(response.data) == 0:
                    return {'success': False, 'message': 'Email hoặc mật khẩu không đúng'}
                
                user = response.data[0]
                hashed_password = self.hash_password(password)
                
                if user['password'] != hashed_password:
                    return {'success': False, 'message': 'Email hoặc mật khẩu không đúng'}
                
                token = self.generate_token(user['id'], user['username'])
                
                # Cập nhật last_login
                self.supabase.table('users').update({'last_login': datetime.now().isoformat()}).eq('id', user['id']).execute()
                
                return {
                    'success': True,
                    'message': 'Đăng nhập thành công',
                    'token': token,
                    'user_id': user['id'],
                    'username': user['username'],
                    'elo': user['elo']
                }
            else:
                # Use demo mode
                if email not in DEMO_USERS:
                    return {'success': False, 'message': 'Email hoặc mật khẩu không đúng'}
                
                user = DEMO_USERS[email]
                hashed_password = self.hash_password(password)
                
                if user['password'] != hashed_password:
                    return {'success': False, 'message': 'Email hoặc mật khẩu không đúng'}
                
                token = self.generate_token(user['id'], user['username'])
                user['last_login'] = datetime.now().isoformat()
                
                return {
                    'success': True,
                    'message': 'Đăng nhập thành công',
                    'token': token,
                    'user_id': user['id'],
                    'username': user['username'],
                    'elo': user['elo']
                }
        except Exception as e:
            print(f"Login error: {e}")
            return {'success': False, 'message': f'Lỗi: {str(e)}'}
    
    def get_user(self, user_id):
        """Lấy thông tin user theo user_id"""
        try:
            if self.use_db:
                response = self.supabase.table('users').select('*').eq('id', user_id).execute()
                
                if response.data and len(response.data) > 0:
                    user_data = response.data[0].copy()
                    if 'password' in user_data:
                        del user_data['password']
                    return user_data
                return None
            else:
                for user in DEMO_USERS.values():
                    if user.get('id') == user_id:
                        user_data = user.copy()
                        del user_data['password']
                        return user_data
                return None
        except Exception as e:
            print(f"Get user error: {e}")
            return None
    
    def update_user(self, user_id, **kwargs):
        """Cập nhật thông tin user"""
        try:
            if self.use_db:
                update_data = {k: v for k, v in kwargs.items() if k not in ['password', 'id']}
                response = self.supabase.table('users').update(update_data).eq('id', user_id).execute()
                return bool(response.data)
            else:
                for user in DEMO_USERS.values():
                    if user.get('id') == user_id:
                        for key, value in kwargs.items():
                            if key not in ['password', 'id']:
                                user[key] = value
                        return True
                return False
        except Exception as e:
            print(f"Update user error: {e}")
            return False
    
    def get_leaderboard(self, limit=100):
        """Lấy bảng xếp hạng"""
        try:
            if self.use_db:
                response = self.supabase.table('users').select('username,elo,wins,losses,draws').order('elo', desc=True).limit(limit).execute()
                return response.data if response.data else []
            else:
                users_list = []
                for user in DEMO_USERS.values():
                    users_list.append({
                        'username': user['username'],
                        'elo': user['elo'],
                        'wins': user['wins'],
                        'losses': user['losses'],
                        'draws': user['draws']
                    })
                users_list.sort(key=lambda x: x['elo'], reverse=True)
                return users_list[:limit]
        except Exception as e:
            print(f"Get leaderboard error: {e}")
            return []

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

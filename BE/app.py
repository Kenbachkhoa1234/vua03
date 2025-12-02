# backend/app.py

from flask import Flask, render_template, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
import json
import random
import string
import uuid
import os
import sys

# Fix imports - add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from chess_engine import ChessEngine
from auth import auth_manager, token_required

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), '../FE'),
            static_url_path='',
            template_folder=os.path.join(os.path.dirname(__file__), '../FE'))

# Enable CORS for authentication
CORS(app)

# --- Quản lý trạng thái Game ---
games = {} # {game_id: ChessEngine object}

def generate_room_code():
    """Tạo mã phòng ngẫu nhiên 6 chữ số (1-9)."""
    return ''.join(random.choices(string.digits.replace('0', ''), k=6))

@app.route('/')
def index():
    """Phục vụ trang HTML chính."""
    return render_template('TrangChu.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/register.html')
def register_page():
    return render_template('register.html')

@app.route('/BanCo.html')
def game_page():
    return render_template('BanCo.html')

# ===== API AUTHENTICATION =====

@app.route('/api/register', methods=['POST'])
def register():
    """Đăng ký tài khoản mới"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        elo = data.get('elo', 1000)
        
        # Validation
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'Vui lòng điền đầy đủ thông tin'}), 400
        
        # Gọi auth manager
        result = auth_manager.register(username, email, password, elo)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Đăng nhập"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email hoặc mật khẩu không được để trống'}), 400
        
        result = auth_manager.login(email, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/api/validate-token', methods=['GET'])
@token_required
def validate_token():
    """Xác thực token"""
    try:
        user = auth_manager.get_user(request.user_id)
        if user:
            return jsonify({'success': True, 'user': user}), 200
        else:
            return jsonify({'success': False, 'message': 'User không tồn tại'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile():
    """Lấy thông tin profile"""
    try:
        user = auth_manager.get_user(request.user_id)
        if user:
            return jsonify({'success': True, 'user': user}), 200
        else:
            return jsonify({'success': False, 'message': 'User không tồn tại'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Lấy bảng xếp hạng"""
    try:
        limit = request.args.get('limit', 100, type=int)
        leaderboard = auth_manager.get_leaderboard(limit)
        return jsonify({'success': True, 'leaderboard': leaderboard}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

# ===== API cho Game AI =====

@app.route('/api/start_ai', methods=['POST'])
def start_ai_game():
    data = request.json
    level = data.get('level', 'Thành Thạo')
    game_id = str(uuid.uuid4())
    
    engine = ChessEngine()
    games[game_id] = {'engine': engine, 'level': level, 'mode': 'AI'}
    
    return jsonify({
        'game_id': game_id,
        'status': engine.get_status()
    })

@app.route('/api/ai_move/<game_id>', methods=['POST'])
def ai_move(game_id):
    game_data = games.get(game_id)
    if not game_data or game_data['mode'] != 'AI':
        return jsonify({'error': 'Game not found or not AI mode'}), 404
    
    engine = game_data['engine']
    
    # Lấy nước đi của người chơi
    player_uci = request.json.get('uci')
    engine.make_move(player_uci)
    
    # Kiểm tra kết thúc game sau nước đi người chơi
    if engine.is_game_over():
        return jsonify(engine.get_status())
    
    # Lấy nước đi của AI
    ai_uci = engine.get_ai_move(game_data['level'])
    if ai_uci:
        engine.make_move(ai_uci)
        
    return jsonify(engine.get_status())

@app.route('/api/ai_controls/<game_id>', methods=['POST'])
def ai_controls(game_id):
    game_data = games.get(game_id)
    if not game_data:
        return jsonify({'error': 'Game not found'}), 404
        
    engine = game_data['engine']
    action = request.json.get('action')
    
    if action == 'undo':
        engine.undo_move()
        # Quay lại 2 lần (nước đi của AI và người chơi)
        if engine.undo_move(): 
            return jsonify(engine.get_status())
        else:
            return jsonify({'status': 'Board is empty'})
            
    elif action == 'hint':
        hint = engine.get_hint_move()
        return jsonify({'hint': hint})
        
    elif action == 'restart':
        engine.reset_board()
        return jsonify(engine.get_status())

    return jsonify({'error': 'Invalid action'}), 400

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Chess Game API is running'}), 200

# Error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
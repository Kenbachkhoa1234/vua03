import uuid
import random
import string
from datetime import datetime
from chess_engine import ChessEngine

# ===== MULTIPLAYER GAME MANAGER =====

class GameRoom:
    """Phòng chơi chess"""
    def __init__(self, room_id, mode='friends', creator_id=None):
        self.room_id = room_id
        self.mode = mode  # 'friends' hoặc 'random'
        self.creator_id = creator_id
        self.players = {}  # {user_id: {'username': '', 'color': 'white'/'black'}}
        self.engine = ChessEngine()
        self.status = 'waiting'  # 'waiting', 'playing', 'finished'
        self.created_at = datetime.now()
        self.current_turn = 'white'
        self.winner = None
        self.move_history = []
    
    def add_player(self, user_id, username):
        """Thêm người chơi vào phòng"""
        if len(self.players) >= 2:
            return False, 'Phòng đã đầy'
        
        # Gán màu cờ
        if len(self.players) == 0:
            color = 'white'
        else:
            color = 'black'
        
        self.players[user_id] = {
            'username': username,
            'color': color,
            'user_id': user_id,
            'connected': True
        }
        
        # Nếu đủ 2 người, bắt đầu game
        if len(self.players) == 2:
            self.status = 'playing'
            return True, 'Game bắt đầu'
        
        return True, 'Tham gia phòng thành công'
    
    def remove_player(self, user_id):
        """Xóa người chơi"""
        if user_id in self.players:
            del self.players[user_id]
            if len(self.players) == 0:
                return 'empty'
            return 'removed'
        return 'not_found'
    
    def make_move(self, user_id, move):
        """Thực hiện nước đi"""
        if self.status != 'playing':
            return False, 'Game chưa bắt đầu hoặc đã kết thúc'
        
        # Kiểm tra có phải lượt của người chơi
        player = self.players.get(user_id)
        if not player or player['color'] != self.current_turn:
            return False, 'Không phải lượt của bạn'
        
        # Thực hiện nước đi
        success, message = self.engine.make_move(move)
        if not success:
            return False, message
        
        self.move_history.append({
            'move': move,
            'player': user_id,
            'username': player['username'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Đổi lượt
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        # Kiểm tra kết thúc game
        status = self.engine.get_status()
        if status['game_over']:
            self.status = 'finished'
            if status['winner']:
                # Tìm user có color == winner
                for uid, p in self.players.items():
                    if p['color'] == status['winner']:
                        self.winner = uid
                        break
        
        return True, 'Nước đi thành công'
    
    def get_info(self):
        """Lấy thông tin phòng"""
        return {
            'room_id': self.room_id,
            'mode': self.mode,
            'status': self.status,
            'players': list(self.players.values()),
            'current_turn': self.current_turn,
            'board': self.engine.get_board(),
            'game_over': self.engine.get_status()['game_over'],
            'winner': self.winner,
            'move_history': self.move_history
        }

class MultiplayerManager:
    """Quản lý tất cả các phòng game"""
    def __init__(self):
        self.rooms = {}  # {room_id: GameRoom}
        self.waiting_players = []  # Queue chờ random match
        self.user_rooms = {}  # {user_id: room_id}
    
    def create_room(self, creator_id, username, mode='friends'):
        """Tạo phòng mới"""
        if mode == 'friends':
            room_id = self.generate_room_id()
        else:
            room_id = str(uuid.uuid4())
        
        room = GameRoom(room_id, mode, creator_id)
        room.add_player(creator_id, username)
        
        self.rooms[room_id] = room
        self.user_rooms[creator_id] = room_id
        
        return room_id, room.get_info()
    
    def join_room(self, room_id, user_id, username):
        """Tham gia phòng"""
        if room_id not in self.rooms:
            return False, 'Phòng không tồn tại'
        
        room = self.rooms[room_id]
        if room.status != 'waiting':
            return False, 'Phòng đã bắt đầu hoặc kết thúc'
        
        success, message = room.add_player(user_id, username)
        if success:
            self.user_rooms[user_id] = room_id
        
        return success, message, room.get_info()
    
    def find_random_match(self, user_id, username):
        """Tìm đối thủ random"""
        # Nếu có người chờ, match ngay
        if self.waiting_players:
            opponent_id, opponent_name = self.waiting_players.pop(0)
            
            room_id = str(uuid.uuid4())
            room = GameRoom(room_id, 'random', None)
            room.add_player(opponent_id, opponent_name)
            room.add_player(user_id, username)
            
            self.rooms[room_id] = room
            self.user_rooms[opponent_id] = room_id
            self.user_rooms[user_id] = room_id
            
            return True, room_id, room.get_info()
        else:
            # Thêm vào queue chờ
            self.waiting_players.append((user_id, username))
            return False, None, {'status': 'waiting_for_opponent'}
    
    def make_move(self, user_id, move):
        """Thực hiện nước đi"""
        room_id = self.user_rooms.get(user_id)
        if not room_id or room_id not in self.rooms:
            return False, 'Không tìm thấy phòng game'
        
        room = self.rooms[room_id]
        success, message = room.make_move(user_id, move)
        
        if success and room.status == 'finished':
            self.cleanup_room(room_id)
        
        return success, message, room.get_info()
    
    def get_room(self, room_id):
        """Lấy thông tin phòng"""
        if room_id not in self.rooms:
            return None
        return self.rooms[room_id].get_info()
    
    def leave_room(self, user_id):
        """Rời phòng"""
        room_id = self.user_rooms.get(user_id)
        if not room_id or room_id not in self.rooms:
            return False
        
        room = self.rooms[room_id]
        result = room.remove_player(user_id)
        
        if result == 'empty':
            self.cleanup_room(room_id)
        
        del self.user_rooms[user_id]
        return True
    
    def cleanup_room(self, room_id):
        """Xóa phòng"""
        if room_id in self.rooms:
            room = self.rooms[room_id]
            for user_id in list(room.players.keys()):
                if user_id in self.user_rooms:
                    del self.user_rooms[user_id]
            del self.rooms[room_id]
    
    def generate_room_id(self, length=6):
        """Tạo mã phòng 6 chữ số"""
        return ''.join(random.choices(string.digits.replace('0', ''), k=length))
    
    def cancel_matchmaking(self, user_id):
        """Hủy tìm đối thủ random"""
        self.waiting_players = [(uid, name) for uid, name in self.waiting_players if uid != user_id]
        return True

# Initialize manager
multiplayer_manager = MultiplayerManager()

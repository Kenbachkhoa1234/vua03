// Frontend Multiplayer Module
class MultiplayerGame {
    constructor() {
        this.currentRoom = null;
        this.currentUser = null;
        this.apiBase = '/api/multiplayer';
    }

    async createRoom(mode = 'friends') {
        try {
            const response = await fetch(`${this.apiBase}/create-room`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ mode })
            });

            const data = await response.json();
            if (data.success) {
                this.currentRoom = data.room;
                return { success: true, roomId: data.room_id, room: data.room };
            }
            return { success: false, message: data.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async joinRoom(roomId) {
        try {
            const response = await fetch(`${this.apiBase}/join-room`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ room_id: roomId })
            });

            const data = await response.json();
            if (data.success) {
                this.currentRoom = data.room;
                return { success: true, room: data.room };
            }
            return { success: false, message: data.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async findRandom() {
        try {
            const response = await fetch(`${this.apiBase}/find-random`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            const data = await response.json();
            if (data.success) {
                if (data.matched) {
                    this.currentRoom = data.room;
                    return { success: true, matched: true, roomId: data.room_id, room: data.room };
                }
                return { success: true, matched: false, message: 'Đang tìm đối thủ...' };
            }
            return { success: false, message: data.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async cancelMatchmaking() {
        try {
            const response = await fetch(`${this.apiBase}/cancel-matchmaking`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            const data = await response.json();
            return { success: data.success, message: data.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async getRoom(roomId) {
        try {
            const response = await fetch(`${this.apiBase}/get-room/${roomId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            const data = await response.json();
            if (data.success) {
                this.currentRoom = data.room;
                return { success: true, room: data.room };
            }
            return { success: false, message: data.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async makeMove(move) {
        try {
            const response = await fetch(`${this.apiBase}/make-move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ move })
            });

            const data = await response.json();
            if (data.success) {
                this.currentRoom = data.room;
                return { success: true, room: data.room };
            }
            return { success: false, message: data.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async leaveRoom() {
        try {
            const response = await fetch(`${this.apiBase}/leave-room`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            const data = await response.json();
            this.currentRoom = null;
            return { success: data.success, message: data.message };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }
}

// Initialize
const multiplayerGame = new MultiplayerGame();

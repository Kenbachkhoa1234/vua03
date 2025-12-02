# 🎯 Hướng Dẫn Thiết Lập Nhanh - Chess Game Authentication

## ✅ Các File Đã Được Tạo

### Frontend (FE/)
- ✨ `login.html` - Form đăng nhập
- ✨ `register.html` - Form đăng ký
- ✨ `auth.css` - Styling cho authentication
- ✨ `auth.js` - JavaScript xử lý auth logic
- 🔄 `TrangChu.html` - Cập nhật thêm nút đăng ký/đăng nhập và bảng xếp hạng

### Backend (BE/)
- 🔐 `auth.py` - Xử lý authentication (hashing, JWT, database)
- 👥 `users.json` - Database người dùng (tự động tạo khi chạy)
- 🔄 `app.py` - Thêm API endpoints
- 📦 `requirements.txt` - Cập nhật dependencies

---

## 🚀 Bắt Đầu Nhanh

### 1. Cài Đặt Dependencies

```bash
cd "python-chess-main"
pip install -r requirements.txt
```

Nếu gặp lỗi với `PyJWT`, cài riêng:
```bash
pip install PyJWT
pip install flask-cors
```

### 2. Chạy Backend

```bash
cd BE
python app.py
```

Bạn sẽ thấy:
```
 * Running on http://127.0.0.1:5000
```

### 3. Truy Cập Ứng Dụng

Mở trình duyệt và truy cập:
- **Trang Chủ**: http://localhost:5000/
- **Đăng Ký**: http://localhost:5000/register.html
- **Đăng Nhập**: http://localhost:5000/login.html

---

## 📝 Tính Năng Chính

### 🔑 Đăng Nhập
```
Email: test@example.com
Mật khẩu: password123
```

### 📝 Đăng Ký
```
Tên: player1
Email: player1@example.com
Mật khẩu: pass123
ELO: 1000 (mặc định)
```

### 🏆 Bảng Xếp Hạng
- Hiển thị 50 người chơi top
- Sắp xếp theo ELO giảm dần
- Hiển thị Win/Loss/Draw stats

---

## 🔍 Kiểm Tra Database

```bash
# Xem nội dung users.json
cat BE/users.json

# Hoặc dùng editor yêu thích
# Sẽ hiển thị dạng:
{
  "test@example.com": {
    "user_id": "uuid...",
    "username": "player1",
    "email": "test@example.com",
    "password": "hashed_password",
    "elo": 1000,
    "wins": 0,
    "losses": 0,
    "draws": 0,
    "created_at": "2024-12-03T...",
    "last_login": "2024-12-03T..."
  }
}
```

---

## 🧪 Testing API

### Dùng cURL hoặc Postman

#### Đăng Ký
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "elo": 1000
  }'
```

#### Đăng Nhập
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Lấy Profile (cần token)
```bash
curl -X GET http://localhost:5000/api/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Bảng Xếp Hạng
```bash
curl -X GET "http://localhost:5000/api/leaderboard?limit=10"
```

---

## 🎨 Tuỳ Chỉnh

### Đổi Màu Chính

Sửa trong `auth.css`:
```css
:root {
  --primary-color: #667eea;  /* Đổi màu chính ở đây */
  --success-color: #11998e;  /* Màu thành công */
}
```

### Đổi Thời Gian Hết Hạn Token

Sửa trong `BE/auth.py`:
```python
TOKEN_EXPIRATION = 24 * 60 * 60  # Thay 24 với số giờ mong muốn
```

### Đổi Secret Key (IMPORTANT)

Sửa trong `BE/auth.py`:
```python
SECRET_KEY = 'your-secret-key-change-this-in-production'
# Thay bằng key mạnh (ví dụ: os.urandom(32).hex())
```

---

## ⚙️ Cấu Hình Production

### 1. Đổi DEBUG Mode
```python
# app.py - dòng cuối
app.run(debug=False, host='0.0.0.0', port=5000)
```

### 2. Sử dụng HTTPS
```python
# Cài pip install pyopenssl
app.run(ssl_context='adhoc')
```

### 3. Sử dụng Database Thực (Recommended)
Thay thế `users.json` bằng:
- SQLite: `sqlite3`
- PostgreSQL: `psycopg2`
- MongoDB: `pymongo`

---

## 🐛 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'flask'"
```bash
pip install Flask==2.3.0
```

### ❌ "ModuleNotFoundError: No module named 'jwt'"
```bash
pip install PyJWT
```

### ❌ "Address already in use"
```bash
# Tìm process dùng port 5000
lsof -i :5000

# Hoặc chạy trên port khác
python app.py  # sửa port trong app.py
```

### ❌ "Login thất bại nhưng tư rằng đúng"
```bash
# Xóa users.json và tạo lại
rm BE/users.json
# Đăng ký tài khoản mới
```

### ❌ "CORS Error"
```python
# Đã thêm trong app.py:
from flask_cors import CORS
CORS(app)
```

---

## 📊 Cấu Trúc Project

```
Chess_game/
├── FE/
│   ├── login.html           ✨ NEW
│   ├── register.html        ✨ NEW
│   ├── auth.css             ✨ NEW
│   ├── auth.js              ✨ NEW
│   ├── TrangChu.html        🔄 UPDATED
│   ├── TrangChu.css
│   ├── BanCo.html
│   ├── script.js
│   └── style.css
│
├── BE/
│   ├── auth.py              ✨ NEW
│   ├── users.json           ✨ NEW
│   ├── app.py               🔄 UPDATED
│   ├── chess_engine.py
│   └── requirements.txt      🔄 UPDATED
│
├── README_AUTH.md           ✨ NEW
└── SETUP.md                 ✨ NEW
```

---

## 🎯 Next Steps

1. ✅ Chạy backend: `python BE/app.py`
2. ✅ Truy cập: http://localhost:5000
3. ✅ Đăng ký tài khoản
4. ✅ Đăng nhập
5. ✅ Chơi cờ vua!

---

## 💡 Mẹo Hữu Ích

- **Lưu Email**: Tích "Nhớ mật khẩu" để lưu email (localStorage)
- **Token Validation**: Token tự động kiểm tra khi load trang
- **Bảng Xếp Hạng**: Bấm nút 🏆 ở trang chủ
- **Debug Console**: F12 > Console để xem logs

---

## 📞 Cần Giúp?

1. Kiểm tra terminal backend (xem lỗi Python)
2. Mở F12 > Console (xem lỗi JavaScript)
3. Xem file `users.json` (kiểm tra dữ liệu)

---

**Chúc mừng! 🎉 Bạn đã sẵn sàng chơi cờ vua với authentication!**

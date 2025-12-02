# 🎮 Hướng Dẫn Sử Dụng Tính Năng Đăng Ký & Đăng Nhập

## 📋 Tổng Quan

Dự án Chess Game đã được thêm hệ thống đăng ký và đăng nhập hoàn chỉnh cho phép người dùng:
- ✅ Tạo tài khoản mới
- ✅ Đăng nhập an toàn với mã hóa
- ✅ Quản lý thông tin cá nhân
- ✅ Theo dõi thống kê (ELO, Wins, Losses, Draws)
- ✅ Xem bảng xếp hạng

---

## 📁 Cấu Trúc File Mới

```
Chess_game/
├── FE/
│   ├── login.html          # 🔑 Form đăng nhập
│   ├── register.html       # 📝 Form đăng ký
│   ├── auth.css            # 💅 Styling cho auth
│   ├── auth.js             # ⚙️ Logic authentication
│   └── TrangChu.html       # 🏠 Trang chủ (cập nhật link đăng ký/đăng nhập)
├── BE/
│   ├── app.py              # ✨ Flask app (thêm API endpoints)
│   ├── auth.py             # 🔐 Authentication logic
│   ├── users.json          # 📊 Database người dùng
│   ├── chess_engine.py
│   └── requirements.txt     # 📦 Dependencies
└── README_AUTH.md
```

---

## 🚀 Cài Đặt & Chạy

### 1️⃣ Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Chạy Backend

```bash
cd BE
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

### 3️⃣ Truy Cập Ứng Dụng

- **Trang Chủ**: http://localhost:5000/
- **Đăng Ký**: http://localhost:5000/register.html
- **Đăng Nhập**: http://localhost:5000/login.html

---

## 📝 Hướng Dẫn Sử Dụng

### 📌 Đăng Ký Tài Khoản

1. Nhấp vào link **"Đăng ký tại đây"** trên trang đăng nhập
2. Hoặc trực tiếp truy cập: `http://localhost:5000/register.html`
3. Điền thông tin:
   - **Tên người dùng**: 3-20 ký tự
   - **Email**: Email hợp lệ
   - **Mật khẩu**: Ít nhất 6 ký tự
   - **Xác nhận mật khẩu**: Phải khớp
   - **ELO**: Rating ban đầu (mặc định 1000)
4. Chọn "Tôi đồng ý với Điều khoản dịch vụ"
5. Nhấp "✨ Tạo Tài Khoản"

### 🔑 Đăng Nhập

1. Truy cập: `http://localhost:5000/login.html`
2. Điền:
   - **Email**: Email đã đăng ký
   - **Mật khẩu**: Mật khẩu đã đặt
3. Tùy chọn: Chọn "Nhớ mật khẩu" để lưu email
4. Nhấp "🚀 Đăng Nhập"
5. Nếu thành công, sẽ chuyển hướng về trang chủ

### 🎮 Chơi Cờ Vua

Sau khi đăng nhập, người dùng có thể:
- Đánh với máy (AI)
- Đánh với người chơi khác
- Xem bảng xếp hạng

---

## 🔒 Bảo Mật

### Mã Hóa Mật Khẩu
- Sử dụng **SHA-256** để hash mật khẩu
- Mật khẩu **không bao giờ** được lưu dưới dạng plain text

### Token Authentication
- Sử dụng **JWT (JSON Web Tokens)**
- Token hết hạn sau **24 giờ**
- Token được lưu trong `localStorage` của trình duyệt

### Kết Nối HTTPS (Production)
```python
# Trong file app.py (production)
app.run(debug=False, host='0.0.0.0', port=5000, ssl_context='adhoc')
```

---

## 📊 Database (users.json)

Cấu trúc dữ liệu:
```json
{
  "user@example.com": {
    "user_id": "uuid-string",
    "username": "user_name",
    "email": "user@example.com",
    "password": "hashed_password",
    "elo": 1000,
    "wins": 5,
    "losses": 3,
    "draws": 1,
    "created_at": "2024-12-03T10:30:00",
    "last_login": "2024-12-03T15:45:00"
  }
}
```

---

## 🌐 API Endpoints

### 📝 Đăng Ký
```
POST /api/register
Content-Type: application/json

{
  "username": "player_name",
  "email": "email@example.com",
  "password": "password123",
  "elo": 1000
}

Response (201):
{
  "success": true,
  "message": "Tạo tài khoản thành công",
  "user_id": "uuid"
}
```

### 🔑 Đăng Nhập
```
POST /api/login
Content-Type: application/json

{
  "email": "email@example.com",
  "password": "password123"
}

Response (200):
{
  "success": true,
  "message": "Đăng nhập thành công",
  "token": "jwt_token",
  "user_id": "uuid",
  "username": "player_name",
  "elo": 1000
}
```

### ✅ Xác Thực Token
```
GET /api/validate-token
Authorization: Bearer jwt_token

Response (200):
{
  "success": true,
  "user": { user_data }
}
```

### 👤 Lấy Profile
```
GET /api/profile
Authorization: Bearer jwt_token

Response (200):
{
  "success": true,
  "user": { user_data }
}
```

### 🏆 Bảng Xếp Hạng
```
GET /api/leaderboard?limit=100

Response (200):
{
  "success": true,
  "leaderboard": [
    {
      "username": "player1",
      "elo": 1500,
      "wins": 10,
      "losses": 5,
      "draws": 2
    },
    ...
  ]
}
```

---

## 🎨 Giao Diện

### Màu Sắc Chính
- 🟣 **Primary**: `#667eea` (Tím)
- 🟢 **Success**: `#11998e` (Xanh lá)
- 🟠 **Warning**: `#f093fb` (Hồng)
- 🔴 **Error**: `#e74c3c` (Đỏ)

### Kiểu Form
- ✨ Input fields có hover effect
- 💬 Error messages hiển thị động
- ⚡ Password strength indicator
- 🎯 Form validation real-time

---

## 🐛 Xử Lý Lỗi Thường Gặp

### ❌ "Email đã được sử dụng"
- Sử dụng email khác hoặc đăng nhập nếu đã có tài khoản

### ❌ "Mật khẩu không đúng"
- Kiểm tra lại mật khẩu (chữ hoa/thường)
- Sử dụng tính năng "Quên mật khẩu" (cần triển khai thêm)

### ❌ "Lỗi kết nối"
- Kiểm tra backend có chạy: `python app.py`
- Kiểm tra port 5000 có sẵn sàng

### ❌ "Token không hợp lệ"
- Đăng xuất và đăng nhập lại
- Clear localStorage: `localStorage.clear()`

---

## 📈 Tính Năng Nâng Cao (TODO)

- [ ] Quên mật khẩu (Email reset)
- [ ] Xác thực email
- [ ] Upload ảnh đại diện
- [ ] Thay đổi mật khẩu
- [ ] Xóa tài khoản
- [ ] 2FA (Two-Factor Authentication)
- [ ] Social login (Google, Facebook)

---

## 💡 Tips & Tricks

### Debug Mode
```python
# Trong app.py
app.run(debug=True)  # Tự reload khi có thay đổi
```

### Xem Database
```bash
# Mở file users.json với text editor
cat BE/users.json
```

### Reset Database
```bash
# Xóa file users.json
rm BE/users.json
```

---

## 📞 Liên Hệ & Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra console browser (F12 - Console tab)
2. Kiểm tra terminal backend (xem error logs)
3. Đảm bảo tất cả dependencies đã cài đặt

---

## 📄 License

Dự án được phát hành dưới giấy phép MIT.

**Made with ❤️ for Chess Lovers**

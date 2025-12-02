# Setup Supabase Database

## Bước 1: Tạo Supabase Account
1. Vào https://supabase.com
2. Click "Sign Up"
3. Đăng ký bằng GitHub hoặc email

## Bước 2: Tạo Project
1. Click "New project"
2. Nhập tên project (ví dụ: chess-game)
3. Tạo password database
4. Chọn region gần nhất (ví dụ: Asia - Singapore)
5. Click "Create new project"

## Bước 3: Lấy Credentials
1. Vào **Settings → API**
2. Copy **Project URL** → lưu làm `SUPABASE_URL`
3. Copy **anon public key** → lưu làm `SUPABASE_KEY`

## Bước 4: Tạo Users Table
1. Vào **SQL Editor**
2. Click **New Query**
3. Copy-paste nội dung từ `SUPABASE_SETUP.sql`
4. Click **Run**

## Bước 5: Setup Environment Variables

### Local Development
Tạo file `.env` trong thư mục project:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

### Vercel Deployment
1. Vào Project Settings → Environment Variables
2. Thêm 2 variables:
   - `SUPABASE_URL` = Project URL từ Supabase
   - `SUPABASE_KEY` = Anon Key từ Supabase

## Bước 6: Test
```bash
# Local
python app.py

# Hoặc test register API
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "elo": 1000
  }'
```

## Troubleshooting

### Connection Failed Error
- ✅ Check SUPABASE_URL, SUPABASE_KEY đúng chưa
- ✅ Check network connection
- ✅ Restart application

### Insert Error
- ✅ Check table schema đúng (chạy SUPABASE_SETUP.sql lại)
- ✅ Check columns name: id, username, email, password, elo, wins, losses, draws, created_at, last_login

### Demo Mode
Nếu không có Supabase, app sẽ tự động chạy mode demo (in-memory database)
- Lưu ý: Dữ liệu sẽ mất khi server restart

## Query Examples

### Get User by Email
```sql
SELECT * FROM users WHERE email = 'user@example.com';
```

### Get Leaderboard
```sql
SELECT username, elo, wins, losses, draws FROM users ORDER BY elo DESC LIMIT 100;
```

### Update User ELO
```sql
UPDATE users SET elo = elo + 50 WHERE id = 'user_id';
```

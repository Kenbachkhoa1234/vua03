// ===== AUTH.JS - Xử lý Authentication Frontend =====

// Kiểm tra xem user đã đăng nhập hay chưa
function isUserLoggedIn() {
    return localStorage.getItem('authToken') !== null;
}

// Lấy thông tin user
function getCurrentUser() {
    return {
        token: localStorage.getItem('authToken'),
        username: localStorage.getItem('userName'),
        userId: localStorage.getItem('userId')
    };
}

// Đăng xuất
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userId');
    window.location.href = 'login.html';
}

// Redirect to login nếu chưa đăng nhập (dùng cho các trang game)
function checkAuthentication() {
    if (!isUserLoggedIn()) {
        window.location.href = 'login.html';
    }
}

// Thêm token vào request header
function getAuthHeaders() {
    const user = getCurrentUser();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user.token}`
    };
}

// Kiểm tra token còn hợp lệ hay không
async function validateToken() {
    const user = getCurrentUser();
    
    if (!user.token) {
        return false;
    }

    try {
        const response = await fetch('/api/validate-token', {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (response.status === 401) {
            logout();
            return false;
        }

        return response.ok;
    } catch (error) {
        console.error('Token validation error:', error);
        return false;
    }
}

// Hiển thị thông tin user ở header (nếu có)
function displayUserInfo() {
    const user = getCurrentUser();
    const userInfoEl = document.getElementById('user-info');
    
    if (user.username && userInfoEl) {
        userInfoEl.innerHTML = `
            <span class="user-name">👤 ${user.username}</span>
            <button class="btn-logout" onclick="logout()">🚪 Đăng xuất</button>
        `;
    }
}

// Gọi khi trang load
window.addEventListener('DOMContentLoaded', () => {
    displayUserInfo();
});

// Export functions để sử dụng trong các trang khác
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isUserLoggedIn,
        getCurrentUser,
        logout,
        checkAuthentication,
        getAuthHeaders,
        validateToken,
        displayUserInfo
    };
}

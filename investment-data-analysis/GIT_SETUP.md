# 🔐 Hướng dẫn Push Code lên GitHub An Toàn

## ✅ Các bước đã hoàn tất

- ✅ Tạo `.gitignore` - bỏ qua file nhạy cảm (venv, .env, __pycache__, logs)
- ✅ Tạo `.env.example` - template cho biến môi trường
- ✅ Commit code với message rõ ràng
- ✅ Code đã sẵn sàng push

## 🔑 Push lên GitHub

### Nếu dùng HTTPS (có mật khẩu):

```bash
cd "d:\Project CODE\Python"
git push origin main
# Nhập: username = khiemtv1212
# Nhập: password = tạo Personal Access Token (PAT)
```

### 📱 Tạo Personal Access Token (Khuyến nghị):

1. Vào: https://github.com/settings/tokens
2. Nhấp "Generate new token" → "Generate new token (classic)"
3. Điền:
   - **Name**: `GitHub_Push_Token`
   - **Expiration**: 90 days (hoặc cao hơn)
   - **Scope**: ✅ repo (tất cả)
4. Nhấp "Generate token"
5. **Copy token** (chỉ hiện 1 lần!)

### 🔐 Lưu token an toàn:

```bash
# Windows - Lưu vào Credential Manager
git credential approve
# protocol=https
# host=github.com
# username=khiemtv1212
# password=<paste_token_here>
# [blank line to finish]
```

Hoặc dùng:
```bash
git config --global credential.helper wincred
```

### 🚀 Push code:

```bash
cd "d:\Project CODE\Python"
git push origin main
```

## 🛡️ Bảo mật - Điều cần kiểm tra

✅ **Trước khi push:**
```bash
git log --oneline -1        # Xem commit cuối cùng
git diff origin/main        # Xem thay đổi
```

✅ **File không được commit:**
- `.env` (biến môi trường)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `*.log` (log files)
- `models/` (trained models)
- Các file nhạy cảm khác

✅ **File được commit:**
- `.gitignore` ✅
- `.env.example` ✅ (template, không có giá trị thực)
- `*.py` (code)
- `requirements.txt` (dependencies)
- `README.md` (documentation)
- `config.json` (cấu hình công khai)

## 📊 Sau khi push thành công

```bash
# Kiểm tra commit đã có trên GitHub
git log --oneline origin/main -5

# Xem trạng thái
git status
# On branch main
# Your branch is up to date with 'origin/main'.
```

## ⚠️ Nếu gặp lỗi

### Lỗi: "Permission denied"
→ Kiểm tra token có hợp lệ không
→ Token hết hạn? Tạo token mới

### Lỗi: "fatal: bad revision 'origin/main'"
```bash
git remote -v  # Kiểm tra remote URL
git remote set-url origin https://github.com/khiemtv1212/Python.git
```

### Lỗi: Commit nhiều file lớn
```bash
# Xem kích thước file
git ls-files -s | sort -k4 -n -r | head -20
```

## 🔄 Quy trình hàng ngày

```bash
# 1. Làm việc
python analysis_engine.py

# 2. Kiểm tra thay đổi
git status
git diff

# 3. Commit
git add .
git commit -m "feat: [mô tả thay đổi]"

# 4. Push
git push origin main
```

## 📝 Conventional Commits (Chuẩn mực)

```
feat:  Tính năng mới
fix:   Sửa lỗi
docs:  Cập nhật tài liệu
style: Code style (không thay đổi logic)
refactor: Cải cấu trúc code
test:  Thêm test
perf:  Cải thiện performance
ci:    Thay đổi CI/CD
```

**Ví dụ:**
```bash
git commit -m "feat: Add price prediction for 30 days"
git commit -m "fix: Correct RSI calculation algorithm"
git commit -m "docs: Update README with usage examples"
```

---

💡 **Tips:** Giữ commit size nhỏ, 1 commit = 1 tính năng

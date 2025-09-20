# راهنمای سیستم احراز هویت (بدون کد دعوت)

## 🚀 **تغییرات اعمال شده**

### ✅ **حذف شده:**
- ❌ `POST /auth/register` - ثبت نام عمومی
- ❌ `POST /auth/register-with-invite` - ثبت نام با کد دعوت
- ❌ `POST /invite-codes/` - ایجاد کد دعوت
- ❌ `GET /invite-codes/` - مشاهده کدهای دعوت
- ❌ `DELETE /invite-codes/{code}` - حذف کد دعوت

### ✅ **اضافه شده:**
- ✅ `POST /auth/bootstrap-admin` - ایجاد اولین ادمین
- ✅ `POST /auth/admin-login` - ورود ادمین‌ها

## 🔧 **نحوه راه‌اندازی**

### **روش 1: استفاده از Script (پیشنهادی)**
```bash
# اجرای script برای ایجاد ادمین
python3 create_super_admin.py
```

### **روش 2: استفاده از Endpoint**
```bash
# ایجاد اولین ادمین
curl -X POST "http://localhost:8000/auth/bootstrap-admin" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "00001",
    "password": "admin123!",
    "full_name": "مدیر اصلی",
    "phone": "09123456789",
    "email": "admin@company.com"
  }'
```

### **روش 3: خودکار در Startup**
- ادمین پیش‌فرض به صورت خودکار در startup ایجاد می‌شود
- Employee ID: `00001`
- Password: `admin123!`

## 📋 **فرآیند مدیریت کاربران**

### **1. ورود ادمین**
```bash
curl -X POST "http://localhost:8000/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "00001",
    "password": "admin123!"
  }'
```

### **2. ایجاد کاربر توسط ادمین**
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "12345",
    "full_name": "علی احمدی",
    "role": "employee",
    "phone": "09123456789",
    "email": "ali@company.com",
    "department": "IT",
    "position": "Developer"
  }'
```

### **3. ورود کاربر عادی**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "12345",
    "password": "mypassword123"
  }'
```

## 🔐 **سطوح دسترسی**

| نقش | دسترسی | توضیح |
|-----|---------|-------|
| **admin1** | کامل | ادمین اصلی - دسترسی به همه چیز |
| **admin2** | محدود | ادمین فرعی - مدیریت کاربران |
| **manager_women** | مدیریت زنان | مدیریت کارمندان زن |
| **manager_men** | مدیریت مردان | مدیریت کارمندان مرد |
| **employee** | پایه | کارمند عادی |

## 🛡️ **امنیت**

### **ویژگی‌های امنیتی:**
- ✅ رمزنگاری bcrypt برای رمز عبور
- ✅ JWT با امضای دیجیتال
- ✅ مدیریت توکن‌ها در دیتابیس
- ✅ کنترل دسترسی بر اساس نقش
- ✅ غیرفعال کردن توکن‌های قدیمی

### **مدیریت کاربران:**
- ✅ فقط ادمین‌ها می‌توانند کاربر ایجاد کنند
- ✅ کنترل کامل روی نقش‌ها
- ✅ مدیریت دپارتمان‌ها
- ✅ لاگ کامل تمام عملیات

## 📊 **مدیریت دیتابیس**

### **Collections:**
- `admins` - اطلاعات ادمین‌ها
- `employees` - اطلاعات کارمندان
- `tokens` - توکن‌های فعال

### **ساختار Admin:**
```json
{
  "_id": "ObjectId",
  "employee_id": "00001",
  "full_name": "مدیر اصلی",
  "password_hash": "$2b$12$...",
  "role": "admin1",
  "status": "active",
  "phone": "09123456789",
  "email": "admin@company.com",
  "is_super_admin": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

## 🚨 **نکات مهم**

### **⚠️ امنیت:**
1. **تغییر رمز عبور پیش‌فرض** بعد از اولین ورود
2. **مدیریت کاربران** فقط توسط ادمین‌ها
3. **کنترل دقیق نقش‌ها** و دسترسی‌ها

### **📝 لاگ‌گیری:**
- تمام عملیات احراز هویت لاگ می‌شوند
- تغییرات نقش‌ها ثبت می‌شوند
- دسترسی‌های غیرمجاز ردیابی می‌شوند

## 🔄 **Migration از سیستم قدیم**

اگر از سیستم قدیم استفاده می‌کردید:

1. **پشتیبان‌گیری** از دیتابیس
2. **اجرای script** برای ایجاد ادمین
3. **تست** سیستم جدید
4. **حذف** endpoint register قدیم

## 📞 **پشتیبانی**

در صورت بروز مشکل:
1. بررسی لاگ‌های سیستم
2. تست endpoint‌های احراز هویت
3. بررسی وضعیت دیتابیس
4. تماس با تیم توسعه

---

**🎉 سیستم جدید آماده استفاده است!**

## 📋 **Endpoint های موجود**

### **احراز هویت:**
- `POST /auth/login` - ورود کارمندان
- `POST /auth/admin-login` - ورود ادمین‌ها
- `POST /auth/logout` - خروج از سیستم
- `POST /auth/bootstrap-admin` - ایجاد اولین ادمین

### **مدیریت کاربران:**
- `GET /users/` - مشاهده کاربران (ادمین)
- `POST /users/` - ایجاد کاربر (ادمین)
- `PUT /users/{user_id}` - ویرایش کاربر (ادمین)
- `DELETE /users/{user_id}` - حذف کاربر (ادمین)

### **درخواست مرخصی:**
- `POST /leave-requests/` - ایجاد درخواست (کارمند)
- `GET /leave-requests/` - مشاهده درخواست‌ها
- `POST /leave-requests/{id}/approve-phase1` - تایید مرحله 1
- `POST /leave-requests/{id}/approve-phase2` - تایید مرحله 2
- `POST /leave-requests/{id}/reject` - رد درخواست

### **گزارش‌ها:**
- `POST /reports/` - ایجاد گزارش (کارمند)
- `GET /reports/` - مشاهده گزارش‌ها
- `POST /reports/{id}/approve` - تایید گزارش (مدیر)
- `POST /reports/{id}/reject` - رد گزارش (مدیر)

### **داشبورد:**
- `GET /dashboard/` - مشاهده آمار کلی (مدیر+)

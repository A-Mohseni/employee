# راهنمای کامل Endpoint های احراز هویت

## 🚀 **ساختار جدید Endpoint ها**

### **🔐 LOGIN ENDPOINTS**

#### **1. ورود کارمندان عادی**
```bash
POST /auth/login
```
**توضیح:** برای ورود کارمندان عادی (employee, manager_women, manager_men)

**درخواست:**
```json
{
    "employee_id": "123",
    "password": "password123"
}
```

**پاسخ:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "employee",
    "user_id": "68ce784d5767b9c66da1b06c"
}
```

#### **2. ورود ادمین‌ها**
```bash
POST /auth/admin/login
```
**توضیح:** برای ورود ادمین‌ها (admin1, admin2)

**درخواست:**
```json
{
    "employee_id": "00001",
    "password": "admin123!"
}
```

**پاسخ:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "admin1",
    "user_id": "68ce72ae21b6381404a726a2"
}
```

### **🚪 LOGOUT ENDPOINT**

#### **خروج از سیستم**
```bash
POST /auth/logout
```
**توضیح:** خروج از سیستم (نیاز به احراز هویت)

**Headers:**
```
Authorization: Bearer <token>
```

**پاسخ:**
```json
{
    "message": "Logout successful"
}
```

### **👑 ADMIN MANAGEMENT ENDPOINTS**

#### **1. ایجاد اولین ادمین**
```bash
POST /auth/admin/bootstrap
```
**توضیح:** ایجاد اولین ادمین سیستم (فقط یک بار قابل استفاده)

**درخواست:**
```json
{
    "employee_id": "00001",
    "password": "admin123!",
    "full_name": "مدیر اصلی",
    "phone": "09123456789",
    "email": "admin@company.com"
}
```

**پاسخ:**
```json
{
    "message": "First admin created successfully"
}
```

#### **2. ایجاد ادمین جدید**
```bash
POST /auth/admin/create
```
**توضیح:** ایجاد ادمین جدید (فقط admin1 می‌تواند)

**Headers:**
```
Authorization: Bearer <admin1_token>
```

**درخواست:**
```json
{
    "employee_id": "00002",
    "password": "admin456!",
    "full_name": "ادمین دوم",
    "phone": "09123456790",
    "email": "admin2@company.com",
    "role": "admin2",
    "is_super_admin": false
}
```

**پاسخ:**
```json
{
    "id": "68ce790f6c2d940f37a12232",
    "employee_id": "00002",
    "full_name": "ادمین دوم",
    "role": "admin2",
    "status": "active",
    "phone": "09123456790",
    "email": "admin2@company.com",
    "is_super_admin": false,
    "created_at": "2025-09-20T13:20:00",
    "updated_at": "2025-09-20T13:20:00"
}
```

#### **3. مشاهده لیست ادمین‌ها**
```bash
GET /auth/admin/list
```
**توضیح:** مشاهده تمام ادمین‌ها (فقط ادمین‌ها دسترسی دارند)

**Headers:**
```
Authorization: Bearer <admin_token>
```

**پاسخ:**
```json
[
    {
        "id": "68ce72ae21b6381404a726a2",
        "employee_id": "00001",
        "full_name": "مدیر اصلی",
        "role": "admin1",
        "status": "active",
        "phone": "09123456789",
        "email": "admin@company.com",
        "is_super_admin": true,
        "created_at": "2025-09-20T12:53:58",
        "updated_at": "2025-09-20T12:53:58"
    }
]
```

### **👥 USER MANAGEMENT ENDPOINTS**

#### **1. ایجاد کاربر جدید**
```bash
POST /auth/user/create
```
**توضیح:** ایجاد کاربر جدید (فقط ادمین‌ها می‌توانند)

**Headers:**
```
Authorization: Bearer <admin_token>
```

**درخواست:**
```json
{
    "employee_id": "123",
    "full_name": "کاربر جدید",
    "role": "employee",
    "phone": "09123456789",
    "email": "user@company.com",
    "password": "password123",
    "status": "active"
}
```

**پاسخ:**
```json
{
    "id": "68ce784d5767b9c66da1b06c",
    "employee_id": 123,
    "full_name": "کاربر جدید",
    "role": "employee",
    "status": "active",
    "created_at": "2025-09-20T13:17:57",
    "updated_at": "2025-09-20T13:17:57",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

#### **2. مشاهده لیست کاربران**
```bash
GET /auth/user/list
```
**توضیح:** مشاهده تمام کاربران (فقط ادمین‌ها دسترسی دارند)

**Headers:**
```
Authorization: Bearer <admin_token>
```

## 📋 **فرآیند کامل مدیریت سیستم**

### **مرحله 1: راه‌اندازی اولیه**
```bash
# 1. ایجاد اولین ادمین
curl -X POST "http://localhost:8000/auth/admin/bootstrap" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "00001",
    "password": "admin123!",
    "full_name": "مدیر اصلی",
    "phone": "09123456789",
    "email": "admin@company.com"
  }'
```

### **مرحله 2: ورود ادمین**
```bash
# 2. ورود با ادمین اصلی
curl -X POST "http://localhost:8000/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "00001",
    "password": "admin123!"
  }'
```

### **مرحله 3: ایجاد ادمین دوم**
```bash
# 3. ایجاد ادمین دوم
curl -X POST "http://localhost:8000/auth/admin/create" \
  -H "Authorization: Bearer <admin1_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "00002",
    "password": "admin456!",
    "full_name": "ادمین دوم",
    "phone": "09123456790",
    "email": "admin2@company.com",
    "role": "admin2",
    "is_super_admin": false
  }'
```

### **مرحله 4: ایجاد کاربران**
```bash
# 4. ایجاد کاربر عادی
curl -X POST "http://localhost:8000/auth/user/create" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "123",
    "full_name": "کاربر تست",
    "role": "employee",
    "phone": "09123456789",
    "email": "test@company.com",
    "password": "password123"
  }'

# 5. ایجاد مدیر زنان
curl -X POST "http://localhost:8000/auth/user/create" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "124",
    "full_name": "مدیر زنان",
    "role": "manager_women",
    "phone": "09123456790",
    "email": "manager@company.com",
    "password": "manager123"
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

## ⚠️ **نکات مهم**

1. **احراز هویت**: تمام endpoint های مدیریتی نیاز به token دارند
2. **سطوح دسترسی**: فقط admin1 می‌تواند ادمین ایجاد کند
3. **نقش‌های کاربری**: فقط نقش‌های employee, manager_women, manager_men قابل ایجاد هستند
4. **امنیت**: رمز عبورها هش می‌شوند و توکن‌ها مدیریت می‌شوند

## 🚀 **آماده استفاده!**

سیستم کاملاً آماده است و تمام endpoint ها مرتب و مستند شده‌اند.

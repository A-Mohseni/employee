# Employee Management System API

A complete FastAPI backend project with MongoDB using Motor for async operations. This system provides comprehensive employee management functionality including user management, leave requests, daily reports, shopping lists, and dashboard analytics.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control
- **User Management**: CRUD operations for employees with different roles (admin1, admin2, manager_female, manager_male, employee)
- **Leave Management**: Two-stage approval workflow for leave requests
- **Daily Reports**: Employee daily reporting system with manager approval
- **Shopping Lists**: Admin-managed shopping lists with item tracking
- **Dashboard**: Comprehensive analytics and overview statistics
- **Async Operations**: Full async/await support with Motor for MongoDB
- **Input Validation**: Comprehensive Pydantic validation for all inputs
- **Error Handling**: Structured JSON error responses

## Project Structure

```
app/
├── api/                    # API routers
│   ├── auth.py            # Authentication endpoints
│   ├── users.py           # User management endpoints
│   ├── leave_requests.py  # Leave request endpoints
│   ├── daily_reports.py   # Daily report endpoints
│   ├── shopping_list.py   # Shopping list endpoints
│   └── dashboard.py       # Dashboard endpoints
├── core/                   # Core functionality
│   ├── config.py          # Application configuration
│   ├── security.py        # JWT and password handling
│   └── auth.py            # Authentication middleware
├── db/                     # Database
│   └── database.py        # MongoDB connection
├── models/                 # Pydantic models
│   ├── user.py            # User models
│   ├── leave_request.py   # Leave request models
│   ├── daily_report.py    # Daily report models
│   ├── shopping_list.py   # Shopping list models
│   └── dashboard.py       # Dashboard models
├── services/               # Business logic
│   ├── user_service.py    # User business logic
│   ├── leave_request_service.py  # Leave request logic
│   ├── daily_report_service.py   # Daily report logic
│   ├── shopping_list_service.py  # Shopping list logic
│   └── dashboard_service.py      # Dashboard logic
└── main.py                # FastAPI application entry point
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd employee-management-system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Ensure MongoDB is running on `mongodb://localhost:27017`

5. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=employee_management
   JWT_SECRET_KEY=your-super-secure-secret-key-here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   DEBUG=True
   ```

## Running the Application

1. **Start the server**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/login/form` - Login with form data
- `GET /api/v1/auth/me` - Get current user info

### Users
- `POST /api/v1/users/` - Create new user (admin only)
- `GET /api/v1/users/` - Get all users (manager+)
- `GET /api/v1/users/{user_id}` - Get specific user (manager+)
- `PUT /api/v1/users/{user_id}` - Update user (admin only)
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)
- `GET /api/v1/users/by-role/{role}` - Get users by role (manager+)
- `GET /api/v1/users/by-department/{department}` - Get users by department (manager+)

### Leave Requests
- `POST /api/v1/leave-requests/` - Create leave request (employee+)
- `GET /api/v1/leave-requests/` - Get all leave requests (employee+)
- `GET /api/v1/leave-requests/{leave_id}` - Get specific leave request (employee+)
- `PUT /api/v1/leave-requests/{leave_id}` - Update leave request (employee+)
- `DELETE /api/v1/leave-requests/{leave_id}` - Delete leave request (employee+)
- `POST /api/v1/leave-requests/{leave_id}/approve-stage1` - Approve stage 1 (admin only)
- `POST /api/v1/leave-requests/{leave_id}/approve-stage2` - Approve stage 2 (manager only)
- `POST /api/v1/leave-requests/{leave_id}/reject` - Reject leave request (manager+)
- `GET /api/v1/leave-requests/my-leaves` - Get my leave requests (employee+)

### Daily Reports
- `POST /api/v1/daily-reports/` - Create daily report (employee+)
- `GET /api/v1/daily-reports/` - Get all daily reports (employee+)
- `GET /api/v1/daily-reports/{report_id}` - Get specific report (employee+)
- `PUT /api/v1/daily-reports/{report_id}` - Update report (employee+)
- `DELETE /api/v1/daily-reports/{report_id}` - Delete report (employee+)
- `POST /api/v1/daily-reports/{report_id}/approve` - Approve report (manager+)
- `GET /api/v1/daily-reports/by-date/{date}` - Get reports by date (manager+)
- `GET /api/v1/daily-reports/my-reports` - Get my reports (employee+)
- `GET /api/v1/daily-reports/pending-approval` - Get pending reports (manager+)

### Shopping Lists
- `POST /api/v1/shopping-list/` - Create shopping list (admin only)
- `GET /api/v1/shopping-list/` - Get all shopping lists (manager+)
- `GET /api/v1/shopping-list/{list_id}` - Get specific list (manager+)
- `PUT /api/v1/shopping-list/{list_id}` - Update list (admin only)
- `DELETE /api/v1/shopping-list/{list_id}` - Delete list (admin only)
- `POST /api/v1/shopping-list/{list_id}/toggle-item/{item_index}` - Toggle item (manager+)
- `POST /api/v1/shopping-list/{list_id}/add-item` - Add item (manager+)
- `DELETE /api/v1/shopping-list/{list_id}/remove-item/{item_index}` - Remove item (manager+)
- `GET /api/v1/shopping-list/stats/summary` - Get shopping stats (manager+)

### Dashboard
- `GET /api/v1/dashboard/` - Get dashboard overview (manager+)
- `GET /api/v1/dashboard/stats` - Get dashboard stats (manager+)
- `GET /api/v1/dashboard/department-stats` - Get department stats (manager+)
- `GET /api/v1/dashboard/recent-activities` - Get recent activities (manager+)
- `GET /api/v1/dashboard/upcoming-leaves` - Get upcoming leaves (manager+)

## User Roles

1. **admin1** - Super administrator with full access
2. **admin2** - Administrator with most permissions
3. **manager_female** - Female manager with approval rights
4. **manager_male** - Male manager with approval rights
5. **employee** - Regular employee with basic access

## Leave Request Workflow

1. Employee creates leave request (status: pending)
2. Admin approves stage 1 (status: stage1)
3. Manager approves stage 2 (status: approved)
4. Any admin/manager can reject at any stage (status: rejected)

## Daily Report Workflow

1. Employee creates daily report
2. Manager approves the report
3. Once approved, report cannot be modified

## Shopping List Features

- Admin creates shopping lists
- Managers can add/remove items and toggle completion
- Track total items and completed items
- Comprehensive statistics

## Error Handling

All endpoints return structured JSON errors:
```json
{
  "detail": "Error message"
}
```

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation with Pydantic
- CORS middleware configuration

## Development

To run in development mode with auto-reload:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

The API includes comprehensive error handling and validation. Test the endpoints using the interactive documentation at `/docs`.

## Production Deployment

1. Set `DEBUG=False` in environment variables
2. Use a strong `JWT_SECRET_KEY`
3. Configure proper CORS origins
4. Use a production MongoDB instance
5. Set up proper logging and monitoring

## License

This project is licensed under the MIT License.

# School Examination Results Management System

A full-featured, enterprise-grade desktop application built with **Python + Tkinter (ttk)** and **PostgreSQL via SQLAlchemy ORM**.

---

## Features

| Area | Capabilities |
|---|---|
| **Auth** | Secure bcrypt login, role-based access (Admin / Teacher) |
| **Students** | Full CRUD, search, pagination |
| **Teachers** | Full CRUD (Admin only) |
| **Classes** | Create, update, delete with academic year |
| **Subjects** | Assign to class & teacher |
| **Results** | Enter marks, auto grade/GPA, duplicate prevention, **real-time table update** |
| **Analytics** | Embedded Matplotlib charts: class avg, subject avg, top 5, pass/fail, GPA dist |
| **Reports** | PDF report cards, PDF class reports, CSV export |

---

## Project Structure

```
school_results_system/
├── main.py                  # Entry point
├── config.py                # DB connection, constants, theme
├── .env                     # Credentials (never commit this)
├── requirements.txt
│
├── models/
│   ├── user.py              # Admin, Teacher ORM models
│   ├── student.py
│   ├── class_model.py
│   ├── subject.py
│   └── result.py            # Auto grade/GPA calculation
│
├── services/
│   ├── auth_service.py      # Login, bcrypt hashing
│   ├── student_service.py   # CRUD + search + pagination
│   ├── teacher_service.py
│   ├── class_service.py
│   ├── subject_service.py
│   ├── result_service.py    # Marks validation, duplicate prevention
│   ├── analytics_service.py # SQL aggregations
│   └── report_service.py    # PDF + CSV generation
│
├── views/
│   ├── login_view.py
│   ├── base_dashboard.py    # Sidebar + topbar layout
│   ├── admin_dashboard.py
│   ├── teacher_dashboard.py
│   ├── students_panel.py
│   ├── teachers_panel.py
│   ├── classes_subjects_panel.py
│   ├── results_panel.py     # Real-time append on submit
│   ├── analytics_panel.py   # Matplotlib embedded charts
│   └── reports_panel.py
│
└── utils/
    └── ui_helpers.py        # Reusable widgets, dark theme styles
```

---

## Setup

### 1. Create PostgreSQL Database

```sql
CREATE DATABASE "SCHOOL_RESULTS";
```

### 2. Configure `.env`

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=SCHOOL_RESULTS
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

Tables are **auto-created** on first launch. A default admin is seeded:

| Email | Password |
|---|---|
| admin@school.edu | Admin@1234 |

---

## Grade Scale

| Marks | Grade | GPA | Remarks |
|---|---|---|---|
| 80–100 | A | 4.0 | Distinction |
| 70–79 | B | 3.0 | Credit |
| 60–69 | C | 2.0 | Merit |
| 50–59 | D | 1.0 | Pass |
| 0–49 | F | 0.0 | Fail |

---

## Architecture

- **MVC / Layered**: Models (SQLAlchemy ORM) → Services (business logic) → Views (Tkinter)
- **OOP**: All database records as Python objects; no raw SQL
- **Security**: bcrypt password hashing, `.env` credential loading
- **Real-time UI**: Newly submitted results instantly prepended to the Treeview without restart
- **Logging**: Rotating log file `school_results.log`

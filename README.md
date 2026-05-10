# Team Task Manager — Backend

A role-based task management REST API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. It implements full CRUD for users, projects, and tasks with JWT authentication and an RBAC (Role-Based Access Control) system for Admins and Members.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Auth | JWT (python-jose) + OAuth2 |
| Password Hashing | passlib[bcrypt] |
| Validation | Pydantic v2 + pydantic-settings |
| ASGI Server | Uvicorn |
| DB Driver | psycopg2-binary |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app, CORS, router mounting
│   ├── api/
│   │   ├── api.py                 # Central router, combines all sub-routers
│   │   ├── deps.py                # Shared dependencies (DB session, auth guards)
│   │   └── endpoints/
│   │       ├── auth.py            # Signup, login (form + JSON)
│   │       ├── dashboard.py       # Admin & Member dashboard stats
│   │       ├── projects.py        # Project CRUD + member management
│   │       ├── tasks.py           # Task CRUD with RBAC
│   │       └── users.py           # User listing
│   ├── core/
│   │   ├── config.py              # Settings (env vars via pydantic-settings)
│   │   ├── database.py            # SQLAlchemy engine, SessionLocal, Base
│   │   └── security.py            # JWT creation, password hash/verify
│   ├── models/
│   │   ├── __init__.py            # Imports all models (for Alembic auto-detection)
│   │   ├── enums.py               # UserRole, TaskStatus, ProjectStatus enums
│   │   ├── user.py                # User SQLAlchemy model
│   │   ├── project.py             # Project + project_members association table
│   │   └── task.py                # Task SQLAlchemy model
│   └── schemas/
│       ├── user.py                # UserCreate, UserResponse Pydantic schemas
│       ├── project.py             # ProjectCreate, ProjectResponse schemas
│       └── task.py                # TaskCreate, TaskUpdate, TaskResponse schemas
├── .env                           # Environment variables (not committed)
├── requirements.txt               # Python dependencies
└── alembic/                       # Database migration files
```

---

## Environment Variables

Create a `.env` file in the `backend/` root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/team_task_manager
SECRET_KEY=your-super-secret-key-for-jwt
```

| Variable | Description |
|---|---|
| `DATABASE_URL` | Full PostgreSQL connection string |
| `SECRET_KEY` | Random secret for signing JWT tokens |

---

## Database Schema

### `users`

| Column | Type | Description |
|---|---|---|
| `id` | UUID (String 36) | Primary key, auto-generated |
| `name` | String | Full name |
| `email` | String (unique) | Login email |
| `hashed_password` | String | bcrypt hashed password |
| `role` | Enum | `Admin` or `Member` |
| `created_at` | DateTime | Server-side timestamp |
| `updated_at` | DateTime | Auto-updated on change |

### `projects`

| Column | Type | Description |
|---|---|---|
| `id` | UUID (String 36) | Primary key, auto-generated |
| `title` | String | Project name |
| `description` | String | Optional description |
| `owner_id` | FK → users.id | Admin who created it |
| `status` | String | `Todo`, `In-Progress`, `Completed`, `On-Hold` |
| `start_date` | DateTime | Optional start date |
| `estimation_date` | DateTime | Optional estimated completion |
| `closed_date` | DateTime | Optional closure date |
| `created_at` | DateTime | Server-side timestamp |
| `updated_at` | DateTime | Auto-updated on change |

### `project_members` (Association Table)

| Column | Type | Description |
|---|---|---|
| `user_id` | FK → users.id | Member user |
| `project_id` | FK → projects.id | Project being joined |

> Composite primary key on `(user_id, project_id)`. Both columns cascade on delete.

### `tasks`

| Column | Type | Description |
|---|---|---|
| `id` | UUID (String 36) | Primary key, auto-generated |
| `title` | String | Task name |
| `description` | String | Optional detail |
| `status` | Enum | `Todo`, `In-Progress`, `Completed`, `Overdue`, `On-Hold` |
| `project_id` | FK → projects.id | Parent project (cascade delete) |
| `assignee_id` | FK → users.id | Assigned user (SET NULL on delete) |
| `due_date` | DateTime | Optional due date |
| `start_date` | DateTime | Optional start date |
| `estimation_date` | DateTime | Optional estimated completion |
| `closed_date` | DateTime | Optional closure date |
| `created_at` | DateTime | Server-side timestamp |
| `updated_at` | DateTime | Auto-updated on change |

### Enums

**`UserRole`**
```
Admin | Member
```

**`TaskStatus`**
```
Todo | In-Progress | Completed | Overdue | On-Hold
```

**`ProjectStatus`**
```
Todo | In-Progress | Completed | On-Hold
```

---

## API Routes

All routes are prefixed with `/api/v1`.

### Auth — `/api/v1`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/signup` | Public | Register a new user |
| POST | `/login/access-token` | Public | OAuth2 form-based login → returns JWT |
| POST | `/login` | Public | JSON-based login → returns JWT |

### Dashboard — `/api/v1/dashboard`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/admin` | Admin only | Returns full team stats: projects, tasks, members |
| GET | `/member` | Any user | Returns personal stats for the logged-in member |

### Projects — `/api/v1/projects`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | Any user | Admin: own projects. Member: joined projects |
| GET | `/{project_id}` | Any user | Single project (RBAC checked) |
| POST | `/` | Admin only | Create a new project |
| PUT | `/{project_id}` | Admin (owner) | Update project details |
| DELETE | `/{project_id}` | Admin (owner) | Delete project + cascade tasks |
| POST | `/{project_id}/members/{user_id}` | Admin (owner) | Add a member to the project |

### Tasks — `/api/v1/tasks`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | Any user | Admin: all tasks. Member: only assigned tasks |
| POST | `/` | Admin only | Create a task |
| PUT | `/{task_id}` | Any user (RBAC) | Admin: full update. Member: status only |
| DELETE | `/{task_id}` | Admin only | Delete a task |

### Users — `/api/v1/users`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | Any user | List all users (for task assignment dropdown) |

---

## RBAC Logic

### Admin
- Full CRUD on all projects they own
- Full CRUD on all tasks within their projects
- Can add members to projects
- Can view all tasks and users

### Member
- Can view only tasks they are directly assigned to
- Can view only projects they have been added to
- On `PUT /tasks/{id}`: **only the `status` field is updated**; all other submitted fields are silently ignored
- Cannot create/delete tasks or projects

---

## Authentication Flow

1. Client sends credentials to `POST /login/access-token` or `POST /login`
2. Server returns a JWT token with the user `id`, `name`, and `role` in the payload
3. Client stores token in `localStorage`
4. All subsequent requests include `Authorization: Bearer <token>` header
5. `deps.get_current_user` decodes the JWT on every protected endpoint
6. `deps.require_admin` additionally checks the role is `Admin`

JWT settings:
- Algorithm: `HS256`
- Expiry: 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`)

---

## Running Locally

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with DATABASE_URL and SECRET_KEY

# 4. Run database migrations (if using Alembic)
alembic upgrade head

# 5. Start the dev server
uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## Key Design Decisions

- **UUID PKs everywhere** — prevents ID enumeration attacks
- **Cascade deletes** — deleting a project deletes all its tasks automatically
- **Computed properties** — `Task.assigneeName` and `Task.projectName` are Python `@property` fields resolved at serialization time, so the API returns human-readable names without extra queries in the endpoint code
- **`exclude_unset=True`** on `TaskUpdate` — only fields explicitly sent by the client are applied; this prevents accidental null overwrites
- **CORS** — currently `allow_origins=["*"]`; restrict to your frontend domain in production

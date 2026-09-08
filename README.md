# FastAPI To-Do CRUD API

A lightweight RESTful CRUD API built using Python and FastAPI for the FlyRank AI Internship Backend Track.

## 🚀 How to Install & Run

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Subhajotipatra78/Task-API.git](https://github.com/Subhajotipatra78/Task-API.git)
   cd Task-API
   ```

2. **Set up virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install fastapi uvicorn pydantic
   ```

3. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```
   The API will run locally at `http://localhost:8000`.

---

## 🛠️ API Endpoints Summary

| CRUD Operation | Method | Endpoint | Description | Expected Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| **Read** | GET | `/` | API Metadata | 200 |
| **Read** | GET | `/health` | System Health Check | 200 |
| **Read** | GET | `/tasks` | List all tasks | 200 |
| **Read** | GET | `/tasks/{id}` | Get task by ID | 200, 404 |
| **Create** | POST | `/tasks` | Create a new task | 201, 400 |
| **Update** | PUT | `/tasks/{id}` | Update task title/done | 200, 400, 404 |
| **Delete** | DELETE | `/tasks/{id}` | Delete task | 204, 404 |

---

## 💻 Sample `curl` Output

```bash
curl -i http://localhost:8000/tasks/1
```
**Response:**
```http
HTTP/1.1 200 OK
date: Wed, 29 Jul 2026 10:00:00 GMT
server: uvicorn
content-length: 63
content-type: application/json

{"id":1,"title":"Learn FastAPI fundamentals","done":true}
```

---

## 📸 Interactive Swagger Documentation

Access Swagger UI interactive docs at `http://localhost:8000/docs`.https://github.com/Subhajotipatra78/Task-API/blob/main/Screenshot%20(33).png

## 🗄️ Database Integration (SQLite)

In Week 3, the storage layer was migrated from an in-memory Python list to **SQLite** (`tasks.db`)[span_9](start_span)[span_9](end_span).

---

# 🔐 Week 4 - Assignment: Auth (Login & Protect)

A secure authentication API built with FastAPI and Supabase Auth[span_1](start_span)[span_1](end_span). The application demonstrates user registration, login, session termination, JWT verification via reusable dependency guards, and interactive Swagger UI Bearer authentication[span_2](start_span)[span_2](end_span).

## 🛠️ Environment Configuration

Create a `.env` file based on `.env.example` containing your Supabase credentials[span_3](start_span)[span_3](end_span):

```env
SUPABASE_URL=[https://your-project-id.supabase.co](https://your-project-id.supabase.co)
SUPABASE_KEY=your-anon-public-jwt-key
PORT=8000

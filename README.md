
---

# BiteBuilder — Full-Stack Nutrition Platform

BiteBuilder is a full-stack nutrition and meal-tracking web application built with Django (Python) for the backend and React + Vite (TypeScript) for the frontend.

This project was developed collaboratively as part of a university group assignment and deployed on an AWS EC2 instance.

💻 A demonstration video showcasing the fully functional application is available [here](https://github.com/S-A-M-22/BiteBuilder/blob/main/BiteBuilder%20App%20Demo%20Video.mp4) to download.

This guide explains how to set up, run, and troubleshoot both the backend and frontend locally.

---

## Prerequisites

Ensure you have:

* Python 3.12+
* Node.js 18+ and npm
* PostgreSQL (if using production mode)

You must also have:

```
BiteBuilder\BiteBuilderApp\.env
```

For environment variables, contact **redacted** at [redacted].

---

## 1. Backend Setup — Django API Server

### Create and Activate a Virtual Environment

**Windows (PowerShell):**

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

If Python 3.14 causes dependency issues:

```bash
py -3.12 -m venv venv312
.\venv312\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Apply Migrations

**Windows:**

```bash
cd BiteBuilderApp
python manage.py makemigrations
python manage.py migrate
```

**macOS / Linux:**

```bash
cd BiteBuilderApp
python3 manage.py makemigrations
python3 manage.py migrate
```

---

### Run the Backend

```bash
python manage.py runserver 127.0.0.1:8000
```

Backend will be available at:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

Then return to the root directory:

```bash
cd ..
```

---

## 2. Frontend Setup — React + Vite

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create a new folder named: "HTTPScerts"

Install mkcert:

For mac:
```bash
brew install mkcert nss
```

For Window:
```bash
choco install mkcert nss -y
```

For Linux:
```bash
sudo apt install mkcert libnss3-tools
```

Create certs:
```bash
mkcert -install
mkcert localhost 127.0.0.1 ::1
```

---

## 3. Run Both Servers (Frontend + Backend)

Start both Django and Vite concurrently:

```bash
npm run dev
```

| Service  | URL                                            |
| -------- | ---------------------------------------------- |
| Frontend | [http://localhost:5173](http://localhost:5173) |
| Backend  | [http://127.0.0.1:8000](http://127.0.0.1:8000) |

All `/api` requests are automatically proxied to the Django backend.
Proxy configuration is defined in `vite.config.ts`:

```ts
proxy: {
  "/api": "http://127.0.0.1:8000"
}
```

---

## 4. Common Commands

| Command                | Description                   |
| ---------------------- | ----------------------------- |
| `npm run dev:frontend` | Run frontend only             |
| `npm run dev:backend`  | Run backend only              |
| `npm run build`        | Build frontend for production |
| `npm run preview`      | Preview production build      |
| `npm run lint`         | Run ESLint checks             |

---

## 5. Troubleshooting and Notes

### CORS

If using different ports or domains, update:

```
BiteBuilderApp/settings.py → CORS_ALLOWED_ORIGINS
```

### Stop Servers

Press `Ctrl + C` in the terminal.

### Port Conflicts

Change backend port:

```bash
python manage.py runserver 127.0.0.1:8080
```

Or modify the frontend port in `vite.config.ts`.

### Static Files (Production)

```bash
python manage.py collectstatic
```

### macOS Permissions

If activation fails:

```bash
chmod +x venv/bin/activate
```

---

## 6. Quick Startup Summary

```bash
cd BiteBuilderApp
python -m venv venv
# Windows:
venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
npm run dev
```

---

## 7. Stack Overview

| Layer      | Technology                     | Purpose                              |
| ---------- | ------------------------------ | ------------------------------------ |
| Backend    | Django + Django REST Framework | API, database models, authentication |
| Frontend   | React + TypeScript + Vite      | Dynamic user interface               |
| Styling    | Tailwind CSS + Theme Tokens    | Consistent UI theming                |
| Validation | Zod                            | Schema validation and type safety    |
| Database   | PostgreSQL (via Django ORM)    | Persistent data storage              |
| Auth       | Supabase / JWT                 | Secure user sessions                 |

---

## 8. Database and Migration Reset (Local Development Only)

Use this when migrations break or the schema changes heavily.

**Run:**

```bash
python reset_db.py
```

**What it does:**

* Deletes `db.sqlite3`
* Clears migration files (except `__init__.py`)
* Recreates migrations for `users` and `core`
* Runs all migrations

**Notes:**

* Use for local development only
* All data will be permanently deleted
* Ensure `DEBUG=True` in settings before running

---

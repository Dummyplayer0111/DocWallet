# DocWallet

A personal bill-tracking web app that stores receipt images on Google Drive and lets you export filtered reports as PDF.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5, Django REST Framework |
| Frontend | React 19, React Router 7 |
| Storage | Google Drive (via Google API) |
| Auth | Google OAuth 2.0 |
| PDF export | ReportLab |
| Database | SQLite (session/user data) |

## Features

- Sign in with Google
- Organise bills into categories
- Upload bill images directly to your Google Drive
- View, edit, and delete bills
- Export bills by date range (all categories or a single one)
- Download a formatted PDF report

## Project Structure

```
docwallet/
├── DocWallet/          # Django project settings & root URLs
├── Category_Handler/   # Bills & categories API (views, models, Drive utils)
├── Login_Handler/      # Google OAuth login/logout flow
├── frontend/           # React app (Create React App)
│   └── src/pages/      # Page components (SignIn, Home, BillsPage, …)
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## Setup

### Prerequisites

- Python 3.x
- Node.js & npm
- A Google Cloud project with OAuth 2.0 credentials

### 1. Create a virtual environment

```bash
mkdir DocWallet && cd DocWallet
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Clone and install Python dependencies

```bash
git clone <repo-url> docwallet
cd docwallet
pip install -r requirements.txt
```

### 3. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Set up an **OAuth 2.0 Client ID** (External, Web application) with the following scopes:
   - `auth/drive.appdata`
   - `auth/userinfo.email`
3. Add `http://localhost:8000` to **Authorised JavaScript origins**.
4. Add `http://localhost:8000/...` (your callback URL) to **Authorised redirect URIs**.

### 4. Create the `.env` file

Inside `DocWallet/` (the Django project package folder), create a file named `.env`:

```
GOOGLE_OAUTH_CLIENT_ID='your-client-id'
GOOGLE_OAUTH_CLIENT_SECRET='your-client-secret'
SECRET_KEY='your-django-secret-key'
```

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Start the Django backend

```bash
python manage.py runserver
```

The API is available at `http://localhost:8000`.

### 7. Start the React frontend (development)

In a separate terminal:

```bash
cd frontend
npm install
npm start
```

The frontend runs at `http://localhost:3000` and proxies API requests to the Django backend.

### 8. Open the app

Navigate to `http://localhost:3000` (dev) or `http://localhost:8000` (if serving the built frontend via Django).

> **Note:** An internet connection is required for Google OAuth and Drive operations.

## Building for Production

```bash
cd frontend
npm run build
```

Then serve the built static files through Django (configure `STATICFILES_DIRS` / `WhiteNoise` as needed).

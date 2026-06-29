# Charitable Organization Website

A modern, responsive website built with Flask and PostgreSQL.

## Features
- **Home Page**: Modern hero section with call-to-actions.
- **About & Mission**: Detailed information about the organization.
- **Programs**: Dynamic display of ongoing projects.
- **Donation**: Integrated with **Flutterwave** for secure online payments.
- **Gallery**: Photo and video showcase.
- **Admin Dashboard**: Secure management of donations and content.
- **Dark Theme Login**: Modern dark-themed administrative login.
- **SEO Optimized**: Meta tags and structured HTML.
- **Email Notifications**: Ready for SMTP integration.

## Setup Instructions

1. **Environment Variables**:
   Create a `.env` file with the following:
   ```env
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@localhost/dbname
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Initialization**:
   The database tables are automatically created on the first run.
   ```bash
   python app.py
   ```

4. **Deployment**:
   - Use a production server like Gunicorn: `gunicorn app:app`
   - Ensure PostgreSQL is running and accessible.
   - Replace the Flutterwave public key in `donate.html` with your live key.

## Technologies Used
- Backend: Flask, SQLAlchemy, Flask-Login, Flask-Mail
- Frontend: HTML5, CSS3 (Bootstrap 5), JavaScript
- Database: PostgreSQL
- Payment: Flutterwave API

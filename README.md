# TrueTank - Septic Service Management

A web-based septic tank field service management software designed for septic service businesses.

## 🚀 Quick Start

### Local Development Setup
```bash
# First time setup
./setup_dev.sh

# Start development server
./run_dev.sh
```

The application will be available at: http://localhost:5000

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

## 🎯 Features

- **Job Board**: Kanban-style board for managing septic service jobs
- **Database**: SQLite database for ticket tracking and management
- **Drag & Drop**: Move jobs between pending, in-progress, and completed
- **Responsive Design**: Works on desktop and mobile devices

## 🔧 Development

### Local vs Production
- **Local**: Uses SQLite database (`truetank_dev.db`)
- **Production**: Uses Railway's database (automatically configured)

### Environment Variables
- `FLASK_ENV`: Set to `development` for local development
- `FLASK_DEBUG`: Enable/disable debug mode
- `DATABASE_URL`: Database connection string
- `PORT`: Server port (defaults to 5000 locally, 8080 on Railway)

### Project Structure
```
├── app.py              # Main Flask application
├── models.py           # Database models
├── templates/          # HTML templates
├── static/            # CSS and JavaScript files
├── requirements.txt   # Python dependencies
├── Procfile          # Railway deployment configuration
└── .env              # Local environment variables (not committed)
```

## 🚢 Deployment

### To Railway
```bash
# Quick deploy (commits changes and pushes)
./deploy.sh

# Manual deploy
git add .
git commit -m "Your commit message"
git push origin main
```

### Production URL
https://truetank-production.up.railway.app

## 📊 API Endpoints

- `GET /` - Dashboard
- `GET /job-board` - Job board interface
- `GET /database` - Database view
- `GET /api/tickets` - Get all tickets
- `POST /api/tickets` - Create new ticket
- `PUT /api/tickets/<id>` - Update ticket

## 🛠️ Development Workflow

1. **Make changes locally** using the development server
2. **Test thoroughly** at http://localhost:5000
3. **Deploy to Railway** using `./deploy.sh`
4. **Verify on production** at the Railway URL

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop browsers
- Mobile phones
- Tablets

## 🔒 Security

- Environment variables for configuration
- SQLite for local development
- Production database on Railway
- No sensitive data in repository
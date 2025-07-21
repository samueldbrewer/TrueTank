# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrueTank is a Flask-based septic tank field service management application for septic service businesses. It provides job scheduling, customer management, fleet tracking, and AI-powered service estimation.

## Development Commands

### Setup and Run
```bash
# First time setup
./setup_dev.sh

# Start development server (http://localhost:5555)
./run_dev.sh

# Manual setup alternative
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Deployment
```bash
# Deploy to Railway
./deploy.sh
./deploy_simple.sh
./deploy_to_railway.sh
```

## Architecture

### Database Models (`models.py`)
Core entities with SQLAlchemy ORM:
- **Ticket**: Service tickets with status workflow (New → Assigned → In Progress → Completed)
- **Customer**: Customer information with address and contact details
- **SepticSystem**: Tank specifications (size, type, pumping frequency)
- **ServiceHistory**: Historical service records linked to tickets
- **Location**: Geographic data for service locations
- **Truck**: Fleet vehicle management with capacity and specifications
- **TeamMember**: Staff with roles and specializations
- **TruckTeamAssignment**: Many-to-many truck-staff relationships

### Service Types
Enum-based service categorization: Pumping, Inspection, Repair, Installation, Preventive Maintenance, Emergency Service, Line Cleaning/Rooter, Grease Trap Service, Lift Station Service.

### Application Structure
- **Flask App** (`app.py`): Main application with route handlers
- **Templates**: 15+ Jinja2 templates for different views
- **Static Assets**: Custom CSS and JavaScript for job board drag & drop
- **Database**: SQLite (dev), PostgreSQL (production via Railway)

### Key Features Architecture
- **Job Board**: Kanban interface with drag & drop functionality using custom JavaScript
- **AI Estimator**: OpenAI integration for septic service cost estimation
- **Fleet Management**: Truck assignment and team coordination
- **Database Interface**: Direct database viewing and management tools

## Environment Configuration

### Local Development
- Database: `instance/truetank_dev.db` (SQLite)
- Port: 5555
- Debug mode enabled

### Production (Railway)
- Database: PostgreSQL via Railway
- URL: https://truetank-production.up.railway.app
- Port: 8080 (configured in Procfile)
- Gunicorn WSGI server

## Data Management

### Sample Data
Multiple deployment scripts handle sample data creation and export:
- Sample tickets, customers, and service histories
- Concentrated schedule creation tools
- Export/import functionality for data migration

### Database Schema
Models use comprehensive enums for standardization (ServiceType, TicketStatus, TruckType, etc.). Foreign key relationships maintain data integrity across customers, locations, tickets, and service history.

## Development Workflow

### Adding New Features
1. Database changes: Update `models.py` with new models or fields
2. Routes: Add endpoints in `app.py`
3. Templates: Create/update HTML templates in `templates/`
4. Frontend: Add CSS/JS in `static/` for interactive features

### Testing Routes
Use the `/database` endpoint to inspect data during development. The application provides REST API endpoints (e.g., `/api/tickets`) for programmatic access.

## Important Notes

- **AI Integration**: OpenAI API key required for AI estimator functionality
- **Database Migrations**: Use Flask-Migrate for schema changes
- **Mobile Responsive**: Templates designed for mobile and desktop use
- **Production Ready**: Includes proper WSGI configuration and Railway deployment setup
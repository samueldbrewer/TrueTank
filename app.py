import os
from flask import Flask, render_template, request, jsonify
from models import db, Ticket, Customer, SepticSystem, ServiceHistory
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///truetank.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Development vs Production configuration
if os.environ.get('FLASK_ENV') == 'development':
    app.config['DEBUG'] = True
else:
    app.config['DEBUG'] = False

# Initialize database
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/job-board')
def job_board():
    return render_template('job_board.html')

@app.route('/database')
def database_view():
    tickets = Ticket.query.all()
    return render_template('database.html', tickets=tickets)

@app.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('ticket_detail.html', ticket=ticket)

@app.route('/customers')
def customers_view():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    tickets = Ticket.query.all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    try:
        data = request.get_json()
        
        # Check if job_id already exists
        existing_ticket = Ticket.query.filter_by(job_id=data.get('job_id')).first()
        if existing_ticket:
            return jsonify({'error': 'Job ID already exists'}), 400
        
        ticket = Ticket(
            job_id=data.get('job_id'),
            customer_name=data.get('customer_name'),
            customer_address=data.get('customer_address'),
            customer_phone=data.get('customer_phone'),
            service_type=data.get('service_type'),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            description=data.get('description'),
            estimated_cost=data.get('estimated_cost'),
            assigned_technician=data.get('assigned_technician')
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify(ticket.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(ticket, key):
            setattr(ticket, key, value)
    
    db.session.commit()
    return jsonify(ticket.to_dict())

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'TrueTank'}

# Create database tables
with app.app_context():
    db.create_all()
    
    # Add sample data if database is empty
    if Customer.query.count() == 0:
        # Create sample customers
        customers = [
            Customer(
                first_name='John',
                last_name='Smith',
                customer_type='residential',
                email='john.smith@email.com',
                phone_primary='(555) 123-4567',
                street_address='123 Main St',
                city='Anytown',
                state='TX',
                zip_code='12345',
                county='Sample County'
            ),
            Customer(
                first_name='Jane',
                last_name='Doe',
                customer_type='residential',
                email='jane.doe@email.com',
                phone_primary='(555) 987-6543',
                street_address='456 Oak Ave',
                city='Somewhere',
                state='TX',
                zip_code='67890',
                county='Sample County'
            ),
            Customer(
                first_name='Bob',
                last_name='Wilson',
                company_name='Wilson Industries',
                customer_type='commercial',
                email='bob@wilsonindustries.com',
                phone_primary='(555) 456-7890',
                street_address='789 Pine Rd',
                city='Elsewhere',
                state='TX',
                zip_code='54321',
                county='Sample County'
            )
        ]
        
        for customer in customers:
            db.session.add(customer)
        
        db.session.flush()  # Flush to get customer IDs
        
        # Create sample septic systems
        septic_systems = [
            SepticSystem(
                customer_id=customers[0].id,
                system_type='conventional',
                tank_size=1000,
                tank_material='concrete',
                num_compartments=2,
                pump_frequency_months=36,
                system_condition='good',
                access_notes='Tank is located 20 feet from back door'
            ),
            SepticSystem(
                customer_id=customers[1].id,
                system_type='aerobic',
                tank_size=1500,
                tank_material='fiberglass',
                num_compartments=3,
                pump_frequency_months=24,
                system_condition='fair',
                access_notes='Difficult access - need to move patio furniture'
            ),
            SepticSystem(
                customer_id=customers[2].id,
                system_type='commercial',
                tank_size=3000,
                tank_material='concrete',
                num_compartments=4,
                pump_frequency_months=12,
                system_condition='good',
                access_notes='Industrial area - use loading dock entrance'
            )
        ]
        
        for system in septic_systems:
            db.session.add(system)
        
        db.session.flush()  # Flush to get system IDs
        
        # Create sample tickets
        sample_tickets = [
            Ticket(
                job_id='JOB-001',
                customer_id=customers[0].id,
                septic_system_id=septic_systems[0].id,
                service_type='Septic Pumping',
                service_description='Routine septic tank pumping service',
                status='pending',
                priority='high',
                estimated_cost=350.00,
                estimated_duration=90,
                assigned_technician='Mike Johnson',
                office_notes='Customer prefers morning appointments',
                tank_condition='good',
                gallons_pumped=900,
                waste_type='domestic'
            ),
            Ticket(
                job_id='JOB-002',
                customer_id=customers[1].id,
                septic_system_id=septic_systems[1].id,
                service_type='Septic Inspection',
                service_description='Pre-purchase septic system inspection',
                status='in-progress',
                priority='medium',
                estimated_cost=200.00,
                estimated_duration=60,
                assigned_technician='Sarah Davis',
                office_notes='Real estate transaction - need report by Friday',
                inspection_required=True,
                permit_required=True
            ),
            Ticket(
                job_id='JOB-003',
                customer_id=customers[2].id,
                septic_system_id=septic_systems[2].id,
                service_type='Septic Repair',
                service_description='Repair broken septic line',
                status='completed',
                priority='high',
                estimated_cost=800.00,
                actual_cost=750.00,
                estimated_duration=240,
                assigned_technician='Tom Wilson',
                work_performed='Replaced 20 feet of damaged drain line',
                materials_used='PVC pipe, fittings, gravel',
                issues_found='Tree roots had invaded the drain line',
                recommendations='Annual root treatment recommended',
                payment_status='paid',
                payment_method='check'
            )
        ]
        
        for ticket in sample_tickets:
            db.session.add(ticket)
        
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(debug=True, host='0.0.0.0', port=port)
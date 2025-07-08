import os
from flask import Flask, render_template, request, jsonify
from models import db, Ticket

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///truetank.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    if Ticket.query.count() == 0:
        sample_tickets = [
            Ticket(
                job_id='JOB-001',
                customer_name='John Smith',
                customer_address='123 Main St, Anytown, USA',
                customer_phone='(555) 123-4567',
                service_type='Septic Pumping',
                status='pending',
                priority='high',
                description='Routine septic tank pumping service',
                estimated_cost=350.00
            ),
            Ticket(
                job_id='JOB-002',
                customer_name='Jane Doe',
                customer_address='456 Oak Ave, Somewhere, USA',
                customer_phone='(555) 987-6543',
                service_type='Septic Inspection',
                status='in-progress',
                priority='medium',
                description='Pre-purchase septic system inspection',
                estimated_cost=200.00,
                assigned_technician='Mike Johnson'
            ),
            Ticket(
                job_id='JOB-003',
                customer_name='Bob Wilson',
                customer_address='789 Pine Rd, Elsewhere, USA',
                customer_phone='(555) 456-7890',
                service_type='Septic Repair',
                status='completed',
                priority='high',
                description='Repair broken septic line',
                estimated_cost=800.00,
                actual_cost=750.00,
                assigned_technician='Sarah Davis'
            )
        ]
        
        for ticket in sample_tickets:
            db.session.add(ticket)
        
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
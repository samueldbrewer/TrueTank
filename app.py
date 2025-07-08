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

@app.route('/ticket/create')
def create_ticket():
    customers = Customer.query.all()
    septic_systems = SepticSystem.query.all()
    return render_template('ticket_form.html', customers=customers, septic_systems=septic_systems)

@app.route('/ticket/<int:ticket_id>/edit')
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    customers = Customer.query.all()
    septic_systems = SepticSystem.query.all()
    return render_template('ticket_form.html', ticket=ticket, customers=customers, septic_systems=septic_systems)

@app.route('/customer/create')
def create_customer():
    return render_template('customer_form.html')

@app.route('/customer/<int:customer_id>/edit')
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template('customer_form.html', customer=customer)

@app.route('/septic-system/create')
def create_septic_system():
    customers = Customer.query.all()
    return render_template('septic_system_form.html', customers=customers)

@app.route('/septic-system/<int:system_id>/edit')
def edit_septic_system(system_id):
    septic_system = SepticSystem.query.get_or_404(system_id)
    customers = Customer.query.all()
    return render_template('septic_system_form.html', septic_system=septic_system, customers=customers)

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    tickets = Ticket.query.order_by(Ticket.status, Ticket.column_position).all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@app.route('/api/tickets', methods=['POST'])
def create_ticket_api():
    try:
        data = request.get_json()
        
        # Check if job_id already exists
        existing_ticket = Ticket.query.filter_by(job_id=data.get('job_id')).first()
        if existing_ticket:
            return jsonify({'error': 'Job ID already exists'}), 400
        
        # Convert string values to appropriate types
        def safe_float(value):
            try:
                return float(value) if value and value != '' else None
            except (ValueError, TypeError):
                return None
                
        def safe_int(value):
            try:
                return int(value) if value and value != '' else None
            except (ValueError, TypeError):
                return None
                
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        # Parse datetime
        scheduled_date = None
        if data.get('scheduled_date'):
            try:
                from datetime import datetime
                scheduled_date = datetime.fromisoformat(data.get('scheduled_date'))
            except ValueError:
                pass
        
        ticket = Ticket(
            job_id=data.get('job_id'),
            customer_id=safe_int(data.get('customer_id')),
            septic_system_id=safe_int(data.get('septic_system_id')),
            service_type=data.get('service_type'),
            service_description=data.get('service_description'),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'pending'),
            scheduled_date=scheduled_date,
            estimated_duration=safe_int(data.get('estimated_duration')),
            assigned_technician=data.get('assigned_technician'),
            truck_number=data.get('truck_number'),
            estimated_cost=safe_float(data.get('estimated_cost')),
            actual_cost=safe_float(data.get('actual_cost')),
            labor_cost=safe_float(data.get('labor_cost')),
            parts_cost=safe_float(data.get('parts_cost')),
            disposal_cost=safe_float(data.get('disposal_cost')),
            gallons_pumped=safe_int(data.get('gallons_pumped')),
            waste_type=data.get('waste_type'),
            disposal_location=data.get('disposal_location'),
            trip_ticket_number=data.get('trip_ticket_number'),
            tank_condition=data.get('tank_condition'),
            equipment_used=data.get('equipment_used'),
            permit_required=safe_bool(data.get('permit_required')),
            permit_number=data.get('permit_number'),
            inspection_required=safe_bool(data.get('inspection_required')),
            inspection_passed=safe_bool(data.get('inspection_passed')),
            payment_status=data.get('payment_status', 'pending'),
            office_notes=data.get('office_notes'),
            technician_notes=data.get('technician_notes'),
            issues_found=data.get('issues_found'),
            recommendations=data.get('recommendations'),
            work_performed=data.get('work_performed'),
            materials_used=data.get('materials_used')
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify(ticket.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        data = request.get_json()
        
        # Convert string values to appropriate types
        def safe_float(value):
            try:
                return float(value) if value and value != '' else None
            except (ValueError, TypeError):
                return None
                
        def safe_int(value):
            try:
                return int(value) if value and value != '' else None
            except (ValueError, TypeError):
                return None
                
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        # Parse datetime
        if data.get('scheduled_date'):
            try:
                from datetime import datetime
                ticket.scheduled_date = datetime.fromisoformat(data.get('scheduled_date'))
            except ValueError:
                pass
        
        # Update basic fields
        if 'service_type' in data:
            ticket.service_type = data.get('service_type')
        if 'service_description' in data:
            ticket.service_description = data.get('service_description')
        if 'priority' in data:
            ticket.priority = data.get('priority')
        if 'status' in data:
            ticket.status = data.get('status')
        if 'customer_id' in data:
            ticket.customer_id = safe_int(data.get('customer_id'))
        if 'septic_system_id' in data:
            ticket.septic_system_id = safe_int(data.get('septic_system_id'))
        if 'estimated_duration' in data:
            ticket.estimated_duration = safe_int(data.get('estimated_duration'))
        if 'assigned_technician' in data:
            ticket.assigned_technician = data.get('assigned_technician')
        if 'truck_number' in data:
            ticket.truck_number = data.get('truck_number')
            
        # Update pricing fields
        if 'estimated_cost' in data:
            ticket.estimated_cost = safe_float(data.get('estimated_cost'))
        if 'actual_cost' in data:
            ticket.actual_cost = safe_float(data.get('actual_cost'))
        if 'labor_cost' in data:
            ticket.labor_cost = safe_float(data.get('labor_cost'))
        if 'parts_cost' in data:
            ticket.parts_cost = safe_float(data.get('parts_cost'))
        if 'disposal_cost' in data:
            ticket.disposal_cost = safe_float(data.get('disposal_cost'))
            
        # Update service details
        if 'gallons_pumped' in data:
            ticket.gallons_pumped = safe_int(data.get('gallons_pumped'))
        if 'waste_type' in data:
            ticket.waste_type = data.get('waste_type')
        if 'disposal_location' in data:
            ticket.disposal_location = data.get('disposal_location')
        if 'trip_ticket_number' in data:
            ticket.trip_ticket_number = data.get('trip_ticket_number')
        if 'tank_condition' in data:
            ticket.tank_condition = data.get('tank_condition')
        if 'equipment_used' in data:
            ticket.equipment_used = data.get('equipment_used')
            
        # Update compliance fields
        if 'permit_required' in data:
            ticket.permit_required = safe_bool(data.get('permit_required'))
        if 'permit_number' in data:
            ticket.permit_number = data.get('permit_number')
        if 'inspection_required' in data:
            ticket.inspection_required = safe_bool(data.get('inspection_required'))
        if 'inspection_passed' in data:
            ticket.inspection_passed = safe_bool(data.get('inspection_passed'))
            
        # Update payment
        if 'payment_status' in data:
            ticket.payment_status = data.get('payment_status')
            
        # Update notes
        if 'office_notes' in data:
            ticket.office_notes = data.get('office_notes')
        if 'technician_notes' in data:
            ticket.technician_notes = data.get('technician_notes')
        if 'issues_found' in data:
            ticket.issues_found = data.get('issues_found')
        if 'recommendations' in data:
            ticket.recommendations = data.get('recommendations')
        if 'work_performed' in data:
            ticket.work_performed = data.get('work_performed')
        if 'materials_used' in data:
            ticket.materials_used = data.get('materials_used')
        
        db.session.commit()
        return jsonify(ticket.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/next-id')
def get_next_job_id():
    # Find the highest job number
    latest_ticket = Ticket.query.filter(Ticket.job_id.like('JOB-%')).order_by(Ticket.job_id.desc()).first()
    
    if latest_ticket:
        try:
            # Extract number from JOB-XXX format
            job_num = int(latest_ticket.job_id.split('-')[1])
            next_num = job_num + 1
        except (ValueError, IndexError):
            next_num = 1
    else:
        next_num = 1
    
    next_job_id = f"JOB-{str(next_num).zfill(3)}"
    return jsonify({'job_id': next_job_id})

@app.route('/api/tickets/reorder', methods=['POST'])
def reorder_tickets():
    try:
        data = request.get_json()
        ticket_id = data.get('ticket_id')
        new_status = data.get('new_status')
        new_position = data.get('new_position', 0)
        
        # Get the ticket being moved
        ticket = Ticket.query.get_or_404(ticket_id)
        old_status = ticket.status
        old_position = ticket.column_position
        
        # If moving to a different column, update all positions in both columns
        if old_status != new_status:
            # Decrement positions in old column for tickets below the moved ticket
            Ticket.query.filter(
                Ticket.status == old_status,
                Ticket.column_position > old_position
            ).update({Ticket.column_position: Ticket.column_position - 1})
            
            # Increment positions in new column for tickets at or above the new position
            Ticket.query.filter(
                Ticket.status == new_status,
                Ticket.column_position >= new_position
            ).update({Ticket.column_position: Ticket.column_position + 1})
            
            # Update the ticket's status and position
            ticket.status = new_status
            ticket.column_position = new_position
            
        else:
            # Moving within the same column
            if new_position > old_position:
                # Moving down: decrement positions of tickets between old and new position
                Ticket.query.filter(
                    Ticket.status == new_status,
                    Ticket.column_position > old_position,
                    Ticket.column_position <= new_position
                ).update({Ticket.column_position: Ticket.column_position - 1})
            elif new_position < old_position:
                # Moving up: increment positions of tickets between new and old position
                Ticket.query.filter(
                    Ticket.status == new_status,
                    Ticket.column_position >= new_position,
                    Ticket.column_position < old_position
                ).update({Ticket.column_position: Ticket.column_position + 1})
            
            # Update the ticket's position
            ticket.column_position = new_position
        
        db.session.commit()
        return jsonify({'success': True, 'ticket': ticket.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Customer Management APIs
@app.route('/api/customers', methods=['POST'])
def create_customer_api():
    try:
        data = request.get_json()
        
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        customer = Customer(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            company_name=data.get('company_name'),
            customer_type=data.get('customer_type', 'residential'),
            email=data.get('email'),
            phone_primary=data.get('phone_primary'),
            phone_secondary=data.get('phone_secondary'),
            street_address=data.get('street_address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            county=data.get('county'),
            billing_street_address=data.get('billing_street_address'),
            billing_city=data.get('billing_city'),
            billing_state=data.get('billing_state'),
            billing_zip_code=data.get('billing_zip_code'),
            preferred_contact_method=data.get('preferred_contact_method', 'phone'),
            payment_terms=data.get('payment_terms', 'net_30'),
            tax_exempt=safe_bool(data.get('tax_exempt')),
            tax_exempt_number=data.get('tax_exempt_number'),
            service_reminders=safe_bool(data.get('service_reminders', True)),
            marketing_emails=safe_bool(data.get('marketing_emails', True))
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'company_name': customer.company_name,
            'customer_type': customer.customer_type,
            'email': customer.email,
            'phone_primary': customer.phone_primary,
            'street_address': customer.street_address,
            'city': customer.city,
            'state': customer.state,
            'zip_code': customer.zip_code
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer_api(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        # Update customer fields
        if 'first_name' in data:
            customer.first_name = data.get('first_name')
        if 'last_name' in data:
            customer.last_name = data.get('last_name')
        if 'company_name' in data:
            customer.company_name = data.get('company_name')
        if 'customer_type' in data:
            customer.customer_type = data.get('customer_type')
        if 'email' in data:
            customer.email = data.get('email')
        if 'phone_primary' in data:
            customer.phone_primary = data.get('phone_primary')
        if 'phone_secondary' in data:
            customer.phone_secondary = data.get('phone_secondary')
        if 'street_address' in data:
            customer.street_address = data.get('street_address')
        if 'city' in data:
            customer.city = data.get('city')
        if 'state' in data:
            customer.state = data.get('state')
        if 'zip_code' in data:
            customer.zip_code = data.get('zip_code')
        if 'county' in data:
            customer.county = data.get('county')
        if 'billing_street_address' in data:
            customer.billing_street_address = data.get('billing_street_address')
        if 'billing_city' in data:
            customer.billing_city = data.get('billing_city')
        if 'billing_state' in data:
            customer.billing_state = data.get('billing_state')
        if 'billing_zip_code' in data:
            customer.billing_zip_code = data.get('billing_zip_code')
        if 'preferred_contact_method' in data:
            customer.preferred_contact_method = data.get('preferred_contact_method')
        if 'payment_terms' in data:
            customer.payment_terms = data.get('payment_terms')
        if 'tax_exempt' in data:
            customer.tax_exempt = safe_bool(data.get('tax_exempt'))
        if 'tax_exempt_number' in data:
            customer.tax_exempt_number = data.get('tax_exempt_number')
        if 'service_reminders' in data:
            customer.service_reminders = safe_bool(data.get('service_reminders'))
        if 'marketing_emails' in data:
            customer.marketing_emails = safe_bool(data.get('marketing_emails'))
        
        db.session.commit()
        
        return jsonify({
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'company_name': customer.company_name,
            'customer_type': customer.customer_type,
            'email': customer.email,
            'phone_primary': customer.phone_primary,
            'street_address': customer.street_address,
            'city': customer.city,
            'state': customer.state,
            'zip_code': customer.zip_code
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer_api(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Check if customer has associated tickets
        tickets = Ticket.query.filter_by(customer_id=customer_id).all()
        if tickets:
            return jsonify({'error': 'Cannot delete customer with associated tickets. Delete tickets first.'}), 400
        
        # Check if customer has associated septic systems
        systems = SepticSystem.query.filter_by(customer_id=customer_id).all()
        if systems:
            return jsonify({'error': 'Cannot delete customer with associated septic systems. Delete systems first.'}), 400
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Customer deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Septic System Management APIs
@app.route('/api/septic-systems', methods=['POST'])
def create_septic_system_api():
    try:
        data = request.get_json()
        
        def safe_int(value):
            try:
                return int(value) if value and value != '' else None
            except (ValueError, TypeError):
                return None
                
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        # Parse dates
        install_date = None
        if data.get('install_date'):
            try:
                from datetime import datetime
                install_date = datetime.fromisoformat(data.get('install_date')).date()
            except ValueError:
                pass
        
        last_pumped = None
        if data.get('last_pumped'):
            try:
                from datetime import datetime
                last_pumped = datetime.fromisoformat(data.get('last_pumped')).date()
            except ValueError:
                pass
                
        next_pump_due = None
        if data.get('next_pump_due'):
            try:
                from datetime import datetime
                next_pump_due = datetime.fromisoformat(data.get('next_pump_due')).date()
            except ValueError:
                pass
        
        septic_system = SepticSystem(
            customer_id=safe_int(data.get('customer_id')),
            system_type=data.get('system_type'),
            tank_size=safe_int(data.get('tank_size')),
            tank_material=data.get('tank_material'),
            num_compartments=safe_int(data.get('num_compartments')),
            install_date=install_date,
            permit_number=data.get('permit_number'),
            installer_company=data.get('installer_company'),
            pump_frequency_months=safe_int(data.get('pump_frequency_months', 36)),
            last_pumped=last_pumped,
            next_pump_due=next_pump_due,
            system_condition=data.get('system_condition', 'good'),
            needs_repair=safe_bool(data.get('needs_repair')),
            repair_notes=data.get('repair_notes'),
            access_notes=data.get('access_notes'),
            gps_coordinates=data.get('gps_coordinates')
        )
        
        db.session.add(septic_system)
        db.session.commit()
        
        return jsonify({
            'id': septic_system.id,
            'customer_id': septic_system.customer_id,
            'system_type': septic_system.system_type,
            'tank_size': septic_system.tank_size,
            'tank_material': septic_system.tank_material,
            'num_compartments': septic_system.num_compartments,
            'pump_frequency_months': septic_system.pump_frequency_months,
            'system_condition': septic_system.system_condition,
            'access_notes': septic_system.access_notes
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/septic-systems/<int:system_id>', methods=['PUT'])
def update_septic_system_api(system_id):
    try:
        septic_system = SepticSystem.query.get_or_404(system_id)
        data = request.get_json()
        
        def safe_int(value):
            try:
                return int(value) if value and value != '' else None
            except (ValueError, TypeError):
                return None
                
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        # Parse dates
        if 'install_date' in data and data.get('install_date'):
            try:
                from datetime import datetime
                septic_system.install_date = datetime.fromisoformat(data.get('install_date')).date()
            except ValueError:
                pass
        
        if 'last_pumped' in data and data.get('last_pumped'):
            try:
                from datetime import datetime
                septic_system.last_pumped = datetime.fromisoformat(data.get('last_pumped')).date()
            except ValueError:
                pass
                
        if 'next_pump_due' in data and data.get('next_pump_due'):
            try:
                from datetime import datetime
                septic_system.next_pump_due = datetime.fromisoformat(data.get('next_pump_due')).date()
            except ValueError:
                pass
        
        # Update other fields
        if 'customer_id' in data:
            septic_system.customer_id = safe_int(data.get('customer_id'))
        if 'system_type' in data:
            septic_system.system_type = data.get('system_type')
        if 'tank_size' in data:
            septic_system.tank_size = safe_int(data.get('tank_size'))
        if 'tank_material' in data:
            septic_system.tank_material = data.get('tank_material')
        if 'num_compartments' in data:
            septic_system.num_compartments = safe_int(data.get('num_compartments'))
        if 'permit_number' in data:
            septic_system.permit_number = data.get('permit_number')
        if 'installer_company' in data:
            septic_system.installer_company = data.get('installer_company')
        if 'pump_frequency_months' in data:
            septic_system.pump_frequency_months = safe_int(data.get('pump_frequency_months'))
        if 'system_condition' in data:
            septic_system.system_condition = data.get('system_condition')
        if 'needs_repair' in data:
            septic_system.needs_repair = safe_bool(data.get('needs_repair'))
        if 'repair_notes' in data:
            septic_system.repair_notes = data.get('repair_notes')
        if 'access_notes' in data:
            septic_system.access_notes = data.get('access_notes')
        if 'gps_coordinates' in data:
            septic_system.gps_coordinates = data.get('gps_coordinates')
        
        db.session.commit()
        
        return jsonify({
            'id': septic_system.id,
            'customer_id': septic_system.customer_id,
            'system_type': septic_system.system_type,
            'tank_size': septic_system.tank_size,
            'tank_material': septic_system.tank_material,
            'num_compartments': septic_system.num_compartments,
            'pump_frequency_months': septic_system.pump_frequency_months,
            'system_condition': septic_system.system_condition,
            'access_notes': septic_system.access_notes
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/septic-systems/<int:system_id>', methods=['DELETE'])
def delete_septic_system_api(system_id):
    try:
        septic_system = SepticSystem.query.get_or_404(system_id)
        
        # Check if system has associated tickets
        tickets = Ticket.query.filter_by(septic_system_id=system_id).all()
        if tickets:
            return jsonify({'error': 'Cannot delete septic system with associated tickets. Delete tickets first.'}), 400
        
        db.session.delete(septic_system)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Septic system deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ticket Deletion API
@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket_api(ticket_id):
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        old_status = ticket.status
        old_position = ticket.column_position
        
        # Delete the ticket
        db.session.delete(ticket)
        
        # Adjust positions of remaining tickets in the same column
        Ticket.query.filter(
            Ticket.status == old_status,
            Ticket.column_position > old_position
        ).update({Ticket.column_position: Ticket.column_position - 1})
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Ticket deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
                column_position=0,
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
                column_position=0,
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
                column_position=0,
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
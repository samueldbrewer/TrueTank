import os
from flask import Flask, render_template, request, jsonify
from models import db, Ticket, Customer, SepticSystem, ServiceHistory, Location, Truck, TeamMember
from dotenv import load_dotenv
from datetime import datetime

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

# Fleet Management Routes
@app.route('/fleet')
def fleet_manager():
    trucks = Truck.query.all()
    locations = Location.query.filter_by(is_active=True).all()
    return render_template('fleet_manager.html', trucks=trucks, locations=locations)

@app.route('/truck/create')
def create_truck():
    locations = Location.query.filter_by(is_active=True).all()
    return render_template('truck_form.html', locations=locations)

@app.route('/truck/<int:truck_id>/edit')
def edit_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    locations = Location.query.filter_by(is_active=True).all()
    return render_template('truck_form.html', truck=truck, locations=locations)

@app.route('/location/create')
def create_location():
    return render_template('location_form.html')

@app.route('/location/<int:location_id>/edit')
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    return render_template('location_form.html', location=location)

# Team Management Routes
@app.route('/team')
def team_manager():
    team_members = TeamMember.query.all()
    return render_template('team_manager.html', team_members=team_members)

@app.route('/team-member/create')
def create_team_member():
    return render_template('team_member_form.html')

@app.route('/team-member/<int:member_id>/edit')
def edit_team_member(member_id):
    team_member = TeamMember.query.get_or_404(member_id)
    return render_template('team_member_form.html', team_member=team_member)

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

# Fleet Management APIs
@app.route('/api/trucks', methods=['GET'])
def get_trucks():
    trucks = Truck.query.all()
    return jsonify([truck.to_dict() for truck in trucks])

@app.route('/api/trucks', methods=['POST'])
def create_truck_api():
    try:
        data = request.get_json()
        
        def safe_int(value):
            try:
                return int(value) if value and value != '' else None
            except (ValueError, TypeError):
                return None
                
        def safe_float(value):
            try:
                return float(value) if value and value != '' else None
            except (ValueError, TypeError):
                return None
                
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        # Parse dates
        purchase_date = None
        if data.get('purchase_date'):
            try:
                from datetime import datetime
                purchase_date = datetime.fromisoformat(data.get('purchase_date')).date()
            except ValueError:
                pass
        
        last_maintenance = None
        if data.get('last_maintenance'):
            try:
                from datetime import datetime
                last_maintenance = datetime.fromisoformat(data.get('last_maintenance')).date()
            except ValueError:
                pass
                
        next_maintenance_due = None
        if data.get('next_maintenance_due'):
            try:
                from datetime import datetime
                next_maintenance_due = datetime.fromisoformat(data.get('next_maintenance_due')).date()
            except ValueError:
                pass
        
        insurance_expiry = None
        if data.get('insurance_expiry'):
            try:
                from datetime import datetime
                insurance_expiry = datetime.fromisoformat(data.get('insurance_expiry')).date()
            except ValueError:
                pass
                
        registration_expiry = None
        if data.get('registration_expiry'):
            try:
                from datetime import datetime
                registration_expiry = datetime.fromisoformat(data.get('registration_expiry')).date()
            except ValueError:
                pass
        
        truck = Truck(
            truck_number=data.get('truck_number'),
            license_plate=data.get('license_plate'),
            vin=data.get('vin'),
            make=data.get('make'),
            model=data.get('model'),
            year=safe_int(data.get('year')),
            color=data.get('color'),
            tank_capacity=safe_int(data.get('tank_capacity')),
            tank_material=data.get('tank_material', 'aluminum'),
            num_compartments=safe_int(data.get('num_compartments', 1)),
            pump_type=data.get('pump_type'),
            pump_cfm=safe_int(data.get('pump_cfm')),
            hose_length=safe_int(data.get('hose_length')),
            hose_diameter=safe_float(data.get('hose_diameter')),
            has_hose_reel=safe_bool(data.get('has_hose_reel')),
            has_pressure_washer=safe_bool(data.get('has_pressure_washer')),
            has_camera_system=safe_bool(data.get('has_camera_system')),
            has_gps_tracking=safe_bool(data.get('has_gps_tracking')),
            special_equipment=data.get('special_equipment'),
            status=data.get('status', 'active'),
            current_location_id=safe_int(data.get('current_location_id')),
            current_mileage=safe_int(data.get('current_mileage')),
            engine_hours=safe_float(data.get('engine_hours')),
            last_maintenance=last_maintenance,
            next_maintenance_due=next_maintenance_due,
            maintenance_interval_miles=safe_int(data.get('maintenance_interval_miles', 5000)),
            maintenance_interval_hours=safe_int(data.get('maintenance_interval_hours', 250)),
            insurance_company=data.get('insurance_company'),
            insurance_policy=data.get('insurance_policy'),
            insurance_expiry=insurance_expiry,
            registration_expiry=registration_expiry,
            dot_number=data.get('dot_number'),
            purchase_date=purchase_date,
            purchase_price=safe_float(data.get('purchase_price')),
            current_value=safe_float(data.get('current_value')),
            notes=data.get('notes')
        )
        
        db.session.add(truck)
        db.session.commit()
        
        return jsonify(truck.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/trucks/<int:truck_id>', methods=['DELETE'])
def delete_truck_api(truck_id):
    try:
        truck = Truck.query.get_or_404(truck_id)
        
        # Check if truck has associated tickets
        tickets = Ticket.query.filter_by(truck_number=truck.truck_number).all()
        if tickets:
            return jsonify({'error': 'Cannot delete truck with associated tickets. Reassign tickets first.'}), 400
        
        db.session.delete(truck)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Truck deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Location Management APIs
@app.route('/api/locations', methods=['GET'])
def get_locations():
    locations = Location.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': loc.id,
        'name': loc.name,
        'location_type': loc.location_type,
        'street_address': loc.street_address,
        'city': loc.city,
        'state': loc.state,
        'zip_code': loc.zip_code,
        'gps_coordinates': loc.gps_coordinates,
        'contact_person': loc.contact_person,
        'phone_number': loc.phone_number
    } for loc in locations])

@app.route('/api/locations', methods=['POST'])
def create_location_api():
    try:
        data = request.get_json()
        
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        location = Location(
            name=data.get('name'),
            location_type=data.get('location_type', 'office'),
            street_address=data.get('street_address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            county=data.get('county'),
            gps_coordinates=data.get('gps_coordinates'),
            access_notes=data.get('access_notes'),
            capacity_notes=data.get('capacity_notes'),
            security_info=data.get('security_info'),
            contact_person=data.get('contact_person'),
            phone_number=data.get('phone_number'),
            is_active=safe_bool(data.get('is_active', True)),
            hours_of_operation=data.get('hours_of_operation')
        )
        
        db.session.add(location)
        db.session.commit()
        
        return jsonify({
            'id': location.id,
            'name': location.name,
            'location_type': location.location_type,
            'street_address': location.street_address,
            'city': location.city,
            'state': location.state,
            'zip_code': location.zip_code
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Team Management APIs
@app.route('/api/team-members', methods=['GET'])
def get_team_members():
    members = TeamMember.query.all()
    return jsonify([member.to_dict() for member in members])

@app.route('/api/team-members', methods=['POST'])
def create_team_member_api():
    try:
        data = request.get_json()
        
        def safe_bool(value):
            return value in [True, 'true', 'True', '1', 1]
        
        # Parse dates
        hire_date = None
        if data.get('hire_date'):
            try:
                from datetime import datetime
                hire_date = datetime.fromisoformat(data.get('hire_date')).date()
            except ValueError:
                pass
        
        cdl_expiry = None
        if data.get('cdl_expiry'):
            try:
                from datetime import datetime
                cdl_expiry = datetime.fromisoformat(data.get('cdl_expiry')).date()
            except ValueError:
                pass
                
        septic_cert_expiry = None
        if data.get('septic_cert_expiry'):
            try:
                from datetime import datetime
                septic_cert_expiry = datetime.fromisoformat(data.get('septic_cert_expiry')).date()
            except ValueError:
                pass
        
        # Parse time
        shift_start_time = None
        if data.get('shift_start_time'):
            try:
                from datetime import datetime
                shift_start_time = datetime.strptime(data.get('shift_start_time'), '%H:%M').time()
            except ValueError:
                pass
                
        shift_end_time = None
        if data.get('shift_end_time'):
            try:
                from datetime import datetime
                shift_end_time = datetime.strptime(data.get('shift_end_time'), '%H:%M').time()
            except ValueError:
                pass
        
        team_member = TeamMember(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            employee_id=data.get('employee_id'),
            phone_primary=data.get('phone_primary'),
            phone_secondary=data.get('phone_secondary'),
            email=data.get('email'),
            home_street_address=data.get('home_street_address'),
            home_city=data.get('home_city'),
            home_state=data.get('home_state'),
            home_zip_code=data.get('home_zip_code'),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            emergency_contact_relationship=data.get('emergency_contact_relationship'),
            position=data.get('position'),
            department=data.get('department', 'field_service'),
            hire_date=hire_date,
            employment_status=data.get('employment_status', 'active'),
            cdl_license=safe_bool(data.get('cdl_license')),
            cdl_expiry=cdl_expiry,
            septic_certification=safe_bool(data.get('septic_certification')),
            septic_cert_expiry=septic_cert_expiry,
            other_certifications=data.get('other_certifications'),
            shift_start_time=shift_start_time,
            shift_end_time=shift_end_time,
            work_days=data.get('work_days', 'weekdays'),
            notes=data.get('notes'),
            is_supervisor=safe_bool(data.get('is_supervisor')),
            can_operate_trucks=safe_bool(data.get('can_operate_trucks', True))
        )
        
        db.session.add(team_member)
        db.session.commit()
        
        return jsonify(team_member.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/team-members/<int:member_id>', methods=['DELETE'])
def delete_team_member_api(member_id):
    try:
        team_member = TeamMember.query.get_or_404(member_id)
        
        db.session.delete(team_member)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Team member deleted successfully'})
        
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
    # First create locations, trucks, and team members, then customers and tickets
    if Location.query.count() == 0:
        # Create sample locations first
        locations = [
            Location(
                name='Main Office',
                location_type='office',
                street_address='123 Business Blvd',
                city='Anytown',
                state='TX',
                zip_code='12345',
                county='Sample County',
                contact_person='Office Manager',
                phone_number='(555) 123-4567',
                hours_of_operation='8:00 AM - 5:00 PM',
                access_notes='Main entrance, visitor parking available'
            ),
            Location(
                name='Storage Facility A',
                location_type='storage',
                street_address='456 Storage Lane',
                city='Anytown',
                state='TX',
                zip_code='12346',
                county='Sample County',
                contact_person='Yard Supervisor',
                phone_number='(555) 234-5678',
                hours_of_operation='24/7 Access',
                capacity_notes='Can store up to 8 trucks',
                security_info='Gate code: 1234, Security cameras active',
                access_notes='Large vehicles use rear entrance'
            ),
            Location(
                name='North Depot',
                location_type='depot',
                street_address='789 Industrial Dr',
                city='Somewhere',
                state='TX',
                zip_code='67890',
                county='Sample County',
                contact_person='Site Manager',
                phone_number='(555) 345-6789',
                hours_of_operation='6:00 AM - 10:00 PM',
                capacity_notes='Can store up to 4 trucks',
                access_notes='Fuel station available on site'
            )
        ]
        
        for location in locations:
            db.session.add(location)
        
        db.session.flush()  # Flush to get location IDs
        
        # Add sample trucks
        trucks = [
            Truck(
                truck_number='T-001',
                license_plate='ST001TX',
                make='International',
                model='DuraStar',
                year=2020,
                color='White',
                tank_capacity=2500,
                tank_material='aluminum',
                num_compartments=2,
                pump_type='Masport HXL4V',
                pump_cfm=400,
                hose_length=200,
                hose_diameter=4.0,
                has_hose_reel=True,
                has_pressure_washer=True,
                has_gps_tracking=True,
                status='active',
                current_location_id=locations[1].id,  # Storage Facility A
                current_mileage=45000,
                engine_hours=1200.5,
                maintenance_interval_miles=5000,
                maintenance_interval_hours=250,
                insurance_company='Fleet Insurance Co',
                purchase_price=125000.00,
                current_value=95000.00,
                notes='Primary pumping truck, excellent condition'
            ),
            Truck(
                truck_number='T-002',
                license_plate='ST002TX',
                make='Freightliner',
                model='Business Class M2',
                year=2019,
                color='Blue',
                tank_capacity=4000,
                tank_material='aluminum',
                num_compartments=3,
                pump_type='Fruitland 8200',
                pump_cfm=500,
                hose_length=300,
                hose_diameter=4.0,
                has_hose_reel=True,
                has_pressure_washer=False,
                has_camera_system=True,
                has_gps_tracking=True,
                status='active',
                current_location_id=locations[2].id,  # North Depot
                current_mileage=52000,
                engine_hours=1450.0,
                special_equipment='Root cutting attachment, industrial pump',
                notes='Heavy-duty truck for commercial jobs'
            ),
            Truck(
                truck_number='T-003',
                license_plate='ST003TX',
                make='Peterbilt',
                model='220',
                year=2018,
                color='Red',
                tank_capacity=1500,
                tank_material='fiberglass',
                num_compartments=1,
                pump_type='Jurop LC420',
                pump_cfm=350,
                hose_length=150,
                hose_diameter=3.0,
                has_hose_reel=False,
                has_pressure_washer=True,
                has_gps_tracking=False,
                status='maintenance',
                current_location_id=locations[0].id,  # Main Office
                current_mileage=78000,
                engine_hours=2100.0,
                notes='Compact truck for residential areas, currently in for maintenance'
            )
        ]
        
        for truck in trucks:
            db.session.add(truck)
        
        # Add sample team members
        team_members = [
            TeamMember(
                first_name='Mike',
                last_name='Johnson',
                employee_id='EMP001',
                phone_primary='(555) 111-2222',
                email='mike.johnson@truetank.com',
                home_street_address='123 Maple St',
                home_city='Anytown',
                home_state='TX',
                home_zip_code='12345',
                emergency_contact_name='Sarah Johnson',
                emergency_contact_phone='(555) 111-3333',
                emergency_contact_relationship='Spouse',
                position='Senior Technician',
                hire_date=datetime(2019, 3, 15).date(),
                employment_status='active',
                cdl_license=True,
                septic_certification=True,
                is_supervisor=True,
                can_operate_trucks=True,
                shift_start_time=datetime.strptime('07:00', '%H:%M').time(),
                shift_end_time=datetime.strptime('16:00', '%H:%M').time(),
                work_days='weekdays',
                notes='Lead technician, certified trainer'
            ),
            TeamMember(
                first_name='Sarah',
                last_name='Davis',
                employee_id='EMP002',
                phone_primary='(555) 222-3333',
                email='sarah.davis@truetank.com',
                home_street_address='456 Oak Ave',
                home_city='Somewhere',
                home_state='TX',
                home_zip_code='67890',
                emergency_contact_name='Tom Davis',
                emergency_contact_phone='(555) 222-4444',
                emergency_contact_relationship='Spouse',
                position='Technician',
                hire_date=datetime(2020, 8, 1).date(),
                employment_status='active',
                cdl_license=True,
                septic_certification=True,
                can_operate_trucks=True,
                shift_start_time=datetime.strptime('08:00', '%H:%M').time(),
                shift_end_time=datetime.strptime('17:00', '%H:%M').time(),
                work_days='weekdays',
                notes='Inspection specialist'
            ),
            TeamMember(
                first_name='Tom',
                last_name='Wilson',
                employee_id='EMP003',
                phone_primary='(555) 333-4444',
                email='tom.wilson@truetank.com',
                home_street_address='789 Pine Rd',
                home_city='Elsewhere',
                home_state='TX',
                home_zip_code='54321',
                emergency_contact_name='Lisa Wilson',
                emergency_contact_phone='(555) 333-5555',
                emergency_contact_relationship='Sister',
                position='Driver/Helper',
                hire_date=datetime(2021, 5, 10).date(),
                employment_status='active',
                cdl_license=True,
                septic_certification=False,
                can_operate_trucks=True,
                shift_start_time=datetime.strptime('06:00', '%H:%M').time(),
                shift_end_time=datetime.strptime('15:00', '%H:%M').time(),
                work_days='all',
                notes='Weekend coverage, working on certification'
            ),
            TeamMember(
                first_name='Carlos',
                last_name='Rodriguez',
                employee_id='EMP004',
                phone_primary='(555) 444-5555',
                email='carlos.rodriguez@truetank.com',
                home_street_address='321 Cedar Ln',
                home_city='Anytown',
                home_state='TX',
                home_zip_code='12347',
                emergency_contact_name='Maria Rodriguez',
                emergency_contact_phone='(555) 444-6666',
                emergency_contact_relationship='Wife',
                position='Technician',
                hire_date=datetime(2021, 9, 20).date(),
                employment_status='active',
                cdl_license=True,
                septic_certification=True,
                can_operate_trucks=True,
                shift_start_time=datetime.strptime('07:30', '%H:%M').time(),
                shift_end_time=datetime.strptime('16:30', '%H:%M').time(),
                work_days='weekdays',
                notes='Bilingual, handles Spanish-speaking customers'
            ),
            TeamMember(
                first_name='Jennifer',
                last_name='Brown',
                employee_id='EMP005',
                phone_primary='(555) 555-6666',
                email='jennifer.brown@truetank.com',
                home_street_address='654 Elm St',
                home_city='Somewhere',
                home_state='TX',
                home_zip_code='67891',
                emergency_contact_name='David Brown',
                emergency_contact_phone='(555) 555-7777',
                emergency_contact_relationship='Husband',
                position='Office Manager',
                hire_date=datetime(2018, 11, 5).date(),
                employment_status='active',
                cdl_license=False,
                septic_certification=False,
                can_operate_trucks=False,
                shift_start_time=datetime.strptime('08:00', '%H:%M').time(),
                shift_end_time=datetime.strptime('17:00', '%H:%M').time(),
                work_days='weekdays',
                notes='Handles scheduling and customer service'
            )
        ]
        
        for member in team_members:
            db.session.add(member)
        
        db.session.commit()
    
    # Now create customers and tickets
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
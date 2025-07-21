import os
import requests
from flask import Flask, render_template, request, jsonify
from models import db, Ticket, Customer, SepticSystem, ServiceHistory, Location, Truck, TeamMember, TruckTeamAssignment
from dotenv import load_dotenv
from datetime import datetime

# Import OpenAI at the top level
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False
    print("Warning: OpenAI module not available")

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///truetank.db')
print(f"Original DATABASE_URL: {database_url[:50]}..." if len(database_url) > 50 else f"Original DATABASE_URL: {database_url}")

# Fix PostgreSQL URL format for newer SQLAlchemy versions
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    print(f"Fixed DATABASE_URL: {database_url[:50]}..." if len(database_url) > 50 else f"Fixed DATABASE_URL: {database_url}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(f"SQLAlchemy URI configured successfully")

# Development vs Production configuration
if os.environ.get('FLASK_ENV') == 'development':
    app.config['DEBUG'] = True
else:
    app.config['DEBUG'] = False

# Initialize database
try:
    print("Initializing database...")
    db.init_app(app)
    print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    raise

# OpenRouteService configuration
OPENROUTE_API_KEY = os.environ.get('OPENROUTE_API_KEY')
OPENROUTE_BASE_URL = 'https://api.openrouteservice.org'

def geocode_address(address):
    """Convert address to coordinates using OpenRouteService geocoding"""
    if not OPENROUTE_API_KEY:
        print("Warning: OPENROUTE_API_KEY not configured")
        return None
    
    try:
        url = f"{OPENROUTE_BASE_URL}/geocode/search"
        params = {
            'api_key': OPENROUTE_API_KEY,
            'text': address,
            'size': 1,
            'layers': 'address'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"Geocoding response for '{address}': {data}")
        print(f"Response type: {type(data)}")
        print(f"Response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
        
        # Check if it's the OpenRouteService features format
        if data.get('features') and len(data['features']) > 0:
            coords = data['features'][0]['geometry']['coordinates']
            return {'longitude': coords[0], 'latitude': coords[1]}
        
        # Check if it's a direct lat/lng format
        elif data.get('lat') and data.get('lng'):
            return {'longitude': data.get('lng'), 'latitude': data.get('lat')}
        
        # Check if it's a direct latitude/longitude format  
        elif data.get('latitude') and data.get('longitude'):
            return {'longitude': data.get('longitude'), 'latitude': data.get('latitude')}
        
        print(f"No geocoding results found for '{address}'")
        return None
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
        return None

def calculate_drive_time(origin_address, destination_address):
    """Calculate drive time between two addresses in minutes"""
    if not OPENROUTE_API_KEY:
        print("Warning: OPENROUTE_API_KEY not configured")
        return None
    
    try:
        # First geocode both addresses
        print(f"Geocoding origin: '{origin_address}'")
        origin_coords = geocode_address(origin_address)
        print(f"Origin coords: {origin_coords}")
        
        print(f"Geocoding destination: '{destination_address}'")
        dest_coords = geocode_address(destination_address)
        print(f"Destination coords: {dest_coords}")
        
        if not origin_coords or not dest_coords:
            print(f"Could not geocode addresses: {origin_address} -> {destination_address}")
            return None
        
        # Calculate route
        url = f"{OPENROUTE_BASE_URL}/v2/directions/driving-car"
        headers = {
            'Authorization': OPENROUTE_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Handle both coordinate formats
        origin_lon = origin_coords.get('longitude') or origin_coords.get('lng')
        origin_lat = origin_coords.get('latitude') or origin_coords.get('lat')
        dest_lon = dest_coords.get('longitude') or dest_coords.get('lng')  
        dest_lat = dest_coords.get('latitude') or dest_coords.get('lat')
        
        print(f"Using coordinates: origin=[{origin_lon}, {origin_lat}], dest=[{dest_lon}, {dest_lat}]")
        
        data = {
            'coordinates': [
                [origin_lon, origin_lat],
                [dest_lon, dest_lat]
            ],
            'instructions': True,
            'elevation': True
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        if result['routes'] and len(result['routes']) > 0:
            route = result['routes'][0]
            
            # Extract all available data
            duration_minutes = route['summary']['duration'] / 60
            distance_km = route['summary']['distance'] / 1000
            
            # Get turn-by-turn instructions if available
            instructions = []
            if 'segments' in route:
                for segment in route['segments']:
                    if 'steps' in segment:
                        for step in segment['steps']:
                            instructions.append({
                                'instruction': step.get('instruction', ''),
                                'distance': round(step.get('distance', 0), 1),
                                'duration': round(step.get('duration', 0) / 60, 1),
                                'type': step.get('type', 0),
                                'name': step.get('name', ''),
                                'way_points': step.get('way_points', [])
                            })
            
            # Get route geometry (polyline) if available
            geometry = route.get('geometry', '')
            
            # Get elevation data if available
            elevation_data = None
            if 'elevation' in route:
                elevation_data = {
                    'ascent': route['elevation'].get('ascent', 0),
                    'descent': route['elevation'].get('descent', 0)
                }
            
            # Get bounds
            bbox = route.get('bbox', [])
            
            return {
                'duration_minutes': round(duration_minutes, 1),
                'distance_km': round(distance_km, 2),
                'origin_coords': {
                    'latitude': origin_lat,
                    'longitude': origin_lon
                },
                'dest_coords': {
                    'latitude': dest_lat,
                    'longitude': dest_lon
                },
                'instructions': instructions,
                'geometry': geometry,
                'bbox': bbox,
                'elevation': elevation_data,
                'warnings': route.get('warnings', []),
                'waypoints': route.get('way_points', [])
            }
        
        return None
    except Exception as e:
        print(f"Drive time calculation error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/job-board')
def job_board():
    trucks = Truck.query.filter_by(status='active').all()
    team_members = TeamMember.query.filter_by(employment_status='active').all()
    return render_template('job_board.html', trucks=trucks, team_members=team_members)

@app.route('/job-board-new')
def job_board_new():
    return render_template('job_board_new.html')

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

# AI Septic Estimator Test Route
@app.route('/ai-estimator')
def ai_estimator():
    return render_template('ai_estimator.html')

@app.route('/drive-time-calculator')
def drive_time_calculator():
    return render_template('drive_time_calculator.html')

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

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

@app.route('/api/job-board', methods=['GET'])
def get_job_board_data():
    from datetime import datetime, date
    
    # Get date parameter (default to today)
    date_str = request.args.get('date', date.today().isoformat())
    try:
        target_date = datetime.fromisoformat(date_str).date()
    except ValueError:
        target_date = date.today()
    
    # Get sort parameter for pending tickets
    sort_by = request.args.get('sort', 'oldest')
    
    # Get trucks
    trucks = Truck.query.filter_by(status='active').all()
    
    # Get pending tickets (only those not scheduled)
    pending_query = Ticket.query.filter(
        Ticket.scheduled_date.is_(None),
        Ticket.status == 'pending'
    )
    
    # Apply sorting
    if sort_by == 'oldest':
        pending_tickets = pending_query.order_by(Ticket.created_at.asc()).all()
    elif sort_by == 'due_date':
        pending_tickets = pending_query.order_by(Ticket.requested_service_date.asc().nullslast()).all()
    elif sort_by == 'priority':
        # Custom priority order: urgent, high, medium, low
        priority_order = db.case(
            (Ticket.priority == 'urgent', 1),
            (Ticket.priority == 'high', 2),
            (Ticket.priority == 'medium', 3),
            (Ticket.priority == 'low', 4),
            else_=5
        )
        pending_tickets = pending_query.order_by(priority_order).all()
    elif sort_by == 'customer':
        pending_tickets = pending_query.join(Customer).order_by(Customer.last_name, Customer.first_name).all()
    else:
        pending_tickets = pending_query.order_by(Ticket.created_at.asc()).all()
    
    # Get scheduled tickets for the target date, organized by truck
    scheduled_tickets = Ticket.query.filter(
        db.func.date(Ticket.scheduled_date) == target_date
    ).all()
    
    # Organize scheduled tickets by truck
    truck_schedules = {}
    for truck in trucks:
        truck_tickets = [t for t in scheduled_tickets if t.truck_id == truck.id]
        print(f"🚛 Before sort - Truck {truck.id}: {[(t.id, t.route_position) for t in truck_tickets]}")
        truck_tickets.sort(key=lambda x: x.route_position if x.route_position is not None else 999)  # Sort by route position
        print(f"🚛 After sort - Truck {truck.id}: {[(t.id, t.route_position) for t in truck_tickets]}")
        # Convert to dict with customer information
        truck_tickets_with_customer = []
        for ticket in truck_tickets:
            ticket_dict = ticket.to_dict()
            if ticket.customer:
                ticket_dict['customer_name'] = f"{ticket.customer.first_name} {ticket.customer.last_name}"
                ticket_dict['customer_address'] = f"{ticket.customer.street_address}, {ticket.customer.city}, {ticket.customer.state}"
            else:
                ticket_dict['customer_name'] = 'No customer'
                ticket_dict['customer_address'] = 'No address'
            truck_tickets_with_customer.append(ticket_dict)
        
        truck_schedules[str(truck.id)] = truck_tickets_with_customer
    
    # Get team assignments for the target date
    team_assignments = TruckTeamAssignment.query.filter_by(assignment_date=target_date).all()
    team_assignments_dict = {}
    for assignment in team_assignments:
        if assignment.team_member:  # Only include if there's actually a team member assigned
            team_assignments_dict[str(assignment.truck_id)] = {
                'team_member_id': assignment.team_member_id,
                'team_member_name': f"{assignment.team_member.first_name} {assignment.team_member.last_name}",
                'position': assignment.team_member.position
            }
    
    return jsonify({
        'date': target_date.isoformat(),
        'pending_tickets': [ticket.to_dict() for ticket in pending_tickets],
        'truck_schedules': truck_schedules,
        'trucks': [{'id': t.id, 'truck_number': t.truck_number, 'make': t.make, 'model': t.model} for t in trucks],
        'team_assignments': team_assignments_dict,
        'sort_by': sort_by
    })

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
        
        # Ensure ticket_id is an integer for comparison
        ticket_id = int(ticket_id)
        
        # Get the ticket being moved
        ticket = Ticket.query.get_or_404(ticket_id)
        old_status = ticket.status
        old_position = ticket.column_position
        
        print(f"Column reorder: ticket {ticket_id} from {old_status}:{old_position} to {new_status}:{new_position}")
        
        # Get all tickets in the target status/column, ordered by column_position
        all_column_tickets = Ticket.query.filter(
            Ticket.status == new_status
        ).order_by(Ticket.column_position).all()
        
        # Remove the ticket from its current position
        tickets_without_moved = [t for t in all_column_tickets if t.id != ticket_id]
        
        # Create the final ordered list by inserting the moved ticket at the new position
        final_positions = tickets_without_moved.copy()
        final_positions.insert(new_position, ticket)
        
        # Update the ticket's status
        ticket.status = new_status
        
        # Assign sequential column_position values (0, 1, 2, etc.)
        for i, t in enumerate(final_positions):
            t.column_position = i
            
        print(f"Column reorder complete: ticket {ticket_id} now at {new_status}:{ticket.column_position}")
        
        db.session.commit()
        return jsonify({'success': True, 'ticket': ticket.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/reorder-route', methods=['POST'])
def reorder_route():
    try:
        from datetime import datetime
        data = request.get_json()
        
        ticket_id = data.get('ticket_id')
        truck_id = data.get('truck_id')
        new_position = data.get('route_position', 0)
        scheduled_date = data.get('scheduled_date')
        
        print(f"Backend received: ticket_id={ticket_id}, new_position={new_position}")
        
        # Ensure ticket_id is an integer for comparison
        ticket_id = int(ticket_id)
        
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Get all tickets for this truck on this date (including the one being moved)
        target_date = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00')).date()
        all_truck_tickets = Ticket.query.filter(
            Ticket.truck_id == truck_id,
            db.func.date(Ticket.scheduled_date) == target_date
        ).order_by(Ticket.route_position).all()
        
        # Get the old position of the ticket being moved
        old_position = ticket.route_position
        print(f"Old position: {old_position}, New position: {new_position}")
        
        # Remove the ticket from its current position and reorder
        tickets_without_moved = [t for t in all_truck_tickets if t.id != ticket_id]
        print(f"Total tickets: {len(all_truck_tickets)}, Without moved: {len(tickets_without_moved)}")
        
        # Create the final ordered list by inserting the moved ticket at the new position
        final_positions = tickets_without_moved.copy()
        final_positions.insert(new_position, ticket)
        
        # Assign sequential route_position values (0, 1, 2, etc.)
        for i, t in enumerate(final_positions):
            t.route_position = i
            print(f"Setting ticket {t.id} to route_position {i}")
            
        print(f"Moved ticket {ticket.id} from position {old_position} to position {new_position}")
        print(f"Final positions: {[(t.id, t.route_position) for t in final_positions]}")
        
        db.session.commit()
        return jsonify({'success': True, 'ticket': ticket.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/assign', methods=['POST'])
def assign_ticket():
    try:
        from datetime import datetime
        data = request.get_json()
        
        ticket_id = data.get('ticket_id')
        truck_id = data.get('truck_id')
        scheduled_date = data.get('scheduled_date')
        route_position = data.get('route_position', 0)
        
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Update truck assignment
        if truck_id:
            ticket.truck_id = int(truck_id)
        else:
            ticket.truck_id = None
            
        # Update scheduled date
        if scheduled_date:
            try:
                ticket.scheduled_date = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
                ticket.status = 'scheduled'
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        else:
            ticket.scheduled_date = None
            ticket.status = 'pending'
            
        # Update route position
        ticket.route_position = route_position
        
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

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer_api(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer.to_dict())
    except Exception as e:
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
@app.route('/api/septic-systems', methods=['GET'])
def get_septic_systems():
    customer_id = request.args.get('customer_id')
    if customer_id:
        systems = SepticSystem.query.filter_by(customer_id=customer_id).all()
    else:
        systems = SepticSystem.query.all()
    
    return jsonify([{
        'id': system.id,
        'customer_id': system.customer_id,
        'system_type': system.system_type,
        'tank_size': system.tank_size,
        'tank_material': system.tank_material,
        'num_compartments': system.num_compartments,
        'system_condition': system.system_condition,
        'access_notes': system.access_notes
    } for system in systems])

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

@app.route('/api/trucks/<int:truck_id>', methods=['PUT'])
def update_truck_api(truck_id):
    try:
        truck = Truck.query.get_or_404(truck_id)
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
        
        # Update truck fields
        truck.truck_number = data.get('truck_number', truck.truck_number)
        truck.license_plate = data.get('license_plate', truck.license_plate)
        truck.vin = data.get('vin', truck.vin)
        truck.make = data.get('make', truck.make)
        truck.model = data.get('model', truck.model)
        truck.year = safe_int(data.get('year')) or truck.year
        truck.color = data.get('color', truck.color)
        truck.tank_capacity = safe_int(data.get('tank_capacity')) or truck.tank_capacity
        truck.tank_material = data.get('tank_material', truck.tank_material)
        truck.num_compartments = safe_int(data.get('num_compartments')) or truck.num_compartments
        truck.pump_type = data.get('pump_type', truck.pump_type)
        truck.pump_cfm = safe_int(data.get('pump_cfm')) or truck.pump_cfm
        truck.hose_length = safe_int(data.get('hose_length')) or truck.hose_length
        truck.hose_diameter = safe_float(data.get('hose_diameter')) or truck.hose_diameter
        truck.has_hose_reel = safe_bool(data.get('has_hose_reel')) if 'has_hose_reel' in data else truck.has_hose_reel
        truck.has_pressure_washer = safe_bool(data.get('has_pressure_washer')) if 'has_pressure_washer' in data else truck.has_pressure_washer
        truck.has_camera_system = safe_bool(data.get('has_camera_system')) if 'has_camera_system' in data else truck.has_camera_system
        truck.has_gps_tracking = safe_bool(data.get('has_gps_tracking')) if 'has_gps_tracking' in data else truck.has_gps_tracking
        truck.special_equipment = data.get('special_equipment', truck.special_equipment)
        truck.status = data.get('status', truck.status)
        truck.current_location_id = safe_int(data.get('current_location_id')) or truck.current_location_id
        truck.current_mileage = safe_int(data.get('current_mileage')) or truck.current_mileage
        truck.engine_hours = safe_float(data.get('engine_hours')) or truck.engine_hours
        truck.purchase_date = purchase_date or truck.purchase_date
        truck.last_maintenance = last_maintenance or truck.last_maintenance
        truck.next_maintenance_due = next_maintenance_due or truck.next_maintenance_due
        truck.maintenance_interval_miles = safe_int(data.get('maintenance_interval_miles')) or truck.maintenance_interval_miles
        truck.maintenance_interval_hours = safe_int(data.get('maintenance_interval_hours')) or truck.maintenance_interval_hours
        truck.insurance_company = data.get('insurance_company', truck.insurance_company)
        truck.insurance_policy = data.get('insurance_policy', truck.insurance_policy)
        truck.insurance_expiry = insurance_expiry or truck.insurance_expiry
        truck.registration_expiry = registration_expiry or truck.registration_expiry
        truck.dot_number = data.get('dot_number', truck.dot_number)
        truck.purchase_price = safe_float(data.get('purchase_price')) or truck.purchase_price
        truck.current_value = safe_float(data.get('current_value')) or truck.current_value
        truck.notes = data.get('notes', truck.notes)
        
        db.session.commit()
        
        return jsonify({
            'id': truck.id,
            'truck_number': truck.truck_number,
            'make': truck.make,
            'model': truck.model,
            'year': truck.year,
            'status': truck.status
        })
        
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

@app.route('/admin/init-database', methods=['POST'])
def init_database_endpoint():
    """Initialize database tables via web endpoint"""
    try:
        db.create_all()
        return jsonify({'success': True, 'message': 'Database tables created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/import-sample-data', methods=['POST'])
def import_sample_data_endpoint():
    """Import sample data via web endpoint"""
    try:
        # First ensure tables exist
        db.create_all()
        
        from import_sample_data import import_data
        
        # Use the latest sample data file
        filename = 'sample_data_export_20250711_084627.json'
        success = import_data(filename)
        
        if success:
            return jsonify({
                'success': True, 
                'message': 'Sample data imported successfully',
                'records': {
                    'locations': 4,
                    'team_members': 4,
                    'trucks': 4,
                    'customers': 25,
                    'septic_systems': 18,
                    'tickets': 39
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Import failed'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def init_database():
    """Initialize database tables"""
    with app.app_context():
        try:
            # Test connection first
            db.engine.execute('SELECT 1')
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            print("⚠️  App will continue without database initialization")

# Legacy sample data creation (commented out to avoid import issues)
"""
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
"""

# AI Septic Estimator API
@app.route('/api/property-lookup', methods=['POST'])
def property_lookup():
    """Look up property data using free APIs"""
    try:
        data = request.get_json()
        address = data.get('address', '')
        
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        # Step 1: Geocode the address using free service
        geocode_data = geocode_address(address)
        if not geocode_data:
            return jsonify({'error': 'Could not geocode address'}), 400
        
        # Step 2: Get census data for the area
        census_data = get_census_data(geocode_data['lat'], geocode_data['lng'])
        
        # Step 3: Estimate property details using geocoding + census data
        property_data = estimate_property_from_location(address, geocode_data, census_data)
        
        return jsonify(property_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def geocode_address(address):
    """Geocode address using Nominatim (OpenStreetMap) - free service"""
    try:
        import requests
        import urllib.parse
        
        # Nominatim is free and doesn't require API key
        encoded_address = urllib.parse.quote(address)
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_address}&countrycodes=us&limit=1"
        
        headers = {
            'User-Agent': 'TrueTank-SepticService/1.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            results = response.json()
            if results:
                result = results[0]
                return {
                    'lat': float(result['lat']),
                    'lng': float(result['lon']),
                    'display_name': result['display_name'],
                    'address_type': result.get('type', 'unknown')
                }
        return None
        
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def get_census_data(lat, lng):
    """Get census data for coordinates using free Census API"""
    try:
        import requests
        
        # US Census Geocoding API - free, no key required
        url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            'x': lng,
            'y': lat,
            'benchmark': 'Public_AR_Current',
            'vintage': 'Current_Current',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'geographies' in data['result']:
                geographies = data['result']['geographies']
                
                # Extract useful census data
                census_info = {}
                
                # Get census tract info
                if 'Census Tracts' in geographies:
                    tract = geographies['Census Tracts'][0]
                    census_info['tract'] = tract.get('TRACT', '')
                    census_info['state'] = tract.get('STATE', '')
                    census_info['county'] = tract.get('COUNTY', '')
                
                # Get place info (city/town)
                if 'Incorporated Places' in geographies:
                    place = geographies['Incorporated Places'][0]
                    census_info['city'] = place.get('NAME', '')
                    census_info['place_type'] = place.get('LSAD', '')
                
                return census_info
                
        return {}
        
    except Exception as e:
        print(f"Census data error: {e}")
        return {}

def estimate_property_from_location(address, geocode_data, census_data):
    """Estimate property characteristics from location data"""
    import random
    
    # Parse address components
    address_parts = address.split(',')
    
    # Estimate based on location characteristics
    # Urban vs Rural estimation
    display_name = geocode_data.get('display_name', '').lower()
    is_urban = any(word in display_name for word in ['city', 'urban', 'downtown', 'metro'])
    is_rural = any(word in display_name for word in ['rural', 'county', 'township', 'farm'])
    
    # Property size estimation
    if is_urban:
        property_size = round(random.uniform(0.15, 0.75), 2)  # Smaller urban lots
    elif is_rural:
        property_size = round(random.uniform(1.0, 5.0), 2)    # Larger rural lots
    else:
        property_size = round(random.uniform(0.25, 2.0), 2)   # Suburban
    
    # Bedroom estimation based on area type
    if is_urban:
        bedrooms = random.choice([1, 2, 2, 3, 3, 4])  # Smaller urban homes
    elif is_rural:
        bedrooms = random.choice([3, 3, 4, 4, 5, 6])  # Larger rural homes
    else:
        bedrooms = random.choice([2, 3, 3, 3, 4, 4])  # Suburban standard
    
    # Bathroom estimation
    bathrooms = min(bedrooms, random.choice([1, 2, 2, 2.5, 3]))
    if bedrooms >= 4:
        bathrooms = random.choice([2, 2.5, 3, 3.5])
    
    # Year built estimation (newer in urban areas)
    if is_urban:
        year_built = random.randint(1980, 2020)
    elif is_rural:
        year_built = random.randint(1950, 2010)
    else:
        year_built = random.randint(1970, 2020)
    
    # Occupant estimation
    occupants = min(bedrooms + random.choice([0, 1, 2]), 8)
    
    # Property type estimation
    if is_urban:
        property_type = random.choice(['single_family', 'townhouse', 'condo', 'multi_family'])
    elif is_rural:
        property_type = random.choice(['single_family', 'single_family', 'farmhouse', 'manufactured'])
    else:
        property_type = random.choice(['single_family', 'single_family', 'townhouse'])
    
    # Soil type estimation based on region
    state = census_data.get('state', '')
    if state in ['48']:  # Texas
        soil_type = random.choice(['clay', 'clay_loam', 'sandy_clay'])
    elif state in ['12']:  # Florida
        soil_type = random.choice(['sandy', 'sandy_loam'])
    elif state in ['17', '18', '19']:  # Midwest
        soil_type = random.choice(['loam', 'clay_loam', 'silt_loam'])
    else:
        soil_type = random.choice(['clay', 'sandy', 'clay_loam', 'loam', 'sandy_loam'])
    
    # Water table estimation
    if 'coastal' in display_name or 'beach' in display_name:
        water_table = random.choice(['high', 'high', 'normal'])
    elif 'hill' in display_name or 'mountain' in display_name:
        water_table = random.choice(['low', 'normal'])
    else:
        water_table = random.choice(['normal', 'normal', 'high', 'low'])
    
    property_data = {
        'address': address,
        'property_size': property_size,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'year_built': year_built,
        'occupants': occupants,
        'property_type': property_type,
        'soil_type': soil_type,
        'water_table': water_table,
        'lat': geocode_data['lat'],
        'lng': geocode_data['lng'],
        'city': census_data.get('city', 'Unknown'),
        'county': census_data.get('county', 'Unknown'),
        'state': census_data.get('state', 'Unknown'),
        'data_source': 'geocoding_estimation'
    }
    
    return property_data

@app.route('/api/ai-estimate', methods=['POST'])
def ai_estimate():
    """Generate AI-powered septic system estimate"""
    try:
        # Check if OpenAI is available
        if not openai_available:
            return jsonify({'error': 'OpenAI service is not available'}), 503
            
        data = request.get_json()
        property_data = data.get('property_data', {})
        
        # Create enhanced prompt with location-specific considerations
        address = property_data.get('address', 'Unknown')
        
        # Extract state/region info for location-specific recommendations
        location_guidance = ""
        if 'TX' in address or 'Texas' in address:
            location_guidance = "\nTexas-specific considerations: Clay soil common, high water table in coastal areas, minimum 1000-gallon requirement statewide."
        elif 'FL' in address or 'Florida' in address:
            location_guidance = "\nFlorida-specific considerations: Sandy soil common, high water table near coast, advanced treatment often required."
        elif 'CA' in address or 'California' in address:
            location_guidance = "\nCalifornia-specific considerations: Strict environmental regulations, advanced treatment systems often required."
        
        prompt = f"""As a septic system expert, estimate the specifications for a septic system based on these property details, location, and industry standards:

Property Details:
- Address: {address}
- Property Size: {property_data.get('property_size', 'Unknown')} acres
- Customer Type: {property_data.get('customer_type', 'residential')}
- Bedrooms: {property_data.get('bedrooms', 3)}
- Bathrooms: {property_data.get('bathrooms', 2)}
- Year Built: {property_data.get('year_built', 'Unknown')}
- Estimated Occupants: {property_data.get('occupants', 4)}
- Property Type: {property_data.get('property_type', 'single_family')}
- Soil Conditions: {property_data.get('soil_type', 'unknown')}
- Water Table: {property_data.get('water_table', 'normal')}{location_guidance}

Industry Rules of Thumb:
1. Tank Size: 150 gallons per bedroom minimum, typically 1000-1500 gallons for residential
2. For 3-bedroom home: minimum 1000 gallons
3. For 4-bedroom home: minimum 1250 gallons
4. For 5+ bedrooms: add 250 gallons per additional bedroom
5. High water table or clay soil may require larger tank or advanced treatment
6. Compartments: 1-2 for standard residential, 2-3 for larger systems
7. Material: Concrete is standard, fiberglass/plastic for difficult access
8. Commercial properties typically need 25-50% larger systems
9. Consider local regulations and soil conditions for the specific address

Based on the property address, local conditions, and industry standards, provide estimates for:
1. Tank Size (gallons) - consider local requirements
2. System Type (conventional, aerobic, advanced treatment, etc.)
3. Tank Material (concrete, fiberglass, plastic)
4. Number of Compartments
5. Pump Frequency (months)
6. Installation considerations specific to this location
7. Estimated lifespan

Format your response as JSON with these exact keys: tank_size, system_type, tank_material, num_compartments, pump_frequency_months, installation_notes, estimated_lifespan_years"""

        # Call OpenAI API
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-1",
            messages=[
                {"role": "system", "content": "You are a septic system expert who provides accurate estimates based on property data and industry standards."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse the AI response
        import json
        ai_response = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Find JSON content in the response
            start = ai_response.find('{')
            end = ai_response.rfind('}') + 1
            if start >= 0 and end > start:
                estimate_data = json.loads(ai_response[start:end])
            else:
                # Fallback if JSON not found
                estimate_data = {
                    'tank_size': 1000,
                    'system_type': 'conventional',
                    'tank_material': 'concrete',
                    'num_compartments': 2,
                    'pump_frequency_months': 36,
                    'installation_notes': 'Standard residential installation',
                    'estimated_lifespan_years': 20
                }
        except:
            # Fallback estimate based on bedrooms
            bedrooms = property_data.get('bedrooms', 3)
            estimate_data = {
                'tank_size': max(1000, bedrooms * 250),
                'system_type': 'conventional',
                'tank_material': 'concrete',
                'num_compartments': 2,
                'pump_frequency_months': 36,
                'installation_notes': f'Standard {bedrooms}-bedroom residential system',
                'estimated_lifespan_years': 20
            }
        
        # Add property data to the response
        estimate_data['property_data'] = property_data
        estimate_data['ai_confidence'] = 'high' if 'bedrooms' in property_data else 'medium'
        
        return jsonify(estimate_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Team Assignment API
@app.route('/api/team-assignments', methods=['POST'])
def save_team_assignment():
    """Save or update team assignment for a truck on a specific date"""
    try:
        data = request.get_json()
        truck_id = data.get('truck_id')
        team_member_id = data.get('team_member_id')  # Can be None to remove assignment
        assignment_date_str = data.get('assignment_date')
        
        if not truck_id or not assignment_date_str:
            return jsonify({'error': 'truck_id and assignment_date are required'}), 400
        
        # Parse date
        try:
            assignment_date = datetime.fromisoformat(assignment_date_str).date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Check if assignment already exists
        existing = TruckTeamAssignment.query.filter_by(
            truck_id=truck_id,
            assignment_date=assignment_date
        ).first()
        
        if existing:
            if team_member_id:
                # Update existing assignment
                existing.team_member_id = team_member_id
                existing.updated_at = datetime.utcnow()
            else:
                # Remove assignment
                db.session.delete(existing)
        else:
            if team_member_id:
                # Create new assignment
                assignment = TruckTeamAssignment(
                    truck_id=truck_id,
                    team_member_id=team_member_id,
                    assignment_date=assignment_date
                )
                db.session.add(assignment)
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# NEW JOB BOARD API (Clean rebuild)
# ============================================================================

@app.route('/api/job-board/tickets', methods=['GET'])
def get_job_board_tickets():
    """Get all tickets organized by status for the kanban board"""
    try:
        # Define the status columns we want to show
        statuses = ['pending', 'assigned', 'in-progress', 'completed']
        
        result = {}
        
        for status in statuses:
            # Get tickets for this status, ordered by column_position
            tickets = Ticket.query.filter(
                Ticket.status == status
            ).order_by(Ticket.column_position.asc().nullslast()).all()
            
            # Convert to dict format
            result[status] = [ticket.to_dict() for ticket in tickets]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-board/move', methods=['POST'])
def move_job_board_ticket():
    """Move a ticket to a new status and position"""
    try:
        data = request.get_json()
        
        ticket_id = int(data.get('ticket_id'))
        new_status = data.get('new_status')
        new_position = int(data.get('new_position', 0))
        
        print(f"Job Board Move: ticket {ticket_id} to {new_status} at position {new_position}")
        
        # Get the ticket being moved
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Get all tickets in the target status, ordered by column_position
        all_status_tickets = Ticket.query.filter(
            Ticket.status == new_status
        ).order_by(Ticket.column_position.asc().nullslast()).all()
        
        # Remove the moved ticket from the list (if it was already in this status)
        tickets_without_moved = [t for t in all_status_tickets if t.id != ticket_id]
        
        # Create the final ordered list by inserting the moved ticket at the new position
        final_positions = tickets_without_moved.copy()
        final_positions.insert(new_position, ticket)
        
        # Update the ticket's status
        ticket.status = new_status
        
        # Assign sequential column_position values (0, 1, 2, etc.)
        for i, t in enumerate(final_positions):
            t.column_position = i
            
        print(f"Job Board Move Complete: ticket {ticket_id} now at {new_status}:{ticket.column_position}")
        
        db.session.commit()
        return jsonify({'success': True, 'ticket': ticket.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in move_job_board_ticket: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-board/create', methods=['POST'])
def create_job_board_ticket():
    """Create a new ticket for the job board"""
    try:
        data = request.get_json()
        
        # Generate next job ID
        latest_ticket = Ticket.query.order_by(Ticket.id.desc()).first()
        if latest_ticket and latest_ticket.job_id.startswith('TT'):
            latest_num = int(latest_ticket.job_id[2:])
            next_num = latest_num + 1
        else:
            next_num = 1
        
        job_id = f"TT{str(next_num).zfill(8)}"
        
        # Create new ticket
        ticket = Ticket(
            job_id=job_id,
            customer_name=data.get('customer_name', '[New Customer]'),
            service_type=data.get('service_type', 'Septic Service'),
            status='pending',
            priority=data.get('priority', 'medium'),
            service_description=data.get('description', 'New septic service job'),
            column_position=0  # Always add at top of pending column
        )
        
        # Shift other pending tickets down
        Ticket.query.filter(Ticket.status == 'pending').update(
            {Ticket.column_position: Ticket.column_position + 1}
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({'success': True, 'ticket': ticket.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating ticket: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-board/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_job_board_ticket(ticket_id):
    """Delete a ticket from the job board"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        old_status = ticket.status
        old_position = ticket.column_position
        
        # Delete the ticket
        db.session.delete(ticket)
        
        # Shift remaining tickets in the same status up to fill the gap
        if old_position is not None:
            Ticket.query.filter(
                Ticket.status == old_status,
                Ticket.column_position > old_position
            ).update({Ticket.column_position: Ticket.column_position - 1})
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting ticket: {e}")
        return jsonify({'error': str(e)}), 500

# Drive Time API Endpoints
@app.route('/api/drive-time', methods=['POST'])
def calculate_drive_time_api():
    """Calculate drive time between two addresses"""
    try:
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        
        if not origin or not destination:
            return jsonify({'error': 'Origin and destination addresses required'}), 400
        
        result = calculate_drive_time(origin, destination)
        
        if result:
            return jsonify({
                'success': True,
                'duration_minutes': result['duration_minutes'],
                'distance_km': result['distance_km'],
                'origin_coords': result['origin_coords'],
                'dest_coords': result['dest_coords'],
                'instructions': result['instructions'],
                'geometry': result['geometry'],
                'bbox': result['bbox'],
                'elevation': result['elevation'],
                'warnings': result['warnings'],
                'waypoints': result['waypoints']
            })
        else:
            return jsonify({'error': 'Could not calculate drive time'}), 400
            
    except Exception as e:
        print(f"Drive time API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/route-optimization/<int:truck_id>/<date>', methods=['GET'])
def optimize_truck_route(truck_id, date):
    """Calculate optimized route with drive times for a truck's schedule"""
    try:
        from datetime import datetime
        
        # Parse date
        target_date = datetime.fromisoformat(date).date()
        
        # Get truck tickets for the date
        tickets = Ticket.query.filter(
            Ticket.truck_id == truck_id,
            db.func.date(Ticket.scheduled_date) == target_date
        ).order_by(Ticket.route_position).all()
        
        if not tickets:
            return jsonify({'success': True, 'route': [], 'total_drive_time': 0})
        
        # Get truck's starting location (we'll use first customer for now)
        truck = Truck.query.get_or_404(truck_id)
        
        # Calculate drive times between consecutive stops
        route_with_times = []
        total_drive_time = 0
        
        for i, ticket in enumerate(tickets):
            if not ticket.customer:
                continue
                
            customer_address = f"{ticket.customer.street_address}, {ticket.customer.city}, {ticket.customer.state}"
            
            ticket_data = {
                'ticket_id': ticket.id,
                'job_id': ticket.job_id,
                'customer_name': f"{ticket.customer.first_name} {ticket.customer.last_name}",
                'address': customer_address,
                'service_type': ticket.service_type,
                'estimated_duration': ticket.estimated_duration or 60,
                'route_position': ticket.route_position
            }
            
            # Calculate drive time to this stop
            if i > 0:
                prev_customer = tickets[i-1].customer
                if prev_customer:
                    prev_address = f"{prev_customer.street_address}, {prev_customer.city}, {prev_customer.state}"
                    drive_result = calculate_drive_time(prev_address, customer_address)
                    
                    if drive_result:
                        ticket_data['drive_time_from_previous'] = drive_result['duration_minutes']
                        ticket_data['distance_from_previous'] = drive_result['distance_km']
                        total_drive_time += drive_result['duration_minutes']
                    else:
                        ticket_data['drive_time_from_previous'] = None
                        ticket_data['distance_from_previous'] = None
            else:
                ticket_data['drive_time_from_previous'] = 0
                ticket_data['distance_from_previous'] = 0
            
            route_with_times.append(ticket_data)
        
        return jsonify({
            'success': True,
            'truck_id': truck_id,
            'date': date,
            'route': route_with_times,
            'total_drive_time': round(total_drive_time, 1),
            'total_stops': len(route_with_times)
        })
        
    except Exception as e:
        print(f"Route optimization error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/update-all-dates', methods=['POST'])
def update_all_ticket_dates():
    """Update all tickets to be scheduled for today and tomorrow"""
    try:
        from datetime import timedelta
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        tickets = Ticket.query.all()
        total_tickets = len(tickets)
        
        for i, ticket in enumerate(tickets):
            if i < total_tickets // 2:
                ticket.scheduled_date = datetime.combine(today, datetime.min.time())
            else:
                ticket.scheduled_date = datetime.combine(tomorrow, datetime.min.time())
            
            if ticket.route_position is None:
                ticket.route_position = i % 10
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Updated {total_tickets} tickets',
            'today_count': total_tickets // 2,
            'tomorrow_count': total_tickets - (total_tickets // 2)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database when app starts (commented out during debugging)
    # init_database()
    
    port = int(os.environ.get('PORT', 5555))
    app.run(debug=True, host='0.0.0.0', port=port)
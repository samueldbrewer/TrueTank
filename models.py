from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class ServiceType(Enum):
    PUMPING = "Septic Pumping"
    INSPECTION = "Septic Inspection"
    REPAIR = "Septic Repair"
    INSTALLATION = "Septic Installation"
    MAINTENANCE = "Preventive Maintenance"
    EMERGENCY = "Emergency Service"
    CLEANING = "Septic Cleaning"
    ROOTER = "Line Cleaning/Rooter"
    GREASE_TRAP = "Grease Trap Service"
    LIFT_STATION = "Lift Station Service"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Status(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on-hold"

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(100), nullable=True)
    customer_type = db.Column(db.String(20), nullable=False, default='residential')  # residential, commercial
    
    # Contact Info
    email = db.Column(db.String(100), nullable=True)
    phone_primary = db.Column(db.String(20), nullable=True)
    phone_secondary = db.Column(db.String(20), nullable=True)
    
    # Address
    street_address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    county = db.Column(db.String(100), nullable=True)
    
    # Billing Address (if different)
    billing_street_address = db.Column(db.String(200), nullable=True)
    billing_city = db.Column(db.String(100), nullable=True)
    billing_state = db.Column(db.String(50), nullable=True)
    billing_zip_code = db.Column(db.String(20), nullable=True)
    
    # Business Info
    preferred_contact_method = db.Column(db.String(20), nullable=True, default='phone')
    payment_terms = db.Column(db.String(50), nullable=True, default='net_30')
    tax_exempt = db.Column(db.Boolean, default=False)
    tax_exempt_number = db.Column(db.String(50), nullable=True)
    
    # Preferences
    service_reminders = db.Column(db.Boolean, default=True)
    marketing_emails = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='customer', lazy=True)
    septic_systems = db.relationship('SepticSystem', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.first_name} {self.last_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'customer_type': self.customer_type,
            'email': self.email,
            'phone_primary': self.phone_primary,
            'phone_secondary': self.phone_secondary,
            'street_address': self.street_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'county': self.county,
            'billing_street_address': self.billing_street_address,
            'billing_city': self.billing_city,
            'billing_state': self.billing_state,
            'billing_zip_code': self.billing_zip_code,
            'preferred_contact_method': self.preferred_contact_method,
            'payment_terms': self.payment_terms,
            'tax_exempt': self.tax_exempt,
            'tax_exempt_number': self.tax_exempt_number,
            'service_reminders': self.service_reminders,
            'marketing_emails': self.marketing_emails,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SepticSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    
    # System Details
    system_type = db.Column(db.String(50), nullable=True)  # conventional, aerobic, etc.
    tank_size = db.Column(db.Integer, nullable=True)  # gallons
    tank_material = db.Column(db.String(50), nullable=True)  # concrete, plastic, fiberglass
    num_compartments = db.Column(db.Integer, nullable=True)
    
    # Installation Info
    install_date = db.Column(db.Date, nullable=True)
    permit_number = db.Column(db.String(50), nullable=True)
    installer_company = db.Column(db.String(100), nullable=True)
    
    # Maintenance Schedule
    pump_frequency_months = db.Column(db.Integer, nullable=True, default=36)
    last_pumped = db.Column(db.Date, nullable=True)
    next_pump_due = db.Column(db.Date, nullable=True)
    
    # System Status
    system_condition = db.Column(db.String(20), nullable=True, default='good')
    needs_repair = db.Column(db.Boolean, default=False)
    repair_notes = db.Column(db.Text, nullable=True)
    
    # Location Info
    access_notes = db.Column(db.Text, nullable=True)
    gps_coordinates = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='septic_system', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    job_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    septic_system_id = db.Column(db.Integer, db.ForeignKey('septic_system.id'), nullable=True)
    
    # Service Details
    service_type = db.Column(db.String(50), nullable=True)
    service_description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False, default='medium')
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime, nullable=True)
    requested_service_date = db.Column(db.Date, nullable=True)  # When customer wants service by
    estimated_duration = db.Column(db.Integer, nullable=True)  # minutes
    route_position = db.Column(db.Integer, nullable=True)
    column_position = db.Column(db.Integer, nullable=True, default=0)  # Position within kanban column
    
    # Assignment
    assigned_technician = db.Column(db.String(100), nullable=True)
    assigned_crew = db.Column(db.String(200), nullable=True)
    
    # Pricing
    estimated_cost = db.Column(db.Float, nullable=True)
    actual_cost = db.Column(db.Float, nullable=True)
    parts_cost = db.Column(db.Float, nullable=True)
    labor_cost = db.Column(db.Float, nullable=True)
    disposal_cost = db.Column(db.Float, nullable=True)
    
    # Service Details
    gallons_pumped = db.Column(db.Integer, nullable=True)
    waste_type = db.Column(db.String(50), nullable=True)
    disposal_location = db.Column(db.String(100), nullable=True)
    trip_ticket_number = db.Column(db.String(50), nullable=True)
    
    # Conditions Found
    tank_condition = db.Column(db.String(50), nullable=True)
    sludge_level = db.Column(db.String(50), nullable=True)
    scum_level = db.Column(db.String(50), nullable=True)
    liquid_level = db.Column(db.String(50), nullable=True)
    
    # Issues and Recommendations
    issues_found = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    follow_up_needed = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date, nullable=True)
    follow_up_notes = db.Column(db.Text, nullable=True)
    
    # Completion Info
    work_performed = db.Column(db.Text, nullable=True)
    materials_used = db.Column(db.Text, nullable=True)
    customer_signature = db.Column(db.Text, nullable=True)  # base64 encoded
    technician_signature = db.Column(db.Text, nullable=True)  # base64 encoded
    
    # Payment Info
    payment_method = db.Column(db.String(50), nullable=True)
    payment_status = db.Column(db.String(20), nullable=True, default='pending')
    invoice_number = db.Column(db.String(50), nullable=True)
    
    # Time Tracking
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    travel_time = db.Column(db.Integer, nullable=True)  # minutes
    work_time = db.Column(db.Integer, nullable=True)  # minutes
    
    # Notes and Communication
    office_notes = db.Column(db.Text, nullable=True)
    technician_notes = db.Column(db.Text, nullable=True)
    customer_notes = db.Column(db.Text, nullable=True)
    internal_notes = db.Column(db.Text, nullable=True)
    
    # Compliance and Regulations
    permit_required = db.Column(db.Boolean, default=False)
    permit_number = db.Column(db.String(50), nullable=True)
    inspection_required = db.Column(db.Boolean, default=False)
    inspection_passed = db.Column(db.Boolean, nullable=True)
    
    # Equipment Used
    equipment_used = db.Column(db.Text, nullable=True)
    truck_number = db.Column(db.String(20), nullable=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'), nullable=True)
    
    # GPS and Photos
    gps_location = db.Column(db.String(100), nullable=True)
    photo_paths = db.Column(db.Text, nullable=True)  # JSON array of photo paths
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Ticket {self.job_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'customer_id': self.customer_id,
            'septic_system_id': self.septic_system_id,
            'service_type': self.service_type,
            'service_description': self.service_description,
            'priority': self.priority,
            'status': self.status,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'requested_service_date': self.requested_service_date.isoformat() if self.requested_service_date else None,
            'estimated_duration': self.estimated_duration,
            'column_position': self.column_position,
            'assigned_technician': self.assigned_technician,
            'assigned_crew': self.assigned_crew,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'parts_cost': self.parts_cost,
            'labor_cost': self.labor_cost,
            'disposal_cost': self.disposal_cost,
            'gallons_pumped': self.gallons_pumped,
            'waste_type': self.waste_type,
            'disposal_location': self.disposal_location,
            'trip_ticket_number': self.trip_ticket_number,
            'tank_condition': self.tank_condition,
            'sludge_level': self.sludge_level,
            'scum_level': self.scum_level,
            'liquid_level': self.liquid_level,
            'issues_found': self.issues_found,
            'recommendations': self.recommendations,
            'follow_up_needed': self.follow_up_needed,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'work_performed': self.work_performed,
            'materials_used': self.materials_used,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'invoice_number': self.invoice_number,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'travel_time': self.travel_time,
            'work_time': self.work_time,
            'office_notes': self.office_notes,
            'technician_notes': self.technician_notes,
            'customer_notes': self.customer_notes,
            'internal_notes': self.internal_notes,
            'permit_required': self.permit_required,
            'permit_number': self.permit_number,
            'inspection_required': self.inspection_required,
            'inspection_passed': self.inspection_passed,
            'equipment_used': self.equipment_used,
            'truck_number': self.truck_number,
            'gps_location': self.gps_location,
            'photo_paths': self.photo_paths,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            
            # Include customer info if available
            'customer_name': f"{self.customer.first_name} {self.customer.last_name}" if self.customer else None,
            'customer_phone': self.customer.phone_primary if self.customer else None,
            'customer_address': f"{self.customer.street_address}, {self.customer.city}, {self.customer.state}" if self.customer and self.customer.street_address else None,
        }

class ServiceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    septic_system_id = db.Column(db.Integer, db.ForeignKey('septic_system.id'), nullable=True)
    
    # Service Summary
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    technician = db.Column(db.String(100), nullable=False)
    
    # Key Metrics
    gallons_pumped = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float, nullable=True)
    
    # Quick Notes
    summary = db.Column(db.Text, nullable=True)
    next_service_due = db.Column(db.Date, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    ticket = db.relationship('Ticket', backref='service_history_entry')
    customer = db.relationship('Customer', backref='service_history')
    septic_system = db.relationship('SepticSystem', backref='service_history')

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Location Details
    name = db.Column(db.String(100), nullable=False)  # "Main Office", "Storage Facility A", etc.
    location_type = db.Column(db.String(50), nullable=False, default='office')  # office, storage, depot
    
    # Address Information
    street_address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    county = db.Column(db.String(100), nullable=True)
    
    # Location Specifications
    gps_coordinates = db.Column(db.String(50), nullable=True)
    access_notes = db.Column(db.Text, nullable=True)
    capacity_notes = db.Column(db.Text, nullable=True)  # How many trucks can be stored
    security_info = db.Column(db.Text, nullable=True)  # Gate codes, security details
    
    # Contact Information
    contact_person = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Operational Details
    is_active = db.Column(db.Boolean, default=True)
    hours_of_operation = db.Column(db.String(200), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trucks = db.relationship('Truck', backref='storage_location', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.name}>'

class Truck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Vehicle Identification
    truck_number = db.Column(db.String(20), unique=True, nullable=False)
    license_plate = db.Column(db.String(20), nullable=True)
    vin = db.Column(db.String(50), nullable=True)
    
    # Vehicle Details
    make = db.Column(db.String(50), nullable=True)
    model = db.Column(db.String(50), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    color = db.Column(db.String(30), nullable=True)
    
    # Tank Specifications
    tank_capacity = db.Column(db.Integer, nullable=True)  # gallons
    tank_material = db.Column(db.String(50), nullable=True, default='aluminum')  # aluminum, steel, fiberglass
    num_compartments = db.Column(db.Integer, nullable=True, default=1)
    
    # Equipment Details
    pump_type = db.Column(db.String(100), nullable=True)  # Masport, Fruitland, Jurop, NVE
    pump_cfm = db.Column(db.Integer, nullable=True)  # cubic feet per minute
    hose_length = db.Column(db.Integer, nullable=True)  # feet
    hose_diameter = db.Column(db.Float, nullable=True)  # inches
    has_hose_reel = db.Column(db.Boolean, default=False)
    
    # Additional Equipment
    has_pressure_washer = db.Column(db.Boolean, default=False)
    has_camera_system = db.Column(db.Boolean, default=False)
    has_gps_tracking = db.Column(db.Boolean, default=False)
    special_equipment = db.Column(db.Text, nullable=True)  # Additional equipment notes
    
    # Operational Status
    status = db.Column(db.String(20), nullable=False, default='active')  # active, maintenance, out_of_service
    current_location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    
    # Maintenance Tracking
    current_mileage = db.Column(db.Integer, nullable=True)
    engine_hours = db.Column(db.Float, nullable=True)
    last_maintenance = db.Column(db.Date, nullable=True)
    next_maintenance_due = db.Column(db.Date, nullable=True)
    maintenance_interval_miles = db.Column(db.Integer, nullable=True, default=5000)
    maintenance_interval_hours = db.Column(db.Integer, nullable=True, default=250)
    
    # Insurance & Registration
    insurance_company = db.Column(db.String(100), nullable=True)
    insurance_policy = db.Column(db.String(50), nullable=True)
    insurance_expiry = db.Column(db.Date, nullable=True)
    registration_expiry = db.Column(db.Date, nullable=True)
    dot_number = db.Column(db.String(20), nullable=True)
    
    # Financial Information
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_price = db.Column(db.Float, nullable=True)
    current_value = db.Column(db.Float, nullable=True)
    
    # Notes
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='truck', lazy=True, foreign_keys='Ticket.truck_id')
    
    def __repr__(self):
        return f'<Truck {self.truck_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'truck_number': self.truck_number,
            'license_plate': self.license_plate,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'tank_capacity': self.tank_capacity,
            'pump_type': self.pump_type,
            'status': self.status,
            'current_mileage': self.current_mileage,
            'engine_hours': self.engine_hours,
            'storage_location': self.storage_location.name if self.storage_location else None,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance_due': self.next_maintenance_due.isoformat() if self.next_maintenance_due else None
        }

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=True)
    
    # Contact Information
    phone_primary = db.Column(db.String(20), nullable=True)
    phone_secondary = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    
    # Home Address
    home_street_address = db.Column(db.String(200), nullable=True)
    home_city = db.Column(db.String(100), nullable=True)
    home_state = db.Column(db.String(50), nullable=True)
    home_zip_code = db.Column(db.String(20), nullable=True)
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    emergency_contact_relationship = db.Column(db.String(50), nullable=True)
    
    # Employment Information
    position = db.Column(db.String(100), nullable=True)  # Technician, Driver, Supervisor, etc.
    department = db.Column(db.String(50), nullable=True, default='field_service')
    hire_date = db.Column(db.Date, nullable=True)
    employment_status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, terminated
    
    # Certifications & Licenses
    cdl_license = db.Column(db.Boolean, default=False)
    cdl_expiry = db.Column(db.Date, nullable=True)
    septic_certification = db.Column(db.Boolean, default=False)
    septic_cert_expiry = db.Column(db.Date, nullable=True)
    other_certifications = db.Column(db.Text, nullable=True)
    
    # Work Schedule
    shift_start_time = db.Column(db.Time, nullable=True)
    shift_end_time = db.Column(db.Time, nullable=True)
    work_days = db.Column(db.String(20), nullable=True, default='weekdays')  # weekdays, weekends, all
    
    # Performance & Notes
    notes = db.Column(db.Text, nullable=True)
    is_supervisor = db.Column(db.Boolean, default=False)
    can_operate_trucks = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Note: assigned_technician in Ticket is currently a string field
    
    def __repr__(self):
        return f'<TeamMember {self.first_name} {self.last_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'employee_id': self.employee_id,
            'position': self.position,
            'phone_primary': self.phone_primary,
            'email': self.email,
            'home_address': f"{self.home_street_address}, {self.home_city}, {self.home_state}" if self.home_street_address else None,
            'employment_status': self.employment_status,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'cdl_license': self.cdl_license,
            'septic_certification': self.septic_certification
        }

class TruckTeamAssignment(db.Model):
    __tablename__ = 'truck_team_assignment'
    
    id = db.Column(db.Integer, primary_key=True)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'), nullable=False)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=True)  # Null = no assignment
    assignment_date = db.Column(db.Date, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    truck = db.relationship('Truck', backref='team_assignments')
    team_member = db.relationship('TeamMember', backref='truck_assignments')
    
    # Unique constraint - one assignment per truck per date
    __table_args__ = (db.UniqueConstraint('truck_id', 'assignment_date', name='unique_truck_assignment_per_date'),)
    
    def __repr__(self):
        return f'<TruckTeamAssignment Truck:{self.truck_id} Member:{self.team_member_id} Date:{self.assignment_date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'truck_id': self.truck_id,
            'team_member_id': self.team_member_id,
            'assignment_date': self.assignment_date.isoformat() if self.assignment_date else None,
            'truck_number': self.truck.truck_number if self.truck else None,
            'team_member_name': f"{self.team_member.first_name} {self.team_member.last_name}" if self.team_member else None
        }
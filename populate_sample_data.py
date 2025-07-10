#!/usr/bin/env python3
"""
Sample Data Population Script for TrueTank
Creates realistic sample data for Pewee Valley, KY area
"""

import os
import sys
from datetime import datetime, date, timedelta
from random import choice, randint, uniform
from faker import Faker

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import (
    db, Customer, SepticSystem, Ticket, TeamMember, Truck, Location, 
    TruckTeamAssignment, ServiceHistory
)

# Initialize Faker with US locale
fake = Faker('en_US')

def clear_all_data():
    """Clear all existing data from the database"""
    print("🗑️  Clearing existing data...")
    
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
    print("✅ Database cleared and tables recreated")

def create_locations():
    """Create office and storage locations in Pewee Valley, KY area"""
    print("🏢 Creating locations...")
    
    locations = [
        {
            'name': 'TrueTank Main Office',
            'location_type': 'office',
            'street_address': '123 Main Street',
            'city': 'Pewee Valley',
            'state': 'KY',
            'zip_code': '40056',
            'county': 'Oldham',
            'gps_coordinates': '38.3148, -85.4569',
            'contact_person': 'Sarah Johnson',
            'phone_number': '(502) 241-5000',
            'is_active': True,
            'hours_of_operation': 'Mon-Fri 7:00 AM - 5:00 PM',
            'access_notes': 'Main entrance, visitor parking available',
            'capacity_notes': 'Administrative offices, customer service'
        },
        {
            'name': 'TrueTank Equipment Storage',
            'location_type': 'storage',
            'street_address': '456 Industrial Drive',
            'city': 'Pewee Valley',
            'state': 'KY',
            'zip_code': '40056',
            'county': 'Oldham',
            'gps_coordinates': '38.3125, -85.4580',
            'contact_person': 'Mike Thompson',
            'phone_number': '(502) 241-5001',
            'is_active': True,
            'hours_of_operation': '24/7 Access for Employees',
            'access_notes': 'Gate code: 2580, Key card required',
            'capacity_notes': 'Can store 8 trucks, parts warehouse',
            'security_info': 'Fenced lot, security cameras, gate code 2580'
        },
        {
            'name': 'Louisville Satellite Depot',
            'location_type': 'depot',
            'street_address': '789 Commerce Way',
            'city': 'Louisville',
            'state': 'KY',
            'zip_code': '40223',
            'county': 'Jefferson',
            'gps_coordinates': '38.2542, -85.5907',
            'contact_person': 'David Rodriguez',
            'phone_number': '(502) 459-7500',
            'is_active': True,
            'hours_of_operation': 'Mon-Sat 6:00 AM - 6:00 PM',
            'access_notes': 'Loading dock on east side',
            'capacity_notes': 'Emergency equipment storage, 3 truck capacity'
        },
        {
            'name': 'Oldham County Service Center',
            'location_type': 'depot',
            'street_address': '321 County Road 42',
            'city': 'LaGrange',
            'state': 'KY',
            'zip_code': '40031',
            'county': 'Oldham',
            'gps_coordinates': '38.4048, -85.3816',
            'is_active': True,
            'hours_of_operation': 'Mon-Fri 7:00 AM - 4:00 PM',
            'capacity_notes': 'Backup location, 2 truck parking'
        }
    ]
    
    created_locations = []
    for loc_data in locations:
        location = Location(**loc_data)
        db.session.add(location)
        created_locations.append(location)
    
    db.session.commit()
    print(f"✅ Created {len(created_locations)} locations")
    return created_locations

def create_team_members():
    """Create 4 team members"""
    print("👥 Creating team members...")
    
    team_data = [
        {
            'first_name': 'James',
            'last_name': 'Wilson',
            'employee_id': 'TT001',
            'position': 'Senior Technician',
            'department': 'field_service',
            'hire_date': date(2020, 3, 15),
            'employment_status': 'active',
            'phone_primary': '(502) 555-0101',
            'email': 'james.wilson@truetank.com',
            'home_street_address': '234 Oak Street',
            'home_city': 'Pewee Valley',
            'home_state': 'KY',
            'home_zip_code': '40056',
            'emergency_contact_name': 'Lisa Wilson',
            'emergency_contact_phone': '(502) 555-0102',
            'emergency_contact_relationship': 'Spouse',
            'cdl_license': True,
            'cdl_expiry': date(2025, 8, 15),
            'septic_certification': True,
            'septic_cert_expiry': date(2025, 12, 31),
            'other_certifications': 'OSHA 30-Hour, Hazmat Certified',
            'is_supervisor': True,
            'can_operate_trucks': True,
            'notes': 'Lead technician, excellent customer service skills'
        },
        {
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'employee_id': 'TT002',
            'position': 'Pump Technician',
            'department': 'field_service',
            'hire_date': date(2021, 7, 20),
            'employment_status': 'active',
            'phone_primary': '(502) 555-0201',
            'email': 'maria.garcia@truetank.com',
            'home_street_address': '567 Maple Avenue',
            'home_city': 'Louisville',
            'home_state': 'KY',
            'home_zip_code': '40223',
            'emergency_contact_name': 'Carlos Garcia',
            'emergency_contact_phone': '(502) 555-0202',
            'emergency_contact_relationship': 'Husband',
            'cdl_license': True,
            'cdl_expiry': date(2026, 2, 28),
            'septic_certification': True,
            'septic_cert_expiry': date(2025, 6, 30),
            'other_certifications': 'Pump Maintenance Certified',
            'can_operate_trucks': True,
            'notes': 'Specializes in pump repairs and maintenance'
        },
        {
            'first_name': 'Robert',
            'last_name': 'Smith',
            'employee_id': 'TT003',
            'position': 'Field Technician',
            'department': 'field_service',
            'hire_date': date(2022, 1, 10),
            'employment_status': 'active',
            'phone_primary': '(502) 555-0301',
            'email': 'robert.smith@truetank.com',
            'home_street_address': '890 Pine Road',
            'home_city': 'LaGrange',
            'home_state': 'KY',
            'home_zip_code': '40031',
            'emergency_contact_name': 'Nancy Smith',
            'emergency_contact_phone': '(502) 555-0302',
            'emergency_contact_relationship': 'Wife',
            'cdl_license': True,
            'cdl_expiry': date(2025, 11, 15),
            'septic_certification': True,
            'septic_cert_expiry': date(2025, 9, 30),
            'can_operate_trucks': True,
            'notes': 'Reliable worker, good with customer interactions'
        },
        {
            'first_name': 'Ashley',
            'last_name': 'Johnson',
            'employee_id': 'TT004',
            'position': 'Junior Technician',
            'department': 'field_service',
            'hire_date': date(2023, 6, 5),
            'employment_status': 'active',
            'phone_primary': '(502) 555-0401',
            'email': 'ashley.johnson@truetank.com',
            'home_street_address': '456 Elm Street',
            'home_city': 'Crestwood',
            'home_state': 'KY',
            'home_zip_code': '40014',
            'emergency_contact_name': 'Michael Johnson',
            'emergency_contact_phone': '(502) 555-0402',
            'emergency_contact_relationship': 'Father',
            'cdl_license': True,
            'cdl_expiry': date(2026, 4, 20),
            'septic_certification': True,
            'septic_cert_expiry': date(2025, 10, 31),
            'can_operate_trucks': True,
            'notes': 'Recent hire, eager to learn, good mechanical aptitude'
        }
    ]
    
    created_members = []
    for member_data in team_data:
        member = TeamMember(**member_data)
        db.session.add(member)
        created_members.append(member)
    
    db.session.commit()
    print(f"✅ Created {len(created_members)} team members")
    return created_members

def create_trucks(locations):
    """Create truck fleet"""
    print("🚛 Creating truck fleet...")
    
    truck_data = [
        {
            'truck_number': 'TT-01',
            'license_plate': 'KY-7892',
            'vin': '1FDXF46P67EB12345',
            'make': 'Ford',
            'model': 'F-450',
            'year': 2020,
            'color': 'White',
            'tank_capacity': 3000,
            'tank_material': 'aluminum',
            'num_compartments': 2,
            'pump_type': 'Masport',
            'pump_cfm': 850,
            'hose_length': 200,
            'hose_diameter': 4.0,
            'has_hose_reel': True,
            'has_pressure_washer': True,
            'has_camera_system': True,
            'has_gps_tracking': True,
            'special_equipment': 'Hydraulic lift gate, LED work lights',
            'status': 'active',
            'current_location_id': locations[1].id,  # Equipment Storage
            'current_mileage': 45230,
            'engine_hours': 2150.5,
            'last_maintenance': date(2024, 11, 15),
            'next_maintenance_due': date(2025, 2, 15),
            'insurance_company': 'State Farm Commercial',
            'insurance_policy': 'SF-COM-789456',
            'insurance_expiry': date(2025, 6, 30),
            'registration_expiry': date(2025, 4, 30),
            'purchase_date': date(2020, 2, 15),
            'purchase_price': 125000.00,
            'current_value': 85000.00,
            'notes': 'Primary truck, excellent condition'
        },
        {
            'truck_number': 'TT-02',
            'license_plate': 'KY-7893',
            'vin': '1FDXF46P67EB12346',
            'make': 'Ford',
            'model': 'F-550',
            'year': 2019,
            'color': 'Blue',
            'tank_capacity': 4000,
            'tank_material': 'aluminum',
            'num_compartments': 3,
            'pump_type': 'Fruitland',
            'pump_cfm': 950,
            'hose_length': 250,
            'hose_diameter': 4.0,
            'has_hose_reel': True,
            'has_pressure_washer': True,
            'has_camera_system': False,
            'has_gps_tracking': True,
            'special_equipment': 'Backup camera, tool box package',
            'status': 'active',
            'current_location_id': locations[1].id,
            'current_mileage': 62150,
            'engine_hours': 3240.0,
            'last_maintenance': date(2024, 10, 20),
            'next_maintenance_due': date(2025, 1, 20),
            'insurance_company': 'State Farm Commercial',
            'insurance_policy': 'SF-COM-789457',
            'insurance_expiry': date(2025, 6, 30),
            'registration_expiry': date(2025, 3, 31),
            'purchase_date': date(2019, 5, 10),
            'purchase_price': 115000.00,
            'current_value': 75000.00,
            'notes': 'Heavy duty truck for large jobs'
        },
        {
            'truck_number': 'TT-03',
            'license_plate': 'KY-7894',
            'vin': '1FDXF46P67EB12347',
            'make': 'International',
            'model': 'DuraStar',
            'year': 2021,
            'color': 'White',
            'tank_capacity': 2500,
            'tank_material': 'steel',
            'num_compartments': 2,
            'pump_type': 'NVE',
            'pump_cfm': 750,
            'hose_length': 175,
            'hose_diameter': 3.5,
            'has_hose_reel': False,
            'has_pressure_washer': True,
            'has_camera_system': True,
            'has_gps_tracking': True,
            'special_equipment': 'Compact design for residential areas',
            'status': 'active',
            'current_location_id': locations[2].id,  # Louisville Depot
            'current_mileage': 28750,
            'engine_hours': 1450.0,
            'last_maintenance': date(2024, 12, 1),
            'next_maintenance_due': date(2025, 3, 1),
            'insurance_company': 'State Farm Commercial',
            'insurance_policy': 'SF-COM-789458',
            'insurance_expiry': date(2025, 6, 30),
            'registration_expiry': date(2025, 5, 31),
            'purchase_date': date(2021, 8, 20),
            'purchase_price': 135000.00,
            'current_value': 105000.00,
            'notes': 'Newest truck, ideal for residential work'
        },
        {
            'truck_number': 'TT-04',
            'license_plate': 'KY-7895',
            'vin': '1FDXF46P67EB12348',
            'make': 'Freightliner',
            'model': 'Business Class M2',
            'year': 2018,
            'color': 'Yellow',
            'tank_capacity': 3500,
            'tank_material': 'aluminum',
            'num_compartments': 2,
            'pump_type': 'Jurop',
            'pump_cfm': 900,
            'hose_length': 225,
            'hose_diameter': 4.0,
            'has_hose_reel': True,
            'has_pressure_washer': False,
            'has_camera_system': False,
            'has_gps_tracking': True,
            'special_equipment': 'Heavy duty pump, commercial grade',
            'status': 'maintenance',
            'current_location_id': locations[1].id,
            'current_mileage': 78920,
            'engine_hours': 4120.5,
            'last_maintenance': date(2024, 12, 10),
            'next_maintenance_due': date(2024, 12, 20),
            'insurance_company': 'State Farm Commercial',
            'insurance_policy': 'SF-COM-789459',
            'insurance_expiry': date(2025, 6, 30),
            'registration_expiry': date(2025, 2, 28),
            'purchase_date': date(2018, 3, 15),
            'purchase_price': 105000.00,
            'current_value': 55000.00,
            'notes': 'In maintenance - transmission service'
        }
    ]
    
    created_trucks = []
    for truck_data in truck_data:
        truck = Truck(**truck_data)
        db.session.add(truck)
        created_trucks.append(truck)
    
    db.session.commit()
    print(f"✅ Created {len(created_trucks)} trucks")
    return created_trucks

def create_customers():
    """Create customers in Pewee Valley, KY area"""
    print("👨‍👩‍👧‍👦 Creating customers...")
    
    # Kentucky cities near Pewee Valley
    ky_cities = [
        ('Pewee Valley', '40056', 'Oldham'),
        ('Louisville', '40223', 'Jefferson'),
        ('Louisville', '40222', 'Jefferson'),
        ('LaGrange', '40031', 'Oldham'),
        ('Crestwood', '40014', 'Oldham'),
        ('Buckner', '40010', 'Oldham'),
        ('Prospect', '40059', 'Jefferson'),
        ('Goshen', '40026', 'Oldham'),
        ('Ballardsville', '40025', 'Oldham'),
    ]
    
    customer_types = ['residential', 'commercial']
    
    created_customers = []
    
    for i in range(25):  # Create 25 customers
        city, zip_code, county = choice(ky_cities)
        customer_type = choice(customer_types)
        
        if customer_type == 'commercial':
            # Commercial customer
            company_names = [
                f"{fake.company()} Restaurant",
                f"{fake.company()} Manufacturing",
                f"{fake.company()} Offices",
                f"{fake.company()} Medical Center",
                f"{fake.company()} Shopping Center",
                f"{fake.company()} Auto Sales"
            ]
            
            customer_data = {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'company_name': choice(company_names),
                'customer_type': 'commercial',
                'email': fake.company_email(),
                'phone_primary': fake.phone_number(),
                'street_address': fake.street_address(),
                'city': city,
                'state': 'KY',
                'zip_code': zip_code,
                'county': county,
                'preferred_contact_method': choice(['phone', 'email']),
                'payment_terms': choice(['net_30', 'net_15', 'due_on_receipt']),
                'tax_exempt': choice([True, False]),
                'service_reminders': True,
                'marketing_emails': choice([True, False])
            }
        else:
            # Residential customer
            customer_data = {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'customer_type': 'residential',
                'email': fake.email(),
                'phone_primary': fake.phone_number(),
                'phone_secondary': fake.phone_number() if choice([True, False]) else None,
                'street_address': fake.street_address(),
                'city': city,
                'state': 'KY',
                'zip_code': zip_code,
                'county': county,
                'preferred_contact_method': 'phone',
                'payment_terms': 'due_on_receipt',
                'service_reminders': True,
                'marketing_emails': choice([True, False])
            }
        
        customer = Customer(**customer_data)
        db.session.add(customer)
        created_customers.append(customer)
    
    db.session.commit()
    print(f"✅ Created {len(created_customers)} customers")
    return created_customers

def create_septic_systems(customers):
    """Create septic systems for customers"""
    print("🏠 Creating septic systems...")
    
    system_types = ['conventional', 'aerobic', 'advanced_treatment', 'chamber']
    tank_materials = ['concrete', 'plastic', 'fiberglass']
    tank_sizes = [750, 1000, 1250, 1500, 2000, 2500, 3000]
    conditions = ['excellent', 'good', 'fair', 'poor']
    
    created_systems = []
    
    for customer in customers:
        # 80% of customers have septic systems
        if randint(1, 100) <= 80:
            # Commercial customers might have larger systems
            if customer.customer_type == 'commercial':
                tank_size = choice([2000, 2500, 3000, 4000, 5000])
                system_type = choice(['conventional', 'advanced_treatment'])
            else:
                tank_size = choice(tank_sizes)
                system_type = choice(system_types)
            
            # Generate installation date (1-15 years ago)
            install_date = fake.date_between(start_date=date(2010, 1, 1), end_date=date(2023, 12, 31))
            
            # Generate last pumped date (1-4 years ago)
            last_pumped = fake.date_between(start_date=date(2021, 1, 1), end_date=date(2024, 6, 1))
            
            # Calculate next pump due based on frequency
            pump_frequency = choice([24, 36, 48]) if customer.customer_type == 'residential' else choice([12, 18, 24])
            next_pump_due = last_pumped.replace(year=last_pumped.year + (pump_frequency // 12))
            
            system_data = {
                'customer_id': customer.id,
                'system_type': system_type,
                'tank_size': tank_size,
                'tank_material': choice(tank_materials),
                'num_compartments': choice([1, 2, 3]),
                'install_date': install_date,
                'permit_number': f"OC-{randint(1000, 9999)}-{install_date.year}",
                'installer_company': choice([
                    'Kentucky Septic Solutions',
                    'Oldham County Septic',
                    'Blue Grass Septic Systems',
                    'Louisville Septic Services'
                ]),
                'pump_frequency_months': pump_frequency,
                'last_pumped': last_pumped,
                'next_pump_due': next_pump_due,
                'system_condition': choice(conditions),
                'needs_repair': choice([True, False]) if choice(conditions) in ['fair', 'poor'] else False,
                'access_notes': choice([
                    'Tank located behind house, accessible from driveway',
                    'System in front yard, 20 feet from road',
                    'Pump chamber near garage, easy access',
                    'Tank under deck - may need deck board removal',
                    'Located in wooded area, follow flagged path',
                    'Near property line, coordinate with neighbor'
                ]),
                'gps_coordinates': f"{uniform(38.2, 38.5):.4f}, {uniform(-85.7, -85.2):.4f}"
            }
            
            if system_data['needs_repair']:
                system_data['repair_notes'] = choice([
                    'Baffle needs replacement',
                    'Outlet filter requires cleaning',
                    'Pump chamber pump not working properly',
                    'Distribution box needs leveling',
                    'Effluent filter needs replacement'
                ])
            
            system = SepticSystem(**system_data)
            db.session.add(system)
            created_systems.append(system)
    
    db.session.commit()
    print(f"✅ Created {len(created_systems)} septic systems")
    return created_systems

def create_tickets(customers, septic_systems, trucks):
    """Create 20 tickets with various statuses"""
    print("🎫 Creating tickets...")
    
    service_types = [
        'Septic Pumping', 'Septic Inspection', 'Septic Repair',
        'Septic Installation', 'Preventive Maintenance', 'Emergency Service',
        'Septic Cleaning', 'Line Cleaning/Rooter', 'Grease Trap Service'
    ]
    
    priorities = ['low', 'medium', 'high', 'urgent']
    statuses = ['pending', 'scheduled', 'in-progress', 'completed']
    
    # Team member names for assignment
    technicians = ['James Wilson', 'Maria Garcia', 'Robert Smith', 'Ashley Johnson']
    
    created_tickets = []
    
    for i in range(20):
        customer = choice(customers)
        
        # Try to find a septic system for this customer
        customer_systems = [s for s in septic_systems if s.customer_id == customer.id]
        septic_system = choice(customer_systems) if customer_systems else None
        
        service_type = choice(service_types)
        status = choice(statuses)
        priority = choice(priorities)
        
        # Generate dates based on status
        if status == 'completed':
            completed_date = fake.date_between(start_date=date(2024, 10, 1), end_date=date(2024, 12, 15))
            scheduled_date = fake.date_time_between(start_date=completed_date, end_date=completed_date)
            created_date = scheduled_date - timedelta(days=randint(1, 7))
        elif status in ['scheduled', 'in-progress']:
            scheduled_date = fake.date_time_between(start_date=date(2024, 12, 16), end_date=date(2025, 1, 15))
            created_date = scheduled_date - timedelta(days=randint(1, 5))
            completed_date = None
        else:  # pending
            scheduled_date = None
            completed_date = None
            created_date = fake.date_time_between(start_date=date(2024, 12, 1), end_date=datetime.now())
        
        # Generate costs based on service type
        if 'Pumping' in service_type:
            estimated_cost = uniform(200, 400)
        elif 'Inspection' in service_type:
            estimated_cost = uniform(150, 250)
        elif 'Repair' in service_type:
            estimated_cost = uniform(300, 800)
        elif 'Installation' in service_type:
            estimated_cost = uniform(2000, 5000)
        else:
            estimated_cost = uniform(150, 500)
        
        ticket_data = {
            'job_id': f"TT{datetime.now().year}{str(i+1).zfill(4)}",
            'customer_id': customer.id,
            'septic_system_id': septic_system.id if septic_system else None,
            'service_type': service_type,
            'service_description': f"{service_type} for {customer.first_name} {customer.last_name}",
            'priority': priority,
            'status': status,
            'scheduled_date': scheduled_date,
            'requested_service_date': fake.date_between(start_date=date.today(), end_date=date.today() + timedelta(days=30)),
            'estimated_duration': choice([60, 90, 120, 150, 180, 240]),
            'assigned_technician': choice(technicians) if status != 'pending' else None,
            'truck_number': choice([t.truck_number for t in trucks if t.status == 'active']) if status != 'pending' else None,
            'estimated_cost': round(estimated_cost, 2),
            'created_at': created_date,
            'completed_at': completed_date
        }
        
        # Add completion details for completed tickets
        if status == 'completed':
            ticket_data.update({
                'actual_cost': round(estimated_cost * uniform(0.9, 1.1), 2),
                'labor_cost': round(estimated_cost * 0.7, 2),
                'parts_cost': round(estimated_cost * 0.2, 2),
                'disposal_cost': round(estimated_cost * 0.1, 2),
                'gallons_pumped': randint(800, 3000) if 'Pumping' in service_type else None,
                'waste_type': 'domestic',
                'disposal_location': 'Oldham County Waste Treatment Plant',
                'tank_condition': choice(['excellent', 'good', 'fair']),
                'work_performed': f"Completed {service_type.lower()} service. System functioning properly.",
                'payment_status': choice(['paid', 'pending']),
                'office_notes': 'Customer satisfied with service',
                'technician_notes': 'No issues encountered during service'
            })
        
        ticket = Ticket(**ticket_data)
        db.session.add(ticket)
        created_tickets.append(ticket)
    
    db.session.commit()
    print(f"✅ Created {len(created_tickets)} tickets")
    return created_tickets

def create_team_assignments(trucks, team_members):
    """Create team assignments for trucks"""
    print("👥 Creating team assignments...")
    
    assignments = []
    today = date.today()
    
    # Create assignments for the past week and next week
    for days_offset in range(-7, 8):
        assignment_date = today + timedelta(days=days_offset)
        
        # Only assign to active trucks
        active_trucks = [t for t in trucks if t.status == 'active']
        
        for truck in active_trucks:
            # 90% chance of assignment on weekdays, 30% on weekends
            if assignment_date.weekday() < 5:  # Monday-Friday
                assign_probability = 0.9
            else:  # Weekend
                assign_probability = 0.3
            
            if uniform(0, 1) < assign_probability:
                assignment = TruckTeamAssignment(
                    truck_id=truck.id,
                    team_member_id=choice(team_members).id,
                    assignment_date=assignment_date
                )
                db.session.add(assignment)
                assignments.append(assignment)
    
    db.session.commit()
    print(f"✅ Created {len(assignments)} team assignments")
    return assignments

def main():
    """Main function to populate all sample data"""
    print("🚀 Starting TrueTank sample data population for Pewee Valley, KY")
    print("=" * 60)
    
    # Clear existing data
    clear_all_data()
    
    with app.app_context():
        # Create all sample data
        locations = create_locations()
        team_members = create_team_members()
        trucks = create_trucks(locations)
        customers = create_customers()
        septic_systems = create_septic_systems(customers)
        tickets = create_tickets(customers, septic_systems, trucks)
        assignments = create_team_assignments(trucks, team_members)
        
        print("=" * 60)
        print("✅ Sample data population completed successfully!")
        print(f"📊 Summary:")
        print(f"   • {len(locations)} Locations")
        print(f"   • {len(team_members)} Team Members")
        print(f"   • {len(trucks)} Trucks")
        print(f"   • {len(customers)} Customers")
        print(f"   • {len(septic_systems)} Septic Systems")
        print(f"   • {len(tickets)} Tickets")
        print(f"   • {len(assignments)} Team Assignments")
        print("🏁 Ready to test TrueTank!")

if __name__ == "__main__":
    main()
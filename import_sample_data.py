#!/usr/bin/env python3
"""
Import sample data to Railway database
"""

import json
import os
import sys
from datetime import datetime, date

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Customer, SepticSystem, TeamMember, Truck, Location, Ticket

def import_data(filename):
    """Import sample data from JSON file to database"""
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return False
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    with app.app_context():
        print("🗑️  Clearing existing data...")
        
        # Clear existing data in correct order (respecting foreign keys)
        Ticket.query.delete()
        SepticSystem.query.delete()
        Customer.query.delete()
        Truck.query.delete()
        TeamMember.query.delete()
        Location.query.delete()
        
        db.session.commit()
        print("  ✅ Existing data cleared")
        
        # Import Locations
        print("\n📍 Importing locations...")
        created_locations = []
        for loc_data in data['locations']:
            location = Location(
                name=loc_data['name'],
                location_type=loc_data['location_type'],
                street_address=loc_data['street_address'],
                city=loc_data['city'],
                state=loc_data['state'],
                zip_code=loc_data['zip_code'],
                county=loc_data.get('county'),
                gps_coordinates=loc_data.get('gps_coordinates'),
                contact_person=loc_data.get('contact_person'),
                phone_number=loc_data.get('phone_number'),
                is_active=loc_data.get('is_active', True),
                hours_of_operation=loc_data.get('hours_of_operation'),
                access_notes=loc_data.get('access_notes'),
                capacity_notes=loc_data.get('capacity_notes'),
                security_info=loc_data.get('security_info')
            )
            db.session.add(location)
            created_locations.append(location)
        
        db.session.commit()
        print(f"  ✅ Imported {len(created_locations)} locations")
        
        # Import Team Members
        print("\n👥 Importing team members...")
        created_members = []
        for member_data in data['team_members']:
            member = TeamMember(
                first_name=member_data['first_name'],
                last_name=member_data['last_name'],
                employee_id=member_data.get('employee_id'),
                position=member_data.get('position'),
                department=member_data.get('department'),
                hire_date=datetime.fromisoformat(member_data['hire_date']).date() if member_data.get('hire_date') else None,
                employment_status=member_data.get('employment_status', 'active'),
                phone_primary=member_data.get('phone_primary'),
                email=member_data.get('email'),
                home_street_address=member_data.get('home_street_address'),
                home_city=member_data.get('home_city'),
                home_state=member_data.get('home_state'),
                home_zip_code=member_data.get('home_zip_code'),
                emergency_contact_name=member_data.get('emergency_contact_name'),
                emergency_contact_phone=member_data.get('emergency_contact_phone'),
                emergency_contact_relationship=member_data.get('emergency_contact_relationship'),
                cdl_license=member_data.get('cdl_license', False),
                cdl_expiry=datetime.fromisoformat(member_data['cdl_expiry']).date() if member_data.get('cdl_expiry') else None,
                septic_certification=member_data.get('septic_certification', False),
                septic_cert_expiry=datetime.fromisoformat(member_data['septic_cert_expiry']).date() if member_data.get('septic_cert_expiry') else None,
                other_certifications=member_data.get('other_certifications'),
                is_supervisor=member_data.get('is_supervisor', False),
                can_operate_trucks=member_data.get('can_operate_trucks', True),
                notes=member_data.get('notes')
            )
            db.session.add(member)
            created_members.append(member)
        
        db.session.commit()
        print(f"  ✅ Imported {len(created_members)} team members")
        
        # Import Trucks
        print("\n🚛 Importing trucks...")
        created_trucks = []
        for truck_data in data['trucks']:
            truck = Truck(
                truck_number=truck_data['truck_number'],
                license_plate=truck_data.get('license_plate'),
                vin=truck_data.get('vin'),
                make=truck_data.get('make'),
                model=truck_data.get('model'),
                year=truck_data.get('year'),
                color=truck_data.get('color'),
                tank_capacity=truck_data.get('tank_capacity'),
                tank_material=truck_data.get('tank_material'),
                num_compartments=truck_data.get('num_compartments'),
                pump_type=truck_data.get('pump_type'),
                pump_cfm=truck_data.get('pump_cfm'),
                hose_length=truck_data.get('hose_length'),
                hose_diameter=truck_data.get('hose_diameter'),
                has_hose_reel=truck_data.get('has_hose_reel', False),
                has_pressure_washer=truck_data.get('has_pressure_washer', False),
                has_camera_system=truck_data.get('has_camera_system', False),
                has_gps_tracking=truck_data.get('has_gps_tracking', False),
                special_equipment=truck_data.get('special_equipment'),
                status=truck_data.get('status', 'active'),
                current_location_id=created_locations[1].id if len(created_locations) > 1 else None,  # Storage location
                current_mileage=truck_data.get('current_mileage'),
                engine_hours=truck_data.get('engine_hours'),
                last_maintenance=datetime.fromisoformat(truck_data['last_maintenance']).date() if truck_data.get('last_maintenance') else None,
                next_maintenance_due=datetime.fromisoformat(truck_data['next_maintenance_due']).date() if truck_data.get('next_maintenance_due') else None,
                insurance_company=truck_data.get('insurance_company'),
                insurance_policy=truck_data.get('insurance_policy'),
                insurance_expiry=datetime.fromisoformat(truck_data['insurance_expiry']).date() if truck_data.get('insurance_expiry') else None,
                registration_expiry=datetime.fromisoformat(truck_data['registration_expiry']).date() if truck_data.get('registration_expiry') else None,
                purchase_date=datetime.fromisoformat(truck_data['purchase_date']).date() if truck_data.get('purchase_date') else None,
                purchase_price=truck_data.get('purchase_price'),
                current_value=truck_data.get('current_value'),
                notes=truck_data.get('notes')
            )
            db.session.add(truck)
            created_trucks.append(truck)
        
        db.session.commit()
        print(f"  ✅ Imported {len(created_trucks)} trucks")
        
        # Import Customers
        print("\n👨‍👩‍👧‍👦 Importing customers...")
        created_customers = []
        for customer_data in data['customers']:
            customer = Customer(
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                company_name=customer_data.get('company_name'),
                customer_type=customer_data.get('customer_type', 'residential'),
                email=customer_data.get('email'),
                phone_primary=customer_data.get('phone_primary'),
                phone_secondary=customer_data.get('phone_secondary'),
                street_address=customer_data.get('street_address'),
                city=customer_data.get('city'),
                state=customer_data.get('state'),
                zip_code=customer_data.get('zip_code'),
                county=customer_data.get('county'),
                billing_street_address=customer_data.get('billing_street_address'),
                billing_city=customer_data.get('billing_city'),
                billing_state=customer_data.get('billing_state'),
                billing_zip_code=customer_data.get('billing_zip_code'),
                preferred_contact_method=customer_data.get('preferred_contact_method'),
                payment_terms=customer_data.get('payment_terms'),
                tax_exempt=customer_data.get('tax_exempt', False),
                tax_exempt_number=customer_data.get('tax_exempt_number'),
                service_reminders=customer_data.get('service_reminders', True),
                marketing_emails=customer_data.get('marketing_emails', False)
            )
            db.session.add(customer)
            created_customers.append(customer)
        
        db.session.commit()
        print(f"  ✅ Imported {len(created_customers)} customers")
        
        # Import Septic Systems
        print("\n🏠 Importing septic systems...")
        created_systems = []
        for system_data in data['septic_systems']:
            customer_index = system_data.get('customer_index', 0)
            if customer_index < len(created_customers):
                system = SepticSystem(
                    customer_id=created_customers[customer_index].id,
                    system_type=system_data.get('system_type'),
                    tank_size=system_data.get('tank_size'),
                    tank_material=system_data.get('tank_material'),
                    num_compartments=system_data.get('num_compartments'),
                    install_date=datetime.fromisoformat(system_data['install_date']).date() if system_data.get('install_date') else None,
                    permit_number=system_data.get('permit_number'),
                    installer_company=system_data.get('installer_company'),
                    pump_frequency_months=system_data.get('pump_frequency_months'),
                    last_pumped=datetime.fromisoformat(system_data['last_pumped']).date() if system_data.get('last_pumped') else None,
                    next_pump_due=datetime.fromisoformat(system_data['next_pump_due']).date() if system_data.get('next_pump_due') else None,
                    system_condition=system_data.get('system_condition'),
                    needs_repair=system_data.get('needs_repair', False),
                    repair_notes=system_data.get('repair_notes'),
                    access_notes=system_data.get('access_notes'),
                    gps_coordinates=system_data.get('gps_coordinates')
                )
                db.session.add(system)
                created_systems.append(system)
        
        db.session.commit()
        print(f"  ✅ Imported {len(created_systems)} septic systems")
        
        # Import Tickets
        print("\n🎫 Importing tickets...")
        created_tickets = []
        for ticket_data in data['tickets']:
            customer_index = ticket_data.get('customer_index', 0)
            truck_index = ticket_data.get('truck_index')
            septic_index = ticket_data.get('septic_system_index')
            
            if customer_index < len(created_customers):
                ticket = Ticket(
                    job_id=ticket_data['job_id'],
                    customer_id=created_customers[customer_index].id,
                    septic_system_id=created_systems[septic_index].id if septic_index is not None and septic_index < len(created_systems) else None,
                    service_type=ticket_data.get('service_type'),
                    service_description=ticket_data.get('service_description'),
                    priority=ticket_data.get('priority', 'medium'),
                    status=ticket_data.get('status', 'pending'),
                    scheduled_date=datetime.fromisoformat(ticket_data['scheduled_date']) if ticket_data.get('scheduled_date') else None,
                    requested_service_date=datetime.fromisoformat(ticket_data['requested_service_date']).date() if ticket_data.get('requested_service_date') else None,
                    estimated_duration=ticket_data.get('estimated_duration'),
                    route_position=ticket_data.get('route_position'),
                    column_position=ticket_data.get('column_position', 0),
                    assigned_technician=ticket_data.get('assigned_technician'),
                    truck_number=ticket_data.get('truck_number'),
                    truck_id=created_trucks[truck_index].id if truck_index is not None and truck_index < len(created_trucks) else None,
                    estimated_cost=ticket_data.get('estimated_cost'),
                    actual_cost=ticket_data.get('actual_cost'),
                    parts_cost=ticket_data.get('parts_cost'),
                    labor_cost=ticket_data.get('labor_cost'),
                    disposal_cost=ticket_data.get('disposal_cost'),
                    gallons_pumped=ticket_data.get('gallons_pumped'),
                    waste_type=ticket_data.get('waste_type'),
                    disposal_location=ticket_data.get('disposal_location'),
                    tank_condition=ticket_data.get('tank_condition'),
                    work_performed=ticket_data.get('work_performed'),
                    payment_status=ticket_data.get('payment_status'),
                    office_notes=ticket_data.get('office_notes'),
                    technician_notes=ticket_data.get('technician_notes'),
                    completed_at=datetime.fromisoformat(ticket_data['completed_at']) if ticket_data.get('completed_at') else None
                )
                db.session.add(ticket)
                created_tickets.append(ticket)
        
        db.session.commit()
        print(f"  ✅ Imported {len(created_tickets)} tickets")
        
        print(f"\n🎉 Import completed successfully!")
        print(f"📊 Summary:")
        print(f"  • {len(created_locations)} Locations")
        print(f"  • {len(created_members)} Team Members")
        print(f"  • {len(created_trucks)} Trucks")
        print(f"  • {len(created_customers)} Customers")
        print(f"  • {len(created_systems)} Septic Systems")
        print(f"  • {len(created_tickets)} Tickets")
        
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_sample_data.py <json_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    success = import_data(filename)
    
    if success:
        print("\n✅ Ready to test on Railway!")
    else:
        print("\n❌ Import failed")
        sys.exit(1)
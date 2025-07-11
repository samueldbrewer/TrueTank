#!/usr/bin/env python3
"""
Export sample data from local database to Railway
"""

import json
import os
import sys
from datetime import datetime, date

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Customer, SepticSystem, TeamMember, Truck, Location, Ticket, TruckTeamAssignment

def serialize_date(obj):
    """JSON serializer for date objects"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def export_data():
    """Export all sample data to JSON files"""
    
    with app.app_context():
        data = {}
        
        print("📤 Exporting sample data from local database...")
        
        # Export Locations
        locations = Location.query.all()
        data['locations'] = []
        for location in locations:
            loc_data = {
                'name': location.name,
                'location_type': location.location_type,
                'street_address': location.street_address,
                'city': location.city,
                'state': location.state,
                'zip_code': location.zip_code,
                'county': location.county,
                'gps_coordinates': location.gps_coordinates,
                'contact_person': location.contact_person,
                'phone_number': location.phone_number,
                'is_active': location.is_active,
                'hours_of_operation': location.hours_of_operation,
                'access_notes': location.access_notes,
                'capacity_notes': location.capacity_notes,
                'security_info': location.security_info
            }
            data['locations'].append(loc_data)
        
        print(f"  ✅ Exported {len(data['locations'])} locations")
        
        # Export Team Members
        team_members = TeamMember.query.all()
        data['team_members'] = []
        for member in team_members:
            member_data = {
                'first_name': member.first_name,
                'last_name': member.last_name,
                'employee_id': member.employee_id,
                'position': member.position,
                'department': member.department,
                'hire_date': member.hire_date.isoformat() if member.hire_date else None,
                'employment_status': member.employment_status,
                'phone_primary': member.phone_primary,
                'email': member.email,
                'home_street_address': member.home_street_address,
                'home_city': member.home_city,
                'home_state': member.home_state,
                'home_zip_code': member.home_zip_code,
                'emergency_contact_name': member.emergency_contact_name,
                'emergency_contact_phone': member.emergency_contact_phone,
                'emergency_contact_relationship': member.emergency_contact_relationship,
                'cdl_license': member.cdl_license,
                'cdl_expiry': member.cdl_expiry.isoformat() if member.cdl_expiry else None,
                'septic_certification': member.septic_certification,
                'septic_cert_expiry': member.septic_cert_expiry.isoformat() if member.septic_cert_expiry else None,
                'other_certifications': member.other_certifications,
                'is_supervisor': member.is_supervisor,
                'can_operate_trucks': member.can_operate_trucks,
                'notes': member.notes
            }
            data['team_members'].append(member_data)
        
        print(f"  ✅ Exported {len(data['team_members'])} team members")
        
        # Export Trucks
        trucks = Truck.query.all()
        data['trucks'] = []
        truck_id_mapping = {}  # To map old IDs to new ones
        
        for i, truck in enumerate(trucks):
            truck_data = {
                'truck_number': truck.truck_number,
                'license_plate': truck.license_plate,
                'vin': truck.vin,
                'make': truck.make,
                'model': truck.model,
                'year': truck.year,
                'color': truck.color,
                'tank_capacity': truck.tank_capacity,
                'tank_material': truck.tank_material,
                'num_compartments': truck.num_compartments,
                'pump_type': truck.pump_type,
                'pump_cfm': truck.pump_cfm,
                'hose_length': truck.hose_length,
                'hose_diameter': truck.hose_diameter,
                'has_hose_reel': truck.has_hose_reel,
                'has_pressure_washer': truck.has_pressure_washer,
                'has_camera_system': truck.has_camera_system,
                'has_gps_tracking': truck.has_gps_tracking,
                'special_equipment': truck.special_equipment,
                'status': truck.status,
                'current_mileage': truck.current_mileage,
                'engine_hours': truck.engine_hours,
                'last_maintenance': truck.last_maintenance.isoformat() if truck.last_maintenance else None,
                'next_maintenance_due': truck.next_maintenance_due.isoformat() if truck.next_maintenance_due else None,
                'insurance_company': truck.insurance_company,
                'insurance_policy': truck.insurance_policy,
                'insurance_expiry': truck.insurance_expiry.isoformat() if truck.insurance_expiry else None,
                'registration_expiry': truck.registration_expiry.isoformat() if truck.registration_expiry else None,
                'purchase_date': truck.purchase_date.isoformat() if truck.purchase_date else None,
                'purchase_price': truck.purchase_price,
                'current_value': truck.current_value,
                'notes': truck.notes
            }
            data['trucks'].append(truck_data)
            truck_id_mapping[truck.id] = i  # Store mapping for tickets
        
        print(f"  ✅ Exported {len(data['trucks'])} trucks")
        
        # Export Customers
        customers = Customer.query.all()
        data['customers'] = []
        customer_id_mapping = {}
        
        for i, customer in enumerate(customers):
            customer_data = {
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'company_name': customer.company_name,
                'customer_type': customer.customer_type,
                'email': customer.email,
                'phone_primary': customer.phone_primary,
                'phone_secondary': customer.phone_secondary,
                'street_address': customer.street_address,
                'city': customer.city,
                'state': customer.state,
                'zip_code': customer.zip_code,
                'county': customer.county,
                'billing_street_address': customer.billing_street_address,
                'billing_city': customer.billing_city,
                'billing_state': customer.billing_state,
                'billing_zip_code': customer.billing_zip_code,
                'preferred_contact_method': customer.preferred_contact_method,
                'payment_terms': customer.payment_terms,
                'tax_exempt': customer.tax_exempt,
                'tax_exempt_number': customer.tax_exempt_number,
                'service_reminders': customer.service_reminders,
                'marketing_emails': customer.marketing_emails
            }
            data['customers'].append(customer_data)
            customer_id_mapping[customer.id] = i
        
        print(f"  ✅ Exported {len(data['customers'])} customers")
        
        # Export Septic Systems
        septic_systems = SepticSystem.query.all()
        data['septic_systems'] = []
        septic_id_mapping = {}
        
        for i, system in enumerate(septic_systems):
            system_data = {
                'customer_index': customer_id_mapping.get(system.customer_id, 0),  # Reference by index
                'system_type': system.system_type,
                'tank_size': system.tank_size,
                'tank_material': system.tank_material,
                'num_compartments': system.num_compartments,
                'install_date': system.install_date.isoformat() if system.install_date else None,
                'permit_number': system.permit_number,
                'installer_company': system.installer_company,
                'pump_frequency_months': system.pump_frequency_months,
                'last_pumped': system.last_pumped.isoformat() if system.last_pumped else None,
                'next_pump_due': system.next_pump_due.isoformat() if system.next_pump_due else None,
                'system_condition': system.system_condition,
                'needs_repair': system.needs_repair,
                'repair_notes': system.repair_notes,
                'access_notes': system.access_notes,
                'gps_coordinates': system.gps_coordinates
            }
            data['septic_systems'].append(system_data)
            septic_id_mapping[system.id] = i
        
        print(f"  ✅ Exported {len(data['septic_systems'])} septic systems")
        
        # Export Tickets
        tickets = Ticket.query.all()
        data['tickets'] = []
        
        for ticket in tickets:
            ticket_data = {
                'job_id': ticket.job_id,
                'customer_index': customer_id_mapping.get(ticket.customer_id, 0),
                'septic_system_index': septic_id_mapping.get(ticket.septic_system_id) if ticket.septic_system_id else None,
                'service_type': ticket.service_type,
                'service_description': ticket.service_description,
                'priority': ticket.priority,
                'status': ticket.status,
                'scheduled_date': ticket.scheduled_date.isoformat() if ticket.scheduled_date else None,
                'requested_service_date': ticket.requested_service_date.isoformat() if ticket.requested_service_date else None,
                'estimated_duration': ticket.estimated_duration,
                'route_position': ticket.route_position,
                'column_position': ticket.column_position,
                'assigned_technician': ticket.assigned_technician,
                'truck_number': ticket.truck_number,
                'truck_index': truck_id_mapping.get(ticket.truck_id) if ticket.truck_id else None,
                'estimated_cost': ticket.estimated_cost,
                'actual_cost': ticket.actual_cost,
                'parts_cost': ticket.parts_cost,
                'labor_cost': ticket.labor_cost,
                'disposal_cost': ticket.disposal_cost,
                'gallons_pumped': ticket.gallons_pumped,
                'waste_type': ticket.waste_type,
                'disposal_location': ticket.disposal_location,
                'tank_condition': ticket.tank_condition,
                'work_performed': ticket.work_performed,
                'payment_status': ticket.payment_status,
                'office_notes': ticket.office_notes,
                'technician_notes': ticket.technician_notes,
                'completed_at': ticket.completed_at.isoformat() if ticket.completed_at else None
            }
            data['tickets'].append(ticket_data)
        
        print(f"  ✅ Exported {len(data['tickets'])} tickets")
        
        # Save to file
        filename = f"sample_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=serialize_date)
        
        print(f"\n💾 Data exported to: {filename}")
        print(f"📊 Total records: {sum(len(data[key]) for key in data.keys())}")
        
        return filename

if __name__ == "__main__":
    export_data()
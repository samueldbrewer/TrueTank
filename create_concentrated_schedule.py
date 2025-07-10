#!/usr/bin/env python3
"""
Create concentrated schedule with 5-7 jobs per truck for today and tomorrow
"""

import sys
import os
from datetime import datetime, date, timedelta
from random import choice, randint

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Ticket, Truck, Customer, SepticSystem

def create_concentrated_schedule():
    """Create 5-7 jobs per truck for today and tomorrow"""
    
    with app.app_context():
        # Get active trucks
        trucks = Truck.query.filter_by(status='active').all()
        customers = Customer.query.all()
        septic_systems = SepticSystem.query.all()
        
        print(f"Creating concentrated schedule for {len(trucks)} trucks")
        
        # Clear ALL existing tickets to avoid conflicts
        Ticket.query.delete()
        
        # Service types with realistic durations and costs
        service_configs = {
            'Septic Pumping': {'duration': [90, 120, 150], 'cost': [250, 350]},
            'Septic Inspection': {'duration': [60, 90], 'cost': [150, 250]},
            'Septic Repair': {'duration': [120, 180, 240], 'cost': [300, 800]},
            'Preventive Maintenance': {'duration': [60, 90], 'cost': [180, 280]},
            'Emergency Service': {'duration': [90, 150], 'cost': [400, 600]},
            'Septic Cleaning': {'duration': [120, 180], 'cost': [300, 500]},
            'Line Cleaning/Rooter': {'duration': [90, 120], 'cost': [200, 350]},
            'Grease Trap Service': {'duration': [60, 90], 'cost': [150, 300]}
        }
        
        priorities = ['low', 'medium', 'high', 'urgent']
        technicians = ['James Wilson', 'Maria Garcia', 'Robert Smith', 'Ashley Johnson']
        
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        all_tickets = []
        ticket_counter = 1
        
        # Create jobs for today and tomorrow
        for target_date in [today, tomorrow]:
            date_name = "today" if target_date == today else "tomorrow"
            print(f"\nCreating jobs for {date_name} ({target_date}):")
            
            for truck in trucks:
                num_jobs = randint(5, 7)
                print(f"  {truck.truck_number}: {num_jobs} jobs")
                
                # Start times throughout the day
                start_times = [8, 9, 10, 11, 13, 14, 15, 16]  # Skip lunch hour (12)
                
                for job_idx in range(num_jobs):
                    customer = choice(customers)
                    
                    # Try to find a septic system for this customer
                    customer_systems = [s for s in septic_systems if s.customer_id == customer.id]
                    septic_system = choice(customer_systems) if customer_systems else None
                    
                    service_type = choice(list(service_configs.keys()))
                    config = service_configs[service_type]
                    
                    # Calculate start time (spread throughout day)
                    base_hour = start_times[job_idx % len(start_times)]
                    start_minute = choice([0, 15, 30, 45])
                    scheduled_time = datetime.combine(target_date, datetime.min.time().replace(
                        hour=base_hour, 
                        minute=start_minute
                    ))
                    
                    # Create ticket
                    ticket_data = {
                        'job_id': f"TT{datetime.now().year}{str(ticket_counter).zfill(4)}",
                        'customer_id': customer.id,
                        'septic_system_id': septic_system.id if septic_system else None,
                        'service_type': service_type,
                        'service_description': f"{service_type} for {customer.first_name} {customer.last_name}",
                        'priority': choice(priorities),
                        'status': 'scheduled',
                        'scheduled_date': scheduled_time,
                        'requested_service_date': target_date,
                        'estimated_duration': choice(config['duration']),
                        'estimated_cost': round(choice(config['cost']) + randint(-50, 50), 2),
                        'assigned_technician': choice(technicians),
                        'truck_number': truck.truck_number,
                        'truck_id': truck.id,
                        'created_at': datetime.now() - timedelta(days=randint(1, 7)),
                        'column_position': job_idx  # For ordering within truck column
                    }
                    
                    ticket = Ticket(**ticket_data)
                    db.session.add(ticket)
                    all_tickets.append(ticket)
                    ticket_counter += 1
                    
                    print(f"    {scheduled_time.strftime('%H:%M')}: {service_type} - {customer.first_name} {customer.last_name}")
        
        # Keep some pending tickets (unscheduled)
        print(f"\nCreating additional pending tickets:")
        for i in range(5):
            customer = choice(customers)
            customer_systems = [s for s in septic_systems if s.customer_id == customer.id]
            septic_system = choice(customer_systems) if customer_systems else None
            
            service_type = choice(list(service_configs.keys()))
            config = service_configs[service_type]
            
            ticket_data = {
                'job_id': f"TT{datetime.now().year}{str(ticket_counter).zfill(4)}",
                'customer_id': customer.id,
                'septic_system_id': septic_system.id if septic_system else None,
                'service_type': service_type,
                'service_description': f"{service_type} for {customer.first_name} {customer.last_name}",
                'priority': choice(priorities),
                'status': 'pending',
                'scheduled_date': None,
                'requested_service_date': today + timedelta(days=randint(1, 14)),
                'estimated_duration': choice(config['duration']),
                'estimated_cost': round(choice(config['cost']) + randint(-50, 50), 2),
                'created_at': datetime.now() - timedelta(days=randint(1, 5))
            }
            
            ticket = Ticket(**ticket_data)
            db.session.add(ticket)
            all_tickets.append(ticket)
            ticket_counter += 1
            
            print(f"  Pending: {service_type} - {customer.first_name} {customer.last_name}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Created {len(all_tickets)} total tickets")
        print(f"📊 Summary:")
        
        # Today's summary
        today_tickets = [t for t in all_tickets if t.scheduled_date and t.scheduled_date.date() == today]
        truck_counts_today = {}
        for ticket in today_tickets:
            truck_num = ticket.truck_number
            truck_counts_today[truck_num] = truck_counts_today.get(truck_num, 0) + 1
        
        print(f"   Today ({today}):")
        for truck_num, count in truck_counts_today.items():
            print(f"     {truck_num}: {count} jobs")
        
        # Tomorrow's summary
        tomorrow_tickets = [t for t in all_tickets if t.scheduled_date and t.scheduled_date.date() == tomorrow]
        truck_counts_tomorrow = {}
        for ticket in tomorrow_tickets:
            truck_num = ticket.truck_number
            truck_counts_tomorrow[truck_num] = truck_counts_tomorrow.get(truck_num, 0) + 1
        
        print(f"   Tomorrow ({tomorrow}):")
        for truck_num, count in truck_counts_tomorrow.items():
            print(f"     {truck_num}: {count} jobs")
        
        pending_count = len([t for t in all_tickets if t.status == 'pending'])
        print(f"   Pending: {pending_count} jobs")
        
        print(f"\n🎯 Job board is now ready with concentrated scheduling!")

if __name__ == "__main__":
    create_concentrated_schedule()
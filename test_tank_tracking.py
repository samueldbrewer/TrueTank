#!/usr/bin/env python3
"""
Test the tank tracking system functionality
"""

from app import app, db
from models import Truck, Ticket, DumpSite
import tank_tracking
from datetime import datetime

def test_tank_tracking():
    """Test tank tracking system"""
    
    with app.app_context():
        print('🚛💧 TANK TRACKING SYSTEM TEST')
        print('=' * 50)
        
        # Test truck TT-04 (73.3% full - should need dump soon)
        truck = Truck.query.filter_by(truck_number='TT-04').first()
        if truck:
            print()
            print(f'📋 Testing Truck: {truck.truck_number}')
            print(f'Tank Capacity: {truck.tank_capacity} gallons')
            print(f'Current Level: {truck.current_tank_level} gallons')
            print(f'Fill Percentage: {truck.current_tank_level/truck.tank_capacity*100:.1f}%')
            print(f'Dump Threshold: {truck.tank_full_threshold*100:.1f}%')
            
            # Get tank status
            tank_status = tank_tracking.get_tank_status(truck.to_dict())
            print(f'Status: {tank_status["status"]}')
            print(f'Gallons until dump needed: {tank_status["gallons_until_full"]}')
            
            # Get tickets for this truck today
            today = datetime.now().date()
            tickets = Ticket.query.filter(
                Ticket.truck_id == truck.id,
                db.func.date(Ticket.scheduled_date) == today
            ).order_by(Ticket.route_position).all()
            
            print()
            print(f'📝 Jobs scheduled for today: {len(tickets)}')
            tickets_data = []
            for ticket in tickets:
                if ticket.customer:
                    customer_address = f'{ticket.customer.street_address}, {ticket.customer.city}, {ticket.customer.state}'
                    ticket_data = {
                        'id': ticket.id,
                        'job_id': ticket.job_id,
                        'service_type': ticket.service_type,
                        'estimated_gallons': ticket.estimated_gallons or 0,
                        'customer_name': f'{ticket.customer.first_name} {ticket.customer.last_name}',
                        'customer_address': customer_address
                    }
                    tickets_data.append(ticket_data)
                    print(f'  {ticket.job_id}: {ticket.service_type} ({ticket.estimated_gallons or 0} gallons)')
            
            # Calculate tank progression
            progression = tank_tracking.calculate_tank_fill_progression(
                truck.tank_capacity, truck.current_tank_level, tickets_data
            )
            
            print()
            print(f'📈 Tank Fill Progression:')
            for p in progression:
                print(f'  After job {p["job_index"]+1}: {p["gallons_after"]} gallons ({p["fill_percentage_after"]:.1f}% full)')
            
            # Find dump points
            dump_points = tank_tracking.find_dump_points(
                truck.tank_capacity, truck.current_tank_level, truck.tank_full_threshold, tickets_data
            )
            
            if dump_points:
                print()
                print(f'🗑️ Dump Required:')
                for i, gallons in dump_points:
                    print(f'  Before job {i+1}: Tank will have {gallons} gallons')
            else:
                print()
                print(f'✅ No dumps needed for todays route!')
            
            # Test with dump sites
            dump_sites = DumpSite.query.filter_by(is_active=True).all()
            print()
            print(f'📍 Available Dump Sites: {len(dump_sites)}')
            for site in dump_sites:
                print(f'  {site.name}: ${site.cost_per_gallon:.3f}/gal ({site.operating_hours})')
        
        print()
        print(f'🎯 Tank Tracking System Test Completed!')

if __name__ == '__main__':
    test_tank_tracking()
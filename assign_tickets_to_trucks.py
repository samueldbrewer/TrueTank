#!/usr/bin/env python3
"""
Assign some tickets to trucks for demonstration
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Ticket, Truck

def assign_tickets_to_trucks():
    """Assign pending and scheduled tickets to trucks for today and tomorrow"""
    
    with app.app_context():
        # Get active trucks
        trucks = Truck.query.filter_by(status='active').all()
        truck_numbers = [t.truck_number for t in trucks]
        
        print(f"Available trucks: {truck_numbers}")
        
        # Get today and tomorrow
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        print(f"Assigning tickets for {today} and {tomorrow}")
        
        # Get some pending tickets and assign them to today
        pending_tickets = Ticket.query.filter_by(status='pending').limit(3).all()
        
        for i, ticket in enumerate(pending_tickets):
            truck = trucks[i % len(trucks)]
            ticket.status = 'scheduled'
            ticket.scheduled_date = datetime.combine(today, datetime.min.time().replace(hour=8 + i, minute=0))
            ticket.truck_number = truck.truck_number
            ticket.truck_id = truck.id
            ticket.assigned_technician = ['James Wilson', 'Maria Garcia', 'Robert Smith'][i % 3]
            print(f"Assigned {ticket.job_id} to {truck.truck_number} for {ticket.scheduled_date}")
        
        # Get some more tickets and assign them to tomorrow
        more_tickets = Ticket.query.filter(
            Ticket.status.in_(['scheduled', 'in-progress']),
            Ticket.truck_id.is_(None)
        ).limit(2).all()
        
        for i, ticket in enumerate(more_tickets):
            truck = trucks[i % len(trucks)]
            ticket.scheduled_date = datetime.combine(tomorrow, datetime.min.time().replace(hour=9 + i, minute=30))
            ticket.truck_number = truck.truck_number
            ticket.truck_id = truck.id
            if not ticket.assigned_technician:
                ticket.assigned_technician = ['Ashley Johnson', 'Robert Smith'][i % 2]
            print(f"Assigned {ticket.job_id} to {truck.truck_number} for {ticket.scheduled_date}")
        
        # Commit changes
        db.session.commit()
        
        print("✅ Ticket assignments completed!")
        
        # Show summary
        print("\nSummary of today's assignments:")
        today_tickets = Ticket.query.filter(
            db.func.date(Ticket.scheduled_date) == today,
            Ticket.truck_id.isnot(None)
        ).all()
        
        for ticket in today_tickets:
            print(f"  {ticket.truck_number}: {ticket.job_id} - {ticket.service_type} at {ticket.scheduled_date.strftime('%H:%M')}")

if __name__ == "__main__":
    assign_tickets_to_trucks()
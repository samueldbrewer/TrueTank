#!/usr/bin/env python3
"""Management commands for TrueTank"""

import sys
from app import app, db
from models import Ticket
from datetime import datetime, timedelta

def update_all_tickets_dates():
    """Update all tickets to be scheduled for today and tomorrow"""
    with app.app_context():
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        tickets = Ticket.query.all()
        total_tickets = len(tickets)
        
        print(f"Found {total_tickets} tickets to update")
        
        for i, ticket in enumerate(tickets):
            if i < total_tickets // 2:
                ticket.scheduled_date = datetime.combine(today, datetime.min.time())
                print(f"Ticket {ticket.job_id} -> today ({today})")
            else:
                ticket.scheduled_date = datetime.combine(tomorrow, datetime.min.time())
                print(f"Ticket {ticket.job_id} -> tomorrow ({tomorrow})")
            
            if ticket.route_position is None:
                ticket.route_position = i % 10
        
        try:
            db.session.commit()
            print(f"\n✅ Successfully updated {total_tickets} tickets!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "update_dates":
        update_all_tickets_dates()
    else:
        print("Usage: python manage_commands.py update_dates")
#!/usr/bin/env python3
"""
Initialize Railway PostgreSQL database with current schema
This script will recreate all tables and populate with fresh sample data
"""

import os
import sys
from datetime import datetime

# Set environment for Railway production database
os.environ['DATABASE_URL'] = 'postgresql://postgres:mvqnOAuUuTLVLWqePdOKTuoqNckRFnMn@junction.proxy.rlwy.net:27479/railway'
os.environ['FLASK_ENV'] = 'production'

def init_railway_database():
    """Initialize the Railway PostgreSQL database with current schema"""
    print("🚀 Initializing Railway PostgreSQL database...")
    
    try:
        # Import app to initialize database connection
        from app import app, db
        from models import Customer, Ticket, SepticSystem, ServiceHistory, Location, Truck, TeamMember, TruckTeamAssignment, DumpSite
        
        with app.app_context():
            print("🗑️ Dropping all existing tables...")
            db.drop_all()
            
            print("📊 Creating fresh database tables with current schema...")
            db.create_all()
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Created {len(tables)} tables: {', '.join(tables)}")
            
            # Add essential dump sites
            print("🗑️ Adding essential dump sites...")
            dump_sites = [
                DumpSite(
                    name='Jefferson County Waste Management',
                    facility_type='Municipal',
                    street_address='8900 National Turnpike',
                    city='Louisville',
                    state='KY',
                    zip_code='40214',
                    county='Jefferson',
                    operating_hours='6:00 AM - 6:00 PM, Mon-Fri',
                    cost_per_gallon=0.08,
                    estimated_dump_time=20,
                    is_active=True,
                    accepts_septic_waste=True,
                    accepts_grease_waste=True
                ),
                DumpSite(
                    name='Oldham County Wastewater Treatment',
                    facility_type='County',
                    street_address='1356 S 4th St',
                    city='La Grange',
                    state='KY', 
                    zip_code='40031',
                    county='Oldham',
                    operating_hours='7:00 AM - 4:00 PM, Mon-Fri',
                    cost_per_gallon=0.10,
                    estimated_dump_time=25,
                    is_active=True,
                    accepts_septic_waste=True,
                    accepts_grease_waste=False
                ),
                DumpSite(
                    name='Bullitt County Sewage Treatment Plant',
                    facility_type='County',
                    street_address='300 Dixie Hwy',
                    city='Shepherdsville', 
                    state='KY',
                    zip_code='40165',
                    county='Bullitt',
                    operating_hours='8:00 AM - 5:00 PM, Mon-Fri',
                    cost_per_gallon=0.12,
                    estimated_dump_time=30,
                    is_active=True,
                    accepts_septic_waste=True,
                    accepts_grease_waste=True
                )
            ]
            
            for site in dump_sites:
                db.session.add(site)
            
            db.session.commit()
            print(f"✅ Added {len(dump_sites)} dump sites")
            
            print("🎉 Database initialization completed successfully!")
            print(f"🕒 Completed at: {datetime.now()}")
            
            # Final verification
            print("\n📊 Database Summary:")
            print(f"   Customers: {Customer.query.count()}")
            print(f"   Tickets: {Ticket.query.count()}")
            print(f"   Trucks: {Truck.query.count()}")
            print(f"   Dump Sites: {DumpSite.query.count()}")
            print(f"   Locations: {Location.query.count()}")
            print(f"   Team Members: {TeamMember.query.count()}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    
    return True

if __name__ == '__main__':
    success = init_railway_database()
    if success:
        print("\n✅ Railway database ready!")
        sys.exit(0)
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
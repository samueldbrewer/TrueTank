#!/usr/bin/env python3
"""
Populate Railway PostgreSQL database with sample data including dump sites and tank tracking
"""

import os
import sys
import json
import requests
from datetime import datetime, date, timedelta
from models import db, Customer, Ticket, SepticSystem, ServiceHistory, Location, Truck, TeamMember, TruckTeamAssignment, DumpSite
from populate_sample_data import main as create_sample_data

# Set environment for production database
os.environ['DATABASE_URL'] = 'postgresql://postgres:mvqnOAuUuTLVLWqePdOKTuoqNckRFnMn@junction.proxy.rlwy.net:27479/railway'
os.environ['FLASK_ENV'] = 'production'

def populate_production_database():
    """Populate the Railway PostgreSQL database with comprehensive sample data"""
    print("🚀 Populating Railway PostgreSQL database...")
    
    # Import app to initialize database connection
    from app import app, db
    
    with app.app_context():
        print("📊 Creating database tables...")
        db.create_all()
        
        # Check if data already exists
        existing_customers = Customer.query.count()
        existing_dump_sites = DumpSite.query.count()
        
        print(f"📈 Current database state:")
        print(f"   Customers: {existing_customers}")
        print(f"   Dump Sites: {existing_dump_sites}")
        print(f"   Tickets: {Ticket.query.count()}")
        print(f"   Trucks: {Truck.query.count()}")
        
        if existing_customers > 0:
            print("✅ Database has existing data. Adding missing dump sites and tank tracking data...")
            # Don't clear data, just add missing components
            if False:  # This condition will never be true, so we skip clearing
                print("🗑️ Clearing existing data...")
                # Clear all tables in dependency order
                TruckTeamAssignment.query.delete()
                ServiceHistory.query.delete()
                Ticket.query.delete()
                SepticSystem.query.delete()
                Customer.query.delete()
                Truck.query.delete()
                DumpSite.query.delete()
                TeamMember.query.delete()
                Location.query.delete()
                db.session.commit()
            else:
                print("✅ Keeping existing data, adding missing dump sites and tank tracking data...")
        
        # Create comprehensive sample data
        print("📦 Creating sample data...")
        create_sample_data()
        
        # Geocode customer addresses
        print("🌍 Geocoding customer addresses...")
        geocode_all_customers()
        
        # Update truck tank tracking data
        print("🛢️ Setting up tank tracking data...")
        setup_tank_tracking_data()
        
        # Verify data
        print("✅ Verifying populated data:")
        print(f"   Customers: {Customer.query.count()}")
        print(f"   Tickets: {Ticket.query.count()}")
        print(f"   Trucks: {Truck.query.count()}")
        print(f"   Dump Sites: {DumpSite.query.count()}")
        print(f"   Locations: {Location.query.count()}")
        print(f"   Team Members: {TeamMember.query.count()}")
        print(f"   Service History: {ServiceHistory.query.count()}")
        
        print("🎉 Database populated successfully!")

def geocode_all_customers():
    """Geocode all customer addresses using Nominatim"""
    customers = Customer.query.filter(Customer.gps_coordinates.is_(None)).all()
    
    print(f"🗺️ Geocoding {len(customers)} customer addresses...")
    
    success_count = 0
    for i, customer in enumerate(customers):
        try:
            # Build address
            address_parts = []
            if customer.street_address:
                address_parts.append(customer.street_address)
            if customer.city:
                address_parts.append(customer.city)
            if customer.state:
                address_parts.append(customer.state)
            if customer.zip_code:
                address_parts.append(customer.zip_code)
            
            if not address_parts:
                continue
                
            full_address = ', '.join(address_parts)
            
            # Geocode using Nominatim
            coords = geocode_address_nominatim(full_address)
            
            if coords:
                gps_string = f"{coords['latitude']},{coords['longitude']}"
                customer.gps_coordinates = gps_string
                customer.updated_at = datetime.utcnow()
                success_count += 1
                print(f"   ✅ {customer.first_name} {customer.last_name}: {gps_string}")
            else:
                print(f"   ❌ Failed: {customer.first_name} {customer.last_name}")
                
        except Exception as e:
            print(f"   ❌ Error geocoding {customer.first_name} {customer.last_name}: {e}")
    
    db.session.commit()
    print(f"🎯 Successfully geocoded {success_count}/{len(customers)} customers")

def geocode_address_nominatim(address):
    """Geocode address using Nominatim (OpenStreetMap)"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'addressdetails': 1,
            'limit': 1,
            'countrycodes': 'us'
        }
        
        headers = {
            'User-Agent': 'TrueTank-Septic-Service/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            result = data[0]
            return {
                'latitude': float(result['lat']),
                'longitude': float(result['lon'])
            }
        
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

def setup_tank_tracking_data():
    """Set up realistic tank tracking data for trucks"""
    trucks = Truck.query.all()
    
    print(f"🚛 Setting up tank tracking for {len(trucks)} trucks...")
    
    for truck in trucks:
        # Set realistic tank levels (20-60% full to start)
        if truck.tank_capacity:
            fill_percentage = 0.2 + (hash(truck.truck_number) % 40) / 100  # 20-60%
            truck.current_tank_level = truck.tank_capacity * fill_percentage
        else:
            truck.current_tank_level = 0.0
        
        # Set tank full threshold (80-90%)
        truck.tank_full_threshold = 0.80 + (hash(truck.truck_number[-1:]) % 10) / 100
        
        # Set last dump time (1-7 days ago)
        days_ago = (hash(truck.truck_number) % 7) + 1
        truck.last_dump_time = datetime.utcnow() - timedelta(days=days_ago)
        
        print(f"   🛢️ {truck.truck_number}: {truck.current_tank_level:.0f}/{truck.tank_capacity or 3000} gal ({truck.current_tank_level/truck.tank_capacity*100:.1f}%)" if truck.tank_capacity else f"   🛢️ {truck.truck_number}: No capacity set")
    
    db.session.commit()
    print("✅ Tank tracking data configured")

if __name__ == '__main__':
    populate_production_database()
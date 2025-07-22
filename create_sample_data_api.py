#!/usr/bin/env python3
"""
Create basic sample data for Railway production database via API
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://truetank-production.up.railway.app"

def create_customer(customer_data):
    """Create a customer via API"""
    response = requests.post(f"{BASE_URL}/api/customers", json=customer_data)
    return response.json()

def create_truck(truck_data):
    """Create a truck via API"""
    response = requests.post(f"{BASE_URL}/api/trucks", json=truck_data)
    return response.json()

def create_ticket(ticket_data):
    """Create a ticket via API"""
    response = requests.post(f"{BASE_URL}/api/tickets", json=ticket_data)
    return response.json()

def create_basic_sample_data():
    """Create minimal sample data to make the app functional"""
    print("🚀 Creating basic sample data for Railway production...")
    
    # Create a few customers
    customers = [
        {
            "first_name": "John",
            "last_name": "Smith", 
            "street_address": "123 Main St",
            "city": "Louisville",
            "state": "KY",
            "zip_code": "40214",
            "phone_number": "(502) 555-0123",
            "email": "john.smith@email.com"
        },
        {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "street_address": "456 Oak Ave", 
            "city": "La Grange",
            "state": "KY",
            "zip_code": "40031",
            "phone_number": "(502) 555-0456",
            "email": "sarah.johnson@email.com"
        },
        {
            "first_name": "Mike",
            "last_name": "Davis",
            "street_address": "789 Pine Rd",
            "city": "Shepherdsville", 
            "state": "KY",
            "zip_code": "40165",
            "phone_number": "(502) 555-0789",
            "email": "mike.davis@email.com"
        }
    ]
    
    created_customers = []
    for customer in customers:
        try:
            result = create_customer(customer)
            if result.get('success'):
                created_customers.append(result['customer'])
                print(f"✅ Created customer: {customer['first_name']} {customer['last_name']}")
            else:
                print(f"❌ Failed to create customer: {customer['first_name']} {customer['last_name']}")
        except Exception as e:
            print(f"❌ Error creating customer: {e}")
    
    # Create a few trucks
    trucks = [
        {
            "truck_number": "TT-01",
            "make": "Ford",
            "model": "F-550",
            "year": 2020,
            "tank_capacity": 3000,
            "current_tank_level": 750,
            "license_plate": "KY-TT01"
        },
        {
            "truck_number": "TT-02", 
            "make": "Chevrolet",
            "model": "Silverado 3500",
            "year": 2021,
            "tank_capacity": 4000,
            "current_tank_level": 1200,
            "license_plate": "KY-TT02"
        }
    ]
    
    created_trucks = []
    for truck in trucks:
        try:
            result = create_truck(truck)
            if result.get('success'):
                created_trucks.append(result['truck'])
                print(f"✅ Created truck: {truck['truck_number']}")
            else:
                print(f"❌ Failed to create truck: {truck['truck_number']}")
        except Exception as e:
            print(f"❌ Error creating truck: {e}")
    
    # Create some tickets if we have customers and trucks
    if created_customers and created_trucks:
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        tickets = [
            {
                "job_id": f"JOB-{today.strftime('%Y%m%d')}-001",
                "customer_id": created_customers[0]['id'],
                "service_type": "Septic Pumping",
                "priority": "medium", 
                "status": "pending",
                "scheduled_date": today.strftime('%Y-%m-%d'),
                "estimated_duration": 90,
                "service_description": "Regular septic pumping service"
            },
            {
                "job_id": f"JOB-{today.strftime('%Y%m%d')}-002",
                "customer_id": created_customers[1]['id'],
                "service_type": "Septic Inspection",
                "priority": "high",
                "status": "pending", 
                "scheduled_date": today.strftime('%Y-%m-%d'),
                "estimated_duration": 60,
                "service_description": "Annual septic system inspection"
            },
            {
                "job_id": f"JOB-{tomorrow.strftime('%Y%m%d')}-001",
                "customer_id": created_customers[2]['id'],
                "service_type": "Emergency Service",
                "priority": "urgent",
                "status": "pending",
                "scheduled_date": tomorrow.strftime('%Y-%m-%d'),
                "estimated_duration": 120,
                "service_description": "Emergency septic backup"
            }
        ]
        
        for ticket in tickets:
            try:
                result = create_ticket(ticket)
                if result.get('success'):
                    print(f"✅ Created ticket: {ticket['job_id']}")
                else:
                    print(f"❌ Failed to create ticket: {ticket['job_id']}")
            except Exception as e:
                print(f"❌ Error creating ticket: {e}")
    
    print("🎉 Basic sample data creation completed!")

if __name__ == '__main__':
    create_basic_sample_data()
#!/usr/bin/env python3
"""
Tank Fill Tracking and Dump Site Logic for TrueTank

This module handles:
- Gallons estimation by service type
- Tank fill calculation and monitoring
- Dump site selection and routing logic
- Route optimization with dump stops
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime
import math

# Service type gallons estimation based on industry averages
SERVICE_TYPE_GALLONS = {
    'Septic Pumping': 400,          # Average residential septic pumping
    'Septic Inspection': 0,         # No pumping during inspection
    'Septic Repair': 50,            # Minor pumping for access/cleaning
    'Septic Installation': 0,       # New installation, no existing waste
    'Preventive Maintenance': 150,  # Partial pumping and cleaning
    'Emergency Service': 300,       # Emergency pumping (usually substantial)
    'Septic Cleaning': 200,         # Deep cleaning with moderate pumping
    'Line Cleaning/Rooter': 25,     # Minimal pumping for line access
    'Grease Trap Service': 100,     # Commercial grease trap pumping
    'Lift Station Service': 500,    # Large capacity lift station pumping
}

def estimate_gallons_for_job(service_type: str, septic_tank_size: Optional[int] = None, 
                           customer_history: Optional[List[int]] = None) -> float:
    """
    Estimate gallons that will be pumped for a specific job
    
    Args:
        service_type: Type of service (matches ServiceType enum values)
        septic_tank_size: Size of septic tank in gallons (if known)
        customer_history: List of previous gallons pumped for this customer
    
    Returns:
        Estimated gallons to be pumped
    """
    
    # Start with base estimate from service type
    base_estimate = SERVICE_TYPE_GALLONS.get(service_type, 200)
    
    # Adjust based on septic tank size if available
    if septic_tank_size and service_type == 'Septic Pumping':
        # For pumping, estimate 60-80% of tank capacity
        tank_based_estimate = septic_tank_size * 0.7
        # Use average of service type and tank size estimates
        base_estimate = (base_estimate + tank_based_estimate) / 2
    
    # Adjust based on customer history if available
    if customer_history and len(customer_history) > 0:
        avg_history = sum(customer_history) / len(customer_history)
        # Weight recent history at 30%, base estimate at 70%
        base_estimate = (base_estimate * 0.7) + (avg_history * 0.3)
    
    return round(base_estimate, 1)

def calculate_tank_fill_progression(truck_capacity: int, current_level: float, 
                                  tickets: List[Dict]) -> List[Dict]:
    """
    Calculate how full the truck tank gets after each job
    
    Args:
        truck_capacity: Maximum tank capacity in gallons
        current_level: Current gallons in tank
        tickets: List of ticket dictionaries with estimated_gallons
    
    Returns:
        List of dictionaries with cumulative fill data for each job
    """
    
    progression = []
    running_total = current_level
    
    for i, ticket in enumerate(tickets):
        estimated_add = ticket.get('estimated_gallons', 0) or 0
        running_total += estimated_add
        
        fill_percentage = (running_total / truck_capacity) * 100 if truck_capacity else 0
        
        progression.append({
            'job_index': i,
            'ticket_id': ticket.get('id'),
            'job_id': ticket.get('job_id'),
            'gallons_before': running_total - estimated_add,
            'gallons_added': estimated_add,
            'gallons_after': running_total,
            'fill_percentage_before': ((running_total - estimated_add) / truck_capacity) * 100 if truck_capacity else 0,
            'fill_percentage_after': fill_percentage,
            'tank_capacity': truck_capacity
        })
    
    return progression

def find_dump_points(truck_capacity: int, current_level: float, 
                    dump_threshold: float, tickets: List[Dict]) -> List[Tuple[int, float]]:
    """
    Determine where dump stops are needed in the route
    
    Args:
        truck_capacity: Maximum tank capacity in gallons
        current_level: Current gallons in tank  
        dump_threshold: Threshold percentage (0.0-1.0) to trigger dump
        tickets: List of ticket dictionaries with estimated_gallons
    
    Returns:
        List of tuples: (job_index_before_dump, projected_gallons_at_dump)
    """
    
    dump_points = []
    running_total = current_level
    dump_trigger_gallons = truck_capacity * dump_threshold
    
    for i, ticket in enumerate(tickets):
        estimated_add = ticket.get('estimated_gallons', 0) or 0
        projected_total = running_total + estimated_add
        
        # Check if this job would put us over the threshold
        if projected_total > dump_trigger_gallons:
            dump_points.append((i, running_total))
            running_total = estimated_add  # Tank empty after dump, then add this job
        else:
            running_total = projected_total
    
    return dump_points

def find_nearest_dump_site(current_location: Dict, dump_sites: List[Dict], 
                          waste_type: str = 'septic') -> Optional[Dict]:
    """
    Find the nearest appropriate dump site to current location
    
    Args:
        current_location: Dict with 'lat' and 'lng' keys
        dump_sites: List of dump site dictionaries
        waste_type: Type of waste ('septic', 'grease', etc.)
    
    Returns:
        Best dump site dictionary or None if none available
    """
    
    if not dump_sites or not current_location.get('lat') or not current_location.get('lng'):
        return None
    
    # Filter active dump sites that accept the waste type
    suitable_sites = []
    for site in dump_sites:
        if not site.get('is_active', True):
            continue
            
        # Check if site accepts the waste type
        if waste_type == 'septic' and not site.get('accepts_septic_waste', True):
            continue
        if waste_type == 'grease' and not site.get('accepts_grease_waste', False):
            continue
            
        suitable_sites.append(site)
    
    if not suitable_sites:
        return None
    
    # Calculate distances and find nearest
    current_lat = current_location['lat']
    current_lng = current_location['lng']
    
    best_site = None
    min_distance = float('inf')
    
    for site in suitable_sites:
        # Parse GPS coordinates if available
        gps_coords = site.get('gps_coordinates', '')
        if gps_coords and ',' in gps_coords:
            try:
                site_lat, site_lng = map(float, gps_coords.split(','))
                # Simple distance calculation (not perfect but good enough for selection)
                distance = math.sqrt((current_lat - site_lat)**2 + (current_lng - site_lng)**2)
                
                if distance < min_distance:
                    min_distance = distance
                    best_site = site
                    
            except (ValueError, IndexError):
                continue
    
    # If no GPS coordinates available, return first suitable site
    return best_site or suitable_sites[0]

def optimize_route_with_dumps(truck: Dict, tickets: List[Dict], 
                            dump_sites: List[Dict]) -> List[Dict]:
    """
    Create optimized route including necessary dump stops
    
    Args:
        truck: Truck dictionary with capacity and current level
        tickets: List of ticket dictionaries in route order
        dump_sites: List of available dump sites
    
    Returns:
        List of route stops including customer jobs and dump sites
    """
    
    tank_capacity = truck.get('tank_capacity', 3000)
    current_level = truck.get('current_tank_level', 0)
    dump_threshold = truck.get('tank_full_threshold', 0.85)
    
    # Find where dumps are needed
    dump_points = find_dump_points(tank_capacity, current_level, dump_threshold, tickets)
    
    # Build route with dump stops inserted
    route_stops = []
    dump_index = 0
    
    for i, ticket in enumerate(tickets):
        # Check if we need a dump before this job
        if dump_index < len(dump_points) and dump_points[dump_index][0] == i:
            # Find nearest dump site (simplified - using first customer location as reference)
            current_location = {
                'lat': 38.25,  # Default Louisville area
                'lng': -85.75
            }
            
            dump_site = find_nearest_dump_site(current_location, dump_sites)
            if dump_site:
                route_stops.append({
                    'type': 'dump_site',
                    'dump_site_id': dump_site['id'],
                    'name': dump_site['name'],
                    'address': dump_site['full_address'],
                    'description': f"Dump at {dump_site['name']}",
                    'estimated_time': dump_site.get('estimated_dump_time', 15),
                    'icon': '🗑️',
                    'gallons_dumped': dump_points[dump_index][1]
                })
            dump_index += 1
        
        # Add the customer job
        route_stops.append({
            'type': 'customer_job',
            'ticket_id': ticket['id'],
            'job_id': ticket['job_id'],
            'customer_name': ticket.get('customer_name', 'Unknown'),
            'address': ticket.get('customer_address', ''),
            'service_type': ticket.get('service_type', ''),
            'estimated_gallons': ticket.get('estimated_gallons', 0),
            'estimated_duration': ticket.get('estimated_duration', 60),
            'description': f"{ticket.get('customer_name', 'Job')} - {ticket.get('service_type', '')}",
            'icon': '🏠'
        })
    
    return route_stops

def update_ticket_gallons_estimates(tickets: List[Dict]) -> List[Dict]:
    """
    Update estimated_gallons for tickets that don't have estimates
    
    Args:
        tickets: List of ticket dictionaries
    
    Returns:
        Updated list of tickets with estimated_gallons populated
    """
    
    updated_tickets = []
    
    for ticket in tickets:
        ticket_copy = ticket.copy()
        
        # Only estimate if not already set
        if not ticket_copy.get('estimated_gallons'):
            service_type = ticket_copy.get('service_type', '')
            estimated = estimate_gallons_for_job(service_type)
            ticket_copy['estimated_gallons'] = estimated
        
        updated_tickets.append(ticket_copy)
    
    return updated_tickets

# Tank status calculations
def get_tank_status(truck: Dict) -> Dict:
    """Get current tank status and capacity info"""
    capacity = truck.get('tank_capacity', 3000)
    current = truck.get('current_tank_level', 0)
    threshold = truck.get('tank_full_threshold', 0.85)
    
    fill_percentage = (current / capacity) * 100 if capacity else 0
    gallons_until_full = max(0, (capacity * threshold) - current)
    dump_recommended = fill_percentage >= (threshold * 100)
    
    return {
        'tank_capacity': capacity,
        'current_level': current,
        'fill_percentage': round(fill_percentage, 1),
        'gallons_until_full': round(gallons_until_full, 1),
        'dump_threshold_percentage': round(threshold * 100, 1),
        'dump_recommended': dump_recommended,
        'status': 'DUMP NEEDED' if dump_recommended else 'OK'
    }
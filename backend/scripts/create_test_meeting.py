#!/usr/bin/env python3
"""
Create Test Meeting Room Script
Generates a test appointment with Jitsi meeting room for video conference testing
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import SupabaseClient

# Initialize Supabase client
supabase = SupabaseClient()


def generate_meeting_room(doctor_uid, appointment_date=None, appointment_time=None):
    """Generate Jitsi meeting room name and URL"""
    if not appointment_date:
        appointment_date = datetime.now().strftime("%Y-%m-%d")
    if not appointment_time:
        appointment_time = datetime.now().strftime("%H:%M")
    
    safe_date = appointment_date.replace("-", "")
    safe_time = appointment_time.replace(":", "")
    room_suffix = uuid.uuid4().hex[:8]
    room_name = f"medichain-{doctor_uid}-{safe_date}-{safe_time}-{room_suffix}"
    meeting_url = f"https://meet.jit.si/{room_name}#config.prejoinPageEnabled=false&config.enableKnockingLobby=true&config.enableLobbyChat=true&config.membersOnly=false"
    
    return room_name, meeting_url


def create_test_appointment(doctor_uid, patient_uid, appointment_date=None, appointment_time=None):
    """Create a test appointment with meeting room"""
    # Use current time if not specified
    if not appointment_date:
        appointment_date = datetime.now().strftime("%Y-%m-%d")
    if not appointment_time:
        # Set to 5 minutes ago so it can be joined immediately
        appointment_time = (datetime.now() - timedelta(minutes=5)).strftime("%H:%M")
    
    room_name, meeting_url = generate_meeting_room(doctor_uid, appointment_date, appointment_time)
    
    # Create appointment data
    appointment_data = {
        "patient_firebase_uid": patient_uid,
        "doctor_firebase_uid": doctor_uid,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "appointment_type": "consultation",
        "meeting_link": meeting_url,
        "status": "scheduled",
        "notes": f"Test appointment for video conference testing. Meeting: {meeting_url}"
    }
    
    # Insert appointment
    response = supabase.service_client.table("appointments").insert(appointment_data).execute()
    
    if response.data:
        appointment = response.data[0]
        print(f"✅ Test appointment created successfully!")
        print(f"   Appointment ID: {appointment['id']}")
        print(f"   Room Name: {room_name}")
        print(f"   Meeting URL: {meeting_url}")
        print(f"   Frontend Route: /video/{room_name}")
        print(f"\n🔗 To test, navigate to: http://localhost:3000/video/{room_name}")
        return appointment
    else:
        print("❌ Failed to create appointment")
        return None


def update_existing_appointment(appointment_id, doctor_uid):
    """Update existing appointment with meeting room"""
    appointment_date = datetime.now().strftime("%Y-%m-%d")
    appointment_time = (datetime.now() - timedelta(minutes=5)).strftime("%H:%M")
    
    room_name, meeting_url = generate_meeting_room(doctor_uid, appointment_date, appointment_time)
    
    # Update appointment
    response = supabase.service_client.table("appointments").update({
        "meeting_link": meeting_url,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "status": "scheduled"
    }).eq("id", appointment_id).execute()
    
    if response.data:
        appointment = response.data[0]
        print(f"✅ Appointment updated successfully!")
        print(f"   Appointment ID: {appointment['id']}")
        print(f"   Room Name: {room_name}")
        print(f"   Meeting URL: {meeting_url}")
        print(f"   Frontend Route: /video/{room_name}")
        print(f"\n🔗 To test, navigate to: http://localhost:3000/video/{room_name}")
        return appointment
    else:
        print("❌ Failed to update appointment")
        return None


if __name__ == "__main__":
    load_dotenv()
    
    # Example usage
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Create new appointment: python create_test_meeting.py <doctor_uid> <patient_uid>")
        print("  Update existing: python create_test_meeting.py --update <appointment_id> <doctor_uid>")
        print("\nExample:")
        print("  python create_test_meeting.py Bm6UWulzevUcte17xElckmGCJbb2 patient123")
        sys.exit(1)
    
    if sys.argv[1] == "--update":
        appointment_id = sys.argv[2]
        doctor_uid = sys.argv[3]
        update_existing_appointment(appointment_id, doctor_uid)
    else:
        doctor_uid = sys.argv[1]
        patient_uid = sys.argv[2]
        create_test_appointment(doctor_uid, patient_uid)


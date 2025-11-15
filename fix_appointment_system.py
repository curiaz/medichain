"""
Fix doctor verification status and set up appointment system
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from supabase import create_client
from datetime import date, timedelta

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  FIXING APPOINTMENT SYSTEM AFTER SUPABASE RESTART")
print("="*70 + "\n")

# 1. Approve all pending doctors
print("Step 1: Approving doctors...")
try:
    # Update doctor_profiles
    result = client.table('doctor_profiles').update({
        'verification_status': 'approved'
    }).eq('verification_status', 'pending').execute()
    
    print(f"✅ Updated {len(result.data) if result.data else 0} doctor profiles to approved")
    
    # Also update user_profiles
    result2 = client.table('user_profiles').update({
        'verification_status': 'approved'
    }).eq('role', 'doctor').eq('verification_status', 'pending').execute()
    
    print(f"✅ Updated {len(result2.data) if result2.data else 0} user profiles to approved")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Set up availability for doctors
print("\nStep 2: Setting up doctor availability...")
try:
    # Get all approved doctors
    doctors = client.table('doctor_profiles').select('firebase_uid, specialization, availability').eq('verification_status', 'approved').execute()
    
    for doc in doctors.data:
        uid = doc['firebase_uid']
        current_availability = doc.get('availability', [])
        
        # Check if availability is empty or old format
        if not current_availability or not isinstance(current_availability, list):
            # Create new availability for next 7 days
            new_availability = []
            for i in range(1, 8):
                future_date = (date.today() + timedelta(days=i)).isoformat()
                new_availability.append({
                    'date': future_date,
                    'time_slots': ['09:00:00', '10:00:00', '11:00:00', '14:00:00', '15:00:00', '16:00:00']
                })
            
            # Update doctor profile
            client.table('doctor_profiles').update({
                'availability': new_availability
            }).eq('firebase_uid', uid).execute()
            
            print(f"✅ Set availability for doctor {uid}")
        else:
            print(f"✅ Doctor {uid} already has availability")
            
except Exception as e:
    print(f"❌ Error setting availability: {e}")

# 3. Test appointment creation
print("\nStep 3: Testing appointment creation...")
try:
    # Get a patient
    patients = client.table('user_profiles').select('firebase_uid, email').eq('role', 'patient').limit(1).execute()
    
    # Get an approved doctor with availability
    doctors = client.table('doctor_profiles').select('firebase_uid, availability').eq('verification_status', 'approved').execute()
    
    if patients.data and doctors.data:
        patient_uid = patients.data[0]['firebase_uid']
        doctor_uid = doctors.data[0]['firebase_uid']
        availability = doctors.data[0].get('availability', [])
        
        print(f"Patient: {patients.data[0]['email']}")
        print(f"Doctor: {doctor_uid}")
        
        if availability and isinstance(availability, list) and len(availability) > 0:
            # Use first available slot
            test_date = availability[0]['date']
            test_time = availability[0]['time_slots'][0]
            
            print(f"Testing slot: {test_date} at {test_time}")
            
            # Create test appointment
            appointment_data = {
                'patient_firebase_uid': patient_uid,
                'doctor_firebase_uid': doctor_uid,
                'appointment_date': test_date,
                'appointment_time': test_time,
                'appointment_type': 'general-practitioner',
                'notes': 'Test appointment after Supabase restart',
                'status': 'scheduled'
            }
            
            result = client.table('appointments').insert(appointment_data).execute()
            
            if result.data:
                appt_id = result.data[0]['id']
                print(f"✅ Test appointment created! ID: {appt_id}")
                
                # Remove the time slot from availability
                updated_availability = []
                for slot in availability:
                    if slot['date'] == test_date:
                        remaining_times = [t for t in slot['time_slots'] if t != test_time]
                        if remaining_times:
                            updated_availability.append({
                                'date': slot['date'],
                                'time_slots': remaining_times
                            })
                    else:
                        updated_availability.append(slot)
                
                # Update doctor availability
                client.table('doctor_profiles').update({
                    'availability': updated_availability
                }).eq('firebase_uid', doctor_uid).execute()
                
                print(f"✅ Time slot removed from doctor availability")
                
                # Clean up test appointment
                client.table('appointments').delete().eq('id', appt_id).execute()
                print(f"✅ Test appointment cleaned up")
                
                # Restore the time slot
                client.table('doctor_profiles').update({
                    'availability': availability
                }).eq('firebase_uid', doctor_uid).execute()
                print(f"✅ Doctor availability restored")
            else:
                print(f"❌ Failed to create appointment")
        else:
            print(f"⚠️  No availability found for doctor")
    else:
        print(f"⚠️  Insufficient test data")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("  SUMMARY")
print("="*70 + "\n")

# Final status check
try:
    approved_docs = client.table('doctor_profiles').select('firebase_uid').eq('verification_status', 'approved').execute()
    appointments = client.table('appointments').select('id').execute()
    
    print(f"✅ Approved doctors: {len(approved_docs.data) if approved_docs.data else 0}")
    print(f"✅ Total appointments: {len(appointments.data) if appointments.data else 0}")
    print(f"\n✅ Appointment system is ready!")
    print(f"\n📋 You can now:")
    print(f"   - Access API at: http://localhost:5000/api/appointments")
    print(f"   - Book appointments through the frontend")
    print(f"   - View approved doctors at: http://localhost:5000/api/appointments/doctors/approved")
    
except Exception as e:
    print(f"Error in summary: {e}")

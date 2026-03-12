#!/usr/bin/env python3
"""
Test script to simulate booking an appointment with symptoms
This will test the full flow: booking → AI processing → data retrieval
"""

import os
import sys
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from db.supabase_client import SupabaseClient
from datetime import datetime, timedelta

def test_booking_with_symptoms():
    """Test creating an appointment with symptoms and verifying AI processing"""
    
    print("=" * 60)
    print("Testing Booking with Symptoms Flow")
    print("=" * 60)
    
    # Initialize Supabase client
    try:
        supabase = SupabaseClient()
        if not supabase.service_client:
            print("❌ ERROR: Supabase service_client not initialized")
            return False
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize Supabase client: {e}")
        return False
    
    # Get a test patient and doctor UID
    print("\n1. Finding test patient and doctor...")
    try:
        # Get a patient
        patients = supabase.service_client.table("user_profiles").select("firebase_uid").eq("role", "patient").limit(1).execute()
        if not patients.data:
            print("❌ No patients found in database")
            return False
        patient_uid = patients.data[0]["firebase_uid"]
        print(f"✅ Found patient: {patient_uid[:20]}...")
        
        # Get a doctor
        doctors = supabase.service_client.table("user_profiles").select("firebase_uid").eq("role", "doctor").limit(1).execute()
        if not doctors.data:
            print("❌ No doctors found in database")
            return False
        doctor_uid = doctors.data[0]["firebase_uid"]
        print(f"✅ Found doctor: {doctor_uid[:20]}...")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to find test users: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Create test appointment with symptoms
    print("\n2. Creating test appointment with symptoms...")
    try:
        # Future date
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        future_time = "10:00"
        
        appointment_data = {
            "patient_firebase_uid": patient_uid,
            "doctor_firebase_uid": doctor_uid,
            "appointment_date": future_date,
            "appointment_time": future_time,
            "appointment_type": "consultation",
            "status": "scheduled",
            "symptoms": ["Headache", "Fever", "Fatigue", "Cough"],
            "documents": [
                {
                    "name": "test_lab_results.pdf",
                    "size": 102400,
                    "type": "application/pdf"
                }
            ],
            "notes": "Test appointment with symptoms for AI diagnosis testing",
            "ai_diagnosis_processed": False
        }
        
        result = supabase.service_client.table("appointments").insert(appointment_data).execute()
        
        if not result.data:
            print("❌ Failed to create appointment")
            return False
        
        appointment_id = result.data[0]["id"]
        print(f"✅ Created test appointment: {appointment_id}")
        print(f"   Date: {future_date} at {future_time}")
        print(f"   Symptoms: {appointment_data['symptoms']}")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create appointment: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test AI processing (simulate what backend does)
    print("\n3. Testing AI diagnosis processing...")
    try:
        from app import StreamlinedAIDiagnosis
        
        # Initialize AI system
        print("   Initializing AI system...")
        ai_system = StreamlinedAIDiagnosis()
        
        # Process symptoms
        symptoms_text = ", ".join(appointment_data["symptoms"])
        print(f"   Processing symptoms: {symptoms_text}")
        
        predictions = ai_system.predict_conditions(symptoms_text)
        
        if predictions and len(predictions) > 0:
            print(f"   ✅ Got {len(predictions)} predictions")
            
            # Get detailed results
            detailed_results = []
            for pred in predictions[:3]:  # Top 3
                condition = pred.get('condition', '')
                reason = ai_system.get_condition_reason(condition)
                action_data = ai_system.get_recommended_action_and_medication(condition)
                
                detailed_results.append({
                    'condition': condition,
                    'confidence': pred.get('confidence', 0),
                    'confidence_percent': pred.get('confidence_percent', '0%'),
                    'reason': reason,
                    'recommended_action': action_data.get('recommended_action', ''),
                    'medication': action_data.get('medication', ''),
                    'dosage': action_data.get('dosage', ''),
                })
            
            # Update appointment with AI diagnosis
            ai_diagnosis_data = {
                'primary_condition': predictions[0].get('condition', ''),
                'confidence_score': predictions[0].get('confidence', 0),
                'detailed_results': detailed_results,
                'symptoms_analyzed': appointment_data["symptoms"],
                'processed_at': datetime.utcnow().isoformat()
            }
            
            print(f"   Primary condition: {ai_diagnosis_data['primary_condition']}")
            print(f"   Confidence: {ai_diagnosis_data['confidence_score']:.2%}")
            
            # Update appointment
            update_result = supabase.service_client.table("appointments").update({
                "ai_diagnosis": ai_diagnosis_data,
                "ai_diagnosis_processed": True,
                "ai_diagnosis_processed_at": datetime.utcnow().isoformat()
            }).eq("id", appointment_id).execute()
            
            print(f"   ✅ AI diagnosis stored in appointment")
            
        else:
            print("   ⚠️  No predictions returned from AI system")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to process AI diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test fetching the appointment (simulating doctor schedule view)
    print("\n4. Testing appointment data retrieval (doctor schedule view)...")
    try:
        # Fetch as doctor would
        fetched_appts = supabase.service_client.table("appointments").select("*").eq("doctor_firebase_uid", doctor_uid).eq("id", appointment_id).execute()
        
        if not fetched_appts.data:
            print("❌ Appointment not found")
            return False
        
        appt = fetched_appts.data[0]
        
        print(f"   ✅ Appointment retrieved successfully")
        print(f"   - Has symptoms: {bool(appt.get('symptoms'))}")
        print(f"   - Has documents: {bool(appt.get('documents'))}")
        print(f"   - Has AI diagnosis: {bool(appt.get('ai_diagnosis'))}")
        print(f"   - AI processed: {appt.get('ai_diagnosis_processed', False)}")
        
        if appt.get('symptoms'):
            print(f"   - Symptoms: {appt['symptoms']}")
        
        if appt.get('ai_diagnosis'):
            ai_data = appt['ai_diagnosis']
            print(f"   - Primary condition: {ai_data.get('primary_condition')}")
            print(f"   - Confidence: {ai_data.get('confidence_score', 0):.2%}")
            
            if ai_data.get('detailed_results'):
                print(f"   - Detailed results: {len(ai_data['detailed_results'])} conditions")
                for i, result in enumerate(ai_data['detailed_results'][:2], 1):
                    print(f"     {i}. {result.get('condition')} ({result.get('confidence_percent')})")
        
        # Verify all required fields are present for frontend
        required_fields = ['symptoms', 'documents', 'ai_diagnosis', 'ai_diagnosis_processed']
        missing_fields = [f for f in required_fields if f not in appt]
        
        if missing_fields:
            print(f"   ⚠️  Missing fields: {missing_fields}")
        else:
            print(f"   ✅ All required fields present for frontend display")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to fetch appointment: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ Full flow test completed successfully!")
    print("=" * 60)
    print(f"\nTest appointment ID: {appointment_id}")
    print("You can now check the doctor schedule page to see the AI diagnosis display.")
    
    return True

if __name__ == "__main__":
    success = test_booking_with_symptoms()
    sys.exit(0 if success else 1)


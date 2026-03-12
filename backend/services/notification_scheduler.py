"""
Notification Scheduler Service
Handles scheduled notifications for appointments (e.g., Video Consultation Ready at appointment time)
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from db.supabase_client import SupabaseClient
from services.notification_service import NotificationService
import pytz
import atexit

# Initialize scheduler
scheduler = BackgroundScheduler(timezone='Asia/Manila')
scheduler.start()

# Initialize services
notification_service = NotificationService()
supabase_client = SupabaseClient()

# Store scheduler instance to prevent garbage collection
_scheduler_instance = scheduler

def schedule_video_consultation_notification(appointment_id, appointment_date, appointment_time, 
                                            patient_uid, doctor_uid, doctor_name, patient_name, 
                                            meeting_url, send_before_minutes=0):
    """
    Schedule a "Video Consultation Ready" notification to be sent at the appointment time
    
    Args:
        appointment_id: Appointment ID
        appointment_date: Appointment date (YYYY-MM-DD)
        appointment_time: Appointment time (HH:MM)
        patient_uid: Patient Firebase UID
        doctor_uid: Doctor Firebase UID
        doctor_name: Doctor's name
        patient_name: Patient's name
        meeting_url: Jitsi meeting URL
        send_before_minutes: Minutes before appointment to send notification (default: 0 = at appointment time)
    """
    try:
        # Parse appointment datetime
        appointment_datetime_str = f"{appointment_date} {appointment_time}"
        appointment_datetime = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M")
        
        # Convert to Manila timezone
        try:
            manila_tz = pytz.timezone('Asia/Manila')
            # Assume the appointment datetime is in Manila timezone
            appointment_datetime = manila_tz.localize(appointment_datetime)
        except:
            # If timezone already applied or error, use as is
            pass
        
        # Calculate when to send the notification (appointment time minus send_before_minutes)
        notification_time = appointment_datetime - timedelta(minutes=send_before_minutes)
        
        # Ensure current_time is timezone-aware if appointment_datetime is timezone-aware
        if hasattr(appointment_datetime, 'tzinfo') and appointment_datetime.tzinfo:
            current_time = datetime.now(manila_tz)
        else:
            current_time = datetime.now()
        
        # Calculate how many minutes until/past the appointment
        time_diff = notification_time - current_time
        minutes_diff = time_diff.total_seconds() / 60
        
        # Only schedule if the notification time is in the future
        if minutes_diff > 0:
            print(f"📅 Scheduling Video Consultation Ready notification:")
            print(f"   Appointment ID: {appointment_id}")
            print(f"   Appointment time: {appointment_datetime}")
            print(f"   Notification time: {notification_time}")
            print(f"   Current time: {current_time}")
            print(f"   Minutes until notification: {minutes_diff:.1f}")
            
            # Schedule patient notification
            scheduler.add_job(
                func=_send_video_consultation_notification,
                trigger=DateTrigger(run_date=notification_time),
                args=[appointment_id, appointment_date, appointment_time, patient_uid, doctor_name, None, meeting_url, 'patient'],
                id=f"video_ready_patient_{appointment_id}",
                replace_existing=True
            )
            
            # Schedule doctor notification
            scheduler.add_job(
                func=_send_video_consultation_notification,
                trigger=DateTrigger(run_date=notification_time),
                args=[appointment_id, appointment_date, appointment_time, doctor_uid, None, patient_name, meeting_url, 'doctor'],
                id=f"video_ready_doctor_{appointment_id}",
                replace_existing=True
            )
            
            print(f"✅ Scheduled notifications for appointment {appointment_id} at {notification_time}")
            return True
        elif minutes_diff >= -15:
            # Appointment time has passed, but within the last 15 minutes - send immediately
            # This handles cases where the appointment was just confirmed and the time has just passed
            print(f"⚠️  Appointment time has passed ({-minutes_diff:.1f} minutes ago), but within 15-minute window. Sending notification immediately.")
            _send_video_consultation_notification(appointment_id, appointment_date, appointment_time, 
                                                 patient_uid, doctor_name, None, meeting_url, 'patient')
            _send_video_consultation_notification(appointment_id, appointment_date, appointment_time, 
                                                 doctor_uid, None, patient_name, meeting_url, 'doctor')
            return True
        else:
            # Appointment time has passed more than 15 minutes ago - don't send notification
            print(f"⚠️  Cannot schedule notification: appointment time ({notification_time}) passed {-minutes_diff:.1f} minutes ago. Too late to send notification.")
            return False
            
    except Exception as e:
        print(f"❌ Error scheduling video consultation notification: {e}")
        import traceback
        traceback.print_exc()
        return False

def _send_video_consultation_notification(appointment_id, appointment_date, appointment_time, 
                                         user_uid, doctor_name, patient_name, meeting_url, user_type):
    """
    Internal function to send video consultation notification
    Called by the scheduler at the scheduled time
    """
    try:
        print(f"📹 Sending scheduled Video Consultation Ready notification:")
        print(f"   Appointment ID: {appointment_id}")
        print(f"   User UID: {user_uid}")
        print(f"   User Type: {user_type}")
        print(f"   Meeting URL: {meeting_url}")
        
        # Format date and time for display
        try:
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except:
            formatted_date = appointment_date
        
        try:
            time_obj = datetime.strptime(appointment_time, "%H:%M")
            formatted_time = time_obj.strftime("%I:%M %p")
        except:
            formatted_time = appointment_time
        
        # Send notification
        if user_type == 'patient':
            notification_service.create_video_call_notification(
                user_id=user_uid,
                appointment_id=appointment_id,
                appointment_date=formatted_date,
                appointment_time=formatted_time,
                doctor_name=doctor_name,
                meeting_url=meeting_url,
                notification_type='video_call_ready'
            )
        else:  # doctor
            notification_service.create_video_call_notification(
                user_id=user_uid,
                appointment_id=appointment_id,
                appointment_date=formatted_date,
                appointment_time=formatted_time,
                patient_name=patient_name,
                meeting_url=meeting_url,
                notification_type='video_call_ready'
            )
        
        print(f"✅ Successfully sent Video Consultation Ready notification to {user_type} {user_uid}")
        
    except Exception as e:
        print(f"❌ Error sending scheduled video consultation notification: {e}")
        import traceback
        traceback.print_exc()

def cancel_scheduled_notification(appointment_id):
    """
    Cancel scheduled notifications for an appointment
    """
    try:
        scheduler.remove_job(f"video_ready_patient_{appointment_id}")
        scheduler.remove_job(f"video_ready_doctor_{appointment_id}")
        print(f"✅ Cancelled scheduled notifications for appointment {appointment_id}")
        return True
    except Exception as e:
        print(f"⚠️  Error cancelling scheduled notification (may not exist): {e}")
        return False

def get_scheduled_jobs():
    """
    Get all scheduled jobs (for debugging)
    """
    jobs = scheduler.get_jobs()
    return [{"id": job.id, "next_run_time": str(job.next_run_time)} for job in jobs]

# Shutdown scheduler when application exits
atexit.register(lambda: scheduler.shutdown())



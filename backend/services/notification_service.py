"""
Notification Service for Supabase
Handles creating notifications in Supabase database
"""

from db.supabase_client import SupabaseClient
from datetime import datetime, timedelta
import json

class NotificationService:
    """Service for creating and managing notifications in Supabase"""
    
    def __init__(self):
        try:
            self.supabase = SupabaseClient()
            print("✅ NotificationService initialized")
        except Exception as e:
            print(f"❌ Error initializing NotificationService: {e}")
            self.supabase = None
    
    def create_notification(self, user_id, title, message, notification_type='info', 
                          category='general', priority='normal', action_url=None, 
                          action_label=None, metadata=None, expires_at=None):
        """
        Create a notification in Supabase
        
        Args:
            user_id: Firebase UID of the user
            title: Notification title
            message: Notification message
            notification_type: Type (info, success, warning, error, alert)
            category: Category (general, medical, appointment, system, etc.)
            priority: Priority (low, normal, high, urgent)
            action_url: Optional URL to navigate to
            action_label: Optional label for action button
            metadata: Optional JSON metadata
            expires_at: Optional expiration datetime
        """
        if not self.supabase:
            print("⚠️  NotificationService not available, skipping notification creation")
            return {"success": False, "error": "Notification service unavailable"}
        
        try:
            notification_data = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "category": category,
                "priority": priority,
                "is_read": False,
                "is_archived": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if action_url:
                notification_data["action_url"] = action_url
            if action_label:
                notification_data["action_label"] = action_label
            if metadata:
                notification_data["metadata"] = json.dumps(metadata) if isinstance(metadata, dict) else metadata
            if expires_at:
                notification_data["expires_at"] = expires_at.isoformat() if hasattr(expires_at, 'isoformat') else expires_at
            
            # Use service_client to bypass RLS for system notifications
            response = self.supabase.service_client.table("notifications").insert(notification_data).execute()
            
            if response.data:
                print(f"✅ Notification created for user {user_id}: {title}")
                return {"success": True, "notification": response.data[0]}
            else:
                print(f"❌ Failed to create notification for user {user_id}")
                return {"success": False, "error": "Failed to create notification"}
                
        except Exception as e:
            print(f"❌ Error creating notification: {e}")
            return {"success": False, "error": str(e)}
    
    def create_appointment_notification(self, user_id, appointment_id, appointment_date, 
                                       appointment_time, doctor_name=None, patient_name=None,
                                       notification_type='appointment_created', meeting_url=None):
        """
        Create appointment-related notification
        
        Args:
            user_id: Firebase UID of recipient
            appointment_id: Appointment ID
            appointment_date: Appointment date
            appointment_time: Appointment time
            doctor_name: Doctor's name (for patient notifications)
            patient_name: Patient's name (for doctor notifications)
            notification_type: Type of notification (appointment_created, appointment_reminder, etc.)
            meeting_url: Jitsi meeting URL
        """
        if notification_type == 'appointment_created':
            if doctor_name:
                # Patient notification
                title = "Appointment Scheduled"
                message = f"Your appointment with {doctor_name} is scheduled for {appointment_date} at {appointment_time}"
            else:
                # Doctor notification
                title = "New Appointment Request"
                message = f"You have a new appointment with {patient_name} on {appointment_date} at {appointment_time}"
            
            metadata = {
                "appointment_id": str(appointment_id),
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "meeting_url": meeting_url
            }
            
            action_url = f"/appointments/{appointment_id}" if appointment_id else "/appointments"
            action_label = "View Appointment"
            
            return self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type='info',
                category='appointment',
                priority='high',
                action_url=action_url,
                action_label=action_label,
                metadata=metadata
            )
        
        elif notification_type == 'appointment_reminder':
            if doctor_name:
                title = "Appointment Reminder"
                message = f"Reminder: Your appointment with {doctor_name} is tomorrow at {appointment_time}"
            else:
                title = "Appointment Reminder"
                message = f"Reminder: You have an appointment with {patient_name} tomorrow at {appointment_time}"
            
            metadata = {
                "appointment_id": str(appointment_id),
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "meeting_url": meeting_url
            }
            
            return self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type='warning',
                category='appointment',
                priority='high',
                action_url=meeting_url or f"/appointments/{appointment_id}",
                action_label="Join Meeting" if meeting_url else "View Appointment",
                metadata=metadata
            )
        
        elif notification_type == 'appointment_starting':
            if doctor_name:
                title = "Appointment Starting Soon"
                message = f"Your appointment with {doctor_name} is starting in 5 minutes. Click to join the video call."
            else:
                title = "Appointment Starting Soon"
                message = f"Your appointment with {patient_name} is starting in 5 minutes. Click to join the video call."
            
            metadata = {
                "appointment_id": str(appointment_id),
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "meeting_url": meeting_url
            }
            
            return self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type='alert',
                category='appointment',
                priority='urgent',
                action_url=meeting_url,
                action_label="Join Now",
                metadata=metadata
            )
        
        return {"success": False, "error": "Unknown notification type"}
    
    def create_video_call_notification(self, user_id, appointment_id, appointment_date, 
                                      appointment_time, doctor_name=None, patient_name=None,
                                      meeting_url=None, notification_type='video_call_ready'):
        """
        Create video consultation call notification
        
        Args:
            user_id: Firebase UID of recipient
            appointment_id: Appointment ID
            appointment_date: Appointment date
            appointment_time: Appointment time
            doctor_name: Doctor's name (for patient notifications)
            patient_name: Patient's name (for doctor notifications)
            meeting_url: Jitsi meeting URL
            notification_type: Type of notification (video_call_ready, video_call_starting, etc.)
        """
        if notification_type == 'video_call_ready':
            if doctor_name:
                # Patient notification
                title = "Video Consultation Ready"
                message = f"Your video consultation with {doctor_name} is ready. Click to join the call."
            else:
                # Doctor notification
                title = "Video Consultation Ready"
                message = f"Your video consultation with {patient_name} is ready. Click to join the call."
            
            metadata = {
                "appointment_id": str(appointment_id),
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "meeting_url": meeting_url,
                "notification_type": "video_call"
            }
            
            return self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type='info',
                category='appointment',
                priority='high',
                action_url=meeting_url,
                action_label="Join Video Call",
                metadata=metadata
            )
        
        elif notification_type == 'video_call_starting':
            if doctor_name:
                title = "Video Call Starting Now"
                message = f"Your video consultation with {doctor_name} is starting now. Click to join immediately."
            else:
                title = "Video Call Starting Now"
                message = f"Your video consultation with {patient_name} is starting now. Click to join immediately."
            
            metadata = {
                "appointment_id": str(appointment_id),
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "meeting_url": meeting_url,
                "notification_type": "video_call"
            }
            
            return self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type='alert',
                category='appointment',
                priority='urgent',
                action_url=meeting_url,
                action_label="Join Now",
                metadata=metadata
            )
        
        elif notification_type == 'video_call_reminder':
            if doctor_name:
                title = "Video Consultation Reminder"
                message = f"Reminder: Your video consultation with {doctor_name} is scheduled for {appointment_date} at {appointment_time}."
            else:
                title = "Video Consultation Reminder"
                message = f"Reminder: Your video consultation with {patient_name} is scheduled for {appointment_date} at {appointment_time}."
            
            metadata = {
                "appointment_id": str(appointment_id),
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "meeting_url": meeting_url,
                "notification_type": "video_call"
            }
            
            return self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type='warning',
                category='appointment',
                priority='high',
                action_url=meeting_url or f"/appointments/{appointment_id}",
                action_label="View Details",
                metadata=metadata
            )
        
        return {"success": False, "error": "Unknown video call notification type"}

# Global instance
notification_service = NotificationService()


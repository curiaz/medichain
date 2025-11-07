import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import '../assets/styles/JitsiVideoConference.css';

/**
 * Jitsi Video Conference Component
 * Embeds Jitsi Meet for video consultations
 * Shows appointment info and countdown before joining
 */
const JitsiVideoConference = () => {
  const { roomName } = useParams();
  const navigate = useNavigate();
  const { user, getFirebaseToken } = useAuth();
  const jitsiContainerRef = useRef(null);
  const apiRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [appointmentInfo, setAppointmentInfo] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [canJoin, setCanJoin] = useState(false);
  const [timeUntilAppointment, setTimeUntilAppointment] = useState(null);

  // Fetch appointment information based on room name
  useEffect(() => {
    const fetchAppointmentInfo = async () => {
      if (!roomName) {
        setError("No room name provided");
        setLoading(false);
        return;
      }

      try {
        // Get token for authentication
        let token = null;
        try {
          if (getFirebaseToken) {
            token = await getFirebaseToken();
          }
        } catch (authError) {
          console.warn("Could not get Firebase token via AuthContext:", authError);
        }

        if (!token) {
          const storedFirebaseToken = sessionStorage.getItem('firebase_id_token') || 
                                      localStorage.getItem('firebase_id_token');
          token = storedFirebaseToken;
        }

        if (!token) {
          token = localStorage.getItem('medichain_token');
        }

        if (!token) {
          setError("Please log in to join the video consultation");
          setLoading(false);
          return;
        }

        // Fetch appointments to find the one matching this room
        const response = await axios.get('http://localhost:5000/api/appointments', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data?.success && response.data?.appointments) {
          // Find appointment with matching meeting_link or room name
          const appointment = response.data.appointments.find(appt => {
            const meetingLink = appt.meeting_link || appt.meeting_url || '';
            return meetingLink.includes(roomName) || meetingLink.endsWith(roomName);
          });

          if (appointment) {
            setAppointmentInfo(appointment);
            
            // Parse appointment date and time
            let appointmentDate = appointment.appointment_date;
            let appointmentTime = appointment.appointment_time || "00:00";
            
            if (typeof appointmentDate === 'string') {
              appointmentDate = appointmentDate.split('T')[0];
            }
            
            if (typeof appointmentTime === 'string') {
              appointmentTime = appointmentTime.substring(0, 5);
            }
            
            // Create datetime object
            const appointmentDateTime = new Date(`${appointmentDate}T${appointmentTime.padStart(5, "0")}:00`);
            const now = new Date();
            
            // Calculate time difference
            const diffMs = appointmentDateTime - now;
            const diffMinutes = Math.floor(diffMs / (1000 * 60));
            
            // If appointment is in the past or more than 15 minutes away, allow joining (late comers)
            if (diffMs <= 0 || diffMinutes <= -15) {
              setCanJoin(true);
              setTimeUntilAppointment(null);
            } else if (diffMinutes <= 15) {
              // Within 15 minutes - show countdown
              setTimeUntilAppointment(diffMs);
              // Start countdown timer
              const countdownInterval = setInterval(() => {
                const newDiffMs = appointmentDateTime - new Date();
                if (newDiffMs <= 0) {
                  setCanJoin(true);
                  setTimeUntilAppointment(null);
                  clearInterval(countdownInterval);
                } else {
                  setTimeUntilAppointment(newDiffMs);
                }
              }, 1000);
              
              // Cleanup interval on unmount
              return () => clearInterval(countdownInterval);
            } else {
              // More than 15 minutes away
              setTimeUntilAppointment(diffMs);
            }
          } else {
            // Appointment not found, allow joining anyway (late comers)
            setCanJoin(true);
          }
        } else {
          // Could not fetch appointments, allow joining anyway
          setCanJoin(true);
        }
      } catch (err) {
        console.error('Error fetching appointment info:', err);
        // Allow joining even if fetch fails (late comers can still enter)
        setCanJoin(true);
      } finally {
        setLoading(false);
      }
    };

    fetchAppointmentInfo();
  }, [roomName, getFirebaseToken]);

  // Format countdown time
  const formatCountdown = (ms) => {
    if (ms <= 0) return '00:00';
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  };

  // Format appointment date and time
  const formatAppointmentDateTime = () => {
    if (!appointmentInfo) return null;
    
    let appointmentDate = appointmentInfo.appointment_date;
    let appointmentTime = appointmentInfo.appointment_time || "00:00";
    
    if (typeof appointmentDate === 'string') {
      appointmentDate = appointmentDate.split('T')[0];
    }
    
    if (typeof appointmentTime === 'string') {
      appointmentTime = appointmentTime.substring(0, 5);
    }
    
    try {
      const dateStr = `${appointmentDate}T${appointmentTime.padStart(5, "0")}:00`;
      const d = new Date(dateStr);
      if (!isNaN(d.getTime())) {
        const formattedDate = d.toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
        const formattedTime = d.toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: true 
        });
        return { date: formattedDate, time: formattedTime };
      }
    } catch (e) {
      console.error('Error parsing date:', e);
    }
    
    return { date: appointmentDate, time: appointmentTime };
  };

  // Initialize Jitsi when can join
  useEffect(() => {
    if (!canJoin || !roomName || !jitsiContainerRef.current) {
      return;
    }

    // Load Jitsi Meet API
    const loadJitsiScript = () => {
      if (window.JitsiMeetExternalAPI) {
        initializeJitsi();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://meet.jit.si/external_api.js';
      script.async = true;
      script.onload = initializeJitsi;
      script.onerror = () => {
        setError("Failed to load Jitsi Meet API. Please check your internet connection.");
        setLoading(false);
      };
      document.body.appendChild(script);
    };

    const initializeJitsi = () => {
      if (!jitsiContainerRef.current || !roomName || !window.JitsiMeetExternalAPI) {
        return;
      }

      try {
        const domain = 'meet.jit.si';
        
        // Get user display name
        const displayName = user?.profile 
          ? `${user.profile.first_name || ''} ${user.profile.last_name || ''}`.trim() || 'MediChain User'
          : user?.email?.split('@')[0] || 'MediChain User';

        const options = {
          roomName: roomName,
          parentNode: jitsiContainerRef.current,
          width: '100%',
          height: '100%',
          configOverwrite: {
            prejoinPageEnabled: true,
            startWithAudioMuted: false,
            startWithVideoMuted: false,
            enableWelcomePage: false,
            enableClosePage: true,
            disableDeepLinking: true,
            enableNoAudioDetection: true,
            enableNoisyMicDetection: true,
            enableLayerSuspension: true,
            enableInsecureRoomNameWarning: false,
            enableDisplayNameInStats: true,
            enableLocalVideoFlip: true,
            enableRemb: true,
            enableTcc: true,
            enableP2P: true,
            p2p: {
              enabled: true,
              stunServers: [
                { urls: 'stun:stun.l.google.com:19302' }
              ]
            },
            analytics: {
              disabled: true
            }
          },
          interfaceConfigOverwrite: {
            TOOLBAR_BUTTONS: [
              'microphone',
              'camera',
              'closedcaptions',
              'desktop',
              'fullscreen',
              'fodeviceselection',
              'hangup',
              'profile',
              'recording',
              'settings',
              'raisehand',
              'videoquality',
              'filmstrip',
              'feedback',
              'stats',
              'shortcuts',
              'tileview',
              'videobackgroundblur',
              'download',
              'help',
              'mute-everyone',
              'security'
            ],
            SETTINGS_SECTIONS: ['devices', 'language', 'moderator', 'profile'],
            SHOW_JITSI_WATERMARK: false,
            SHOW_WATERMARK_FOR_GUESTS: false,
            SHOW_BRAND_WATERMARK: false,
            BRAND_WATERMARK_LINK: '',
            SHOW_POWERED_BY: false,
            DISPLAY_WELCOME_PAGE_CONTENT: false,
            DISPLAY_WELCOME_PAGE_TOOLBAR_ADDITIONAL_CONTENT: false,
            APP_NAME: 'MediChain',
            NATIVE_APP_NAME: 'MediChain',
            PROVIDER_NAME: 'MediChain',
            DEFAULT_BACKGROUND: '#000000',
            DEFAULT_LOCAL_DISPLAY_NAME: 'Me',
            DEFAULT_REMOTE_DISPLAY_NAME: 'Participant'
          },
          userInfo: {
            displayName: displayName,
            email: user?.email || ''
          },
        };

        apiRef.current = new window.JitsiMeetExternalAPI(domain, options);

        // Event handlers
        apiRef.current.addEventListeners({
          readyToClose: () => {
            console.log('Jitsi: Ready to close');
            handleClose();
          },
          participantLeft: (participant) => {
            console.log('Jitsi: Participant left:', participant);
          },
          participantJoined: (participant) => {
            console.log('Jitsi: Participant joined:', participant);
          },
          videoConferenceJoined: (data) => {
            console.log('Jitsi: Video conference joined', data);
            setLoading(false);
          },
          videoConferenceLeft: () => {
            console.log('Jitsi: Video conference left');
            handleClose();
          },
          audioMuteStatusChanged: (data) => {
            console.log('Jitsi: Audio mute status changed', data);
          },
          videoMuteStatusChanged: (data) => {
            console.log('Jitsi: Video mute status changed', data);
          },
          raiseHandUpdated: (data) => {
            console.log('Jitsi: Raise hand updated', data);
          },
          errorOccurred: (error) => {
            console.error('Jitsi: Error occurred', error);
            setError("An error occurred in the video conference. Please try again.");
            setLoading(false);
          }
        });

        setLoading(false);
      } catch (error) {
        console.error('Error initializing Jitsi:', error);
        setError("Failed to initialize video conference. Please try again.");
        setLoading(false);
      }
    };

    loadJitsiScript();

    // Cleanup
    return () => {
      if (apiRef.current) {
        try {
          apiRef.current.dispose();
        } catch (error) {
          console.error('Error disposing Jitsi:', error);
        }
      }
    };
  }, [canJoin, roomName, user]);

  const handleClose = () => {
    if (apiRef.current) {
      try {
        apiRef.current.dispose();
      } catch (error) {
        console.error('Error disposing Jitsi:', error);
      }
    }
    navigate('/my-appointments');
  };

  if (error) {
    return (
      <div className="jitsi-error-container">
        <div className="jitsi-error-content">
          <h2>Video Conference Error</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/my-appointments')} className="jitsi-error-button">
            Back to Appointments
          </button>
        </div>
      </div>
    );
  }

  // Show appointment info and countdown if not ready to join
  if (!canJoin && appointmentInfo) {
    const dateTime = formatAppointmentDateTime();
    const countdownText = timeUntilAppointment ? formatCountdown(timeUntilAppointment) : null;
    
    return (
      <div className="jitsi-loading-container">
        <div className="jitsi-loading-content" style={{ textAlign: 'center', padding: '40px' }}>
          <h2 style={{ marginBottom: '20px', color: '#2563eb' }}>Your Upcoming Appointment</h2>
          {dateTime && (
            <div style={{ marginBottom: '20px', fontSize: '18px' }}>
              <p style={{ marginBottom: '10px' }}>
                <strong>Date:</strong> {dateTime.date}
              </p>
              <p style={{ marginBottom: '10px' }}>
                <strong>Time:</strong> {dateTime.time}
              </p>
            </div>
          )}
          {countdownText && (
            <div style={{ marginTop: '30px' }}>
              <p style={{ fontSize: '16px', marginBottom: '10px' }}>Joining in:</p>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#2563eb', fontFamily: 'monospace' }}>
                {countdownText}
              </div>
            </div>
          )}
          {!timeUntilAppointment && (
            <p style={{ marginTop: '20px', color: '#6b7280' }}>
              Your appointment will start soon. Please wait...
            </p>
          )}
        </div>
      </div>
    );
  }

  if (loading && !canJoin) {
    return (
      <div className="jitsi-loading-container">
        <div className="jitsi-loading-content">
          <div className="jitsi-spinner"></div>
          <p>Loading video conference...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="jitsi-conference-container">
      <div ref={jitsiContainerRef} className="jitsi-container" />
      <button onClick={handleClose} className="jitsi-exit-button" aria-label="Exit meeting">
        Exit Meeting
      </button>
    </div>
  );
};

export default JitsiVideoConference;

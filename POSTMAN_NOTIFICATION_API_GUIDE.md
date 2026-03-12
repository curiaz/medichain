# Postman Testing Guide - Notification API

## Base URL
```
https://medichain.clinic/api/notifications
```

## Authentication
All endpoints require a Firebase ID token in the Authorization header.

**Header:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
```

### How to Get Firebase Token:
1. Login through the frontend
2. Open browser DevTools (F12) → Console
3. Run: `localStorage.getItem('firebase_id_token')` or `sessionStorage.getItem('firebase_id_token')`
4. Copy the token value

---

## Endpoints

### 1. GET Notifications
**Get all notifications for the authenticated user**

**Request:**
```
GET https://medichain.clinic/api/notifications
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
Content-Type: application/json
```

**Query Parameters (Optional):**
- `is_read` - Filter by read status: `true` or `false`
- `category` - Filter by category: `appointment`, `medical`, `system`, etc.
- `limit` - Number of notifications to return (default: 50)

**Example:**
```
GET https://medichain.clinic/api/notifications?is_read=false&category=appointment&limit=20
```

**Success Response (200):**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "123",
      "user_id": "firebase_uid_here",
      "title": "Appointment Scheduled",
      "message": "Your appointment with Dr. Smith is scheduled for January 15, 2025 at 02:00 PM",
      "type": "info",
      "category": "appointment",
      "priority": "high",
      "is_read": false,
      "is_archived": false,
      "action_url": "/appointments/456",
      "action_label": "View Appointment",
      "metadata": {
        "appointment_id": "456",
        "appointment_date": "January 15, 2025",
        "appointment_time": "02:00 PM",
        "meeting_url": "https://meet.jit.si/room-name"
      },
      "created_at": "2025-01-10T10:30:00Z",
      "updated_at": "2025-01-10T10:30:00Z"
    }
  ],
  "unread_count": 5,
  "total": 10
}
```

---

### 2. GET Notification Stats
**Get notification statistics for the authenticated user**

**Request:**
```
GET https://medichain.clinic/api/notifications/stats
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
```

**Success Response (200):**
```json
{
  "success": true,
  "stats": {
    "total": 10,
    "unread": 5,
    "read": 5
  }
}
```

---

### 3. PUT Update Notification
**Update a notification (mark as read, archive, etc.)**

**Request:**
```
PUT https://medichain.clinic/api/notifications/<notification_id>
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "is_read": true,
  "is_archived": false
}
```

**Success Response (200):**
```json
{
  "success": true,
  "notification": {
    "id": "123",
    "user_id": "firebase_uid_here",
    "title": "Appointment Scheduled",
    "message": "Your appointment...",
    "is_read": true,
    "read_at": "2025-01-10T11:00:00Z",
    "updated_at": "2025-01-10T11:00:00Z"
  }
}
```

---

### 4. POST Mark All as Read
**Mark all unread notifications as read**

**Request:**
```
POST https://medichain.clinic/api/notifications/read-all
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
Content-Type: application/json
```

**Body (can be empty):**
```json
{}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "All notifications marked as read",
  "updated_count": 5
}
```

---

### 5. DELETE Notification
**Delete a specific notification**

**Request:**
```
DELETE https://medichain.clinic/api/notifications/<notification_id>
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Notification deleted"
}
```

---

## Testing Workflow

### Step 1: Get Your Firebase Token
1. Login to the frontend
2. Open DevTools → Console
3. Run: `localStorage.getItem('firebase_id_token') || sessionStorage.getItem('firebase_id_token')`
4. Copy the token

### Step 2: Test GET Notifications
1. **Method:** GET
2. **URL:** `https://medichain.clinic/api/notifications`
3. **Headers:**
   - `Authorization: Bearer <YOUR_TOKEN>`
4. **Send Request**
5. **Expected:** List of notifications for your user

### Step 3: Test GET Stats
1. **Method:** GET
2. **URL:** `https://medichain.clinic/api/notifications/stats`
3. **Headers:**
   - `Authorization: Bearer <YOUR_TOKEN>`
4. **Send Request**
5. **Expected:** Statistics about your notifications

### Step 4: Test Mark as Read
1. **Method:** PUT
2. **URL:** `https://medichain.clinic/api/notifications/<NOTIFICATION_ID>`
   - Replace `<NOTIFICATION_ID>` with an actual ID from Step 2
3. **Headers:**
   - `Authorization: Bearer <YOUR_TOKEN>`
   - `Content-Type: application/json`
4. **Body (JSON):**
   ```json
   {
     "is_read": true
   }
   ```
5. **Send Request**
6. **Expected:** Updated notification with `is_read: true`

### Step 5: Test Mark All as Read
1. **Method:** POST
2. **URL:** `https://medichain.clinic/api/notifications/read-all`
3. **Headers:**
   - `Authorization: Bearer <YOUR_TOKEN>`
   - `Content-Type: application/json`
4. **Body (JSON):**
   ```json
   {}
   ```
5. **Send Request**
6. **Expected:** All unread notifications marked as read

---

## Common Issues

### 401 Unauthorized
- **Cause:** Invalid or expired Firebase token
- **Solution:** Get a fresh token from the frontend

### 500 Internal Server Error
- **Cause:** Database connection issue or server error
- **Solution:** Check backend logs for detailed error messages

### Empty notifications array
- **Cause:** No notifications exist for your user, or user_id mismatch
- **Solution:** 
  - Verify your Firebase UID matches the `user_id` in notifications table
  - Create a test notification by booking an appointment

---

## Testing Notification Creation

To test if notifications are created when booking appointments:

1. **Book an appointment** through the frontend
2. **Check backend logs** for:
   - `🔔 Starting notification creation for appointment...`
   - `✅ Patient notification created successfully`
   - `✅ Doctor notification created successfully`
3. **Fetch notifications** using GET endpoint
4. **Verify** new notifications appear in the response

---

## Postman Collection Setup

### Environment Variables
Create a Postman environment with:
- `base_url`: `https://medichain.clinic`
- `firebase_token`: `<YOUR_FIREBASE_ID_TOKEN>`

### Collection Variables
- `notification_id`: Set this after getting notifications (use an ID from the response)

### Pre-request Script (Optional)
To automatically get token from localStorage:
```javascript
// Note: This only works in Postman's browser version
// For desktop, manually set the token
pm.environment.set("firebase_token", "YOUR_TOKEN_HERE");
```

---

## Example Postman Requests

### Request 1: Get All Notifications
```
GET {{base_url}}/api/notifications
Authorization: Bearer {{firebase_token}}
```

### Request 2: Get Unread Notifications Only
```
GET {{base_url}}/api/notifications?is_read=false
Authorization: Bearer {{firebase_token}}
```

### Request 3: Get Appointment Notifications
```
GET {{base_url}}/api/notifications?category=appointment
Authorization: Bearer {{firebase_token}}
```

### Request 4: Mark Notification as Read
```
PUT {{base_url}}/api/notifications/{{notification_id}}
Authorization: Bearer {{firebase_token}}
Content-Type: application/json

{
  "is_read": true
}
```

---

## Debugging Tips

1. **Check Backend Logs:** All requests log detailed information
   - Look for `📥 Fetching notifications for user: [UID]`
   - Check for any `❌` error messages

2. **Verify User ID:** Make sure the Firebase UID in your token matches the `user_id` in notifications

3. **Check Database:** Query the notifications table directly in Supabase to see if notifications exist

4. **Test Authentication:** Try a simple authenticated endpoint first to verify your token works


## Base URL
```
https://medichain.clinic/api/notifications
```

## Authentication
All endpoints require a Firebase ID token in the Authorization header.

**Header:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
```

### How to Get Firebase Token:
1. Login through the frontend
2. Open browser DevTools (F12) → Console
3. Run: `localStorage.getItem('firebase_id_token')` or `sessionStorage.getItem('firebase_id_token')`
4. Copy the token value

---

## Endpoints

### 1. GET Notifications
**Get all notifications for the authenticated user**

**Request:**
```
GET https://medichain.clinic/api/notifications
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
Content-Type: application/json
```

**Query Parameters (Optional):**
- `is_read` - Filter by read status: `true` or `false`
- `category` - Filter by category: `appointment`, `medical`, `system`, etc.
- `limit` - Number of notifications to return (default: 50)

**Example:**
```
GET https://medichain.clinic/api/notifications?is_read=false&category=appointment&limit=20
```

**Success Response (200):**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "123",
      "user_id": "firebase_uid_here",
      "title": "Appointment Scheduled",
      "message": "Your appointment with Dr. Smith is scheduled for January 15, 2025 at 02:00 PM",
      "type": "info",
      "category": "appointment",
      "priority": "high",
      "is_read": false,
      "is_archived": false,
      "action_url": "/appointments/456",
      "action_label": "View Appointment",
      "metadata": {
        "appointment_id": "456",
        "appointment_date": "January 15, 2025",
        "appointment_time": "02:00 PM",
        "meeting_url": "https://meet.jit.si/room-name"
      },
      "created_at": "2025-01-10T10:30:00Z",
      "updated_at": "2025-01-10T10:30:00Z"
    }
  ],
  "unread_count": 5,
  "total": 10
}
```

---

### 2. GET Notification Stats
**Get notification statistics for the authenticated user**

**Request:**
```
GET https://medichain.clinic/api/notifications/stats
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
```

**Success Response (200):**
```json
{
  "success": true,
  "stats": {
    "total": 10,
    "unread": 5,
    "read": 5
  }
}
```

---

### 3. PUT Update Notification
**Update a notification (mark as read, archive, etc.)**

**Request:**
```
PUT https://medichain.clinic/api/notifications/<notification_id>
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "is_read": true,
  "is_archived": false
}
```

**Success Response (200):**
```json
{
  "success": true,
  "notification": {
    "id": "123",
    "user_id": "firebase_uid_here",
    "title": "Appointment Scheduled",
    "message": "Your appointment...",
    "is_read": true,
    "read_at": "2025-01-10T11:00:00Z",
    "updated_at": "2025-01-10T11:00:00Z"
  }
}
```

---

### 4. POST Mark All as Read
**Mark all unread notifications as read**

**Request:**
```
POST https://medichain.clinic/api/notifications/read-all
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
Content-Type: application/json
```

**Body (can be empty):**
```json
{}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "All notifications marked as read",
  "updated_count": 5
}
```

---

### 5. DELETE Notification
**Delete a specific notification**

**Request:**
```
DELETE https://medichain.clinic/api/notifications/<notification_id>
```

**Headers:**
```
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Notification deleted"
}
```

---

## Testing Workflow

### Step 1: Get Your Firebase Token
1. Login to the frontend
2. Open DevTools → Console
3. Run: `localStorage.getItem('firebase_id_token') || sessionStorage.getItem('firebase_id_token')`
4. Copy the token

### Step 2: Test GET Notifications
1. **Method:** GET
2. **URL:** `https://medichain.clinic/api/notifications`
3. **Headers:**
   - `Authorization: Bearer <YOUR_TOKEN>`
4. **Send Request**
5. **Expected:** List of notifications for your user

### Step 3: Test GET Stats
1. **Method:** GET
2. **URL:** `https://medichain.clinic/api/notifications/stats`
3. **Headers:**
   - `Authorization: Bearer <YOUR_TOKEN>`
4. **Send Request**
5. **Expected:** Statistics about your notifications

### Step 4: Test Mark as Read
1. **Method:** PUT
2. **URL:** `https://medichain.clinic/api/notifications/<NOTIFICATION_ID>`
   - Replace `<NOTIFICATION_ID>` with an actual ID from Step 2
3. **Headers:**
   - `Authorization: Bearer <YOUR_TOKEN>`
   - `Content-Type: application/json`
4. **Body (JSON):**
   ```json
   {
     "is_read": true
   }
   ```
5. **Send Request**
6. **Expected:** Updated notification with `is_read: true`

### Step 5: Test Mark All as Read
1. **Method:** POST
2. **URL:** `https://medichain.clinic/api/notifications/read-all`
3. **Headers:**
   - `Authorization: Bearer <YOUR_TOKEN>`
   - `Content-Type: application/json`
4. **Body (JSON):**
   ```json
   {}
   ```
5. **Send Request**
6. **Expected:** All unread notifications marked as read

---

## Common Issues

### 401 Unauthorized
- **Cause:** Invalid or expired Firebase token
- **Solution:** Get a fresh token from the frontend

### 500 Internal Server Error
- **Cause:** Database connection issue or server error
- **Solution:** Check backend logs for detailed error messages

### Empty notifications array
- **Cause:** No notifications exist for your user, or user_id mismatch
- **Solution:** 
  - Verify your Firebase UID matches the `user_id` in notifications table
  - Create a test notification by booking an appointment

---

## Testing Notification Creation

To test if notifications are created when booking appointments:

1. **Book an appointment** through the frontend
2. **Check backend logs** for:
   - `🔔 Starting notification creation for appointment...`
   - `✅ Patient notification created successfully`
   - `✅ Doctor notification created successfully`
3. **Fetch notifications** using GET endpoint
4. **Verify** new notifications appear in the response

---

## Postman Collection Setup

### Environment Variables
Create a Postman environment with:
- `base_url`: `https://medichain.clinic`
- `firebase_token`: `<YOUR_FIREBASE_ID_TOKEN>`

### Collection Variables
- `notification_id`: Set this after getting notifications (use an ID from the response)

### Pre-request Script (Optional)
To automatically get token from localStorage:
```javascript
// Note: This only works in Postman's browser version
// For desktop, manually set the token
pm.environment.set("firebase_token", "YOUR_TOKEN_HERE");
```

---

## Example Postman Requests

### Request 1: Get All Notifications
```
GET {{base_url}}/api/notifications
Authorization: Bearer {{firebase_token}}
```

### Request 2: Get Unread Notifications Only
```
GET {{base_url}}/api/notifications?is_read=false
Authorization: Bearer {{firebase_token}}
```

### Request 3: Get Appointment Notifications
```
GET {{base_url}}/api/notifications?category=appointment
Authorization: Bearer {{firebase_token}}
```

### Request 4: Mark Notification as Read
```
PUT {{base_url}}/api/notifications/{{notification_id}}
Authorization: Bearer {{firebase_token}}
Content-Type: application/json

{
  "is_read": true
}
```

---

## Debugging Tips

1. **Check Backend Logs:** All requests log detailed information
   - Look for `📥 Fetching notifications for user: [UID]`
   - Check for any `❌` error messages

2. **Verify User ID:** Make sure the Firebase UID in your token matches the `user_id` in notifications

3. **Check Database:** Query the notifications table directly in Supabase to see if notifications exist

4. **Test Authentication:** Try a simple authenticated endpoint first to verify your token works


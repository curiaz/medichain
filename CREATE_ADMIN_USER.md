# How to Create/Locate Admin Users

## Quick Setup Guide

There are several ways to create or locate admin users in MediChain:

### Method 1: Using the Admin Setup Script (Recommended)

1. **Run the setup script:**
   ```bash
   python create_admin_user.py
   ```

2. **Choose an option:**
   - **Option 1**: Create a new admin user (creates Firebase account + database profile)
   - **Option 2**: Promote an existing user to admin
   - **Option 3**: List all existing admin users

3. **Follow the prompts** to complete the setup.

### Method 2: Direct Database Update (Supabase)

If you have direct access to Supabase:

1. **Go to Supabase Dashboard** → SQL Editor

2. **Run this SQL to promote an existing user:**
   ```sql
   UPDATE user_profiles 
   SET role = 'admin' 
   WHERE email = 'your-email@example.com';
   ```

3. **Or create a new admin user:**
   ```sql
   INSERT INTO user_profiles (
     firebase_uid, 
     email, 
     first_name, 
     last_name, 
     role, 
     is_active, 
     is_verified
   ) VALUES (
     'your-firebase-uid-here',
     'admin@example.com',
     'Admin',
     'User',
     'admin',
     true,
     true
   );
   ```

   **Note**: You'll need to create the Firebase account separately if using this method.

### Method 3: Using Signup Endpoint (Frontend)

1. **Sign up through the frontend** with role set to "admin":
   - Go to `/signup`
   - Fill in the form
   - Set role to "admin" (if the signup form allows role selection)

2. **Or use the API directly:**
   ```bash
   curl -X POST http://localhost:5000/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@example.com",
       "password": "YourPassword123",
       "name": "Admin User",
       "role": "admin"
     }'
   ```

### Method 4: Find Existing Admin Users

**Using the script:**
```bash
python create_admin_user.py
# Choose option 3
```

**Using Supabase SQL:**
```sql
SELECT * FROM user_profiles WHERE role = 'admin';
```

**Using the Admin API** (if you already have admin access):
```bash
curl -X GET http://localhost:5000/api/admin/users?role=admin \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## After Creating an Admin User

1. **Log in** with the admin account credentials
2. **Navigate to** `/dashboard` - you should see the Admin Dashboard
3. **Access features:**
   - User Management
   - System Statistics
   - All admin-only endpoints

## Troubleshooting

### "Access denied" error
- Make sure the user's role is set to "admin" in the `user_profiles` table
- Verify the user is logged in with the correct Firebase account
- Check that the `firebase_uid` matches between Firebase and Supabase

### Can't find admin users
- Run the script with option 3 to list all admins
- Check Supabase directly: `SELECT * FROM user_profiles WHERE role = 'admin'`

### Script won't run
- Make sure you're in the project root directory
- Check that `.env` file has correct Supabase and Firebase credentials
- Ensure Python dependencies are installed: `pip install -r backend/requirements.txt`

## Security Notes

⚠️ **Important**: 
- Only create admin users for trusted personnel
- Keep admin credentials secure
- Consider implementing 2FA for admin accounts in production
- Regularly audit admin user list


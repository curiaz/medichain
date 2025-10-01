# 🔧 **Supabase Table Setup Instructions**

Since the OTP system requires specific database tables, you need to create them manually in your Supabase dashboard.

## **Step 1: Access Supabase Dashboard**

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Select your project: `medichain-8773b`
3. Navigate to **Table Editor** in the left sidebar

## **Step 2: Create `password_reset_otps` Table**

Click **"New table"** and create with these settings:

**Table name:** `password_reset_otps`

**Columns:**
| Column Name | Type | Default | Nullable | Primary |
|-------------|------|---------|----------|---------|
| `id` | `int8` | Auto-increment | No | Yes |
| `email` | `varchar` | - | No | No |
| `otp` | `varchar` | - | No | No |
| `created_at` | `timestamptz` | `now()` | No | No |
| `expires_at` | `timestamptz` | - | No | No |
| `used` | `bool` | `false` | No | No |

## **Step 3: Create `password_reset_tokens` Table**

Click **"New table"** and create with these settings:

**Table name:** `password_reset_tokens`

**Columns:**
| Column Name | Type | Default | Nullable | Primary |
|-------------|------|---------|----------|---------|
| `id` | `int8` | Auto-increment | No | Yes |
| `email` | `varchar` | - | No | No |
| `reset_token` | `varchar` | - | No | No |
| `created_at` | `timestamptz` | `now()` | No | No |
| `expires_at` | `timestamptz` | - | No | No |
| `used` | `bool` | `false` | No | No |

## **Step 4: Test the System**

After creating the tables:

1. Restart your Flask backend server
2. Go to `http://localhost:3001/reset-password`
3. Test with a real email address
4. Check that you receive a **numeric-only OTP** (6 digits)

## **SQL Commands (Alternative)**

If you prefer SQL, go to **SQL Editor** in Supabase and run:

```sql
-- Create password_reset_otps table
CREATE TABLE password_reset_otps (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp VARCHAR(6) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

-- Create password_reset_tokens table  
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    reset_token VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

-- Create indexes for performance
CREATE INDEX idx_password_reset_otps_email ON password_reset_otps(email);
CREATE INDEX idx_password_reset_otps_expires ON password_reset_otps(expires_at);
CREATE INDEX idx_password_reset_tokens_email ON password_reset_tokens(email);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(reset_token);
```

## **Features of the New System**

✅ **Numeric-only OTP**: 6-digit codes (e.g., `123456`)  
✅ **Enhanced Email Design**: Beautiful HTML email template with "Medichain" branding  
✅ **Improved UI**: Better OTP input styling with visual feedback  
✅ **Security**: Proper expiration, token validation, and cleanup  
✅ **User Experience**: Step-by-step process with clear feedback  

## **Testing Checklist**

- [ ] Tables created in Supabase
- [ ] Backend server restarted  
- [ ] Can access reset password page
- [ ] Email sent with numeric OTP
- [ ] OTP input shows proper styling
- [ ] Password requirements show visual feedback
- [ ] Complete flow works end-to-end
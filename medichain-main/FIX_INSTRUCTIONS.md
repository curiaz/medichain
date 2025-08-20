# How to Fix the "null value in column 'first_name'" Error

## The Problem
The Supabase database has a trigger that automatically creates profile records when auth users are created, but this trigger doesn't properly handle cases where the user metadata might be missing or null.

## The Solution
Run the SQL script `fix_profile_trigger.sql` in your Supabase database to update the trigger function with proper null handling.

## Steps to Fix:

### Option 1: Using Supabase Dashboard (Recommended)
1. Open your Supabase project dashboard
2. Go to the SQL Editor
3. Copy and paste the contents of `fix_profile_trigger.sql`
4. Run the SQL script
5. Test the signup again

### Option 2: Using Python with Supabase Client
1. Run the following command to execute the SQL script:

```python
# Execute the SQL script using the service client
with open('fix_profile_trigger.sql', 'r') as f:
    sql_script = f.read()
    
# Split the script into individual statements and execute each
statements = sql_script.split(';')
for statement in statements:
    if statement.strip():
        try:
            supabase.service_client.rpc('exec_sql', {'sql': statement.strip()})
        except Exception as e:
            print(f"Error executing: {e}")
```

### Option 3: Alternative Backend Fix (If you can't modify the database)
If you can't modify the database trigger, you can modify the backend to handle this differently by:

1. Creating auth users without metadata first
2. Then manually creating the profile records
3. This bypasses the problematic trigger

## What the Fix Does:
- Updates the trigger function to use `COALESCE()` for default values
- If `first_name` is null, it defaults to "User"
- If `last_name` is null, it defaults to "Account"  
- If `role` is null, it defaults to "patient"
- Adds a safe profile creation function as backup

## Test After Fix:
Once you've run the SQL script, restart the Flask backend and test the signup again with the debug script.

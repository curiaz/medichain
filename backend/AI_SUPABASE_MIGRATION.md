# AI System Supabase Migration

## Overview

The MediChain AI diagnosis system has been successfully migrated from CSV file-based data storage to Supabase database tables. This provides better scalability, real-time data updates, and centralized data management.

## Migrated Tables

The following CSV files have been migrated to Supabase tables:

1. **`condition - Sheet1.csv`** → **`conditions`** table
   - Contains condition/diagnosis names and their associated symptom patterns
   - Used for symptom-to-diagnosis matching

2. **`condition_reason - Sheet1.csv`** → **`condition_reasons`** table
   - Contains explanations/reasons for each medical condition
   - Provides detailed information about why symptoms indicate a condition

3. **`action_medication - Sheet1.csv`** → **`action_conditions`** table
   - Contains recommended actions, medications, dosages, and treatment notes
   - Provides comprehensive treatment information for each diagnosis

## Code Changes

### 1. Supabase Client (`backend/db/supabase_client.py`)

Added three new methods to fetch AI diagnosis data:

```python
def get_conditions(self):
    """Fetch all conditions from Supabase"""
    
def get_condition_reasons(self):
    """Fetch all condition reasons from Supabase"""
    
def get_action_conditions(self):
    """Fetch all action conditions (medications) from Supabase"""
```

### 2. AI System (`backend/app.py`)

**Updated class initialization:**
- Added Supabase client: `self.supabase = SupabaseClient()`
- Updated version: `MediChain-Streamlined-v6.0-Supabase`

**Modified `load_data()` method:**
- Now fetches data from Supabase tables first
- Falls back to CSV files if Supabase data is unavailable
- Converts Supabase JSON responses to pandas DataFrames
- Maintains same data structure for compatibility with existing logic

**All other methods remain unchanged:**
- `train_model()` - Uses DataFrame, works with both sources
- `normalize_symptom()` - String processing, source-agnostic
- `parse_symptoms()` - DataFrame operations, compatible
- `predict_conditions()` - DataFrame-based matching, compatible
- `get_condition_reason()` - DataFrame lookup, compatible
- `get_recommended_action_and_medication()` - DataFrame lookup, compatible
- `diagnose()` - Orchestration method, compatible

## Features

✅ **Seamless Integration**: No changes required to AI logic or prediction algorithms
✅ **Backward Compatible**: Falls back to CSV if Supabase is unavailable
✅ **Real-time Updates**: Data changes in Supabase reflect immediately
✅ **Scalable**: Can handle growing medical knowledge base
✅ **Centralized**: Single source of truth for medical data

## Testing

### Test Supabase Connection

```powershell
cd backend
python test_supabase_ai_data.py
```

This will:
- Connect to Supabase
- Fetch data from all three tables
- Display sample records
- Show migration statistics

### Test AI System

```powershell
cd backend
python test_ai_supabase.py
```

This will:
- Initialize AI system with Supabase data
- Test symptom parsing
- Run diagnosis on sample symptoms
- Verify all components work correctly

### Start the Backend Server

```powershell
cd backend
python app.py
```

The server will:
- Load data from Supabase on startup
- Train the AI model with loaded data
- Expose the same API endpoints as before

## API Endpoints

All existing endpoints remain functional:

- **`GET /health`** - Health check
- **`GET /api/ai/health`** - AI system status with data statistics
- **`POST /api/diagnose`** - Main diagnosis endpoint
- **`POST /api/symptom-explanations`** - Symptom parsing and detection

### Example Request

```bash
curl -X POST http://localhost:5000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "fever, cough, headache, fatigue"}'
```

### Example Response

```json
{
  "success": true,
  "message": "Diagnosis completed successfully",
  "data": {
    "detected_symptoms": ["Fever", "Cough", "Headache", "Fatigue"],
    "primary_condition": "Flu (Influenza)",
    "primary_confidence": "85.5%",
    "detailed_results": [
      {
        "condition": "Flu (Influenza)",
        "confidence": "85.5%",
        "reason": "Flu is caused by influenza viruses...",
        "recommended_action": "Rest and stay hydrated...",
        "medication": "Acetaminophen or Ibuprofen",
        "dosage": "500-1000mg every 6 hours",
        "medication_details": {
          "medicine": "Acetaminophen (Tylenol)",
          "adult_dose": "500-1000mg every 4-6 hours",
          "child_dose": "10-15mg/kg every 4-6 hours",
          "max_daily_dose": "4000mg per day",
          "description": "Pain reliever and fever reducer",
          "notes": "Do not exceed maximum daily dose"
        }
      }
    ]
  }
}
```

## Environment Variables

Ensure these are set in your `.env` file:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## Dependencies

### Required packages (install with pip):

```bash
# From requirements.txt
pip install Flask flask-cors supabase python-dotenv

# From requirements_ai.txt
pip install pandas numpy scikit-learn joblib
```

Or install all at once:

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements_ai.txt
```

## Migration Benefits

1. **Data Consistency**: Single source of truth across all services
2. **Real-time Updates**: Changes propagate immediately without server restart
3. **Scalability**: Database handles concurrent access better than CSV files
4. **Data Integrity**: Database constraints and validation
5. **Backup & Recovery**: Automated backups through Supabase
6. **Collaboration**: Multiple developers can update medical data safely

## Troubleshooting

### Issue: "No conditions data found in Supabase"

**Solution**: Ensure tables are created and populated in Supabase:
- Check table names: `conditions`, `condition_reasons`, `action_conditions`
- Verify data is inserted
- Confirm Supabase credentials in `.env`

### Issue: "Supabase client not initialized"

**Solution**: Check environment variables:
```bash
echo $env:SUPABASE_URL
echo $env:SUPABASE_KEY
```

### Issue: Model training fails

**Solution**: 
- Verify data structure matches expected format
- Check column names in Supabase tables match CSV columns
- Review error logs for specific missing columns

## Future Enhancements

- [ ] Add caching layer for frequently accessed data
- [ ] Implement incremental model retraining when data changes
- [ ] Add data validation and quality checks
- [ ] Create admin API for managing medical data
- [ ] Add versioning for model and data changes

## Support

For issues or questions, please check:
- Server logs: `python app.py` output
- Test scripts: `test_supabase_ai_data.py` and `test_ai_supabase.py`
- Supabase dashboard: Check table data and RLS policies

## Version History

- **v6.0 (Current)**: Supabase integration with CSV fallback
- **v5.0**: CSV-based system with improved matching
- **v4.0**: Enhanced symptom categorization
- **v3.0**: Multi-system condition handling

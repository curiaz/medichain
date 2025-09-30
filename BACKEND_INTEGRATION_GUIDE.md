# 🔗 MediChain Patient Profile - Backend Integration Guide

## 🎯 **Overview**

This guide provides step-by-step instructions for integrating the Patient Profile Management system with the backend API. The system includes comprehensive patient profile management with medical records, document uploads, privacy settings, and audit trails.

---

## 🏗️ **Backend Architecture**

### **API Endpoints**
All patient profile endpoints are prefixed with `/api/profile/patient`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/profile/patient` | Get complete patient profile |
| `PUT` | `/api/profile/patient` | Update patient profile |
| `PUT` | `/api/profile/patient/medical` | Update medical information |
| `POST` | `/api/profile/patient/documents` | Upload health document |
| `PUT` | `/api/profile/patient/privacy` | Update privacy settings |

### **Authentication**
- **Firebase JWT Tokens**: All requests require valid Firebase authentication
- **Role Verification**: Only patients can access these endpoints
- **Token Validation**: Backend verifies token and extracts user information

---

## 🚀 **Setup Instructions**

### **1. Database Setup**

#### **Option A: Manual Setup (Recommended)**
1. **Open Supabase Dashboard**
2. **Go to SQL Editor**
3. **Run the schema file**: `database/enhanced_profile_management_schema.sql`
4. **Verify tables created**:
   - `user_profiles`
   - `patient_medical_info`
   - `patient_documents`
   - `patient_privacy_settings`
   - `patient_audit_log`

#### **Option B: Automated Setup**
```bash
cd backend
python setup_patient_database.py
```

### **2. Environment Configuration**

Create `.env` file in the backend directory:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
SECRET_KEY=your_flask_secret_key
FLASK_DEBUG=True
```

### **3. Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

### **4. Start Backend Server**

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

---

## 🔧 **Backend Implementation**

### **1. SupabaseClient Methods**

The `SupabaseClient` class includes these patient-specific methods:

```python
# Get complete patient profile
def get_patient_profile(self, user_id):
    """Get complete patient profile with medical information"""
    
# Update patient profile
def update_patient_profile(self, user_id, data):
    """Update patient profile information"""
    
# Update medical information
def update_patient_medical_info(self, user_id, data):
    """Update patient medical information"""
    
# Upload health document
def upload_patient_document(self, user_id, file, document_type, description):
    """Upload patient health document"""
    
# Update privacy settings
def update_patient_privacy_settings(self, user_id, data):
    """Update patient privacy settings"""
```

### **2. API Route Implementation**

Each endpoint includes:
- **Authentication verification**
- **Role-based access control**
- **Data validation**
- **Database operations**
- **Audit logging**
- **Error handling**

### **3. Security Features**

- **Role Verification**: Only patients can access endpoints
- **Token Validation**: Firebase JWT token verification
- **Data Sanitization**: Input validation and sanitization
- **Audit Logging**: All changes tracked in audit trail
- **Error Handling**: Comprehensive error responses

---

## 🧪 **Testing Integration**

### **1. Run Integration Tests**

```bash
python test_backend_integration.py
```

This will test:
- Server connection
- Patient profile retrieval
- Profile updates
- Medical information updates
- Privacy settings updates
- Document uploads

### **2. Manual API Testing**

#### **Get Patient Profile**
```bash
curl -X GET "http://localhost:5000/api/profile/patient" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json"
```

#### **Update Patient Profile**
```bash
curl -X PUT "http://localhost:5000/api/profile/patient" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1 (555) 123-4567"
  }'
```

#### **Update Medical Information**
```bash
curl -X PUT "http://localhost:5000/api/profile/patient/medical" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "medical_conditions": ["Hypertension"],
    "allergies": ["Penicillin"],
    "current_medications": ["Metformin 500mg"],
    "blood_type": "O+",
    "medical_notes": "Regular checkups"
  }'
```

---

## 🔗 **Frontend Integration**

### **1. API Configuration**

The frontend is already configured to use the patient-specific endpoints:

```javascript
const API_URL = 'http://localhost:5000/api';

// Patient profile endpoints
GET    /api/profile/patient
PUT    /api/profile/patient
PUT    /api/profile/patient/medical
POST   /api/profile/patient/documents
PUT    /api/profile/patient/privacy
```

### **2. Authentication Flow**

```javascript
// Get Firebase token
const token = await user.getIdToken();

// Make authenticated request
const response = await axios.get(`${API_URL}/profile/patient`, {
  headers: { Authorization: `Bearer ${token}` }
});
```

### **3. Error Handling**

The frontend handles various error scenarios:
- **Authentication errors**: Invalid or expired tokens
- **Authorization errors**: Non-patient users
- **Validation errors**: Invalid data format
- **Network errors**: Connection issues

---

## 📊 **Data Flow**

### **1. Profile Loading**
```
Frontend → GET /api/profile/patient → SupabaseClient.get_patient_profile() → Database
```

### **2. Profile Update**
```
Frontend → PUT /api/profile/patient → SupabaseClient.update_patient_profile() → Database + Audit Log
```

### **3. Medical Info Update**
```
Frontend → PUT /api/profile/patient/medical → SupabaseClient.update_patient_medical_info() → Database + Audit Log
```

### **4. Document Upload**
```
Frontend → POST /api/profile/patient/documents → SupabaseClient.upload_patient_document() → Database + Audit Log
```

---

## 🔒 **Security Considerations**

### **1. Authentication**
- **Firebase JWT**: Secure token-based authentication
- **Token Expiration**: Automatic token refresh
- **Role Verification**: Patient-only access

### **2. Data Protection**
- **Input Validation**: All inputs validated and sanitized
- **SQL Injection**: Parameterized queries prevent SQL injection
- **XSS Protection**: Data sanitization prevents XSS attacks

### **3. Privacy**
- **Data Encryption**: Sensitive data encrypted at rest
- **Access Control**: Role-based access restrictions
- **Audit Trail**: Complete change tracking for compliance

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Error**
```
Error: SUPABASE_URL and SUPABASE_KEY must be set
```
**Solution**: Check your `.env` file has correct Supabase credentials

#### **2. Authentication Error**
```
Error: Invalid or expired token
```
**Solution**: Ensure Firebase authentication is working correctly

#### **3. Role Access Error**
```
Error: Profile Management is only available for patients
```
**Solution**: Verify user role is set to 'patient' in Firebase

#### **4. Table Not Found Error**
```
Error: relation "user_profiles" does not exist
```
**Solution**: Run the database schema SQL file in Supabase

### **Debug Steps**

1. **Check Server Logs**: Look for error messages in Flask console
2. **Verify Database**: Check Supabase dashboard for table existence
3. **Test Authentication**: Verify Firebase token generation
4. **Check Network**: Ensure frontend can reach backend
5. **Validate Data**: Check request/response data format

---

## 📈 **Performance Optimization**

### **1. Database Optimization**
- **Indexes**: Add indexes on frequently queried columns
- **Connection Pooling**: Use connection pooling for better performance
- **Query Optimization**: Optimize database queries

### **2. API Optimization**
- **Caching**: Implement caching for frequently accessed data
- **Pagination**: Add pagination for large datasets
- **Compression**: Enable response compression

### **3. Frontend Optimization**
- **Lazy Loading**: Load data only when needed
- **Debouncing**: Debounce user input to reduce API calls
- **Error Boundaries**: Implement error boundaries for better UX

---

## 🚀 **Deployment**

### **1. Production Environment**
- **Environment Variables**: Set production environment variables
- **Database**: Use production Supabase instance
- **Security**: Enable HTTPS and security headers
- **Monitoring**: Implement logging and monitoring

### **2. Scaling Considerations**
- **Load Balancing**: Use load balancer for multiple instances
- **Database Scaling**: Consider read replicas for better performance
- **CDN**: Use CDN for static assets
- **Caching**: Implement Redis for session and data caching

---

## 📋 **Checklist**

### **Backend Setup**
- [ ] Supabase credentials configured
- [ ] Database schema executed
- [ ] Dependencies installed
- [ ] Server running on port 5000
- [ ] API endpoints responding

### **Frontend Integration**
- [ ] API URL configured correctly
- [ ] Authentication working
- [ ] Patient role verification
- [ ] Error handling implemented
- [ ] UI components functional

### **Testing**
- [ ] Backend integration tests passing
- [ ] Manual API testing successful
- [ ] Frontend-backend communication working
- [ ] Error scenarios handled
- [ ] Performance acceptable

---

## 🎉 **Success Criteria**

The integration is successful when:

1. **✅ Backend server starts without errors**
2. **✅ Database tables created successfully**
3. **✅ API endpoints respond correctly**
4. **✅ Frontend can load patient profiles**
5. **✅ Profile updates work end-to-end**
6. **✅ Medical information can be updated**
7. **✅ Document uploads function**
8. **✅ Privacy settings can be modified**
9. **✅ Audit trail tracks changes**
10. **✅ Error handling works properly**

---

**MediChain Patient Profile Backend Integration** - Complete healthcare data management system.


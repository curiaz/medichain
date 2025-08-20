/* Patients.jsx */
import { useState, useEffect } from "react"
import Header from "./Header"
import { Search, ClipboardCopy, Eye, AlertCircle, CheckCircle, Plus } from "lucide-react"
import "../assets/styles/Patients.css"
import { patientService } from "../services/patientService"
import { useAuth } from "../context/AuthContext"
import LoadingSpinner from "../components/LoadingSpinner"
import { showToast } from "../components/CustomToast"

const truncateHash = (hash) => {
  if (!hash) return 'N/A'
  return `${hash.substring(0, 8)}...${hash.substring(hash.length - 6)}`
}

const Patients = () => {
  const [searchTerm, setSearchTerm] = useState("")
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { user } = useAuth()
  
  const filteredPatients = patients.filter((patient) =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.patient_id.toLowerCase().includes(searchTerm.toLowerCase())
  )

  useEffect(() => {
    loadPatients()
  }, [])

  const loadPatients = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await patientService.getAllPatients()
      
      if (result.success) {
        setPatients(result.data)
        // Removed the success toast to prevent duplicate notifications
      } else {
        setError(result.message)
        showToast.error(result.message)
      }
    } catch (err) {
      setError("Failed to load patients")
      showToast.error("Failed to load patients")
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (fullHash) => {
    navigator.clipboard.writeText(fullHash)
    showToast.success("Hash copied to clipboard!")
  }

  const handleViewPatient = (patientId) => {
    showToast.info(`Viewing patient ${patientId} - Feature coming soon!`)
  }

  const handleNewPatient = () => {
    showToast.info("New Patient feature coming soon!")
  }

  if (loading) {
    return (
      <div className="patients-container">
        {/* Background crosses */}
        <div className="background-crosses">
          {[...Array(24)].map((_, i) => (
            <span key={i} className={`cross cross-${i + 1}`}>
              +
            </span>
          ))}
        </div>
        
        <Header />
        <main className="patients-main-content">
          <LoadingSpinner 
            fullScreen={true} 
            text="Loading patients..." 
            size="large"
          />
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="patients-container">
        {/* Background crosses */}
        <div className="background-crosses">
          {[...Array(24)].map((_, i) => (
            <span key={i} className={`cross cross-${i + 1}`}>
              +
            </span>
          ))}
        </div>
        
        <Header />
        <main className="patients-main-content">
          <div className="error-container">
            <div className="error-card">
              <AlertCircle className="error-icon" size={48} />
              <p className="error-text">{error}</p>
              <button 
                onClick={loadPatients}
                className="retry-button"
              >
                Try Again
              </button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="patients-container">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            +
          </span>
        ))}
      </div>

      <Header />

      <main className="patients-main-content">
        <div className="patients-header">
          <h1 className="patients-title">PATIENTS</h1>
          
          <div className="patients-header-actions">
            <div className="search-input-wrapper">
              <input
                type="text"
                placeholder="Search by name or ID"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <Search className="search-icon" size={18} />
            </div>
            
            {user && (user.role === 'doctor' || user.role === 'admin') && (
              <button 
                className="new-patient-btn"
                onClick={handleNewPatient}
              >
                <Plus size={20} /> New Patient
              </button>
            )}
          </div>
        </div>

        <div className="patients-table-container">
          <table className="patients-table">
            <thead>
              <tr>
                <th>Patient ID</th>
                <th>Full Name</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Last Visit</th>
                <th>Status</th>
                <th>Blockchain Hash</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.map((patient) => (
                <tr key={patient.id}>
                  <td data-label="Patient ID">{patient.patient_id}</td>
                  <td data-label="Full Name">{patient.name}</td>
                  <td data-label="Age">{patient.age}</td>
                  <td data-label="Gender">{patient.gender}</td>
                  <td data-label="Last Visit">{patient.updated_at ? new Date(patient.updated_at).toLocaleDateString() : 'N/A'}</td>
                  <td data-label="Status" className={patient.status === 'Critical' ? 'status-critical' : 'status-stable'}>
                    {patient.status === 'Stable' ? (
                      <CheckCircle size={14} style={{ marginRight: '4px' }} />
                    ) : (
                      <AlertCircle size={14} style={{ marginRight: '4px' }} />
                    )}
                    {patient.status}
                  </td>
                  <td data-label="Blockchain Hash" className="hash-cell" onClick={() => copyToClipboard(patient.blockchain_hash)}>
                    <span>{truncateHash(patient.blockchain_hash)}</span>
                  </td>
                  <td data-label="Actions">
                    <button 
                      className="view-button"
                      onClick={() => handleViewPatient(patient.patient_id)}
                    >
                      <Eye size={16} /> View
                    </button>
                  </td>
                </tr>
              ))}
              {filteredPatients.length === 0 && (
                <tr>
                  <td colSpan="8" className="empty-message">
                    No patients found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Blockchain verification info */}
        <div className="blockchain-info">
          <h3>
            <CheckCircle size={20} />
            Blockchain Record Verification
          </h3>
          <p>
            Each patient record is secured using AES encryption and verified with a SHA-256 hash stored on the
            blockchain. This ensures data integrity and prevents unauthorized modifications to medical records.
          </p>
        </div>
      </main>
    </div>
  )
}

export default Patients

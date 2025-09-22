# MediChain - AI-Powered Medical Diagnosis Platform

MediChain is a comprehensive healthcare platform that combines Firebase authentication, Supabase database, and AI-powered medical diagnosis to provide secure and intelligent healthcare solutions.

## 🚀 Features

- **🔐 Secure Authentication**: Firebase-based authentication with role-based access control
- **🗄️ Robust Database**: PostgreSQL with Supabase, RLS policies, and automatic data synchronization
- **🤖 AI Diagnosis**: Machine learning models for symptom analysis and medical recommendations
- **👥 Multi-Role Support**: Patient, Doctor, and Admin dashboards
- **📱 Responsive UI**: Modern React frontend with intuitive user interfaces
- **🧪 Comprehensive Testing**: Full test coverage with CI/CD pipeline
- **🔒 Security First**: Encrypted data storage and secure API endpoints

## 🏗️ Architecture

```
MediChain/
├── backend/                 # Flask API server
│   ├── auth/               # Authentication routes
│   ├── db/                 # Database connections
│   ├── tests/              # Backend unit tests
│   └── app.py              # Main Flask application
├── src/                    # React frontend
│   ├── components/         # Reusable UI components
│   ├── context/            # React context providers
│   ├── pages/              # Page components
│   └── config/             # Configuration files
├── database/               # SQL schema and migrations
└── .github/workflows/      # CI/CD pipelines
```

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**
- **Flask** - Web framework
- **Supabase** - PostgreSQL database
- **Firebase Admin SDK** - Authentication
- **pytest** - Testing framework

### Frontend
- **React 18** - UI framework
- **Firebase SDK** - Client authentication
- **Axios** - HTTP client
- **React Router** - Navigation
- **Jest + React Testing Library** - Testing

### DevOps
- **GitHub Actions** - CI/CD
- **Codecov** - Coverage reporting
- **ESLint** - Code linting
- **Prettier** - Code formatting

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/curiaz/medichain.git
   cd medichain
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment files
   cp backend/.env.example backend/.env
   cp .env.frontend.example .env.local

   # Edit with your Firebase and Supabase credentials
   ```

5. **Database Setup**
   ```bash
   # Run database migrations (in Supabase dashboard)
   # Execute the SQL files in database/ directory
   ```

### Running the Application

1. **Start Backend**
   ```bash
   cd backend
   python app.py
   ```

2. **Start Frontend** (in a new terminal)
   ```bash
   npm start
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v --cov=.
```

### Frontend Tests
```bash
npm run test:ci
```

### Test Coverage
- **Backend**: 80%+ coverage target
- **Frontend**: 70%+ coverage target

## 🚀 CI/CD Pipeline

The project uses GitHub Actions for automated testing and deployment:

### Workflows
- **Backend Tests**: Python testing with pytest
- **Frontend Tests**: JavaScript testing with Jest
- **Linting**: Code quality checks
- **Security Scan**: Vulnerability scanning
- **Build**: Production build verification

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## 📁 Project Structure

```
medichain/
├── backend/
│   ├── auth/               # Firebase authentication
│   ├── db/                 # Database connections
│   ├── tests/              # Unit tests
│   ├── app.py              # Flask application
│   └── requirements.txt    # Python dependencies
├── src/
│   ├── components/         # React components
│   ├── context/            # React context
│   ├── pages/              # Page components
│   ├── config/             # Configuration
│   └── App.js              # Main React app
├── database/               # SQL schemas
├── .github/workflows/      # CI/CD pipelines
├── TESTING.md              # Testing documentation
└── README.md               # This file
```

## 🔧 Development

### Code Quality
```bash
# Backend linting
cd backend
flake8 .
black --check .
isort --check-only .

# Frontend linting
npm run lint
```

### Adding New Features
1. Create feature branch: `git checkout -b feature/your-feature`
2. Write tests first (TDD approach)
3. Implement feature
4. Ensure tests pass: `npm run test:ci` and `python -m pytest`
5. Update documentation
6. Create pull request

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/verify` - Token verification
- `GET /api/auth/profile` - Get user profile

### Medical Endpoints
- `POST /api/medical/diagnose` - AI diagnosis
- `GET /api/medical/history` - Medical history
- `POST /api/medical/appointment` - Book appointment

## 🔒 Security

- **Authentication**: Firebase JWT tokens
- **Authorization**: Role-based access control
- **Data Encryption**: Encrypted sensitive medical data
- **API Security**: CORS, input validation, rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the TESTING.md for testing guidance
- Review the CI/CD pipeline in `.github/workflows/`

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Advanced AI diagnosis models
- [ ] Telemedicine integration
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

---

**MediChain** - Revolutionizing healthcare with AI and blockchain technology.

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)

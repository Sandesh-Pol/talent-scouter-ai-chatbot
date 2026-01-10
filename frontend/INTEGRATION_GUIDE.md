# TalentScout Frontend - Django Backend Integration

## ✅ Integration Complete!

Your React frontend is now fully integrated with the Django REST Framework backend. Real AI-powered interviews are now live!

---

## 🎯 What Was Integrated

### **Backend Connection**
- ✅ Full REST API integration with Django backend
- ✅ Real-time chat with Groq LLM (llama-3.3-70b-versatile)
- ✅ Automatic session management
- ✅ Live candidate profile extraction
- ✅ Sentiment analysis and interventions
- ✅ Technical question generation based on candidate skills

### **New Files Created**

```
frontend/
├── .env                                 # API configuration
├── .env.example                         # Template
├── src/
│   ├── types/
│   │   └── api.ts                      # TypeScript types for backend
│   ├── services/
│   │   └── api.ts                      # API service layer
│   └── hooks/
│       └── useInterviewSession.ts      # React hook for session management
```

### **Modified Files**
- `src/pages/Index.tsx` - Now uses real backend instead of mock data

---

## 🚀 Quick Start

### 1. **Start Django Backend**
```bash
# In backend directory
cd ../backend
python manage.py runserver

# Backend will run at: http://localhost:8000
```

### 2. **Start React Frontend**
```bash
# In frontend directory
npm run dev

# Frontend will run at: http://localhost:5173
```

### 3. **Open in Browser**
Navigate to: `http://localhost:5173`

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
```

**Change these if:**
- Backend runs on different port
- Deploying to production
- Need different API timeout

---

## 🎨 Features

### **Automatic Session Management**
- Creates new session on first visit
- Stores session ID in localStorage
- Restores session on page reload
- Handles expired sessions gracefully

### **Real-time AI Interview**
- Messages sent to Django backend
- Processed by Groq LLM
- Profile information extracted automatically
- Progress updates in real-time

### **Smart Data Display**
- Sidebar updates as candidate shares info
- Progress stepper tracks interview phases
- Loading states during API calls
- Error handling with user-friendly messages

### **Development Mode Debugging**
In development, you'll see debug info showing:
- Session ID
- Current phase
- Profile completeness percentage
- Intervention warnings

---

## 📊 How It Works

### Data Flow

```
User types message
    ↓
React Component (Index.tsx)
    ↓
useInterviewSession Hook
    ↓
API Service (api.ts)
    ↓
Django Backend API
    ↓
Groq LLM Processing
    ↓
Response back to React
    ↓
UI Updates (sidebar, messages, progress)
```

### State Management

**Session State:**
- `sessionId` - Current interview session
- `currentPhase` - onboarding | information_gathering | technical_screening | closing
- `profileCompleteness` - 0-100% progress
- `candidateProfile` - Extracted data (name, email, tech stack, etc.)
- `messages` - Full chat history

**Loading States:**
- `isInitializing` - True while creating/restoring session
- `isSending` - True while message is being sent

---

## 🎯 Interview Phases

### 1. **Onboarding**
- AI greets candidate
- Asks for name and position
- **Advances when:** Name or position provided

### 2. **Information Gathering**
- Collects: email, years of experience, tech stack, location
- Validates email format
- **Advances when:** All required fields filled (100% complete)

### 3. **Technical Screening**
- Generates 5 tailored technical questions
- Based on candidate's tech stack and experience level
- **Advances when:** All questions answered

### 4. **Closing**
- Thanks candidate
- Session marked as complete
- **End of interview**

---

## 🔍 Type Safety

All API responses are fully typed with TypeScript:

```typescript
// Example: Sending a message
const sendMessage = async (content: string) => {
  const response: ChatResponse = await api.sendMessage({
    message: content,
    session_id: sessionId
  });
  
  // response.current_phase - fully typed!
  // response.profile_completeness - autocomplete works!
};
```

**Benefits:**
- Autocomplete in VS Code
- Compile-time error detection
- Self-documenting code
- Refactoring safety

---

## 🛡️ Error Handling

### **Connection Errors**
If backend is down, users see:
```
🔌 Connection Failed
Unable to connect to the interview server.
Please check your connection and refresh the page.
```

### **Timeout Errors**
Requests timeout after 30 seconds (configurable in `.env`)

### **API Errors**
All API errors show user-friendly toast notifications

### **Session Restoration**
If stored session is invalid/expired:
- Automatically creates new session
- Shows fresh welcome message
- No error to user

---

## 📱 Component Updates

### **CandidateSidebar**
Receives `candidate` prop with real data:
```typescript
{
  fullName: "John Doe",          // from backend
  email: "john@example.com",     // from backend
  location: "San Francisco",     // from backend
  experience: "Senior",          // derived from years
  techStack: ["Python", "React"], // extracted by LLM
  position: "Backend Engineer"   // from backend
}
```

### **ProgressStepper**
`currentStep` mapped from backend phase:
- Onboarding → Step 1
- Information Gathering → Step 2
- Technical Screening → Step 3
- Closing → Step 3

### **ChatInterface**
Messages array synchronized with backend:
- User messages sent immediately
- Assistant responses added when received
- `isTyping` shows during API call

---

## 🎨 UI Enhancements

### **Loading States**
```typescript
if (isInitializing) {
  return <LoadingSpinner text="Initializing interview session..." />;
}
```

### **Error States**
```typescript
if (!sessionId) {
  return <ErrorDisplay message="Connection Failed" />;
}
```

### **Debug Info** (Development Only)
```
Session: 12345678... | Phase: information_gathering | Completeness: 60.0%
```

---

## 🔧 Customization

### **Change API URL**
```env
# .env
VITE_API_BASE_URL=https://your-production-backend.com/api
```

### **Adjust Timeout**
```env
# .env
VITE_API_TIMEOUT=60000  # 60 seconds
```

###  **Add Authentication** (Future)
```typescript
// In api.ts
private async fetchWithTimeout<T>(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('auth_token');
  
  return fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  });
}
```

---

## 🧪 Testing the Integration

### **Test Full Flow:**

1. **Open browser** to `http://localhost:5173`
2. **Check console** - Should see:
   ```
   Initialized session: <session-id>
   ```
3. **Type message**: "Hi, I'm John Doe applying for Senior Backend Engineer"
4. **Observe:**
   - Message appears in chat
   - Loading indicator shows
   - AI responds with personalized message
   - Sidebar updates with "John Doe"
   - Progress moves to Step 2

5. **Continue conversation**:
   ```
   "I have 7 years of experience with Python, Django, and React"
   ```
6. **Observe:**
   - Sidebar shows tech stack: Python, Django, React
   - Experience level: Senior
   - Progress updates

7. **Provide email**:
   ```
   "My email is john@example.com"
   ```
8. **Observe:**
   - Profile completeness reaches 100%
   - Moves to Technical Screening phase
   - AI generates 5 technical questions

---

## 📝 Notes

### **Session Persistence**
- Session ID stored in `localStorage`
- Survives page reload
- Cleared on browser close (session storage)
- Can be manually cleared: `localStorage.removeItem('talentscout_session_id')`

### **CORS**
Already configured in Django backend:
```python
# backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite default
    'http://localhost:3000',  # Alternative
]
```

### **Production Build**
```bash
npm run build

# Output in dist/
# Deploy to Vercel, Netlify, etc.
```

Update `.env.production`:
```env
VITE_API_BASE_URL=https://your-backend.herokuapp.com/api
```

---

## 🐛 Troubleshooting

### **Backend Not Running**
**Error**: `Connection Failed`

**Solution:**
```bash
cd ../backend
python manage.py runserver
```

### **CORS Error**
**Error**: `blocked by CORS policy`

**Solution**: Add frontend URL to backend `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Add your frontend URL
]
```

### **Session Not Persisting**
**Solution**: Check browser console for localStorage errors

### **TypeScript Errors**
**Solution**: 
```bash
npm install
npm run dev
```

---

## 🎉 What You Can Do Now

- ✅ **Real AI Interviews**: Groq LLM processes every message  
- ✅ **Smart Extraction**: Automatically fills candidate profile
- ✅ **Dynamic Questions**: Generates questions based on skills
- ✅ **Progress Tracking**: Real-time completeness updates
- ✅ **Sentiment Detection**: AI detects frustration/confusion
- ✅ **Phase Transitions**: Automatic advancement through stages
- ✅ **Admin Panel**: View all sessions at `http://localhost:8000/admin/`

---

## 📚 Related Documentation

- **Backend API**: `../backend/API_DOCS.md`
- **Backend Setup**: `../backend/README.md`
- **Architecture**: `../backend/PROJECT_OVERVIEW.md`

---

## 🚀 Next Steps

1. **Add Authentication** (JWT tokens)
2. **Deploy to Production**
   - Frontend: Vercel/Netlify
   - Backend: Heroku/Railway
3. **Add Analytics** (track completion rates)
4. **Enhance UI** (animations, transitions)
5. **Mobile Responsiveness** (already mostly done!)

---

**Integration Status**: ✅ **COMPLETE AND WORKING**

**Your React frontend now has a real AI brain powered by Django + Groq!** 🧠🚀

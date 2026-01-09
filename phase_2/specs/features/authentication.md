# Authentication Feature Specification

> **Feature**: User Authentication (Signup, Signin, JWT)
> **Phase**: II
> **Status**: Ready for Implementation

## Overview

Implement secure user authentication using Better Auth with JWT tokens. Users must authenticate to access task management features. Each user's data is isolated and protected.

## Related Specs

- `@specs/api/rest-endpoints.md` - Auth endpoint definitions
- `@specs/database/schema.md` - User model schema
- `@specs/features/task-crud.md` - Protected task endpoints
- `@specs/ui/pages.md` - Signin/Signup pages

---

## User Stories

### US-1: User Signup (P1)
**As a** new user
**I want to** create an account
**So that** I can use the todo application

**Acceptance Criteria:**
- [ ] User provides email, name, and password
- [ ] Email must be unique and valid format
- [ ] Password must be at least 8 characters
- [ ] Password is hashed before storage (never stored plain)
- [ ] Returns JWT token on successful signup
- [ ] Returns user profile (without password)
- [ ] Returns 400 if email already exists
- [ ] Returns 400 if validation fails

### US-2: User Signin (P1)
**As a** registered user
**I want to** sign in to my account
**So that** I can access my tasks

**Acceptance Criteria:**
- [ ] User provides email and password
- [ ] Credentials are validated against database
- [ ] Returns JWT token on successful signin
- [ ] Returns user profile (without password)
- [ ] Returns 401 if credentials are invalid
- [ ] Token is valid for 24 hours

### US-3: Protected Routes (P1)
**As a** system
**I want to** protect all task endpoints
**So that** only authenticated users can access data

**Acceptance Criteria:**
- [ ] All `/api/{user_id}/tasks*` endpoints require JWT
- [ ] JWT must be in `Authorization: Bearer <token>` header
- [ ] Invalid token returns 401 Unauthorized
- [ ] Expired token returns 401 Unauthorized
- [ ] Missing token returns 401 Unauthorized
- [ ] User can only access their own tasks (user_id match)

### US-4: Get Current User (P2)
**As a** logged-in user
**I want to** retrieve my profile
**So that** I can see my account information

**Acceptance Criteria:**
- [ ] Returns current user profile from JWT
- [ ] Does not include password
- [ ] Returns 401 if token invalid/missing

### US-5: Signout (P2)
**As a** logged-in user
**I want to** sign out
**So that** I can end my session

**Acceptance Criteria:**
- [ ] Frontend clears stored JWT token
- [ ] User is redirected to signin page
- [ ] Subsequent requests without token are rejected

---

## Data Model

### User (Managed by Better Auth)
```python
class User:
    id: str              # Primary key (UUID or string)
    email: str           # Unique, required
    name: str            # Display name
    hashed_password: str # Bcrypt hashed
    is_active: bool      # Account status
    created_at: datetime # Registration timestamp
    updated_at: datetime # Last update timestamp
```

### JWT Token Payload
```json
{
  "sub": "user_abc123",      // User ID
  "email": "user@example.com",
  "name": "John Doe",
  "exp": 1704844800,         // Expiration timestamp
  "iat": 1704758400          // Issued at timestamp
}
```

---

## API Endpoints

### POST /api/auth/signup
Create a new user account.

**Request:**
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "created_at": "2026-01-08T10:00:00Z"
  }
}
```

**Error (400 Bad Request):**
```json
{
  "detail": "Email already registered"
}
```

### POST /api/auth/login
Authenticate and receive JWT token.

**Request:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "created_at": "2026-01-08T10:00:00Z"
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

### GET /api/auth/me
Get current authenticated user profile.

**Request:**
```http
GET /api/auth/me
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2026-01-08T10:00:00Z"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid or missing authentication token"
}
```

---

## Security Requirements

### Password Policy
- Minimum 8 characters
- Hashed using bcrypt (or passlib)
- Never stored in plain text
- Never returned in API responses

### JWT Configuration
- Algorithm: HS256
- Secret: `BETTER_AUTH_SECRET` environment variable
- Expiration: 24 hours
- Stored in frontend: `localStorage` or secure cookie

### Token Validation
```python
# Backend validation flow
1. Extract token from Authorization header
2. Verify signature using secret key
3. Check expiration timestamp
4. Extract user_id from payload
5. Verify user exists and is active
6. Attach user to request context
```

### Environment Variables
```bash
# Required in .env or .env.local
BETTER_AUTH_SECRET=your-super-secret-key-minimum-32-chars
DATABASE_URL=postgresql://...
```

---

## Frontend Integration

### Token Storage
```typescript
// On successful login/signup
localStorage.setItem('token', response.access_token);
localStorage.setItem('user', JSON.stringify(response.user));

// On logout
localStorage.removeItem('token');
localStorage.removeItem('user');
```

### API Client Interceptor
```typescript
// Add to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/signin';
    }
    return Promise.reject(error);
  }
);
```

### Auth Context
```typescript
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, name: string, password: string) => Promise<void>;
  logout: () => void;
}
```

---

## Error Handling

| Status | Condition | Response |
|--------|-----------|----------|
| 400 | Invalid input | `{"detail": "Validation error message"}` |
| 400 | Email exists | `{"detail": "Email already registered"}` |
| 401 | Bad credentials | `{"detail": "Invalid email or password"}` |
| 401 | Invalid token | `{"detail": "Invalid or missing authentication token"}` |
| 401 | Expired token | `{"detail": "Token has expired"}` |

---

## Implementation Checklist

### Backend
- [ ] Install Better Auth / passlib / python-jose
- [ ] Create User model with SQLModel
- [ ] Create UserCreate, UserLogin, UserRead schemas
- [ ] Implement password hashing utilities
- [ ] Implement JWT creation/validation utilities
- [ ] Create POST /api/auth/signup endpoint
- [ ] Create POST /api/auth/login endpoint
- [ ] Create GET /api/auth/me endpoint
- [ ] Create `get_current_user` dependency
- [ ] Add auth middleware to task routes

### Frontend
- [ ] Create AuthContext provider
- [ ] Create LoginForm component
- [ ] Create SignupForm component
- [ ] Create /signin page
- [ ] Create /signup page
- [ ] Add token interceptor to API client
- [ ] Add auth guards to protected pages
- [ ] Handle 401 redirects

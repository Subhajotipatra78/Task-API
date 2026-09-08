import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in your .env file")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Auth API (Supabase & FastAPI)",
    description="Secure authentication API featuring JWT verification, route guards, and Swagger UI Bearer auth.",
    version="1.0"
)

# Swagger Bearer Authentication Scheme
security = HTTPBearer()

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class AuthCredentials(BaseModel):
    email: EmailStr
    password: str

# ---------------------------------------------------------
# Reusable Authentication Guard Dependency
# ---------------------------------------------------------
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required"
        )
    
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return user_response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# ---------------------------------------------------------
# Public Auth Routes
# ---------------------------------------------------------
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, summary="Sign Up")
def sign_up(creds: AuthCredentials):
    if not creds.email or not creds.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password cannot be blank"
        )
    try:
        response = supabase.auth.sign_up({
            "email": creds.email,
            "password": creds.password
        })
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed"
            )
        return {
            "id": response.user.id,
            "email": response.user.email,
            "created_at": response.user.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/auth/login", status_code=status.HTTP_200_OK, summary="Log In")
def log_in(creds: AuthCredentials):
    if not creds.email or not creds.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password cannot be blank"
        )
    try:
        response = supabase.auth.sign_in_with_password({
            "email": creds.email,
            "password": creds.password
        })
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials"
            )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )

# ---------------------------------------------------------
# Public Route
# ---------------------------------------------------------
@app.get("/public/info", status_code=status.HTTP_200_OK, summary="Public Info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# ---------------------------------------------------------
# Protected Routes
# ---------------------------------------------------------
@app.get("/protected/profile", status_code=status.HTTP_200_OK, summary="User Profile")
def get_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

@app.get("/protected/dashboard", status_code=status.HTTP_200_OK, summary="User Dashboard")
def get_dashboard(current_user=Depends(get_current_user)):
    return {
        "message": f"Welcome back, {current_user.email}! This is your private dashboard."
    }

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Log Out")
def log_out(current_user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return None
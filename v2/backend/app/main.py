from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from . import crud, models, schemas, auth
from .database import SessionLocal, engine
from .tasks import run_analysis_task
from .celery_worker import celery_app
from celery.result import AsyncResult

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Authentication Endpoints ---
@app.post("/api/auth/token", response_model=schemas.Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# --- Analysis and Task Endpoints ---
@app.post("/api/analyze", status_code=202)
async def submit_analysis(request: schemas.TaskCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    task = run_analysis_task.delay(ticker=request.ticker, date=request.date)
    crud.create_user_task(db=db, task=schemas.Task(id=task.id, **request.dict(), status='PENDING', owner_id=current_user.id), user_id=current_user.id)
    return {"message": "Analysis task submitted", "task_id": task.id}

@app.get("/api/tasks", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return [task for task in tasks if task.owner_id == current_user.id]

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }
    
    if task_result.status == 'FAILURE':
        response['result'] = str(task_result.info)

    return response
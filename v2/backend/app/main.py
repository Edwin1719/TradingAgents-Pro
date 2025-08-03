
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from celery.result import AsyncResult
from .tasks import run_analysis_task

app = FastAPI()

class AnalysisRequest(BaseModel):
    ticker: str
    date: str
    deep_think_llm: Optional[str] = None
    quick_think_llm: Optional[str] = None

@app.post("/analyze", status_code=202)
async def submit_analysis(request: AnalysisRequest):
    """
    Submit a new analysis task to the Celery queue.
    Allows overriding default LLM models.
    """
    # .delay() is the Celery way to call a task asynchronously
    task = run_analysis_task.delay(
        ticker=request.ticker, 
        date=request.date, 
        deep_think_llm=request.deep_think_llm, 
        quick_think_llm=request.quick_think_llm
    )
    return {"message": "Analysis task submitted", "task_id": task.id}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status and result of a Celery task.
    """
    task_result = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }
    
    if task_result.status == 'FAILURE':
        response['result'] = str(task_result.info) # Get exception info

    return response


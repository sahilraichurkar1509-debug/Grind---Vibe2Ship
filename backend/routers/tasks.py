import re
from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
try:
    from ..gemini import breakdown_task, replan_day
except ImportError:
    from gemini import breakdown_task, replan_day
from datetime import date, timedelta

router = APIRouter(prefix="/tasks")

class TaskInput(BaseModel):
    task: str
    deadline: str
    syllabus: str = ""
    existing_tasks: list = []

@router.post("/breakdown")
def breakdown(input: TaskInput):
    task = input.task
    deadline = input.deadline

    if not isinstance(task, str) or not task.strip():
        return JSONResponse(status_code=400, content={"error": "Task cannot be empty"})

    if not isinstance(deadline, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
        return JSONResponse(status_code=400, content={"error": "Deadline must be in YYYY-MM-DD format"})

    try:
        parsed_deadline = date.fromisoformat(deadline)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Deadline must be in YYYY-MM-DD format"})

    if parsed_deadline < date.today() - timedelta(days=365):
        return JSONResponse(status_code=400, content={"error": "Deadline appears to be invalid"})

    existing = getattr(input, 'existing_tasks', [])
    result = breakdown_task(input.task, input.deadline, input.syllabus, existing)
    return {"breakdown": result}

@router.post("/replan")
async def replan(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})

    if isinstance(body, dict):
        pending_tasks = body.get("tasks", [])
        current_schedule = body.get("current_schedule", [])
        constraint = body.get("constraint", "")
        duration_hours = body.get("duration_hours")
    else:
        pending_tasks = body
        current_schedule = []
        constraint = ""
        duration_hours = None

    if not isinstance(pending_tasks, list) or not pending_tasks:
        return JSONResponse(status_code=400, content={"error": "No tasks to replan. Add tasks first."})

    today = date.today().isoformat()

    # Calendar integration removed — always use default daily slots
    free_slots = [
        {"start": "08:00", "end": "10:00", "duration_minutes": 120},
        {"start": "10:00", "end": "12:00", "duration_minutes": 120},
        {"start": "13:00", "end": "14:00", "duration_minutes": 60},
        {"start": "15:00", "end": "16:00", "duration_minutes": 60},
        {"start": "16:00", "end": "18:00", "duration_minutes": 120},
        {"start": "20:00", "end": "22:00", "duration_minutes": 120}
    ]

    result = replan_day(pending_tasks, free_slots, current_schedule=current_schedule, constraint=constraint, duration_hours=duration_hours)
    if not result or result.get("error"):
        return {"plan": [], "reasoning": None, "error": result.get("error") if result else "Unknown error"}

    return {
        "plan": result.get("plan", []),
        "reasoning": result.get("reasoning", "")
    }


@router.post("/journal")
def journal(payload: dict = Body(...)):
    """Endpoint to accept end-of-day journal entries and return an AI reply."""
    finished = payload.get('finished', '')
    blockers = payload.get('blockers', '')
    try:
        try:
            from ..gemini import journal_reply
        except ImportError:
            from gemini import journal_reply
        resp = journal_reply(finished, blockers)
        if not resp:
            return {"error": "AI did not return a response."}
        return resp
    except Exception as e:
        return {"error": str(e)}

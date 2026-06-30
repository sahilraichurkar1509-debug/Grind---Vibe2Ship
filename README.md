<<<<<<< HEAD
# Grind — AI Study Companion

## Problem statement

**The Last-Minute Life Saver**

Grind is built for Indian college students who juggle multiple subjects, tight deadlines, and unpredictable life events. It does more than remind students of work: it breaks a deadline into a personalized study plan, adapts when life interrupts, and surfaces the single most important thing to do today.

## What this project is now

This version of Grind is a student-focused web app with:
- A single-page frontend in `grind.html`
- A Python FastAPI backend in `backend/main.py`
- AI-driven task breakdown and replanning through `backend/gemini.py`
- Local schedule persistence via `localStorage`
- A hidden lunch block reserved at `14:00-15:00`

### Current reality vs original plan

This implementation no longer includes active Google Calendar integration.
- There is no live calendar booking or OAuth flow in the current build.
- Calendar support was deliberately removed to keep the MVP deterministic and self-contained.
- AI still uses Gemini/OpenRouter for planning, but scheduling is based on fixed daily slots.

## Target user

Indian college students aged 18-22 who study across multiple subjects, face last-minute deadlines, and need an assistant that adapts to their changing daily schedule.

## Key features implemented

1. **AI-powered task breakdown with spaced repetition**
   - Students add a task and deadline.
   - The backend returns structured subtasks spread over days leading up to the deadline.
   - Early days focus on learning, middle days on practice, final days on revision.

2. **Syllabus-aware study planning**
   - Students can paste real syllabus topics.
   - The AI receives those topics and is instructed to generate subtasks that match the actual syllabus.

3. **Dynamic rescheduling when life interrupts**
   - Students click "reschedule something" and describe the interruption.
   - The backend replans around the blocked time using current occupied slots.

4. **Three auto-switching modes**
   - Normal: default behavior
   - Exam: activates when the nearest deadline is within 72 hours
   - Crisis: activates when the nearest deadline is within 24 hours
   - Modes update the UI theme and are stored in `localStorage`.

5. **Daily Mission**
   - The app highlights the most urgent subtask for today.
   - This keeps students focused on the single highest-priority item.

6. **Progress tracking with carry-forward**
   - Students tick subtasks as complete.
   - Completion percentage updates instantly.
   - Incomplete work persists across sessions.

7. **Evening check-in / journal reflection**
   - Students submit what they finished and what blocked them.
   - The backend returns an AI-generated reflection reply.

8. **Task persistence**
   - Tasks and plan state are saved in `localStorage`.
   - The app restores work after refresh or restart.

## What is not active in this version

- No Google Calendar OAuth or booking flow.
- No calendar free-slot sync from an external calendar.
- No `/tasks/book`, `/calendar/slots`, or `/auth/*` endpoints are currently available.
- The `frontend/` React/Vite folder is not used by `grind.html`.

## Application flow

### 1. Add a task
- User enters a task name, deadline, optional syllabus, and priority.
- The frontend sends a POST request to `/tasks/breakdown`.
- Backend AI returns subtasks with dates and start times.
- Subtasks are stored in `localStorage` and shown in the today list.

### 2. Review today's plan
- Grind shows the current date and a list of tasks/subtasks.
- The "Daily Mission" card highlights the most urgent pending subtask.
- The UI theme reflects the current mode (Normal / Exam / Crisis).

### 3. Reschedule when interrupted
- User clicks "reschedule something" and describes the interruption.
- The frontend collects current schedule items and sends them to `/tasks/replan`.
- The backend replans only the interrupted task and any affected downstream items.
- The result is rendered without overwriting unrelated tasks.

### 4. End-of-day journal
- User submits finished work and blockers.
- The frontend posts the journal data to `/tasks/journal`.
- The backend returns a short AI coaching reply.

## Architecture overview

### Frontend (`grind.html`)
- Single-file HTML app with Tailwind CSS from CDN.
- Vanilla JavaScript for state, UI rendering, and API requests.
- Uses `localStorage` for:
  - `grind-tasks`
  - `grind-schedule`
  - `grind-mode`

### Backend (`backend/main.py`)
- FastAPI app serving REST endpoints.
- CORS enabled for local browser access.
- Includes `backend/routers/tasks.py`.

### AI layer (`backend/gemini.py`)
- Sends prompts to Gemini or OpenRouter.
- Returns structured JSON responses.
- Includes validation and lunch-slot enforcement.

### Scheduling model
- Fixed free slots are used by rescheduling logic.
- Lunch hour `14:00-15:00` is blocked as unavailable.
- The backend never schedules tasks into the lunch interval.
- The scheduler only postpones tasks; it does not move them earlier than originally planned.

## Backend endpoints

- `POST /tasks/breakdown` — returns task subtasks
- `POST /tasks/replan` — replans schedule around an interruption
- `POST /tasks/journal` — returns AI reflection text

## Current AI / deployment details

- AI uses Gemini if `GEMINI_API_KEY` is configured.
- OpenRouter is supported as a fallback via `OPENROUTER_API_KEY`.
- The default OpenRouter model is `google/gemma-4-31b-it`.
- The app is designed to run locally; `grind.html` points to `http://127.0.0.1:8000`.

## How to run locally

1. Install Python dependencies:
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```
2. Start the backend:
   ```bash
   uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
3. Open `grind.html` in a browser.

## Environment variables

- `GEMINI_API_KEY` — optional Gemini key
- `OPENROUTER_API_KEY` — optional OpenRouter key
- `OPENROUTER_BASE_URL` — optional override for OpenRouter endpoint

## Notes for readers

- The current build is an MVP with a local backend and browser-based frontend.
- The calendar booking feature has been removed from the current code.
- The app is still useful as a smart replanner and AI study companion.
- If you want to restore calendar integration later, it should be rebuilt as a separate layer rather than assumed to be live today.

## Future roadmap ideas

- Add exam readiness scoring
- Confidence rating for topics before/after study
- Multi-device sync via a database
- Offline support with service workers
- WhatsApp/SMS reminders
- Burnout detection based on study patterns
*** End Patch
# Grind — AI Study Companion

## Problem statement

**The Last-Minute Life Saver**

Grind is built for Indian college students who juggle multiple subjects, tight deadlines, and unpredictable life events. It does more than remind students of work: it breaks a deadline into a personalized study plan, adapts when life interrupts, and surfaces the single most important thing to do today.

## What this project is now

This version of Grind is a student-focused web app with:
- A single-page frontend in `grind.html`
- A Python FastAPI backend in `backend/main.py`
- AI-driven task breakdown and replanning through `backend/gemini.py`
- Local schedule persistence via `localStorage`
- A hidden lunch block reserved at `14:00-15:00`

### Current reality vs original plan

This implementation no longer includes active Google Calendar integration.
- There is no live calendar booking or OAuth flow in the current build.
- Calendar support was deliberately removed to keep the MVP deterministic and self-contained.
- AI still uses Gemini/OpenRouter for planning, but scheduling is based on fixed daily slots.

## Target user

Indian college students aged 18-22 who study across multiple subjects, face last-minute deadlines, and need an assistant that adapts to their changing daily schedule.

## Key features implemented

1. **AI-powered task breakdown with spaced repetition**
   - Students add a task and deadline.
   - The backend returns structured subtasks spread over days leading up to the deadline.
   - Early days focus on learning, middle days on practice, final days on revision.

2. **Syllabus-aware study planning**
   - Students can paste real syllabus topics.
   - The AI receives those topics and is instructed to generate subtasks that match the actual syllabus.

3. **Dynamic rescheduling when life interrupts**
   - Students click "reschedule something" and describe the interruption.
   - The backend replans around the blocked time using current occupied slots.

4. **Three auto-switching modes**
   - Normal: default behavior
   - Exam: activates when the nearest deadline is within 72 hours
   - Crisis: activates when the nearest deadline is within 24 hours
   - Modes update the UI theme and are stored in `localStorage`.

5. **Daily Mission**
   - The app highlights the most urgent subtask for today.
   - This keeps students focused on the single highest-priority item.

6. **Progress tracking with carry-forward**
   - Students tick subtasks as complete.
   - Completion percentage updates instantly.
   - Incomplete work persists across sessions.

7. **Evening check-in / journal reflection**
   - Students submit what they finished and what blocked them.
   - The backend returns an AI-generated reflection reply.

8. **Task persistence**
   - Tasks and plan state are saved in `localStorage`.
   - The app restores work after refresh or restart.

## What is not active in this version

- No Google Calendar OAuth or booking flow.
- No calendar free-slot sync from an external calendar.
- No `/tasks/book`, `/calendar/slots`, or `/auth/*` endpoints are currently available.
- The `frontend/` React/Vite folder is not used by `grind.html`.

## Application flow

### 1. Add a task
- User enters a task name, deadline, optional syllabus, and priority.
- The frontend sends a POST request to `/tasks/breakdown`.
- Backend AI returns subtasks with dates and start times.
- Subtasks are stored in `localStorage` and shown in the today list.

### 2. Review today's plan
- Grind shows the current date and a list of tasks/subtasks.
- The "Daily Mission" card highlights the most urgent pending subtask.
- The UI theme reflects the current mode (Normal / Exam / Crisis).

### 3. Reschedule when interrupted
- User clicks "reschedule something" and describes the interruption.
- The frontend collects current schedule items and sends them to `/tasks/replan`.
- The backend replans only the interrupted task and any affected downstream items.
- The result is rendered without overwriting unrelated tasks.

### 4. End-of-day journal
- User submits finished work and blockers.
- The frontend posts the journal data to `/tasks/journal`.
- The backend returns a short AI coaching reply.

## Architecture overview

### Frontend (`grind.html`)
- Single-file HTML app with Tailwind CSS from CDN.
- Vanilla JavaScript for state, UI rendering, and API requests.
- Uses `localStorage` for:
  - `grind-tasks`
  - `grind-schedule`
  - `grind-mode`

### Backend (`backend/main.py`)
- FastAPI app serving REST endpoints.
- CORS enabled for local browser access.
- Includes `backend/routers/tasks.py`.

### AI layer (`backend/gemini.py`)
- Sends prompts to Gemini or OpenRouter.
- Returns structured JSON responses.
- Includes validation and lunch-slot enforcement.

### Scheduling model
- Fixed free slots are used by rescheduling logic.
- Lunch hour `14:00-15:00` is blocked as unavailable.
- The backend never schedules tasks into the lunch interval.
- The scheduler only postpones tasks; it does not move them earlier than originally planned.

## Backend endpoints

- `POST /tasks/breakdown` — returns task subtasks
- `POST /tasks/replan` — replans schedule around an interruption
- `POST /tasks/journal` — returns AI reflection text

## Current AI / deployment details

- AI uses Gemini if `GEMINI_API_KEY` is configured.
- OpenRouter is supported as a fallback via `OPENROUTER_API_KEY`.
- The default OpenRouter model is `google/gemma-4-31b-it`.
- The app is designed to run locally; `grind.html` points to `http://127.0.0.1:8000`.

## How to run locally

1. Install Python dependencies:
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```
2. Start the backend:
   ```bash
   uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
3. Open `grind.html` in a browser.

## Environment variables

- `GEMINI_API_KEY` — optional Gemini key
- `OPENROUTER_API_KEY` — optional OpenRouter key
- `OPENROUTER_BASE_URL` — optional override for OpenRouter endpoint

## Notes for readers

- The current build is an MVP with a local backend and browser-based frontend.
- The calendar booking feature has been removed from the current code.
- The app is still useful as a smart replanner and AI study companion.
- If you want to restore calendar integration later, it should be rebuilt as a separate layer rather than assumed to be live today.

## Future roadmap ideas

- Add exam readiness scoring
- Confidence rating for topics before/after study
- Multi-device sync via a database
- Offline support with service workers
- WhatsApp/SMS reminders
- Burnout detection based on study patterns
>>>>>>> ef288f7 (Initial project import: serve frontend from backend and add Dockerfile)

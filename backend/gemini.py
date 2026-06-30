import os
import json
import re
import time
import urllib.request
import urllib.error
from datetime import date as dt_date, datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv = None

api_key = os.getenv("GEMINI_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")
openrouter_base = os.getenv("OPENROUTER_BASE_URL", "https://api.openrouter.ai/v1/chat/completions")
print(f"GEMINI KEY LOADED: {api_key[:15] if api_key else 'NOT FOUND'}")
print(f"OPENROUTER KEY LOADED: {'YES' if openrouter_key else 'NO'}")

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_AI_RETRIES = 2

def call_ai(prompt: str, system_instruction: str = None):
    default_instruction = "You are a smart productivity assistant for Indian college students. Always respond with valid JSON only, no markdown, no extra text."
    instruction = system_instruction or default_instruction

    if openrouter_key:
        url = openrouter_base
        payload = {
            "model": "google/gemma-4-31b-it",
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openrouter_key}"
        }
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": instruction}]},
            "generationConfig": {"temperature": 0.7}
        }
        headers = {"Content-Type": "application/json"}

    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers)

    for attempt in range(MAX_AI_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                result = json.loads(res.read().decode())
            if openrouter_key:
                return result["choices"][0]["message"]["content"]
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")
            if e.code in RETRY_STATUS_CODES and attempt < MAX_AI_RETRIES:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            if e.code == 429:
                raise RuntimeError("AI rate limit reached. Please try again later.")
            if e.code >= 500:
                raise RuntimeError("AI service unavailable. Please try again later.")
            raise RuntimeError(f"AI service error {e.code}: {body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Unable to reach AI service: {e.reason}")
        except json.JSONDecodeError:
            raise RuntimeError("AI service returned invalid JSON. Please try again.")

def normalize_subtask_start(start_time: str):
    try:
        h, m = map(int, start_time.split(':'))
        h = max(0, min(23, h))
        m = max(0, min(59, m))
        return h * 60 + m
    except Exception:
        return None


def find_allowed_start(duration: int):
    allowed_windows = [
        (8 * 60, 10 * 60),
        (10 * 60, 12 * 60),
        (13 * 60, 14 * 60),
        (15 * 60, 16 * 60),
        (16 * 60, 18 * 60),
        (20 * 60, 22 * 60),
    ]
    for start, end in allowed_windows:
        if end - start >= duration:
            return start
    return None


def fix_lunch_overlap(subtasks: list):
    fixed = []
    for item in subtasks:
        start_min = normalize_subtask_start(item.get('start_time', '00:00'))
        duration = item.get('duration_minutes', 0)
        if start_min is None or duration <= 0:
            fixed.append(item)
            continue

        lunch_start = 14 * 60
        lunch_end = 15 * 60
        if start_min < lunch_end and start_min + duration > lunch_start:
            candidate = find_allowed_start(duration)
            if candidate is not None:
                item['start_time'] = to_time(candidate)
        fixed.append(item)
    return fixed


def breakdown_task(task: str, deadline: str, syllabus: str = "", existing_tasks: list = []):
    today_str = dt_date.today().isoformat()
    syllabus_context = f"\n\nThe student's syllabus topics are:\n{syllabus}\n\nIMPORTANT: Only create subtasks based on these specific syllabus topics." if syllabus.strip() else ""

    existing_context = ""
    if existing_tasks:
        existing_context = f"\n\nThe student already has these other tasks scheduled:\n{json.dumps(existing_tasks, indent=2)}\n\nIMPORTANT: When scheduling subtasks for the new task, check these existing tasks and avoid scheduling at the same time. If multiple tasks fall on the same day, give them different time slots with at least 1 hour gap between them."

    prompt = f"""You are a smart study planner for an Indian college student.
Today is {today_str}. The new task '{task}' is due by {deadline}.{syllabus_context}{existing_context}

CRITICAL RULES:
- Schedule ALL subtasks BEFORE the deadline {deadline}. Never schedule on or after {deadline}.
- Today is {today_str} (day 1). Calculate days available between today and deadline.
- Spread subtasks across available days using spaced repetition:
  * Early days: learn new concepts (2-4 hours)
  * Middle days: practice problems (1-2 hours)
  * Last day before deadline: revision only (max 1 hour)
- If multiple tasks are on the same day, use different time slots with at least 1 hour gap.
- Never schedule after the deadline.
- Each subtask must have a date strictly before {deadline}.
- Use only these available study windows each day: 08:00-10:00, 10:00-12:00, 13:00-14:00, 15:00-16:00, 16:00-18:00, 20:00-22:00.
- Do not schedule any subtask between 14:00 and 15:00.

Return ONLY this exact JSON, no markdown:
{{
    "task_name": "{task}",
    "deadline": "{deadline}",
    "subtasks": [
        {{"name": "subtask name", "duration_minutes": 120, "day": 1, "date": "{today_str}", "start_time": "09:00"}},
        {{"name": "subtask name", "duration_minutes": 90, "day": 2, "date": "next date", "start_time": "10:00"}}
    ],
    "reasoning": "brief explanation of spaced repetition approach and how conflicts were avoided"
}}"""
    try:
        text = call_ai(prompt).strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)

        if not isinstance(result, dict) or "subtasks" not in result or not isinstance(result["subtasks"], list) or not result["subtasks"]:
            return {"error": "AI returned an unexpected response structure. Please try again."}

        for subtask in result["subtasks"]:
            if not isinstance(subtask, dict):
                return {"error": "AI returned an unexpected response structure. Please try again."}
            if not all(k in subtask for k in ["name", "duration_minutes", "day", "date", "start_time"]):
                return {"error": "AI returned an unexpected response structure. Please try again."}
            if not isinstance(subtask.get("name"), str) or not isinstance(subtask.get("duration_minutes"), int) or isinstance(subtask.get("duration_minutes"), bool):
                return {"error": "AI returned an unexpected response structure. Please try again."}

        result["subtasks"] = fix_lunch_overlap(result["subtasks"])
        return result
    except Exception as e:
        return {"error": str(e)}

def parse_time_from_text(text: str):
    if not isinstance(text, str):
        return None
    match = re.search(r"\b(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text, re.IGNORECASE)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    meridiem = (match.group(3) or "").lower()
    if meridiem == "pm" and hour != 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    hour = max(0, min(23, hour))
    minute = max(0, min(59, minute))
    return f"{hour:02d}:{minute:02d}"


def to_minutes(time_str: str):
    try:
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    except Exception:
        return 0


def to_time(minutes: int):
    minutes = max(0, min(23 * 60 + 59, minutes))
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def merge_intervals(intervals):
    sorted_intervals = sorted([interval for interval in intervals if interval[1] > interval[0]])
    merged = []
    for start, end in sorted_intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged


def subtract_intervals(start: int, end: int, occupied):
    occupied = merge_intervals(occupied)
    free = []
    cursor = start
    for occ_start, occ_end in occupied:
        if occ_end <= cursor:
            continue
        if occ_start > cursor:
            free.append((cursor, min(occ_start, end)))
        cursor = max(cursor, occ_end)
        if cursor >= end:
            break
    if cursor < end:
        free.append((cursor, end))
    return free


def interval_overlap(start1: int, duration1: int, start2: int, duration2: int):
    end1 = start1 + duration1
    end2 = start2 + duration2
    return start1 < end2 and start2 < end1


def deterministic_replan(pending_tasks: list, free_slots: list, current_schedule: list, constraint: str, duration_hours: int):
    today = dt_date.today()
    blocked_date = today.isoformat()
    blocked_start = parse_time_from_text(constraint) or (free_slots[0].get('start') if free_slots else '09:00')
    blocked_duration = int(duration_hours) * 60 if isinstance(duration_hours, int) else 120
    blocked_start_min = to_minutes(blocked_start)
    blocked_end_min = blocked_start_min + blocked_duration

    schedule_by_date = {}
    for item in (current_schedule or []):
        date = item.get('date')
        start_time = item.get('start_time')
        duration = item.get('duration_minutes')
        if not date or not start_time or not isinstance(duration, int):
            continue
        schedule_by_date.setdefault(date, []).append(item.copy())

    conflict_items = []
    for item in schedule_by_date.get(blocked_date, []):
        if interval_overlap(to_minutes(item.get('start_time', '00:00')), item.get('duration_minutes', 0), blocked_start_min, blocked_duration):
            conflict_items.append(item)

    def get_deadline(item):
        parent = item.get('parentTask') or item.get('task')
        for task in pending_tasks:
            if task.get('task') == parent and isinstance(task.get('deadline'), str):
                try:
                    return dt_date.fromisoformat(task['deadline'])
                except Exception:
                    return None
        return None

    def find_slot(item, earliest_date, earliest_minute):
        deadline = get_deadline(item) or (earliest_date + timedelta(days=14))
        original_date = None
        original_start_min = None
        try:
            original_date = dt_date.fromisoformat(item.get('date'))
            original_start_min = to_minutes(item.get('start_time', '00:00'))
        except Exception:
            pass

        current_date = earliest_date
        while current_date <= deadline:
            if original_date is not None and current_date < original_date:
                current_date += timedelta(days=1)
                continue

            date_key = current_date.isoformat()
            occupied = []
            for existing in schedule_by_date.get(date_key, []):
                occupied.append((to_minutes(existing.get('start_time', '00:00')), to_minutes(existing.get('start_time', '00:00')) + existing.get('duration_minutes', 0)))
            if date_key == blocked_date:
                occupied.append((blocked_start_min, blocked_end_min))
            occupied.append((14 * 60, 15 * 60))  # keep lunch 2-3pm free
            occupied = merge_intervals(occupied)
            # Merge provided free_slots into contiguous available windows for the day
            day_slots = []
            for slot in free_slots:
                s = to_minutes(slot.get('start', '00:00'))
                e = to_minutes(slot.get('end', '23:59'))
                if e <= s:
                    continue
                day_slots.append((s, e))
            day_slots = merge_intervals(day_slots)

            for slot_start, slot_end in day_slots:
                if current_date == earliest_date:
                    start_search = max(slot_start, earliest_minute)
                else:
                    start_search = slot_start
                if current_date == original_date and original_start_min is not None:
                    start_search = max(start_search, original_start_min)
                free_segments = subtract_intervals(start_search, slot_end, occupied)
                for seg_start, seg_end in free_segments:
                    # allow using the full contiguous slot segment (which may be merged from adjacent free_slots)
                    if seg_end - seg_start >= item.get('duration_minutes', 0):
                        # ensure the candidate does not cross the lunch block (14:00-15:00)
                        candidate_start = seg_start
                        candidate_duration = item.get('duration_minutes', 0)
                        lunch_start = 14 * 60
                        lunch_dur = 60
                        if interval_overlap(candidate_start, candidate_duration, lunch_start, lunch_dur):
                            # skip slots that would overlap lunch
                            continue
                        return date_key, to_time(seg_start)
            current_date += timedelta(days=1)
        return None, None

    # Re-schedule all tasks in order, allowing later tasks to shift if needed.
    all_items = []
    for date_key in sorted(schedule_by_date.keys()):
        for item in sorted(schedule_by_date[date_key], key=lambda x: to_minutes(x.get('start_time', '00:00'))):
            all_items.append(item.copy())

    # Put conflict items first if they should take precedence on the blocked day.
    def item_key(item):
        return (item.get('task'), item.get('date'), item.get('start_time'), item.get('duration_minutes'))

    conflict_keys = set(item_key(item) for item in conflict_items)
    all_items.sort(key=lambda item: (
        0 if item_key(item) in conflict_keys else 1,
        item.get('date', ''),
        to_minutes(item.get('start_time', '00:00'))
    ))

    schedule_by_date = {}
    plan = []

    for item in all_items:
        original_date = None
        original_start_min = None
        try:
            original_date = dt_date.fromisoformat(item.get('date'))
            original_start_min = to_minutes(item.get('start_time', '00:00'))
        except Exception:
            pass

        if item_key(item) in conflict_keys and item.get('date') == blocked_date:
            earliest_date = today
            earliest_minute = blocked_end_min
        else:
            if original_date is None:
                earliest_date = today
            else:
                earliest_date = original_date
            earliest_minute = original_start_min or 0

        new_date, new_start = find_slot(item, earliest_date, earliest_minute)
        if not new_date:
            return {'error': 'Unable to reschedule the task while preserving deadlines. Please try a shorter unavailable window or use a later day.'}

        item_copy = item.copy()
        item_copy['date'] = new_date
        item_copy['start_time'] = new_start
        schedule_by_date.setdefault(new_date, []).append(item_copy)

        plan.append({
            'task': item_copy.get('task'),
            'date': item_copy.get('date'),
            'start_time': item_copy.get('start_time'),
            'duration_minutes': item_copy.get('duration_minutes')
        })

    plan.sort(key=lambda x: (x['date'], to_minutes(x['start_time'])))
    return {
        'reasoning': 'Rescheduled the blocked task and postponed later tasks as needed to preserve the plan.',
        'plan': plan
    }


def replan_day(pending_tasks: list, free_slots: list, current_schedule: list = None, constraint: str = "", duration_hours: int = None):
    if current_schedule or constraint:
        return deterministic_replan(pending_tasks, free_slots, current_schedule, constraint, duration_hours)

    prompt = f"""A college student has these pending tasks: {json.dumps(pending_tasks)}.
Their free time slots today are: {json.dumps(free_slots)}.
Use the provided free time slots to create a schedule that covers today and upcoming days as needed, respecting each task's deadline and priority.
If a task can be scheduled later than today, assign it to a future date before its deadline.
Always provide a date for every plan item in YYYY-MM-DD format.
If you include tasks for today, schedule them only inside the given free slots.
Do not restrict the schedule to only today.
Return this exact JSON structure:
{{
    "reasoning": "explanation of prioritization",
    "plan": [
        {{"task": "task name", "date": "YYYY-MM-DD", "start_time": "09:00", "duration_minutes": 60}}
    ]
}}
"""
    try:
        text = call_ai(prompt).strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)

        plan = result.get('plan', [])
        if not plan or not isinstance(plan, list) or len(plan) == 0:
            return {"error": "AI returned an empty plan. Please try again."}
        # Ensure each item has at least a task name
        for p in plan:
            if 'task' not in p:
                return {"error": "AI returned an unexpected response structure. Please try again."}

        return result
    except Exception as e:
        return {"error": str(e)}


def journal_reply(finished_text: str, blockers_text: str):
    """Generate a short encouraging AI response to an end-of-day journal entry."""
    if not finished_text and not blockers_text:
        return {"error": "No journal content provided."}
    today_str = dt_date.today().isoformat()
    prompt = f"You are a friendly study coach. Today is {today_str}. The student wrote:\n\nFinished: {finished_text}\nBlocked by: {blockers_text}\n\nRespond with a short encouraging message (1-3 sentences) praising effort, suggesting one small improvement for tomorrow, and a motivating closing line. Return only plain text." 
    try:
        resp = call_ai(prompt)
        return {"reply": resp}
    except Exception as e:
        return {"error": str(e)}
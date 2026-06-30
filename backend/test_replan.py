import json
import urllib.request
import urllib.error

API = "http://127.0.0.1:8000"


def test_replan():
    payload = [
        {"task": "Prepare for DSA exam", "deadline": "2026-07-05", "priority": "High"},
        {"task": "Submit Maths assignment", "deadline": "2026-07-03", "priority": "Medium"},
    ]

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API}/tasks/replan",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        res = urllib.request.urlopen(req)
        result = json.loads(res.read().decode())
        print("REPLAN SUCCESS:")
        print(json.dumps(result, indent=2))
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code}:")
        print(e.read().decode()[:500])


if __name__ == "__main__":
    test_replan()

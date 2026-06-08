#!/usr/bin/env python3
import sys
import time
import json
import urllib.request
import urllib.error

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
PROMPT   = sys.argv[2] if len(sys.argv) > 2 else "Explain async task queues in two sentences."

BASE_URL = BASE_URL.rstrip("/")


def get(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=10) as r:
        return json.loads(r.read())


def post(path, data):
    body = json.dumps(data).encode()
    req  = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def colored(text, code):
    return f"\033[{code}m{text}\033[0m"


def main():
    print(colored(f"\n  LLM API Platform - demo", "1;36"))
    print(colored(f"  Target: {BASE_URL}\n", "2"))

    print("  [1/3] Health check ...", end=" ", flush=True)
    try:
        h = get("/health")
        status = h.get("status", "?")
        color  = "32" if status == "ok" else "33"
        print(colored(status, color))
        for svc, s in h.get("services", {}).items():
            icon = "✓" if s in ("ok", "configured") else "✗"
            c    = "32" if s in ("ok", "configured") else "31"
            print(f"     {colored(icon, c)} {svc}: {s}")
    except Exception as e:
        print(colored(f"FAILED ({e})", "31"))
        sys.exit(1)

    print(f"\n  [2/3] Submitting prompt ...", end=" ", flush=True)
    print(colored(f'"{PROMPT}"', "2"))
    try:
        sub = post("/generate", {"prompt": PROMPT})
        task_id = sub["task_id"]
        print(f"     task_id: {colored(task_id, '33')}")
    except Exception as e:
        print(colored(f"FAILED ({e})", "31"))
        sys.exit(1)

    print("\n  [3/3] Waiting for result ", end="", flush=True)
    start = time.time()
    for _ in range(60):
        time.sleep(1)
        print(".", end="", flush=True)
        try:
            s = get(f"/status/{task_id}")
            if s["status"] == "SUCCESS":
                elapsed = round(time.time() - start, 2)
                r = s["result"]
                print(colored(f" done ({elapsed}s)\n", "32"))
                print(colored("  === Response ===", "2"))
                # word-wrap at 72 chars
                words, line = r["response"].split(), ""
                for w in words:
                    if len(line) + len(w) + 1 > 72:
                        print(f"  {line}")
                        line = w
                    else:
                        line = f"{line} {w}" if line else w
                if line:
                    print(f"  {line}")
                print(colored("\n  === Stats ===", "2"))
                print(f"  model:   {r.get('model')}")
                print(f"  latency: {r.get('latency_sec')}s")
                print(f"  tokens:  {r.get('total_tokens')} "
                      f"(prompt {r.get('prompt_tokens')} + completion {r.get('completion_tokens')})")
                print()
                return
            elif s["status"] not in ("PENDING", "PROGRESS"):
                print(colored(f"\n  Task failed: {s.get('error')}", "31"))
                sys.exit(1)
        except Exception:
            pass

    print(colored("\n  Timed out.", "31"))
    sys.exit(1)


if __name__ == "__main__":
    main()

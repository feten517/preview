import json
import sys
import time
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18080"
ORIGINAL_URL = "https://example.com"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Stop urllib from following redirects, so we can inspect them."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)
failures = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL") + ": " + name + (" - " + detail if detail else ""))
    if not ok:
        failures.append(name)


def wait_until_up(timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with opener.open(BASE + "/", timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def post_json(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with opener.open(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None


def get_no_follow(path):
    try:
        with opener.open(BASE + path, timeout=5) as r:
            return r.status, r.headers.get("Location")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")


if not wait_until_up():
    print("FAIL: preview did not become reachable at " + BASE)
    sys.exit(1)

# 1. Home route
with opener.open(BASE + "/", timeout=5) as r:
    body = json.loads(r.read())
check("home route returns the alive message", body.get("message") == "Snip is alive", str(body))

# 2. Shorten a URL
status, data = post_json("/shorten", {"url": ORIGINAL_URL})
code = data.get("short_code") if data else None
check("POST /shorten returns 200 and a short code", status == 200 and bool(code), "status=" + str(status))

# 3. The short code redirects to the original URL
if code:
    status, location = get_no_follow("/" + code)
    check(
        "short code redirects to the original URL",
        status in (301, 302, 303, 307, 308) and location == ORIGINAL_URL,
        f"status={status} location={location}",
    )
else:
    check("short code redirects to the original URL", False, "no short code to test")

# 4. Invalid input is rejected
status, _ = post_json("/shorten", {"url": "not-a-url"})
check("invalid URL is rejected with 422", status == 422, "status=" + str(status))

print()
print(str(len(failures)) + " failed")
sys.exit(1 if failures else 0)

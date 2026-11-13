"""On-time posting loop (see .github/workflows/keeper.yml).

Sleeps until LEAD seconds before each slot, then dispatches publish.yml, which waits for
the exact slot minute and posts. On every wake it also checks for overdue, unpublished
queue folders from today and dispatches publish.yml at once. Exits ~5h40m after start so
the workflow can start the next keeper run before the 6 h job limit.
"""
import datetime as dt, json, os, subprocess, time

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
SLOTS = [(9, 0), (13, 0), (19, 30)]
LEAD = 180                      # dispatch 3 min before the slot
BUDGET = 5 * 3600 + 40 * 60     # leave margin before the 355 min timeout
REPO = os.environ["REPO"]
start = time.time()


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True)


def dispatch(why):
    for i in range(6):
        r = sh("gh", "workflow", "run", "publish.yml", "-R", REPO, "--ref", "main")
        if r.returncode == 0:
            print(f"{dt.datetime.now(IST):%H:%M:%S} dispatched publish ({why})", flush=True)
            return True
        print("dispatch failed:", r.stderr.strip()[:200], flush=True)
        time.sleep(20)
    return False


def overdue():
    """Today's slots that have passed, have a queue folder and are not in published.json."""
    sh("git", "fetch", "-q", "origin", "main")
    pub = sh("git", "show", "origin/main:published.json")
    try:
        published = json.loads(pub.stdout) if pub.returncode == 0 else {}
    except ValueError:
        published = {}
    tree = sh("git", "ls-tree", "--name-only", "origin/main", "queue/").stdout.split()
    folders = [t.split("/", 1)[1] for t in tree if "/" in t]
    now = dt.datetime.now(IST)
    out = []
    for h, m in SLOTS:
        slot = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if slot + dt.timedelta(minutes=4) <= now <= slot + dt.timedelta(hours=6):
            pre = f"{now:%Y-%m-%d}_{h:02d}{m:02d}_"
            out += [f for f in folders if f.startswith(pre) and f not in published]
    return out


def next_fire(now):
    for d in (0, 1):
        day = now + dt.timedelta(days=d)
        for h, m in SLOTS:
            slot = day.replace(hour=h, minute=m, second=0, microsecond=0)
            fire = slot - dt.timedelta(seconds=LEAD)
            if fire > now:
                return fire, slot
    raise RuntimeError("no slot")


while True:
    late = overdue()
    if late:
        dispatch("overdue: " + ", ".join(late))
        time.sleep(240)
        continue
    now = dt.datetime.now(IST)
    fire, slot = next_fire(now)
    left = BUDGET - (time.time() - start)
    wait = (fire - now).total_seconds()
    if wait > left:
        print(f"next slot {slot:%H:%M} is after this run's budget; sleeping {left/60:.0f} min then restarting", flush=True)
        time.sleep(max(0, left))
        break
    print(f"sleeping {wait/60:.1f} min until {fire:%H:%M:%S} for the {slot:%H:%M} slot", flush=True)
    time.sleep(max(0, wait))
    dispatch(f"{slot:%H:%M} slot")
    time.sleep(LEAD + 300)      # let publish post, then re-check (catches failures)

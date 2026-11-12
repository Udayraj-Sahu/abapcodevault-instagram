"""Sleep until the next posting slot if it is close.

GitHub starts scheduled workflows late (often 15-60+ min) or skips them, so the
publish workflow is started well BEFORE each slot and waits here, then posts on time.
If no slot is within WINDOW minutes, return at once (normal catch-up run).
"""
import datetime as dt, time

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
SLOTS = ["09:00", "13:00", "19:30", "21:00"]
WINDOW = 150  # minutes

now = dt.datetime.now(IST)
for s in SLOTS:
    h, m = map(int, s.split(":"))
    t = now.replace(hour=h, minute=m, second=20, microsecond=0)
    wait = (t - now).total_seconds()
    if 0 < wait <= WINDOW * 60:
        print(f"Waiting {wait/60:.1f} min for the {s} IST slot")
        time.sleep(wait)
        break
else:
    print("No slot soon; publishing whatever is due now.")

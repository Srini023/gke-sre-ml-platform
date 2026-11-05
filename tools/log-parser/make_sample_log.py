#!/usr/bin/env python3
"""Generate a fake web access log for practising log parsing."""
import random
from datetime import datetime, timedelta

random.seed(42)  # same log on every run

IPS = ["203.0.113.%d" % n for n in range(1, 31)]
IP_WEIGHTS = [30, 20, 10] + [2] * 27  # a few very busy clients
ENDPOINTS = [  # (path, how common, typical seconds)
    ("/healthz", 40, 0.002),
    ("/readyz", 25, 0.003),
    ("/predict", 30, 0.060),
    ("/docs", 3, 0.010),
    ("/admin", 2, 0.020),
]


def pick_status(path):
    r = random.random()
    if path == "/predict":
        if r < 0.03:
            return 422
        if r < 0.05:
            return 500
        if r < 0.06:
            return 502
        return 200
    if path == "/admin":
        return 404 if r < 0.9 else 403
    return 200 if r < 0.995 else 503


def make_line(ts):
    ip = random.choices(IPS, weights=IP_WEIGHTS)[0]
    path, _, typical = random.choices(ENDPOINTS, weights=[e[1] for e in ENDPOINTS])[0]
    method = "POST" if path == "/predict" else "GET"
    seconds = typical * random.lognormvariate(0, 0.6)
    if random.random() < 0.01:
        seconds *= 20  # a rare very slow request
    return '%s - - [%s +0530] "%s %s HTTP/1.1" %d %d "-" "curl/8.5" %.3f' % (
        ip, ts.strftime("%d/%b/%Y:%H:%M:%S"), method, path,
        pick_status(path), random.randint(200, 2000), seconds,
    )


def main():
    ts = datetime(2026, 11, 5, 13, 0, 0)
    lines = []
    for _ in range(3000):
        ts += timedelta(seconds=random.random())
        lines.append(make_line(ts))
    for junk in ["-", "garbage line", "truncated 1.2.3.4 - - [05/Nov"]:
        lines.insert(random.randrange(len(lines)), junk)
    with open("sample_access.log", "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote %d lines" % len(lines))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""log-parser: summarise a web access log (top IPs, status codes, slow endpoints).

Exit codes: 0 = ok, 1 = no valid lines, 2 = could not read the file.
"""
import argparse
import math
import re
import sys
from collections import Counter, defaultdict

LINE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) [^"]*" '
    r'(?P<status>\d{3}) (?P<size>\d+|-) "[^"]*" "[^"]*" (?P<secs>[\d.]+)$'
)


def parse_line(line):
    """Return a dict for a valid log line, or None for a broken one."""
    match = LINE.match(line.rstrip("\n"))
    if match is None:
        return None
    rec = match.groupdict()
    rec["status"] = int(rec["status"])
    rec["secs"] = float(rec["secs"])
    return rec


def percentile(sorted_values, pct):
    """Nearest-rank percentile of an already sorted list."""
    if not sorted_values:
        return 0.0
    rank = math.ceil(pct / 100 * len(sorted_values))
    return sorted_values[max(rank - 1, 0)]


def summarise(path):
    ips = Counter()
    statuses = Counter()
    errors = Counter()
    times = defaultdict(list)
    good = bad = 0
    with open(path) as f:  # one line at a time: safe for huge files
        for line in f:
            rec = parse_line(line)
            if rec is None:
                bad += 1
                continue
            good += 1
            ips[rec["ip"]] += 1
            statuses[rec["status"]] += 1
            times[rec["path"]].append(rec["secs"])
            if rec["status"] >= 500:
                errors[rec["path"]] += 1
    return good, bad, ips, statuses, errors, times


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarise a web access log.")
    parser.add_argument("path", help="access log file")
    parser.add_argument("--top", type=int, default=5, help="how many IPs to show")
    args = parser.parse_args(argv)

    try:
        good, bad, ips, statuses, errors, times = summarise(args.path)
    except OSError as err:
        print("ERROR: " + str(err), file=sys.stderr)
        return 2

    print("Parsed %d lines, skipped %d bad lines" % (good, bad))
    if good == 0:
        print("No valid lines found.")
        return 1

    print("\nTop %d IPs:" % args.top)
    for ip, n in ips.most_common(args.top):
        print("  %-15s %5d  (%.1f%%)" % (ip, n, 100 * n / good))

    print("\nStatus codes:")
    for code, n in sorted(statuses.items()):
        print("  %d  %5d" % (code, n))
    classes = Counter()
    for code, n in statuses.items():
        classes["%dxx" % (code // 100)] += n
    print("  by class: " + ", ".join("%s=%d" % kv for kv in sorted(classes.items())))

    print("\nEndpoints, slowest p99 first:")
    print("  %-10s %8s %8s %8s %5s" % ("path", "requests", "avg_ms", "p99_ms", "5xx"))
    rows = []
    for path, secs in times.items():
        ordered = sorted(secs)
        rows.append((percentile(ordered, 99), path, len(secs), sum(secs) / len(secs)))
    for p99, path, count, avg in sorted(rows, reverse=True):
        print("  %-10s %8d %8.1f %8.1f %5d" % (path, count, avg * 1000, p99 * 1000, errors[path]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

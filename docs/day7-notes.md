# Day 7: Week 1 wrap-up, log parser, tests

## What I did
- README refresh: roadmap now says GKE (not kind), CKA line removed, `tools/` folder added, new "What works today" section.
- Checked billing: Nov 1 to 5 gross cost Rs 66.32, fully covered by the free-trial credit (total Rs 0.00). About Rs 13 per lab session.
- Ran gke-guard's warning path with a faked cluster list (exit code 1).
- Python Week 1 deliverable: `tools/log-parser/` (make_sample_log.py generates a fake access log, log_parser.py reports top IPs, status codes, per-endpoint average, p99 and 5xx counts).
- pytest tests for both tools: 8 passed (monkeypatch for gke-guard, tmp_path for the parser).

## Findings from the sample log (synthetic data)
- 3000 valid lines, 3 broken lines skipped without crashing.
- /predict: average 91 ms but p99 1140 ms (about 12x), and 28 5xx out of 865 requests (3.2%).
- Overall 36 5xx out of 3000 (1.2%): success rate 98.8%, which would break a 99.9% SLO.
- Averages hide the tail, so SLOs use percentiles.

## Lessons
- Check a file exists (ls, wc -l, cat) before assuming a pasted block ran.
- Keep generated sample data out of Git (.gitignore rule for tools/log-parser/*.log).
- A rate from a tiny sample (2 errors in 91 requests) is noisy.

## Interview points
- Why p99 and not average? What is nearest-rank percentile?
- How to parse a huge log: read line by line, compiled regex, Counter, skip and count bad lines.
- How to test code that calls external tools: monkeypatch the function, no network or cost.
- Exit codes: 0 ok, 1 findings, 2 could not run.

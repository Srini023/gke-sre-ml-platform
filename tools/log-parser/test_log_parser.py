import log_parser

GOOD = '203.0.113.1 - - [05/Nov/2026:13:00:00 +0530] "GET /healthz HTTP/1.1" 200 378 "-" "curl/8.5" 0.001'
ERR = '203.0.113.2 - - [05/Nov/2026:13:00:01 +0530] "POST /predict HTTP/1.1" 500 120 "-" "curl/8.5" 0.250'


def test_parse_good_line():
    rec = log_parser.parse_line(GOOD)
    assert rec["ip"] == "203.0.113.1"
    assert rec["path"] == "/healthz"
    assert rec["status"] == 200
    assert rec["secs"] == 0.001


def test_bad_lines_return_none():
    assert log_parser.parse_line("garbage line") is None
    assert log_parser.parse_line("") is None


def test_percentile():
    values = list(range(1, 11))
    assert log_parser.percentile(values, 50) == 5
    assert log_parser.percentile(values, 100) == 10
    assert log_parser.percentile([], 99) == 0.0


def test_summarise_counts(tmp_path):
    log = tmp_path / "t.log"
    log.write_text(GOOD + "\ngarbage\n" + ERR + "\n")
    good, bad, ips, statuses, errors, times = log_parser.summarise(str(log))
    assert (good, bad) == (2, 1)
    assert statuses[200] == 1 and statuses[500] == 1
    assert errors["/predict"] == 1


def test_missing_file_returns_2():
    assert log_parser.main(["no-such-file.log"]) == 2

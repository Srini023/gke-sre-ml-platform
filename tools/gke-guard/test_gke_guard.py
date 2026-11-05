import gke_guard

FAKE = [{"name": "demo", "location": "asia-south1-a", "status": "RUNNING",
         "currentNodeCount": 2, "createTime": "2026-11-05T10:00:00"}]


def test_no_clusters_returns_0(monkeypatch, capsys):
    monkeypatch.setattr(gke_guard, "list_clusters", lambda project=None: [])
    assert gke_guard.main([]) == 0
    assert "OK" in capsys.readouterr().out


def test_cluster_found_returns_1(monkeypatch, capsys):
    monkeypatch.setattr(gke_guard, "list_clusters", lambda project=None: FAKE)
    assert gke_guard.main([]) == 1
    out = capsys.readouterr().out
    assert "WARNING" in out and "demo" in out


def test_gcloud_error_returns_2(monkeypatch, capsys):
    def boom(project=None):
        raise RuntimeError("gcloud failed: nope")
    monkeypatch.setattr(gke_guard, "list_clusters", boom)
    assert gke_guard.main([]) == 2
    assert "ERROR" in capsys.readouterr().err

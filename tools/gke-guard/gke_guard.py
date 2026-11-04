#!/usr/bin/env python3
"""gke-guard: warn if any GKE cluster is still running (cost guard).

Exit codes: 0 = no clusters, 1 = cluster(s) found, 2 = could not check.
"""
import argparse
import json
import logging
import subprocess
import sys

log = logging.getLogger("gke-guard")


def list_clusters(project=None):
    """Return the clusters gcloud reports, as a list of dicts."""
    cmd = ["gcloud", "container", "clusters", "list", "--format=json"]
    if project:
        cmd += ["--project", project]
    log.debug("running: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=60
        )
    except FileNotFoundError:
        raise RuntimeError("gcloud is not installed or not on PATH")
    except subprocess.TimeoutExpired:
        raise RuntimeError("gcloud timed out after 60 seconds")
    except subprocess.CalledProcessError as err:
        raise RuntimeError("gcloud failed: " + err.stderr.strip())
    return json.loads(result.stdout or "[]")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Warn if a GKE cluster is left running.")
    parser.add_argument("--project", help="GCP project (default: gcloud's active project)")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    try:
        clusters = list_clusters(args.project)
    except RuntimeError as err:
        print("ERROR: " + str(err), file=sys.stderr)
        return 2

    if not clusters:
        print("OK: no GKE clusters running.")
        return 0

    print("WARNING: %d GKE cluster(s) still running (this costs money):" % len(clusters))
    for c in clusters:
        print("  - %s  location=%s  status=%s  nodes=%s  created=%s" % (
            c.get("name"), c.get("location"), c.get("status"),
            c.get("currentNodeCount"), c.get("createTime"),
        ))
    print("Run 'terraform destroy' in infra/gcp when you are done.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

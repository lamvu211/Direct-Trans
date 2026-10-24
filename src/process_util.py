"""Find and terminate other DirectTrans processes (versioned exe names)."""

from __future__ import annotations

import csv
import io
import logging
import os
import time

from subprocess_util import run_hidden


def iter_directtrans_pids(exclude_pid: int | None = None) -> list[int]:
    """PIDs whose image name starts with DirectTrans (case-insensitive)."""
    try:
        result = run_hidden(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as e:
        logging.warning("tasklist failed while enumerating DirectTrans: %s", e)
        return []

    pids: list[int] = []
    for row in csv.reader(io.StringIO(result.stdout or "")):
        if len(row) < 2:
            continue
        name = row[0].strip().strip('"').lower()
        if not name.startswith("directtrans"):
            continue
        try:
            pid = int(row[1].strip().strip('"'))
        except ValueError:
            continue
        if exclude_pid is not None and pid == exclude_pid:
            continue
        pids.append(pid)
    return pids


def kill_other_directtrans_processes(
    exclude_pid: int | None = None,
    wait_seconds: float = 3.0,
) -> bool:
    """Force-kill other DirectTrans instances; wait until they exit. Returns True if any were killed."""
    pids = iter_directtrans_pids(exclude_pid)
    if not pids:
        return False

    killed_any = False
    for pid in pids:
        try:
            run_hidden(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True,
                timeout=10,
            )
            logging.info("Terminated stale DirectTrans process PID %s", pid)
            killed_any = True
        except Exception as e:
            logging.warning("taskkill PID %s failed: %s", pid, e)

    if not killed_any:
        return False

    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        if not iter_directtrans_pids(exclude_pid):
            break
        time.sleep(0.1)
    return True

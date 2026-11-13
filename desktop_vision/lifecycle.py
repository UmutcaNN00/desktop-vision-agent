"""
Application Lifecycle & Process Management Module
Handles spawning applications, waiting for their windows, and safely terminating processes.
"""

import os
import shlex
import subprocess
import time
from typing import List, Optional, Tuple, Union

try:
    import psutil
except ImportError:
    psutil = None

from .waiting import wait_for_window
from .window import WindowInfo


def launch_app(
    command_or_path: Union[str, List[str]],
    wait_window_query: Optional[str] = None,
    timeout: float = 10.0,
) -> Tuple[subprocess.Popen, Optional[WindowInfo]]:
    """
    Spawns an application process and optionally waits for its window to appear.
    """
    if isinstance(command_or_path, list):
        args = command_or_path
        shell = False
    else:
        args = command_or_path
        shell = True

    proc = subprocess.Popen(args, shell=shell)

    win: Optional[WindowInfo] = None
    if wait_window_query:
        win = wait_for_window(wait_window_query, timeout=timeout)

    return proc, win


def is_process_running(name_or_pid: Union[str, int]) -> bool:
    """Checks whether a process is currently running by name or PID."""
    if psutil is None:
        return False
    if isinstance(name_or_pid, int):
        return psutil.pid_exists(name_or_pid)

    query = name_or_pid.lower()
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and p.info["name"].lower() == query:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def terminate_process(name_or_pid: Union[str, int], force: bool = True) -> bool:
    """
    Terminates a process by name (e.g. 'notepad.exe') or PID.
    """
    if isinstance(name_or_pid, int):
        try:
            if psutil:
                proc = psutil.Process(name_or_pid)
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                return True
            else:
                flag = "/F" if force else ""
                subprocess.run(f"taskkill {flag} /PID {name_or_pid}", shell=True, check=True)
                return True
        except Exception:
            return False

    # By name
    killed_any = False
    if psutil:
        query = name_or_pid.lower()
        for p in psutil.process_iter(["name"]):
            try:
                if p.info["name"] and p.info["name"].lower() == query:
                    if force:
                        p.kill()
                    else:
                        p.terminate()
                    killed_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    else:
        flag = "/F" if force else ""
        res = subprocess.run(f"taskkill {flag} /IM {name_or_pid}", shell=True)
        killed_any = res.returncode == 0

    return killed_any

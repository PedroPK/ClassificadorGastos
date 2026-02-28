from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    app_file = project_root / "src" / "app.py"

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
        *sys.argv[1:],
    ]

    if os.name == "nt":
        process = subprocess.Popen(command, cwd=project_root)
    else:
        process = subprocess.Popen(command, cwd=project_root, preexec_fn=os.setsid)

    def shutdown(_signum: int, _frame) -> None:
        if process.poll() is not None:
            return

        print("\nEncerrando aplicação...", flush=True)
        try:
            if os.name == "nt":
                process.terminate()
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            return

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        return process.wait()
    except KeyboardInterrupt:
        shutdown(signal.SIGINT, None)
        try:
            return process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                process.kill()
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            return 130


if __name__ == "__main__":
    raise SystemExit(main())

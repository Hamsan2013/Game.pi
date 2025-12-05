# adb_controller.py
import subprocess, shlex

ADB = 'adb'

def run_cmd(cmd, timeout=30):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

def connect(ip, port=5555):
    return run_cmd(f"{ADB} connect {ip}:{port}")

def disconnect(ip, port=5555):
    return run_cmd(f"{ADB} disconnect {ip}:{port}")

def devices():
    rc, out, err = run_cmd(f"{ADB} devices")
    return out

def send_keyevent(keycode, device=None):
    target = f"-s {device}" if device else ""
    return run_cmd(f"{ADB} {target} shell input keyevent {keycode}")

def tap(x, y, device=None):
    target = f"-s {device}" if device else ""
    return run_cmd(f"{ADB} {target} shell input tap {x} {y}")

def swipe(x1, y1, x2, y2, duration_ms=100, device=None):
    target = f"-s {device}" if device else ""
    return run_cmd(f"{ADB} {target} shell input swipe {x1} {y1} {x2} {y2} {duration_ms}")

def text_input(text, device=None):
    esc = text.replace(' ', '%s')
    target = f"-s {device}" if device else ""
    return run_cmd(f"{ADB} {target} shell input text {esc}")

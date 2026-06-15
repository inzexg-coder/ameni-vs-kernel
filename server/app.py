#!/usr/bin/env python3

import http.server, threading, json, os, socket, webbrowser, sys, time, collections

PORT = 3000
HOST = "0.0.0.0"
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    _HAS_CRYPTOGRAPHY = True
except ImportError:
    _HAS_CRYPTOGRAPHY = False
import json as _json, base64, urllib.request as _urllib, urllib.error as _urlerr

_PUBLIC_KEY_B64 = "t71Kad65MvKZOlex8i/Is8FBzEDV/YNZkvHzoVYI9bM="
AMENOKE_API = "https://amenoke.ru/amenodes/api"
_license_data = None
_amenoke_user = None

def _get_machine_id():
    try:
        with open("/etc/machine-id") as f:
            return f.read().strip()
    except:
        try:
            import subprocess
            if os.name == "nt":
                r = subprocess.run(["wmic", "csproduct", "get", "uuid"], capture_output=True, text=True, timeout=5)
                return r.stdout.strip().split("\n")[-1].strip()
        except:
            pass
    return "unknown"

def _check_license():
    global _license_data
    if not _HAS_CRYPTOGRAPHY:
        return False
    key_path = os.path.expanduser("~/.ameni/license.key")
    if not os.path.exists(key_path):
        return False
    try:
        with open(key_path) as f:
            raw = f.read().strip()
        parts = raw.split(".")
        if len(parts) != 2:
            return False
        data_b64, sig_b64 = parts
        payload_bytes = base64.urlsafe_b64decode(data_b64 + "==")
        sig_bytes = base64.urlsafe_b64decode(sig_b64 + "==")
        pub_bytes = base64.b64decode(_PUBLIC_KEY_B64)
        pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        try:
            pub_key.verify(sig_bytes, payload_bytes)
        except InvalidSignature:
            return False
        payload = _json.loads(payload_bytes)
        from datetime import datetime, timezone
        exp = datetime.fromisoformat(payload["exp"])
        if exp < datetime.now(timezone.utc):
            return False
        mid = _get_machine_id()
        if payload.get("machine_id") and payload["machine_id"] != mid:
            return False
        _license_data = payload
        return True
    except:
        return False

def _amenoke_login(login, password):
    global _amenoke_user
    try:
        data = _json.dumps({"login": login, "password": password}).encode()
        req = _urllib.Request(AMENOKE_API + "/login.php", data=data,
                              headers={"Content-Type": "application/json"})
        resp = _urllib.urlopen(req, timeout=5)
        result = _json.loads(resp.read())
        token = result.get("token", "")
        token_path = os.path.expanduser("~/.ameni/token")
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(token + "\n")
        _amenoke_user = result.get("user", {})
        return True
    except Exception as e:
        _amenoke_user = None
        return False

def _amenoke_logout():
    global _amenoke_user
    token_path = os.path.expanduser("~/.ameni/token")
    if os.path.exists(token_path):
        os.remove(token_path)
    _amenoke_user = None

def _amenoke_check():
    global _amenoke_user
    token_path = os.path.expanduser("~/.ameni/token")
    if not os.path.exists(token_path):
        return None
    try:
        with open(token_path) as f:
            token = f.read().strip()
        if not token:
            return None
        req = _urllib.Request(AMENOKE_API + "/premium_check.php",
                              headers={"Authorization": "Bearer " + token})
        resp = _urllib.urlopen(req, timeout=5)
        result = _json.loads(resp.read())
        if result.get("success") and result.get("premium"):
            _amenoke_user = {"username": result.get("username", "")}
            return True
        return False
    except:
        return None

def _is_premium():
    online = _amenoke_check()
    if online is True:
        return True
    return _check_license()
IS_WIN = os.name == "nt"


def cpu_stats():
    if IS_WIN:
        import ctypes, ctypes.wintypes
        class _FT(ctypes.Structure):
            _fields_ = [("dwLowDateTime", ctypes.wintypes.DWORD), ("dwHighDateTime", ctypes.wintypes.DWORD)]
        i = _FT(); k = _FT(); u = _FT()
        ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(i), ctypes.byref(k), ctypes.byref(u))
        def _c(ft): return (ft.dwHighDateTime << 32) + ft.dwLowDateTime
        return {"total": _c(k) + _c(u), "idle": _c(i)}
    try:
        with open("/proc/stat") as f:
            line = f.readline().split()
        total = sum(int(x) for x in line[1:])
        idle = int(line[4])
        return {"total": total, "idle": idle}
    except:
        return {"total": 0, "idle": 0}

def read_cpu():
    s1 = cpu_stats()
    time.sleep(0.5)
    s2 = cpu_stats()
    dtotal = s2["total"] - s1["total"]
    didle = s2["idle"] - s1["idle"]
    pct = round((1 - didle / dtotal) * 100, 1) if dtotal else 0
    la = [0, 0, 0]
    freqs = []
    temp = 0
    if IS_WIN:
        import ctypes, ctypes.wintypes
        class _MS(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.wintypes.DWORD), ("dwMemoryLoad", ctypes.wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        m = _MS()
        m.dwLength = ctypes.sizeof(_MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        total = m.ullTotalPhys / (1024**3)
        avail = m.ullAvailPhys / (1024**3)
        mpct = round((1 - avail / total) * 100, 1) if total else 0
        swap_total = m.ullTotalPageFile / (1024**3)
        swap_pct = round((1 - m.ullAvailPageFile / m.ullTotalPageFile) * 100, 1) if m.ullTotalPageFile else 0
        freqs = [0]
        try:
            import subprocess
            o = subprocess.run(["powershell","-NoProfile","-Command",
                "(Get-CimInstance Win32_Processor | Select-Object -ExpandProperty MaxClockSpeed)"],
                capture_output=True, text=True, timeout=5)
            if o.stdout.strip():
                freqs = [int(o.stdout.strip())]
        except:
            pass
        return {"usage": pct, "cores": os.cpu_count() or 0, "freq": freqs, "load_avg": la, "temp": temp,
                "_mem": {"total_gb": round(total, 1), "avail_gb": round(avail, 1), "used_pct": mpct,
                         "swap_total_gb": round(swap_total, 1), "swap_used_pct": swap_pct}}
    try:
        with open("/proc/loadavg") as f:
            la = [float(x) for x in f.read().split()[:3]]
    except:
        pass
    try:
        for i in range(os.cpu_count() or 1):
            try:
                with open(f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq") as f:
                    freqs.append(round(int(f.read()) / 1000, 1))
            except:
                freqs.append(0)
    except:
        freqs = [0]
    try:
        vals = []
        for z in os.listdir("/sys/class/thermal/"):
            if z.startswith("thermal_zone"):
                with open(f"/sys/class/thermal/{z}/temp") as f:
                    vals.append(int(f.read()) / 1000)
        if vals: temp = round(max(vals), 1)
    except:
        pass
    return {"usage": pct, "cores": os.cpu_count() or 0, "freq": freqs, "load_avg": la, "temp": temp}

def read_memory():
    if IS_WIN:
        import ctypes, ctypes.wintypes
        class _MS(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.wintypes.DWORD), ("dwMemoryLoad", ctypes.wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        m = _MS()
        m.dwLength = ctypes.sizeof(_MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        total = m.ullTotalPhys / (1024**3)
        avail = m.ullAvailPhys / (1024**3)
        pct = round((1 - avail / total) * 100, 1) if total else 0
        return {"total_gb": round(total, 1), "avail_gb": round(avail, 1), "used_pct": pct,
                "swap_total_gb": round(m.ullTotalPageFile / (1024**3), 1),
                "swap_used_pct": round((1 - m.ullAvailPageFile / m.ullTotalPageFile) * 100, 1) if m.ullTotalPageFile else 0}
    mem = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split()
                if parts[0] in ("MemTotal:", "MemFree:", "MemAvailable:", "Cached:", "SwapTotal:", "SwapFree:", "Buffers:"):
                    mem[parts[0][:-1]] = int(parts[1])
    except:
        pass
    total = mem.get("MemTotal", 0)
    avail = mem.get("MemAvailable", mem.get("MemFree", 0) + mem.get("Cached", 0) + mem.get("Buffers", 0))
    pct = round((1 - avail / total) * 100, 1) if total else 0
    swap_total = mem.get("SwapTotal", 0)
    swap_free = mem.get("SwapFree", 0)
    swap_pct = round((1 - swap_free / swap_total) * 100, 1) if swap_total else 0
    return {"total_gb": round(total / 1024 / 1024, 1), "avail_gb": round(avail / 1024 / 1024, 1),
            "used_pct": pct, "swap_total_gb": round(swap_total / 1024 / 1024, 1), "swap_used_pct": swap_pct}

def read_disk():
    if IS_WIN:
        disks = []
        try:
            import subprocess, json as _j
            o = subprocess.run(["powershell","-NoProfile","-Command",
                'Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Select-Object DeviceID, Size, FreeSpace | ConvertTo-Json'],
                capture_output=True, text=True, timeout=10)
            if o.stdout.strip():
                data = _j.loads(o.stdout)
                if not isinstance(data, list): data = [data]
                for d in data:
                    t = d["Size"] / (1024**3)
                    f = d["FreeSpace"] / (1024**3)
                    u = t - f
                    p = round(u / t * 100, 1) if t else 0
                    disks.append({"mount": d["DeviceID"], "total_gb": round(t, 1), "used_gb": round(u, 1), "used_pct": p, "fstype": "NTFS"})
        except:
            pass
        return disks
    disks = []
    try:
        with open("/proc/mounts") as f:
            for line in f:
                parts = line.split()
                dev, mount, fstype = parts[0], parts[1], parts[2]
                if dev.startswith("/dev") and fstype not in ("proc","sysfs","tmpfs","devtmpfs","devpts","cgroup","cgroup2","pstore","bpf","securityfs","selinuxfs","autofs","efivarfs","fuse.gvfsd-fuse"):
                    try:
                        s = os.statvfs(mount)
                        total = s.f_frsize * s.f_blocks
                        free = s.f_frsize * s.f_bfree
                        used = total - free
                        pct = round(used / total * 100, 1) if total else 0
                        disks.append({"mount": mount, "total_gb": round(total / 1024**3, 1), "used_gb": round(used / 1024**3, 1), "used_pct": pct, "fstype": fstype})
                    except:
                        pass
    except:
        pass
    return disks

def read_network():
    if IS_WIN:
        net = []
        try:
            import subprocess, json as _j
            o = subprocess.run(["powershell","-NoProfile","-Command",
                "Get-NetAdapterStatistics | Select-Object Name, ReceivedBytes, SentBytes | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10)
            if o.stdout.strip():
                data = _j.loads(o.stdout)
                if not isinstance(data, list): data = [data]
                for d in data:
                    net.append({"iface": d["Name"], "rx_bytes": int(d["ReceivedBytes"]), "tx_bytes": int(d["SentBytes"])})
        except:
            pass
        return net
    net = []
    try:
        with open("/proc/net/dev") as f:
            f.readline()
            f.readline()
            for line in f:
                parts = line.split()
                if parts[0].rstrip(":") in ("lo",): continue
                net.append({"iface": parts[0].rstrip(":"), "rx_bytes": int(parts[1]), "tx_bytes": int(parts[9])})
    except:
        pass
    return net

history = collections.deque(maxlen=1800)

def read_all():
    cpu = read_cpu()
    mem = cpu.pop("_mem", None) if IS_WIN else None
    if mem is None:
        mem = read_memory()
    data = {"cpu": cpu, "memory": mem, "disk": read_disk(), "network": read_network(),
            "uptime": read_uptime(), "processes": read_processes(), "battery": read_battery(),
            "time": time.time()}
    if _is_premium():
        data["diskio"] = read_diskio()
        history.append(data)
    return data

class Handler(http.server.SimpleHTTPRequestHandler):
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/system":
            import platform as pl
            info = {"os": pl.system(), "release": pl.release(), "kernel": pl.uname().release, "arch": pl.machine()}
            try:
                if hasattr(pl, "freedesktop_os_release"):
                    info["distro"] = pl.freedesktop_os_release().get("PRETTY_NAME", "")
            except:
                pass
            self.send_json(info)
        elif self.path.startswith("/api/monitor/"):
            sub = self.path.replace("/api/monitor/", "")
            if sub == "all": self.send_json(read_all())
            elif sub == "cpu": self.send_json(read_cpu())
            elif sub == "memory": self.send_json(read_memory())
            elif sub == "disk": self.send_json(read_disk())
            elif sub == "network": self.send_json(read_network())
            elif sub == "uptime": self.send_json(read_uptime())
            elif sub == "processes": self.send_json(read_processes())
            elif sub == "battery": self.send_json(read_battery())
            elif sub == "diskio":
                if _is_premium(): self.send_json(read_diskio())
                else: self.send_json({"error": "premium required", "premium": False}, 402)
            elif sub == "history":
                if _is_premium(): self.send_json(list(history))
                else: self.send_json({"error": "premium required", "premium": False}, 402)
            else: self.send_json({"error": "unknown"}, 404)
        elif self.path == "/api/premium":
            resp = {"premium": _is_premium()}
            if _amenoke_user:
                resp["username"] = _amenoke_user.get("username", "")
            self.send_json(resp)
        else:
            super().do_GET()
    def do_POST(self):
        if self.path == "/api/activate":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                data = _json.loads(body)
                key = data.get("key", "").strip()
            except:
                key = ""
            if not key:
                self.send_json({"ok": False, "error": "empty key"}, 400)
                return
            key_dir = os.path.expanduser("~/.ameni")
            os.makedirs(key_dir, exist_ok=True)
            with open(os.path.join(key_dir, "license.key"), "w") as f:
                f.write(key + "\n")
            prem = _is_premium()
            resp = {"ok": True, "premium": prem}
            if prem and _license_data:
                resp["email"] = _license_data.get("email", "")
                resp["exp"] = _license_data.get("exp", "")
            self.send_json(resp)
        elif self.path == "/api/login":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                data = _json.loads(body)
                login = data.get("login", "")
                password = data.get("password", "")
            except:
                login = password = ""
            if not login or not password:
                self.send_json({"ok": False, "error": "login and password required"}, 400)
                return
            ok = _amenoke_login(login, password)
            if ok:
                self.send_json({"ok": True, "user": _amenoke_user, "premium": _is_premium()})
            else:
                self.send_json({"ok": False, "error": "invalid credentials"}, 401)
        elif self.path == "/api/logout":
            _amenoke_logout()
            self.send_json({"ok": True})
        else:
            self.send_json({"error": "not found"}, 404)

    def log_message(self, format, *args):
        if "/api/" in str(args[0]): print(f"  {args[0]}")

HTML_PAGE = open(os.path.join(os.path.dirname(__file__), "dashboard.html"), encoding="utf-8").read()

def read_uptime():
    if IS_WIN:
        try:
            import ctypes
            lib = ctypes.windll.kernel32
            uptime_ms = lib.GetTickCount64()
            total_sec = uptime_ms // 1000
            days = int(total_sec // 86400)
            hours = int((total_sec % 86400) // 3600)
            mins = int((total_sec % 3600) // 60)
            return {"days": days, "hours": hours, "mins": mins}
        except:
            return {"days": 0, "hours": 0, "mins": 0}
    try:
        with open("/proc/uptime") as f:
            up = float(f.read().split()[0])
            days = int(up // 86400)
            hours = int((up % 86400) // 3600)
            mins = int((up % 3600) // 60)
            return {"days": days, "hours": hours, "mins": mins}
    except:
        return {"days": 0, "hours": 0, "mins": 0}

def read_processes():
    if IS_WIN:
        try:
            import subprocess
            r = subprocess.run(["wmic", "path", "Win32_Process", "get", "ProcessId,Name,WorkingSetSize", "/format:csv"],
                               capture_output=True, text=True, timeout=5)
            procs = []
            for line in r.stdout.strip().split("\n")[1:]:
                if not line.strip(): continue
                parts = line.split(",")
                if len(parts) >= 4:
                    try:
                        pid = int(parts[2])
                        name = parts[1].strip()
                        mem = int(parts[3]) // 1048576
                        procs.append({"pid": pid, "name": name, "mem": mem})
                    except:
                        pass
            procs.sort(key=lambda x: -x["mem"])
            return procs[:5]
        except:
            return []
    procs = []
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit(): continue
            try:
                with open(f"/proc/{pid}/stat") as f:
                    p = f.read().split()
                    n = p[1].strip("()")
                    mem = int(p[23]) * 4096 // 1024 // 1024
                    procs.append({"pid": int(pid), "name": n, "mem": mem})
            except:
                pass
        procs.sort(key=lambda x: -x["mem"])
        return procs[:5]
    except:
        return []

def read_battery():
    if IS_WIN:
        try:
            import subprocess, re
            r = subprocess.run(["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining,Status,BatteryStatus",
                               "/format:csv"], capture_output=True, text=True, timeout=5)
            for line in r.stdout.strip().split("\n")[1:]:
                if not line.strip(): continue
                parts = line.split(",")
                if len(parts) >= 3:
                    try:
                        pct = int(parts[1])
                        st = "Charging" if "2" in parts[2] or "6" in parts[2] or "10" in parts[2] else "Discharging"
                        return {"pct": pct, "status": st}
                    except:
                        pass
        except:
            pass
        return None
    try:
        for bat in os.listdir("/sys/class/power_supply/"):
            if bat.startswith("BAT"):
                with open(f"/sys/class/power_supply/{bat}/capacity") as f:
                    pct = int(f.read().strip())
                with open(f"/sys/class/power_supply/{bat}/status") as f:
                    st = f.read().strip()
                return {"pct": pct, "status": st}
    except:
        pass
    return None

def read_diskio():
    if IS_WIN:
        try:
            import subprocess
            r = subprocess.run(["wmic", "path", "Win32_PerfFormattedData_PerfDisk_LogicalDisk",
                               "get", "Name,DiskReadBytesPersec,DiskWriteBytesPersec", "/format:csv"],
                               capture_output=True, text=True, timeout=5)
            disks = {}
            for line in r.stdout.strip().split("\n")[1:]:
                if not line.strip(): continue
                parts = line.split(",")
                if len(parts) >= 4:
                    try:
                        name = parts[1].strip().replace(":", "")
                        rb = int(parts[2])
                        wb = int(parts[3])
                        if name and name != "_Total":
                            disks[name] = {"rbytes": rb, "wbytes": wb}
                    except:
                        pass
            return disks
        except:
            return {}
    disks = {}
    try:
        with open("/proc/diskstats") as f:
            for line in f:
                p = line.split()
                if len(p) >= 14:
                    n = p[2]
                    if not any(n.startswith(x) for x in ["sd", "nvme", "vd", "mmc", "xvd"]):
                        continue
                    if p[3] == "0": continue
                    rb = int(p[5]) * 512
                    wb = int(p[9]) * 512
                    disks[n] = {"rbytes": rb, "wbytes": wb}
    except:
        pass
    return disks



def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def _print_premium_async():
    if _is_premium():
        email = _license_data.get("email", "unknown") if _license_data else "unknown"
        print(f"  \033[38;5;141mPremium:\033[0m enabled for {email}")

def main():
    auto_open = "--no-browser" not in sys.argv and os.environ.get("AMENI_NO_BROWSER") != "1"
    ip = get_local_ip()
    print("\n  \033[38;5;141mameni monitor \u2014 system dashboard\033[0m")
    print("  \033[38;5;92m\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\033[0m")
    print("  \033[38;5;147mServer started\033[0m")
    print(f"  \033[38;5;92mLocal:\033[0m   http://127.0.0.1:{PORT}")
    print(f"  \033[38;5;92mNetwork:\033[0m http://{ip}:{PORT}")
    print(f"  \033[38;5;141mOpen:\033[0m    http://127.0.0.1:{PORT}")
    print("  \033[38;5;92m\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\033[0m")
    print("  \033[38;5;183mPress Ctrl+C to stop\033[0m\n")
    threading.Thread(target=_print_premium_async, daemon=True).start()
    try:
        server = http.server.HTTPServer((HOST, PORT), Handler)
    except OSError:
        import subprocess as _sp
        try:
            _sp.run(["fuser", "-k", f"{PORT}/tcp"], capture_output=True, timeout=5)
            time.sleep(1)
        except:
            pass
        try:
            server = http.server.HTTPServer((HOST, PORT), Handler)
        except OSError:
            cmd = "netstat -ano | findstr :" + str(PORT) if IS_WIN else f"fuser -k {PORT}/tcp"
            hint = "netstat -ano | findstr :"+str(PORT) if IS_WIN else f"fuser -k {PORT}/tcp"
            print(f"  Port {PORT} in use. Kill it: {hint}")
            return
    if auto_open:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.\n")
        server.server_close()

if __name__ == "__main__":
    main()

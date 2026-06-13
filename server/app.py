#!/usr/bin/env python3
"""ameni monitor — system dashboard"""
import http.server, threading, json, os, socket, webbrowser, sys, time, collections

PORT = 3000
HOST = "0.0.0.0"
PREMIUM = os.environ.get("AMENI_PREMIUM") == "1" or os.path.exists(os.path.expanduser("~/.ameni/premium.key"))
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
    data = {"cpu": cpu, "memory": mem, "disk": read_disk(), "network": read_network(), "time": time.time()}
    if PREMIUM: history.append(data)
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
            elif sub == "history":
                if PREMIUM: self.send_json(list(history))
                else: self.send_json({"error": "premium required", "premium": False}, 402)
            else: self.send_json({"error": "unknown"}, 404)
        elif self.path == "/api/premium":
            self.send_json({"premium": PREMIUM})
        else:
            super().do_GET()
    def log_message(self, format, *args):
        if "/api/" in str(args[0]): print(f"  {args[0]}")

HTML_PAGE = r'<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n<title>ameni monitor — live demo</title>\n<style>\n  @import url(\'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap\');\n  *{margin:0;padding:0;box-sizing:border-box}\n  body{background:#08040e;font-family:\'JetBrains Mono\',monospace;min-height:100vh;color:#c0c0cc;overflow-x:hidden}\n  body::before{content:\'\';position:fixed;top:0;left:0;right:0;bottom:0;\n    background:radial-gradient(ellipse at 20% 50%,#1a0a2e 0%,transparent 60%),\n               radial-gradient(ellipse at 80% 20%,#2a1040 0%,transparent 50%);z-index:-1}\n  .container{max-width:900px;margin:0 auto;padding:20px}\n  .ascii{font-size:7px;line-height:1.1;text-align:center;margin:5px 0 12px;white-space:pre;color:#a855f7;opacity:0.6}\n  h1{font-size:20px;font-weight:300;text-align:center;margin:0 0 4px;\n    background:linear-gradient(90deg,#a855f7,#e9d5ff,#a855f7);background-size:200% auto;\n    -webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shim 4s linear infinite}\n  @keyframes shim{0%{background-position:0% center}50%{background-position:200% center}100%{background-position:0% center}}\n  .sub{color:#6b4a7b;font-size:10px;text-align:center;margin-bottom:16px}\n  .grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}\n  @media(max-width:640px){.grid{grid-template-columns:1fr}}\n  .card{background:linear-gradient(135deg,#12071e,#1a0a2e);border:1px solid #2a1040;border-radius:8px;padding:14px 16px}\n  .card-title{color:#6b4a7b;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px}\n  .metric{display:flex;justify-content:space-between;align-items:center;padding:3px 0;font-size:12px}\n  .label{color:#6b4a7b;min-width:80px}\n  .value{color:#c084fc;font-weight:700}\n  .bar-wrap{width:100%;height:6px;background:#1a0820;border-radius:3px;overflow:hidden;margin:4px 0}\n  .bar-fill{height:100%;border-radius:3px;transition:width .6s ease}\n  .bar-green{background:linear-gradient(90deg,#22c55e,#4ade80)}\n  .bar-yellow{background:linear-gradient(90deg,#f59e0b,#fbbf24)}\n  .bar-red{background:linear-gradient(90deg,#ef4444,#dc2626)}\n  .bar-purple{background:linear-gradient(90deg,#7c3aed,#a855f7)}\n  .disk-row{display:flex;justify-content:space-between;align-items:center;padding:3px 0;font-size:11px}\n  .disk-row .mount{color:#a855f7;min-width:60px}\n  .disk-row .pct{color:#c084fc;min-width:35px;text-align:right}\n  .net-row{display:flex;justify-content:space-between;padding:3px 0;font-size:11px}\n  .net-row .iface{color:#a855f7;min-width:50px}\n  .net-row .speed{color:#c084fc}\n  .footer{text-align:center;margin-top:16px;font-size:9px;color:#4a2a5a}\n  .premium-badge{display:inline-block;background:linear-gradient(90deg,#7c3aed,#a855f7);color:#fff;font-size:8px;padding:2px 6px;border-radius:3px;margin-left:6px}\n  .pulse{animation:pulse 2s ease-in-out infinite}\n  @keyframes pulse{0%{opacity:1}50%{opacity:.4}100%{opacity:1}}\n  .blink{animation:blink 1s step-end infinite}\n  @keyframes blink{0%{opacity:1}50%{opacity:0}}\n</style>\n</head>\n<body>\n<div class="container">\n\n<div class="ascii" id="asciiBlock"></div>\n\n<h1>ameni monitor — system dashboard</h1>\n<div class="sub" id="sysLine">Linux <span id="distro">Arch Linux</span> <span id="kernel">6.5.7</span>  |  <span id="arch">x86_64</span></div>\n\n<div class="grid">\n\n  <!-- CPU -->\n  <div class="card">\n    <div class="card-title">cpu</div>\n    <div class="metric"><span class="label">Usage</span><span class="value" id="cpuUsage">--</span></div>\n    <div class="bar-wrap"><div class="bar-fill" id="cpuBar" style="width:0%"></div></div>\n    <div class="metric"><span class="label">Load Avg</span><span class="value" id="cpuLoad">--</span></div>\n    <div class="metric"><span class="label">Cores</span><span class="value" id="cpuCores">8 cores</span></div>\n    <div class="metric"><span class="label">Freq</span><span class="value" id="cpuFreq">--</span></div>\n    <div class="metric"><span class="label">Temp</span><span class="value" id="cpuTemp">--</span></div>\n  </div>\n\n  <!-- Memory -->\n  <div class="card">\n    <div class="card-title">memory <span class="premium-badge">PREMIUM</span></div>\n    <div class="metric"><span class="label">RAM Used</span><span class="value" id="memUsed">--</span></div>\n    <div class="bar-wrap"><div class="bar-fill" id="memBar" style="width:0%"></div></div>\n    <div class="metric"><span class="label">Available</span><span class="value" id="memAvail">--</span></div>\n    <div class="metric"><span class="label">Swap</span><span class="value" id="memSwap">--</span></div>\n    <div class="bar-wrap"><div class="bar-fill" id="swapBar" style="width:0%"></div></div>\n  </div>\n\n  <!-- Disks -->\n  <div class="card">\n    <div class="card-title">disks</div>\n    <div id="diskContent"></div>\n  </div>\n\n  <!-- Network -->\n  <div class="card">\n    <div class="card-title">network</div>\n    <div id="netContent"></div>\n  </div>\n\n</div>\n\n<!-- History (premium) -->\n<div class="card" style="margin-top:10px">\n  <div class="card-title">history (CPU last 30 min) <span class="premium-badge">PREMIUM</span></div>\n  <canvas id="historyCanvas" width="800" height="200" style="width:100%;height:120px;border-radius:4px;background:#0a0212"></canvas>\n  <div style="display:flex;justify-content:space-between;font-size:8px;color:#4a2a5a;margin-top:4px">\n    <span id="timeStart">now</span><span>CPU % over time</span><span id="timeEnd">now</span>\n  </div>\n</div>\n\n<div class="footer" id="footer"><span class="pulse">●</span> live demo &mdash; обновление каждые 2 сек</div>\n\n</div>\n\n<script>\n(function() {\n  var ascii = [\n    \'⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢲⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\',\n    \'⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\',\n    \'⠀⠀⠀⠀⠀⠀⠀⠀⢀⠄⠂⢉⠤⠐⠋⠈⠡⡈⠉⠐⠠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\',\n    \'⠀⠀⠀⠀⢀⡀⢠⣤⠔⠁⢀⠀⠀⠀⠀⠀⠀⠀⠈⢢⠀⠀⠈⠱⡤⣤⠄⣀⠀⠀⠀⠀⠀\',\n    \'⠀⠀⠰⠁⠀⣰⣿⠃⠀⢠⠃⢸⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠈⢞⣦⡀⠈⡇⠀⠀⠀\',\n    \'⠀⠀⠀⢇⣠⡿⠁⠀⢀⡃⠀⣈⠀⠀⠀⠀⢰⡀⠀⠀⠀⠀⢢⠰⠀⠀⢺⣧⢰⠀⠀⠀⠀\',\n    \'⠀⠀⠀⠈⣿⠁⡘⠀⡌⡇⠀⡿⠸⠀⠀⠀⠈⡕⡄⠀⠐⡀⠈⠀⢃⠀⠀⠾⠇⠀⠀⠀⠀\',\n    \'⠀⠀⠀⠀⠇⡇⠃⢠⠀⠶⡀⡇⢃⠡⡀⠀⠀⠡⠈⢂⡀⢁⠀⡁⠸⠀⡆⠘⡀⠀⠀⠀⠀\',\n    \'⠀⠀⠀⠸⠀⢸⠀⠘⡜⠀⣑⢴⣀⠑⠯⡂⠄⣀⣣⢀⣈⢺⡜⢣⠀⡆⡇⠀⢣⠀⠀⠀⠀\',\n    \'⠀⠀⠀⠇⠀⢸⠀⡗⣰⡿⡻⠿⡳⡅⠀⠀⠀⠀⠈⡵⠿⠿⡻⣷⡡⡇⡇⠀⢸⣇⠀⠀⠀\',\n    \'⠀⠀⢰⠀⠀⡆⡄⣧⡏⠸⢠⢲⢸⠁⠀⠀⠀⠀⠐⢙⢰⠂⢡⠘⣇⡇⠃⠀⠀⢹⡄⠀⠀\',\n    \'⠀⠀⠟⠀⠀⢰⢁⡇⠇⠰⣀⢁⡜⠀⠀⠀⠀⠀⠀⠘⣀⣁⠌⠀⠃⠰⠀⠀⠀⠈⠰⠀⠀\',\n    \'⠀⡘⠀⠀⠀⠀⢊⣤⠀⠀⠤⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠤⠄⠀⢸⠃⠀⠀⠀⠀⠀⠃⠀\',\n    \'⢠⠁⢀⠀⠀⠀⠈⢿⡀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⢀⠏⠀⠀⠀⠀⠀⠀⠸⠀\',\n    \'⠘⠸⠘⡀⠀⠀⠀⠀⢣⠀⠀⠀⠀⠀⠀⠁⠀⠃⠀⠀⠀⠀⢀⠎⠀⠀⠀⠀⠀⢠⠀⠀⡇\',\n    \'⠀⠇⢆⢃⠀⠀⠀⠀⠀⡏⢲⢤⢀⡀⠀⠀⠀⠀⠀⢀⣠⠄⡚⠀⠀⠀⠀⠀⠀⣾⠀⠀⠀\',\n    \'⢰⠈⢌⢎⢆⠀⠀⠀⠀⠁⣌⠆⡰⡁⠉⠉⠀⠉⠁⡱⡘⡼⠇⠀⠀⠀⠀⢀⢬⠃⢠⠀⡆\',\n    \'⠀⢢⠀⠑⢵⣧⡀⠀⠀⡿⠳⠂⠉⠀⠀⠀⠀⠀⠀⠀⠁⢺⡀⠀⠀⢀⢠⣮⠃⢀⠆⡰⠀\',\n    \'⠀⠀⠑⠄⣀⠙⡭⠢⢀⡀⠀⠁⠄⣀⣀⠀⢀⣀⣀⣀⡠⠂⢃⡀⠔⠱⡞⢁⠄⣁⠔⠁⠀\',\n    \'⠀⠀⠀⠀⠀⢠⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠉⠁⠀⠀⠀⠀\',\n    \'⠀⠀⠀⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀\'\n  ];\n  var el = document.getElementById(\'asciiBlock\');\n  var colors = [\'#a855f7\',\'#c084fc\',\'#d8b4fe\',\'#e9d5ff\',\'#7c3aed\',\'#9333ea\'];\n  ascii.forEach(function(l,i){\n    var s = document.createElement(\'span\');\n    s.style.color = colors[i % 6];\n    s.textContent = l;\n    el.appendChild(s);\n    el.appendChild(document.createTextNode(\'\\n\'));\n  });\n})();\n\nfunction rnd(min,max){return Math.round((Math.random()*(max-min)+min)*10)/10}\nfunction rndI(min,max){return Math.floor(Math.random()*(max-min+1)+min)}\nfunction pick(arr){return arr[Math.floor(Math.random()*arr.length)]}\n\nvar hist = [];\nvar t0 = Date.now();\n\nfunction barColor(p){\n  if(p<60) return \'#22c55e\';\n  if(p<85) return \'#f59e0b\';\n  return \'#ef4444\';\n}\n\nfunction fmtB(b){\n  if(b>1073741824) return (b/1073741824).toFixed(1)+\'GB\';\n  if(b>1048576) return (b/1048576).toFixed(1)+\'MB\';\n  if(b>1024) return (b/1024).toFixed(1)+\'KB\';\n  return b+\'B\';\n}\n\nfunction drawHist(){\n  var c = document.getElementById(\'historyCanvas\');\n  if(!c) return;\n  var ctx = c.getContext(\'2d\');\n  var w = c.width, h = c.height;\n  ctx.clearRect(0,0,w,h);\n  if(hist.length<2) return;\n  ctx.beginPath();\n  ctx.moveTo(0, h);\n  for(var i=0;i<hist.length;i++){\n    var x = (i/(hist.length-1))*w;\n    var y = h - (hist[i]/100)*h;\n    ctx.lineTo(x, y);\n  }\n  ctx.lineTo(w, h);\n  ctx.closePath();\n  var grad = ctx.createLinearGradient(0,0,0,h);\n  grad.addColorStop(0,\'rgba(168,85,247,0.4)\');\n  grad.addColorStop(1,\'rgba(168,85,247,0.02)\');\n  ctx.fillStyle = grad;\n  ctx.fill();\n  ctx.beginPath();\n  ctx.moveTo(0, h - (hist[0]/100)*h);\n  for(var i=1;i<hist.length;i++){\n    ctx.lineTo((i/(hist.length-1))*w, h - (hist[i]/100)*h);\n  }\n  ctx.strokeStyle = \'#a855f7\';\n  ctx.lineWidth = 2;\n  ctx.stroke();\n}\n\nfunction update(){\n  var cu = rnd(10,95);\n  document.getElementById(\'cpuUsage\').textContent = cu+\'%\';\n  document.getElementById(\'cpuBar\').style.width = cu+\'%\';\n  document.getElementById(\'cpuBar\').style.background = \'linear-gradient(90deg,\'+barColor(cu)+\',#4ade80)\';\n  document.getElementById(\'cpuLoad\').textContent = rnd(0,3)+\'  \'+rnd(0,2)+\'  \'+rnd(0,1);\n  var freqs = [];\n  for(var i=0;i<8;i++) freqs.push(rndI(400,3200));\n  document.getElementById(\'cpuFreq\').textContent = freqs.slice(0,4).map(function(f){return f+\'MHz\'}).join(\' \');\n  document.getElementById(\'cpuTemp\').textContent = rnd(35,85)+\'\\u00b0C\';\n\n  var mp = rnd(40,92);\n  var mt = rnd(6,32);\n  var ma = mt*(1-mp/100);\n  document.getElementById(\'memUsed\').textContent = mp+\'%\';\n  document.getElementById(\'memBar\').style.width = mp+\'%\';\n  document.getElementById(\'memBar\').style.background = \'linear-gradient(90deg,\'+barColor(mp)+\',#4ade80)\';\n  document.getElementById(\'memAvail\').textContent = ma.toFixed(1)+\' / \'+mt+\' GB\';\n  var sp = rnd(0,90);\n  document.getElementById(\'memSwap\').textContent = sp+\'%\';\n  document.getElementById(\'swapBar\').style.width = sp+\'%\';\n  document.getElementById(\'swapBar\').style.background = \'linear-gradient(90deg,\'+barColor(sp)+\',#4ade80)\';\n\n  var disks = [\n    {m:\'/\', p:rnd(20,95), u:rnd(10,200), t:240},\n    {m:\'/home\', p:rnd(20,95), u:rnd(50,400), t:500},\n    {m:\'/mnt/data\', p:rnd(20,95), u:rnd(100,900), t:1000}\n  ];\n  var dh = \'\';\n  disks.forEach(function(d){\n    var bc = barColor(d.p);\n    dh += \'<div class="disk-row"><span class="mount">\'+d.m+\'</span>\'+\n      \'<span style="flex:1;margin:0 8px"><div class="bar-wrap" style="height:4px">\'+\n      \'<div class="bar-fill" style="width:\'+d.p+\'%;background:linear-gradient(90deg,\'+bc+\',#4ade80)"></div></div></span>\'+\n      \'<span class="pct">\'+d.p.toFixed(1)+\'%</span>\'+\n      \'<span style="color:#6b4a7b;font-size:10px;min-width:50px;text-align:right">\'+d.u.toFixed(1)+\'/\'+d.t+\'G</span></div>\';\n  });\n  document.getElementById(\'diskContent\').innerHTML = dh;\n\n  var ifaces = [\n    {n:\'wlan0\', r:rndI(100,5000000), t:rndI(50,1000000)},\n    {n:\'eth0\', r:rndI(0,1000), t:rndI(0,500)}\n  ];\n  var nh = \'\';\n  ifaces.forEach(function(n){\n    nh += \'<div class="net-row"><span class="iface">\'+n.n+\'</span>\'+\n      \'<span class="speed">\\u2193 \'+fmtB(n.r)+\'  \\u2191 \'+fmtB(n.t)+\'</span></div>\';\n  });\n  document.getElementById(\'netContent\').innerHTML = nh;\n\n  hist.push(cu);\n  if(hist.length>180) hist.shift();\n  drawHist();\n\n  var d = new Date();\n  document.getElementById(\'timeStart\').textContent = d.toLocaleTimeString([],{hour:\'2-digit\',minute:\'2-digit\'});\n  document.getElementById(\'timeEnd\').textContent = d.toLocaleTimeString([],{hour:\'2-digit\',minute:\'2-digit\'});\n}\n\nupdate();\nsetInterval(update, 2000);\n</script>\n</body>\n</html>\n'

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    auto_open = "--no-browser" not in sys.argv and os.environ.get("AMENI_NO_BROWSER") != "1"
    ip = get_local_ip()
    print("\n  \033[38;5;141mameni monitor \u2014 system dashboard\033[0m")
    print("  \033[38;5;92m\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\033[0m")
    print("  \033[38;5;147mServer started\033[0m")
    print(f"  \033[38;5;92mLocal:\033[0m   http://127.0.0.1:{PORT}")
    print(f"  \033[38;5;92mNetwork:\033[0m http://{ip}:{PORT}")
    if PREMIUM: print("  \033[38;5;141mPremium:\033[0m enabled")
    print("  \033[38;5;92m\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\033[0m")
    print("  \033[38;5;183mPress Ctrl+C to stop\033[0m\n")
    server = http.server.HTTPServer((HOST, PORT), Handler)
    if auto_open:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.\n")
        server.server_close()

if __name__ == "__main__":
    main()

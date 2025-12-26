import requests
import socket
import socks
import time
import random

# Fuentes de proxies
SOCKS4_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt"
]

SOCKS5_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt"
]

# APIs
GEO_API = "http://ip-api.com/json/"
IP_CHECK_API = "https://api.ipify.org?format=json"

# Configuración
ALLOWED_COUNTRIES = {"US", "CA"}
TIMEOUT = 6
MAX_PROXIES = 5

# Colores
GREEN = "\033[92m"
RESET = "\033[0m"

original_socket = socket.socket

def reset_socket():
    socket.socket = original_socket

def fetch_proxies(urls):
    proxies = set()
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            for line in r.text.splitlines():
                if ":" in line:
                    proxies.add(line.strip())
        except:
            pass
    proxies = list(proxies)
    random.shuffle(proxies)
    return proxies

def is_north_america(ip):
    try:
        r = requests.get(GEO_API + ip, timeout=5).json()
        if r.get("countryCode") in ALLOWED_COUNTRIES:
            return r.get("country")
    except:
        pass
    return None

def is_anonymous(proxy_type, ip, port):
    try:
        socks.set_default_proxy(proxy_type, ip, port)
        socket.socket = socks.socksocket

        r = requests.get(IP_CHECK_API, timeout=TIMEOUT)
        exit_ip = r.json().get("ip")

        return exit_ip != None  # Proxy está activo (anónimo básico)
    except:
        return False
    finally:
        reset_socket()

def latency_test(proxy_type, ip, port):
    try:
        socks.set_default_proxy(proxy_type, ip, port)
        socket.socket = socks.socksocket

        start = time.time()
        s = socket.create_connection(("1.1.1.1", 80), timeout=TIMEOUT)
        s.close()
        return round((time.time() - start) * 1000, 2)
    except:
        return None
    finally:
        reset_socket()

def test_proxy(proxy, version):
    try:
        ip, port = proxy.split(":")
        port = int(port)
    except:
        return None

    proxy_type = socks.SOCKS4 if version == 4 else socks.SOCKS5

    country = is_north_america(ip)
    if not country:
        return None

    if not is_anonymous(proxy_type, ip, port):
        return None

    latency = latency_test(proxy_type, ip, port)
    if latency is None:
        return None

    return {
        "proxy": proxy,
        "type": "SOCKS" + str(version),
        "country": country,
        "latency": latency
    }

def prochans():
    print(GREEN + "[] prochans iniciado" + RESET)
    print("[] descargando proxies nuevos...")

    socks4 = fetch_proxies(SOCKS4_SOURCES)
    socks5 = fetch_proxies(SOCKS5_SOURCES)

    all_tests = [(p, 4) for p in socks4] + [(p, 5) for p in socks5]
    random.shuffle(all_tests)

    good = []

    for proxy, version in all_tests:
        if len(good) >= MAX_PROXIES:
            break

        result = test_proxy(proxy, version)
        if result:
            good.append(result)
            print(GREEN + "[OK]" + RESET,
                  result["type"],
                  result["proxy"],
                  "|",
                  result["country"],
                  "|",
                  result["latency"],
                  "ms")

    print("\n=== TOP 5 PROXIES SOCKS ANÓNIMOS ===")
    for p in sorted(good, key=lambda x: x["latency"]):
        print(p["type"], p["proxy"], "|", p["country"], "|", p["latency"], "ms")

if __name__ == "__main__":
    prochans()

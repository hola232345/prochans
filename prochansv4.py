import requests
import random
import time
import os

HTTP_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
]

PROXYCHAINS_CONF = "/etc/proxychains4.conf"

GEO_API = "http://ip-api.com/json/"
IP_CHECK_API = "https://api.ipify.org?format=json"

ALLOWED_COUNTRIES = {"US", "CA"}
TIMEOUT = 6
MAX_PROXIES = 5

GREEN = "\033[92m"
RESET = "\033[0m"

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

def test_proxy(proxy):
    ip, port = proxy.split(":")
    country = is_north_america(ip)
    if not country:
        return None

    try:
        start = time.time()
        requests.get(
            IP_CHECK_API,
            proxies={"http": f"http://{proxy}"},
            timeout=TIMEOUT
        )
        latency = round((time.time() - start) * 1000, 2)
    except:
        return None

    return {
        "proxy": proxy,
        "country": country,
        "latency": latency
    }

def update_proxychains(proxies):
    if not os.path.exists(PROXYCHAINS_CONF):
        print("proxychains4.conf no encontrado")
        return

    with open(PROXYCHAINS_CONF, "r") as f:
        lines = f.readlines()

    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)

        if line.strip() == '# defaults set to "tor"' and not inserted:
            for p in proxies:
                ip, port = p["proxy"].split(":")
                new_lines.append(f"http {ip} {port}\n")

            # Tor como fallback final
            new_lines.append("socks5 127.0.0.1 9050\n")
            inserted = True

    if inserted:
        with open(PROXYCHAINS_CONF, "w") as f:
            f.writelines(new_lines)

def prochans():
    print(GREEN + "[] prochans iniciado" + RESET)
    print("[] descargando proxies HTTP desde GitHub...")

    proxies = fetch_proxies(HTTP_SOURCES)
    good = []

    for proxy in proxies:
        if len(good) >= MAX_PROXIES:
            break

        result = test_proxy(proxy)
        if result:
            good.append(result)
            print(
                GREEN + "[OK]" + RESET,
                result["proxy"],
                "|",
                result["country"],
                "|",
                result["latency"],
                "ms"
            )

    if good:
        update_proxychains(sorted(good, key=lambda x: x["latency"]))
        print(GREEN + "\n[] proxychains4.conf actualizado (HTTP + Tor fallback)" + RESET)
    else:
        print("No se encontraron proxies válidos")

if __name__ == "__main__":
    prochans()

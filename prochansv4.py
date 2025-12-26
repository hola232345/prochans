import requests
import random
import time
import os
import re

PROXYCHAINS_CONF = "/etc/proxychains4.conf"
TIMEOUT = 6
MAX_PROXIES = 5
ALLOWED_COUNTRIES = {"US", "CA"}

GEO_API = "http://ip-api.com/json/"
IP_CHECK_API = "https://api.ipify.org?format=json"
PROXYSCRAPE_PAGE = "https://es.proxyscrape.com/lista-proxy-gratuita"

GREEN = "\033[92m"
RESET = "\033[0m"

def fetch_proxyscrape_http():
    proxies = set()
    try:
        r = requests.get(PROXYSCRAPE_PAGE, timeout=10)
        matches = re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}:\d+\b", r.text)
        proxies.update(matches)
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

            # Fallback Tor
            new_lines.append("socks5 127.0.0.1 9050\n")
            inserted = True

    if inserted:
        with open(PROXYCHAINS_CONF, "w") as f:
            f.writelines(new_lines)

def prochans():
    print(GREEN + "[] prochans iniciado" + RESET)
    print("[] obteniendo proxies HTTP desde ProxyScrape...")

    proxies = fetch_proxyscrape_http()
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
        print("No se encontraron proxies HTTP válidos")

if __name__ == "__main__":
    prochans()

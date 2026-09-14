import urllib.request
import re
import json

def parse_html(html, target_day=14):
    root = {"day": target_day, "tides": []}
    
    # 1. Day row
    day_pattern = re.compile(r'<tr[^>]*class="[^"]*tabla_mareas_fila[^"]*"[^>]*>(.*?)</tr>', re.DOTALL)
    for m in day_pattern.finditer(html):
        row = m.group(1)
        num_m = re.search(r'class="tabla_mareas_dia_numero"[^>]*>\s*(\d+)\s*<', row)
        if num_m and num_m.group(1) == str(target_day):
            # Sun
            sun_td = re.search(r'class="tabla_mareas_salida_puesta_sol"[^>]*>(.*?)</td>', row, re.DOTALL)
            if sun_td:
                suns = re.findall(r'(\d{1,2}:\d{2})(?:<[^>]*>|\s)*([apm]+)', sun_td.group(1), re.I)
                if len(suns) >= 2:
                    root["sunrise"] = f"{suns[0][0]} {suns[0][1].lower()}"
                    root["sunset"] = f"{suns[1][0]} {suns[1][1].lower()}"

            # Coef
            coef_td = re.search(r'class="tabla_mareas_coeficiente"[^>]*>(.*?)</td>', row, re.DOTALL)
            if coef_td:
                c_txt = coef_td.group(1)
                c_m = re.search(r'(\d+)', c_txt)
                if c_m:
                    root["coef"] = int(c_m.group(1))
                if "very high" in c_txt.lower(): root["solunar"] = "VERY HIGH"
                elif "high" in c_txt.lower(): root["solunar"] = "HIGH"
                elif "low" in c_txt.lower(): root["solunar"] = "LOW"
                else: root["solunar"] = "MODERATE"

            # Tides
            tide_tds = re.findall(r'<td[^>]*class="[^"]*tabla_mareas_marea[^"]*"[^>]*>(.*?)</td>', row, re.DOTALL)
            for td in tide_tds:
                time_m = re.search(r'class="tabla_mareas_marea_hora[^"]*"[^>]*>\s*(\d{1,2}:\d{2})(?:<[^>]*>|\s)*([apm]+)', td, re.I)
                alt_m = re.search(r'class="tabla_mareas_marea_altura_numero"[^>]*>\s*([-\d.]+)\s*</span>\s*([a-zA-Z]+)', td, re.I)
                if time_m and alt_m:
                    is_high = "tabla_mareas_marea_pleamar" in td
                    root["tides"].append({
                        "type": "HIGH TIDE" if is_high else "LOW TIDE",
                        "time": f"{time_m.group(1)} {time_m.group(2).lower()}",
                        "height": f"{alt_m.group(1)} {alt_m.group(2).lower()}",
                        "val": float(alt_m.group(1))
                    })

            if root["tides"]:
                break

    # Lunar
    p_m = re.search(r'The lunar phase is (?:a |an )?([^.<]+)', html, re.I)
    if p_m: root["moonPhase"] = p_m.group(1).strip()

    a_m = re.search(r'MOON AGE\s*([\d.]+\s*DAYS?)', html, re.I)
    if a_m: root["moonAge"] = a_m.group(1).strip()

    i_m = re.search(r'LIGHTING\s*(\d+\s*%)', html, re.I)
    if i_m: root["moonIllum"] = i_m.group(1).strip()

    return root

url = "https://tides4fishing.com/us/florida-east-coast/fort-pierce-south-beach-causeway"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")
res = parse_html(html, 14)
print(json.dumps(res, indent=2))

import os
import re

html_path = "/home/prime3vil/Documents/Antigravity/App Dev/Ebb&Flow/app/src/main/assets/map/index.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix title heading: Remove word "predictions"
html = html.replace("TODAY'S TIDE TABLE PREDICTIONS", "TODAY'S TIDE TABLE")

# 2. Fix cluster config for faster rendering
old_cluster_pattern = r"clusterGroup = L\.markerClusterGroup\(\{[^}]*\}\);"
new_cluster_code = """clusterGroup = L.markerClusterGroup({
          showCoverageOnHover: false,
          spiderfyOnMaxZoom: false,
          zoomToBoundsOnClick: true,
          chunkedLoading: true,
          chunkInterval: 120,
          chunkDelay: 5,
          maxClusterRadius: 48,
          disableClusteringAtZoom: 16
        });"""
html = re.sub(old_cluster_pattern, new_cluster_code, html, count=1)

# 3. Clean replacement for live handler code
live_code = '''
      // In-memory cache for live station data from tides4fishing
      const liveStationCache = new Map();

      // Native Bridge callback for live station telemetry from tides4fishing.com
      window.onStationLiveDataReceived = function(rawJson) {
        try {
          const data = typeof rawJson === "string" ? JSON.parse(rawJson) : rawJson;
          if (!data || data.error || !currentStation) return;

          liveStationCache.set(currentStation.id, data);
          applyLiveStationData(data);
        } catch (e) {
          console.warn("Error parsing live station data:", e);
        }
      };

      function requestLiveStationData(station) {
        if (!station || !station.url) return;

        if (liveStationCache.has(station.id)) {
          applyLiveStationData(liveStationCache.get(station.id));
          return;
        }

        // 1. Try Native Android Bridge (Zero CORS, background HttpURLConnection)
        if (window.EbbFlowBridge && typeof window.EbbFlowBridge.fetchStationLiveData === "function") {
          window.EbbFlowBridge.fetchStationLiveData(station.url, "window.onStationLiveDataReceived");
          return;
        }

        // 2. Fallback: browser fetch if running in web/electron
        fetch(station.url)
          .then(r => r.text())
          .then(html => {
            const data = parseTidesHtmlClientside(html);
            if (data && data.tides && data.tides.length > 0) {
              liveStationCache.set(station.id, data);
              applyLiveStationData(data);
            }
          })
          .catch(err => console.log("Web live fetch error:", err));
      }

      function parseTidesHtmlClientside(html) {
        const todayDay = new Date().getDate();
        const doc = new DOMParser().parseFromString(html, "text/html");
        const rows = doc.querySelectorAll("tr.tabla_mareas_fila");
        for (const r of rows) {
          const numEl = r.querySelector(".tabla_mareas_dia_numero");
          if (numEl && numEl.textContent.trim() === String(todayDay)) {
            const result = { day: todayDay, tides: [], sunrise: "", sunset: "", coef: 0, solunar: "" };
            
            const sunTd = r.querySelector(".tabla_mareas_salida_puesta_sol");
            if (sunTd) {
              const sunMatches = sunTd.textContent.match(/(\\d{1,2}:\\d{2}\\s*(?:am|pm))/gi);
              if (sunMatches && sunMatches.length >= 2) {
                result.sunrise = sunMatches[0];
                result.sunset = sunMatches[1];
              }
            }

            const coefTd = r.querySelector(".tabla_mareas_coeficiente");
            if (coefTd) {
              const m = coefTd.textContent.match(/(\\d+)/);
              if (m) result.coef = parseInt(m[1]);
              const txt = coefTd.textContent.toLowerCase();
              if (txt.includes("very high")) result.solunar = "VERY HIGH";
              else if (txt.includes("high")) result.solunar = "HIGH";
              else if (txt.includes("low")) result.solunar = "LOW";
              else result.solunar = "MODERATE";
            }

            const tideTds = r.querySelectorAll("td.tabla_mareas_marea");
            for (const td of tideTds) {
              const hEl = td.querySelector(".tabla_mareas_marea_hora");
              const aEl = td.querySelector(".tabla_mareas_marea_altura");
              if (hEl && aEl) {
                const isHigh = td.classList.contains("tabla_mareas_marea_pleamar") || td.innerHTML.includes("tabla_mareas_marea_pleamar");
                result.tides.push({
                  type: isHigh ? "HIGH TIDE" : "LOW TIDE",
                  time: hEl.textContent.trim(),
                  height: aEl.textContent.trim()
                });
              }
            }

            const faseEl = doc.querySelector("#fase_lunar_fondo, .fase_lunar_fondo");
            if (faseEl) {
              const fTxt = faseEl.textContent;
              const pMatch = fTxt.match(/The lunar phase is (?:a |an )?([^.]+)/i);
              if (pMatch) result.moonPhase = pMatch[1].trim();
              const aMatch = fTxt.match(/MOON AGE\\s*([\\d.]+\\s*DAYS?)/i);
              if (aMatch) result.moonAge = aMatch[1].trim();
              const iMatch = fTxt.match(/LIGHTING\\s*(\\d+\\s*%)/i);
              if (iMatch) result.moonIllum = iMatch[1].trim();
            }

            return result;
          }
        }
        return null;
      }

      function applyLiveStationData(data) {
        if (!data || !currentStation) return;

        // Apply real Sunrise / Sunset from tides4fishing
        if (data.sunrise && data.sunset) {
          sunTimesDisplayEl.textContent = data.sunrise.toUpperCase() + " / " + data.sunset.toUpperCase();
        }

        // Apply real Solunar & Coefficient from tides4fishing
        if (data.coef) {
          solunarCoefEl.textContent = data.coef + " / 118";
        }
        if (data.solunar) {
          solunarActivityEl.textContent = data.solunar + " ACTIVITY";
        }

        // Apply real Lunar data from tides4fishing
        if (data.moonPhase) {
          let icon = "🌒";
          const p = data.moonPhase.toLowerCase();
          if (p.includes("full")) icon = "🌕";
          else if (p.includes("new")) icon = "🌑";
          else if (p.includes("quarter")) icon = "🌓";
          else if (p.includes("gibbous")) icon = "🌔";
          lunarPhaseNameEl.textContent = icon + " " + data.moonPhase;
        }
        if (data.moonIllum || data.moonAge) {
          const illum = data.moonIllum || "";
          const age = data.moonAge || "";
          lunarIllumEl.textContent = (illum + " Illum • Age " + age).trim();
        }

        // Apply real tides from tides4fishing
        if (data.tides && data.tides.length > 0) {
          tideTableListEl.innerHTML = "";
          const now = new Date();
          const currentMinutes = now.getHours() * 60 + now.getMinutes();
          let nextFound = false;

          let upcomingHighObj = null;
          let upcomingLowObj = null;

          for (const t of data.tides) {
            const m = t.time.match(/(\\d{1,2}):(\\d{2})\\s*([apm]+)/i);
            let itemMinutes = 0;
            if (m) {
              let h = parseInt(m[1]);
              const min = parseInt(m[2]);
              const ampm = m[3].toLowerCase();
              if (ampm === "pm" && h < 12) h += 12;
              if (ampm === "am" && h === 12) h = 0;
              itemMinutes = h * 60 + min;
            }

            let status = "PAST";
            if (itemMinutes > currentMinutes) {
              if (!nextFound) {
                status = "NEXT";
                nextFound = true;
              } else {
                status = "UPCOMING";
              }
              if (t.type.includes("HIGH") && !upcomingHighObj) upcomingHighObj = Object.assign({}, t, { minutes: itemMinutes });
              if (t.type.includes("LOW") && !upcomingLowObj) upcomingLowObj = Object.assign({}, t, { minutes: itemMinutes });
            }

            const row = document.createElement("div");
            row.className = "tide-table-row " + (status === 'NEXT' ? 'is-next' : '');
            row.innerHTML = 
              '<div class="tide-type-wrap">' +
                '<span class="tide-type-icon ' + (t.type.includes('HIGH') ? 'high' : 'low') + '">' +
                  (t.type.includes('HIGH') ? '▲' : '▼') +
                '</span>' +
                '<span style="font-weight:800; font-size:12px;">' + t.type + '</span>' +
              '</div>' +
              '<span class="tide-time-text">' + t.time.toUpperCase() + '</span>' +
              '<span class="tide-height-text">' + t.height.toUpperCase() + '</span>' +
              '<span class="tide-status-badge ' + status.toLowerCase() + '">' + status + '</span>';
            tideTableListEl.appendChild(row);
          }

          if (upcomingHighObj) {
            const diffMin = upcomingHighObj.minutes - currentMinutes;
            const diffH = Math.floor(diffMin / 60);
            const diffM = diffMin % 60;
            nextHighTimeEl.textContent = upcomingHighObj.time.toUpperCase() + " (" + upcomingHighObj.height + ")";
            nextHighCountdownEl.textContent = String(diffH).padStart(2,'0') + "h " + String(diffM).padStart(2,'0') + "m";
          }
          if (upcomingLowObj) {
            const diffMin = upcomingLowObj.minutes - currentMinutes;
            const diffH = Math.floor(diffMin / 60);
            const diffM = diffMin % 60;
            nextLowTimeEl.textContent = upcomingLowObj.time.toUpperCase() + " (" + upcomingLowObj.height + ")";
            nextLowCountdownEl.textContent = String(diffH).padStart(2,'0') + "h " + String(diffM).padStart(2,'0') + "m";
          }
        }
      }
'''

# Remove any previous broken declaration of liveStationCache if present
if "const liveStationCache = new Map();" in html:
    html = re.sub(r"const liveStationCache = new Map\(\);.*?(?=function selectStation)", "", html, flags=re.DOTALL)

# Inject live_code right before selectStation
html = html.replace("function selectStation(station, animateFly = true, autoOpenPopup = true) {", live_code + "\n      function selectStation(station, animateFly = true, autoOpenPopup = true) {\n        requestLiveStationData(station);")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully injected clean live logic and chunked loading into index.html!")

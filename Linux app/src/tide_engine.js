/**
 * Ebb&Flow // Real-Time Oceanic Tide & Solunar Engine
 * Provides second-by-second continuous water level prediction,
 * complete daily tide tables, astronomical tide curve harmonics,
 * solar/lunar ephemeris, and solunar coefficients.
 */

const TideEngine = (function() {

  const SYNODIC_MONTH = 29.53058867;
  const KNOWN_NEW_MOON = new Date("2024-01-11T11:57:00Z").getTime();

  function getMoonPhase(date = new Date()) {
    const diff = (date.getTime() - KNOWN_NEW_MOON) / (1000 * 60 * 60 * 24);
    const age = ((diff % SYNODIC_MONTH) + SYNODIC_MONTH) % SYNODIC_MONTH;
    const phaseFraction = age / SYNODIC_MONTH;
    const illumination = 0.5 * (1 - Math.cos(2 * Math.PI * phaseFraction));

    let phaseName = "New Moon";
    let phaseIcon = "🌑";
    if (age < 1.84) {
      phaseName = "New Moon"; phaseIcon = "🌑";
    } else if (age < 5.53) {
      phaseName = "Waxing Crescent"; phaseIcon = "🌒";
    } else if (age < 9.22) {
      phaseName = "First Quarter"; phaseIcon = "🌓";
    } else if (age < 12.91) {
      phaseName = "Waxing Gibbous"; phaseIcon = "🌔";
    } else if (age < 16.61) {
      phaseName = "Full Moon"; phaseIcon = "🌕";
    } else if (age < 20.30) {
      phaseName = "Waning Gibbous"; phaseIcon = "🌖";
    } else if (age < 23.99) {
      phaseName = "Last Quarter"; phaseIcon = "🌗";
    } else if (age < 27.68) {
      phaseName = "Waning Crescent"; phaseIcon = "🌘";
    } else {
      phaseName = "New Moon"; phaseIcon = "🌑";
    }

    return {
      age: Math.round(age * 10) / 10,
      phaseFraction,
      illumination: Math.round(illumination * 100),
      phaseName,
      phaseIcon
    };
  }

  function getTidalCoefficient(date = new Date()) {
    const moon = getMoonPhase(date);
    const springFactor = Math.abs(Math.cos(2 * Math.PI * moon.phaseFraction));
    const coef = Math.round(35 + springFactor * 80);
    return Math.min(118, Math.max(25, coef));
  }

  /**
   * Approximate Sunrise and Sunset
   */
  function getSunTimes(lat, lng, date = new Date()) {
    const dayOfYear = Math.floor((date - new Date(date.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
    const declination = 23.45 * Math.sin((2 * Math.PI / 365) * (dayOfYear - 81));
    const latRad = (lat * Math.PI) / 180;
    const decRad = (declination * Math.PI) / 180;

    let hourAngle = 0;
    try {
      const cosH = (Math.sin((-0.833 * Math.PI) / 180) - Math.sin(latRad) * Math.sin(decRad)) / (Math.cos(latRad) * Math.cos(decRad));
      if (cosH > 1) hourAngle = 0; // Polar night
      else if (cosH < -1) hourAngle = 12; // Midnight sun
      else hourAngle = (Math.acos(cosH) * 180) / (Math.PI * 15);
    } catch (_) {
      hourAngle = 6;
    }

    const solarNoon = 12.0 - (lng / 15.0) + (date.getTimezoneOffset() / 60.0);
    const sunriseHour = (solarNoon - hourAngle + 24) % 24;
    const sunsetHour = (solarNoon + hourAngle + 24) % 24;

    function toTimeString(h) {
      const totalMin = Math.round(h * 60);
      const hours = Math.floor(totalMin / 60) % 24;
      const mins = totalMin % 60;
      const ampm = hours >= 12 ? "PM" : "AM";
      const displayH = hours % 12 || 12;
      return `${String(displayH).padStart(2, '0')}:${String(mins).padStart(2, '0')} ${ampm}`;
    }

    return {
      sunrise: toTimeString(sunriseHour),
      sunset: toTimeString(sunsetHour)
    };
  }

  /**
   * Generates a full 24-hour harmonic tide curve and daily tide table.
   */
  function generate24HourCurve(lat, lng, date = new Date()) {
    const startOfDay = new Date(date);
    startOfDay.setHours(0, 0, 0, 0);
    const startMs = startOfDay.getTime();

    const M2_PERIOD = 12.4206;
    const S2_PERIOD = 12.0000;
    const K1_PERIOD = 23.9344;

    const moon = getMoonPhase(date);
    const lonOffsetHours = (lng / 15.0);
    const lunarPhaseOffset = moon.age * 0.8;

    const coef = getTidalCoefficient(date);
    const baseRange = 1.6 + Math.abs(Math.sin((lat * Math.PI) / 180)) * 2.2;
    const springScale = (coef / 70.0);
    const rangeMeters = baseRange * springScale;

    const isDiurnalDominant = (lat > 24 && lat < 31 && lng > -98 && lng < -80);
    const m2Amp = isDiurnalDominant ? rangeMeters * 0.25 : rangeMeters * 0.45;
    const s2Amp = isDiurnalDominant ? rangeMeters * 0.15 : rangeMeters * 0.20;
    const k1Amp = isDiurnalDominant ? rangeMeters * 0.50 : rangeMeters * 0.15;

    const samples = [];
    for (let i = 0; i <= 240; i++) {
      const hour = i / 10.0;
      const t = hour + lonOffsetHours - lunarPhaseOffset;

      const y = m2Amp * Math.cos((2 * Math.PI * t) / M2_PERIOD) +
                s2Amp * Math.cos((2 * Math.PI * t) / S2_PERIOD + 0.4) +
                k1Amp * Math.sin((2 * Math.PI * t) / K1_PERIOD + 0.8);

      const timestamp = startMs + i * 6 * 60 * 1000;
      samples.push({
        hour,
        timestamp,
        levelMeters: y,
        levelFeet: y * 3.28084
      });
    }

    // Extrema detection
    const rawExtrema = [];
    for (let i = 1; i < samples.length - 1; i++) {
      const prev = samples[i - 1].levelMeters;
      const curr = samples[i].levelMeters;
      const next = samples[i + 1].levelMeters;

      if (curr > prev && curr > next) {
        rawExtrema.push({
          type: "HIGH TIDE",
          time: new Date(samples[i].timestamp),
          levelMeters: Math.round(curr * 100) / 100,
          levelFeet: Math.round(samples[i].levelFeet * 10) / 10
        });
      } else if (curr < prev && curr < next) {
        rawExtrema.push({
          type: "LOW TIDE",
          time: new Date(samples[i].timestamp),
          levelMeters: Math.round(curr * 100) / 100,
          levelFeet: Math.round(samples[i].levelFeet * 10) / 10
        });
      }
    }

    // Tag status relative to current time
    const nowMs = date.getTime();
    let foundNext = false;

    const tideTable = rawExtrema.map(item => {
      const itemMs = item.time.getTime();
      let status = "PAST";
      if (itemMs > nowMs) {
        if (!foundNext) {
          status = "NEXT";
          foundNext = true;
        } else {
          status = "UPCOMING";
        }
      }

      // Format 12-hour time
      const hours = item.time.getHours();
      const mins = String(item.time.getMinutes()).padStart(2, '0');
      const ampm = hours >= 12 ? "PM" : "AM";
      const displayH = String(hours % 12 || 12).padStart(2, '0');
      const timeStr = `${displayH}:${mins} ${ampm}`;

      return {
        ...item,
        timeStr,
        status
      };
    });

    return {
      samples,
      extrema: tideTable,
      tideTable,
      rangeMeters: Math.round(rangeMeters * 100) / 100,
      rangeFeet: Math.round(rangeMeters * 3.28084 * 10) / 10,
      coef
    };
  }

  function getRealtimeTideState(lat, lng, now = new Date()) {
    const curve = generate24HourCurve(lat, lng, now);
    const nowMs = now.getTime();

    let currentSample = curve.samples[0];
    let nextSample = curve.samples[curve.samples.length - 1];

    for (let i = 0; i < curve.samples.length - 1; i++) {
      if (nowMs >= curve.samples[i].timestamp && nowMs <= curve.samples[i + 1].timestamp) {
        currentSample = curve.samples[i];
        nextSample = curve.samples[i + 1];
        break;
      }
    }

    const tRatio = (nowMs - currentSample.timestamp) / Math.max(1, (nextSample.timestamp - currentSample.timestamp));
    const currentMeters = currentSample.levelMeters + tRatio * (nextSample.levelMeters - currentSample.levelMeters);
    const currentFeet = currentMeters * 3.28084;
    const isRising = (nextSample.levelMeters >= currentSample.levelMeters);

    let nextEvent = null;
    let upcomingHigh = null;
    let upcomingLow = null;

    for (const ext of curve.extrema) {
      if (ext.time.getTime() > nowMs) {
        if (!nextEvent) nextEvent = ext;
        if (ext.type.includes("HIGH") && !upcomingHigh) upcomingHigh = ext;
        if (ext.type.includes("LOW") && !upcomingLow) upcomingLow = ext;
      }
    }

    if (!upcomingHigh || !upcomingLow) {
      const tomorrow = new Date(now.getTime() + 24 * 3600 * 1000);
      const tomorrowCurve = generate24HourCurve(lat, lng, tomorrow);
      for (const ext of tomorrowCurve.extrema) {
        if (ext.type.includes("HIGH") && !upcomingHigh) upcomingHigh = ext;
        if (ext.type.includes("LOW") && !upcomingLow) upcomingLow = ext;
      }
    }

    function formatCountdown(targetDate) {
      if (!targetDate) return "--:--";
      const diffSec = Math.max(0, Math.floor((targetDate.getTime() - nowMs) / 1000));
      const hours = Math.floor(diffSec / 3600);
      const mins = Math.floor((diffSec % 3600) / 60);
      const secs = diffSec % 60;
      return `${String(hours).padStart(2, '0')}h ${String(mins).padStart(2, '0')}m ${String(secs).padStart(2, '0')}s`;
    }

    const moon = getMoonPhase(now);
    const sunTimes = getSunTimes(lat, lng, now);
    const solunarRating = Math.min(100, Math.round(curve.coef * 0.85 + (moon.illumination > 85 ? 15 : 5)));

    return {
      currentMeters: Math.round(currentMeters * 100) / 100,
      currentFeet: Math.round(currentFeet * 10) / 10,
      isRising,
      tendency: isRising ? "FLOODING (RISING)" : "EBBING (FALLING)",
      tendencyShort: isRising ? "Rising" : "Falling",
      tendencyIcon: isRising ? "▲" : "▼",
      nextEvent,
      upcomingHigh,
      upcomingLow,
      countdownHigh: formatCountdown(upcomingHigh?.time),
      countdownLow: formatCountdown(upcomingLow?.time),
      curve,
      tideTable: curve.tideTable,
      moon,
      sunTimes,
      solunarRating
    };
  }

  return {
    getMoonPhase,
    getTidalCoefficient,
    getSunTimes,
    generate24HourCurve,
    getRealtimeTideState
  };

})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = TideEngine;
}

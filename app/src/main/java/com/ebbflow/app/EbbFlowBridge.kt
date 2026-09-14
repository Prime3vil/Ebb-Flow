package com.ebbflow.app

import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.net.Uri
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.widget.Toast
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import java.util.Calendar
import java.util.Locale
import java.util.concurrent.Executors
import java.util.regex.Pattern

class EbbFlowBridge(private val context: Context, private val webView: WebView) {

    private val prefs: SharedPreferences = context.getSharedPreferences("ebbflow_prefs", Context.MODE_PRIVATE)
    private val executor = Executors.newCachedThreadPool()
    private val cache = HashMap<String, String>()

    @JavascriptInterface
    fun saveLastLocation(json: String) {
        prefs.edit().putString("last_location", json).apply()
    }

    @JavascriptInterface
    fun getLastLocation(): String {
        return prefs.getString("last_location", "") ?: ""
    }

    @JavascriptInterface
    fun saveHomeLocation(json: String) {
        prefs.edit().putString("home_location", json).apply()
        triggerHaptic()
        Toast.makeText(context, "Home Base Saved", Toast.LENGTH_SHORT).show()
    }

    @JavascriptInterface
    fun getHomeLocation(): String {
        return prefs.getString("home_location", "") ?: ""
    }

    @JavascriptInterface
    fun saveQuickAccessList(json: String) {
        prefs.edit().putString("quick_access_list", json).apply()
    }

    @JavascriptInterface
    fun getQuickAccessList(): String {
        return prefs.getString("quick_access_list", "[]") ?: "[]"
    }

    @JavascriptInterface
    fun onQuickAccessChanged() {
        triggerHaptic()
    }

    @JavascriptInterface
    fun openExternalUrl(url: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(context, "Could not open link: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
        }
    }

    @JavascriptInterface
    fun fetchStationLiveData(stationUrl: String, callbackMethod: String) {
        val cached = cache[stationUrl]
        if (cached != null) {
            postToWeb(callbackMethod, cached)
            return
        }

        executor.execute {
            try {
                val fullUrl = if (stationUrl.startsWith("http")) stationUrl else "https://tides4fishing.com$stationUrl"
                val connection = (URL(fullUrl).openConnection() as HttpURLConnection).apply {
                    requestMethod = "GET"
                    connectTimeout = 8000
                    readTimeout = 8000
                    setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36")
                }

                val reader = BufferedReader(InputStreamReader(connection.inputStream))
                val html = reader.readText()
                reader.close()

                val parsedJson = parseTidesHtml(html)
                cache[stationUrl] = parsedJson
                postToWeb(callbackMethod, parsedJson)
            } catch (e: Exception) {
                val errorObj = JSONObject().apply {
                    put("error", e.localizedMessage ?: "Network error")
                }
                postToWeb(callbackMethod, errorObj.toString())
            }
        }
    }

    private fun postToWeb(callbackMethod: String, jsonPayload: String) {
        webView.post {
            val escaped = jsonPayload.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
            webView.evaluateJavascript("$callbackMethod('$escaped')", null)
        }
    }

    private fun parseTidesHtml(html: String): String {
        val root = JSONObject()
        val daysArray = JSONArray()

        // 1. Extract station's exact local date from HTML
        var todayDateStr = ""
        var todayDayNum = 0
        val todayPattern = Pattern.compile("Today\\s+([A-Za-z]+),\\s*(\\d+)(?:<sup>[^<]*</sup>)?\\s+of\\s+([A-Za-z]+)\\s+of\\s+(\\d{4})", Pattern.CASE_INSENSITIVE)
        val todayMatcher = todayPattern.matcher(html)
        if (todayMatcher.find()) {
            val dName = todayMatcher.group(1) ?: ""
            val dNum = todayMatcher.group(2) ?: ""
            val mName = todayMatcher.group(3) ?: ""
            val yr = todayMatcher.group(4) ?: ""
            todayDayNum = dNum.toIntOrNull() ?: 0
            todayDateStr = "$dName, $mName $dNum, $yr"
        }

        // Extract month prefix if available (e.g. 2026-09)
        val monthPrefixPattern = Pattern.compile("Day\\('(\\d{4}-\\d{2})-\\d+'\\)")
        val mpMatcher = monthPrefixPattern.matcher(html)
        val monthPrefix = if (mpMatcher.find()) mpMatcher.group(1) ?: "" else ""

        // 2. Iterate all rows in tabla_mareas_fila
        val dayPattern = Pattern.compile("<tr([^>]*)>(.*?)</tr>", Pattern.DOTALL)
        val matcher = dayPattern.matcher(html)

        val seenDays = HashSet<Int>()
        var todayIndex = 0

        while (matcher.find()) {
            val trAttrs = matcher.group(1) ?: ""
            if (!trAttrs.contains("tabla_mareas_fila")) continue
            val rowHtml = matcher.group(2) ?: continue

            val numPattern = Pattern.compile("class=\"tabla_mareas_dia_numero\"[^>]*>\\s*(\\d+)\\s*<")
            val numMatcher = numPattern.matcher(rowHtml)
            if (!numMatcher.find()) continue
            val dayNum = numMatcher.group(1)?.toIntOrNull() ?: continue

            // Filter out other months if monthPrefix exists
            val dayClickPattern = Pattern.compile("onclick=\"Day\\('([^']+)'\\);\"")
            val clickMatcher = dayClickPattern.matcher(trAttrs)
            if (clickMatcher.find() && monthPrefix.isNotEmpty()) {
                val dVal = clickMatcher.group(1) ?: ""
                if (!dVal.startsWith(monthPrefix)) continue
            }

            if (seenDays.contains(dayNum)) continue
            seenDays.add(dayNum)

            val isToday = (dayNum == todayDayNum) || trAttrs.contains("fondo3") || rowHtml.contains("fondo3")
            if (isToday) {
                todayIndex = daysArray.length()
            }

            val dayNamePattern = Pattern.compile("class=\"tabla_mareas_dia_dia\"[^>]*>\\s*([^<]+)\\s*<")
            val dayNameMatcher = dayNamePattern.matcher(rowHtml)
            val dayName = if (dayNameMatcher.find()) dayNameMatcher.group(1)?.trim() ?: "" else ""

            val titlePattern = Pattern.compile("title=\"([^\"]+)\"")
            val titleMatcher = titlePattern.matcher(trAttrs)
            val dateTitle = if (titleMatcher.find()) titleMatcher.group(1)?.trim() ?: "" else "$dayName, Day $dayNum"

            val dayObj = JSONObject()
            dayObj.put("day", dayNum)
            dayObj.put("dayName", dayName)
            dayObj.put("dateTitle", dateTitle)
            dayObj.put("isToday", isToday)

            // Sunrise / Sunset
            val sunTdPattern = Pattern.compile("class=\"tabla_mareas_salida_puesta_sol\"[^>]*>(.*?)</td>", Pattern.DOTALL)
            val sunTdMatcher = sunTdPattern.matcher(rowHtml)
            var sunrise = ""
            var sunset = ""
            if (sunTdMatcher.find()) {
                val sunContent = sunTdMatcher.group(1) ?: ""
                val sunPattern = Pattern.compile("(\\d{1,2}:\\d{2})(?:<[^>]*>|\\s)*([apm]+|h)?", Pattern.CASE_INSENSITIVE)
                val sunMatcher = sunPattern.matcher(sunContent)
                if (sunMatcher.find()) {
                    val t = sunMatcher.group(1) ?: ""
                    val m = sunMatcher.group(2)?.trim()?.lowercase(Locale.US) ?: ""
                    sunrise = if (m.isNotEmpty()) "$t $m" else t
                }
                if (sunMatcher.find()) {
                    val t = sunMatcher.group(1) ?: ""
                    val m = sunMatcher.group(2)?.trim()?.lowercase(Locale.US) ?: ""
                    sunset = if (m.isNotEmpty()) "$t $m" else t
                }
            }
            dayObj.put("sunrise", sunrise)
            dayObj.put("sunset", sunset)

            // Coefficient & Solunar
            var coef = 0
            var solunar = "MODERATE"
            val coefTdPattern = Pattern.compile("class=\"tabla_mareas_coeficiente\"[^>]*>(.*?)</td>", Pattern.DOTALL)
            val coefMatcher = coefTdPattern.matcher(rowHtml)
            if (coefMatcher.find()) {
                val coefHtml = coefMatcher.group(1) ?: ""
                val cNumMatcher = Pattern.compile("(\\d+)").matcher(coefHtml)
                if (cNumMatcher.find()) coef = cNumMatcher.group(1)?.toIntOrNull() ?: 0
                when {
                    coefHtml.contains("very high", ignoreCase = true) -> solunar = "VERY HIGH"
                    coefHtml.contains("high", ignoreCase = true) -> solunar = "HIGH"
                    coefHtml.contains("low", ignoreCase = true) -> solunar = "LOW"
                    else -> solunar = "MODERATE"
                }
            }
            dayObj.put("coef", coef)
            dayObj.put("solunar", solunar)

            // Tides
            val dayTidesArray = JSONArray()
            val tideTdPattern = Pattern.compile("<td[^>]*class=\"[^\"]*tabla_mareas_marea[^\"]*\"[^>]*>(.*?)</td>", Pattern.DOTALL)
            val tideMatcher = tideTdPattern.matcher(rowHtml)

            while (tideMatcher.find()) {
                val tdHtml = tideMatcher.group(1) ?: continue
                val timeP = Pattern.compile("class=\"tabla_mareas_marea_hora[^\"]*\"[^>]*>\\s*(\\d{1,2}:\\d{2})(?:<[^>]*>|\\s)*([apm]+|h)?", Pattern.CASE_INSENSITIVE)
                val altP = Pattern.compile("class=\"tabla_mareas_marea_altura_numero\"[^>]*>\\s*([-\\d.]+)\\s*</span>\\s*([a-zA-Z]+)", Pattern.CASE_INSENSITIVE)

                val tMatch = timeP.matcher(tdHtml)
                val aMatch = altP.matcher(tdHtml)

                if (tMatch.find() && aMatch.find()) {
                    val tVal = tMatch.group(1) ?: ""
                    val tAmpm = tMatch.group(2)?.trim()?.lowercase(Locale.US) ?: ""
                    val timeStr = if (tAmpm.isNotEmpty()) "$tVal $tAmpm" else tVal

                    val heightVal = aMatch.group(1) ?: "0"
                    val unit = aMatch.group(2)?.trim()?.lowercase(Locale.US) ?: "ft"
                    val isHigh = tdHtml.contains("tabla_mareas_marea_pleamar")

                    val tideObj = JSONObject().apply {
                        put("type", if (isHigh) "HIGH TIDE" else "LOW TIDE")
                        put("time", timeStr)
                        put("height", "$heightVal $unit")
                        put("val", heightVal.toDoubleOrNull() ?: 0.0)
                    }
                    dayTidesArray.put(tideObj)
                }
            }
            dayObj.put("tides", dayTidesArray)

            daysArray.put(dayObj)

            // If this is today, copy top-level fields
            if (isToday) {
                root.put("day", dayNum)
                root.put("dateStr", if (todayDateStr.isNotEmpty()) todayDateStr else dateTitle)
                root.put("sunrise", sunrise)
                root.put("sunset", sunset)
                root.put("coef", coef)
                root.put("solunar", solunar)
                root.put("tides", dayTidesArray)
            }
        }

        root.put("days", daysArray)
        root.put("todayIndex", todayIndex)

        // Fallback if today was not matched
        if (!root.has("tides") && daysArray.length() > 0) {
            val firstDay = daysArray.getJSONObject(0)
            root.put("day", firstDay.optInt("day"))
            root.put("dateStr", firstDay.optString("dateTitle"))
            root.put("sunrise", firstDay.optString("sunrise"))
            root.put("sunset", firstDay.optString("sunset"))
            root.put("coef", firstDay.optInt("coef"))
            root.put("solunar", firstDay.optString("solunar"))
            root.put("tides", firstDay.optJSONArray("tides"))
        }

        // 3. Lunar Phase, Age, Illumination
        val phasePattern = Pattern.compile("The lunar phase is (?:a |an )?([^.<]+)", Pattern.CASE_INSENSITIVE)
        val pMatch = phasePattern.matcher(html)
        if (pMatch.find()) {
            root.put("moonPhase", pMatch.group(1)?.trim() ?: "")
        }

        val agePattern = Pattern.compile("(?:JS_VALOR_EDAD_LUNAR\\s*=\\s*([\\d.]+)|MOON AGE\\s*([\\d.]+))", Pattern.CASE_INSENSITIVE)
        val aMatch = agePattern.matcher(html)
        if (aMatch.find()) {
            val rawAge = aMatch.group(1) ?: aMatch.group(2)
            val d = rawAge?.toDoubleOrNull()
            if (d != null) {
                root.put("moonAge", String.format(Locale.US, "%.1fd", d))
            } else {
                root.put("moonAge", rawAge?.trim() ?: "")
            }
        }

        val illumPattern = Pattern.compile("(?:JS_VALOR_ILUMINACION\\s*=\\s*([\\d.]+)|LIGHTING\\s*(\\d+))", Pattern.CASE_INSENSITIVE)
        val iMatch = illumPattern.matcher(html)
        if (iMatch.find()) {
            val rawIllum = iMatch.group(1) ?: iMatch.group(2)
            val d = rawIllum?.toDoubleOrNull()
            if (d != null) {
                root.put("moonIllum", "${d.toInt()}%")
            } else {
                root.put("moonIllum", rawIllum?.trim() ?: "")
            }
        }

        return root.toString()
    }

    @JavascriptInterface
    fun triggerHaptic() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
                vibratorManager?.defaultVibrator?.vibrate(
                    VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK)
                )
            } else {
                @Suppress("DEPRECATION")
                val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
                @Suppress("DEPRECATION")
                vibrator?.vibrate(20)
            }
        } catch (_: Exception) {}
    }
}

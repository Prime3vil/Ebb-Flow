/**
 * Ebb&Flow // Quick Access, Nicknames & Location Persistence Manager
 * Handles:
 * 1. Persistent last chosen location (restored immediately on launch)
 * 2. Home location designation
 * 3. Quick Access bookmarked list with customizable nicknames
 * 4. Dual-layer storage (LocalStorage + Android Native SharedPreferences bridge)
 */

const QuickAccessManager = (function() {

  const STORAGE_KEYS = {
    LAST_LOCATION: "ebbflow_last_location",
    HOME_LOCATION: "ebbflow_home_location",
    SAVED_LIST: "ebbflow_quick_access_list"
  };

  /**
   * Safe Native Bridge caller
   */
  function callBridge(method, ...args) {
    if (window.EbbFlowBridge && typeof window.EbbFlowBridge[method] === "function") {
      try {
        window.EbbFlowBridge[method](...args);
      } catch (e) {
        console.warn("Bridge call failed:", method, e);
      }
    }
  }

  /**
   * Save last visited location
   */
  function setLastLocation(station) {
    if (!station || !station.id) return;
    try {
      const data = JSON.stringify(station);
      localStorage.setItem(STORAGE_KEYS.LAST_LOCATION, data);
      callBridge("saveLastLocation", data);
    } catch (e) {
      console.warn("Failed saving last location:", e);
    }
  }

  /**
   * Retrieve last visited location
   */
  function getLastLocation() {
    try {
      // Check native bridge first if available
      if (window.EbbFlowBridge && window.EbbFlowBridge.getLastLocation) {
        const nativeVal = window.EbbFlowBridge.getLastLocation();
        if (nativeVal && nativeVal.length > 5) {
          return JSON.parse(nativeVal);
        }
      }
      const val = localStorage.getItem(STORAGE_KEYS.LAST_LOCATION);
      return val ? JSON.parse(val) : null;
    } catch (e) {
      console.warn("Failed getting last location:", e);
      return null;
    }
  }

  /**
   * Set designated Home Location
   */
  function setHomeLocation(station) {
    if (!station || !station.id) return;
    try {
      const data = JSON.stringify(station);
      localStorage.setItem(STORAGE_KEYS.HOME_LOCATION, data);
      callBridge("saveHomeLocation", data);
      
      // Auto-add to quick access if not already there
      addToQuickAccess(station, "Home Base");
      return true;
    } catch (e) {
      console.warn("Failed saving home location:", e);
      return false;
    }
  }

  /**
   * Retrieve Home Location
   */
  function getHomeLocation() {
    try {
      if (window.EbbFlowBridge && window.EbbFlowBridge.getHomeLocation) {
        const nativeVal = window.EbbFlowBridge.getHomeLocation();
        if (nativeVal && nativeVal.length > 5) {
          return JSON.parse(nativeVal);
        }
      }
      const val = localStorage.getItem(STORAGE_KEYS.HOME_LOCATION);
      return val ? JSON.parse(val) : null;
    } catch (e) {
      return null;
    }
  }

  /**
   * Check if station is Home
   */
  function isHomeLocation(stationId) {
    const home = getHomeLocation();
    return home && home.id === stationId;
  }

  /**
   * Get all Quick Access items
   */
  function getQuickAccessList() {
    try {
      if (window.EbbFlowBridge && window.EbbFlowBridge.getQuickAccessList) {
        const nativeVal = window.EbbFlowBridge.getQuickAccessList();
        if (nativeVal && nativeVal.length > 5) {
          return JSON.parse(nativeVal);
        }
      }
      const val = localStorage.getItem(STORAGE_KEYS.SAVED_LIST);
      return val ? JSON.parse(val) : [];
    } catch (e) {
      return [];
    }
  }

  /**
   * Save Quick Access list
   */
  function saveList(list) {
    try {
      const data = JSON.stringify(list);
      localStorage.setItem(STORAGE_KEYS.SAVED_LIST, data);
      callBridge("saveQuickAccessList", data);
    } catch (e) {
      console.warn("Failed saving quick access list:", e);
    }
  }

  /**
   * Add a station to Quick Access with optional nickname
   */
  function addToQuickAccess(station, nickname = "") {
    if (!station || !station.id) return;
    const list = getQuickAccessList();
    const existingIdx = list.findIndex(item => item.id === station.id);

    const entry = {
      id: station.id,
      name: station.name,
      nickname: nickname || (existingIdx >= 0 ? list[existingIdx].nickname : ""),
      region: station.region,
      country: station.country,
      continent: station.continent,
      lat: station.lat,
      lng: station.lng,
      url: station.url,
      savedAt: Date.now()
    };

    if (existingIdx >= 0) {
      list[existingIdx] = { ...list[existingIdx], ...entry };
    } else {
      list.unshift(entry);
    }

    saveList(list);
    callBridge("onQuickAccessChanged");
    return entry;
  }

  /**
   * Update nickname for a saved station
   */
  function updateNickname(stationId, newNickname) {
    const list = getQuickAccessList();
    const item = list.find(x => x.id === stationId);
    if (item) {
      item.nickname = (newNickname || "").trim();
      saveList(list);
      callBridge("onQuickAccessChanged");
      return true;
    }
    return false;
  }

  /**
   * Remove a station from Quick Access
   */
  function removeFromQuickAccess(stationId) {
    let list = getQuickAccessList();
    list = list.filter(item => item.id !== stationId);
    saveList(list);
    
    // If it was home, unset home
    const home = getHomeLocation();
    if (home && home.id === stationId) {
      localStorage.removeItem(STORAGE_KEYS.HOME_LOCATION);
      callBridge("saveHomeLocation", "");
    }

    callBridge("onQuickAccessChanged");
    return true;
  }

  /**
   * Check if a station is in Quick Access
   */
  function isSaved(stationId) {
    const list = getQuickAccessList();
    return list.some(item => item.id === stationId);
  }

  /**
   * Get custom nickname or default name
   */
  function getDisplayName(station) {
    if (!station) return "";
    const list = getQuickAccessList();
    const item = list.find(x => x.id === station.id);
    if (item && item.nickname && item.nickname.trim().length > 0) {
      return item.nickname.trim();
    }
    return station.name;
  }

  return {
    setLastLocation,
    getLastLocation,
    setHomeLocation,
    getHomeLocation,
    isHomeLocation,
    getQuickAccessList,
    addToQuickAccess,
    updateNickname,
    removeFromQuickAccess,
    isSaved,
    getDisplayName
  };

})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = QuickAccessManager;
}

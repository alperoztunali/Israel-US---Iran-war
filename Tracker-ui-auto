import { useState, useEffect } from “react”;

// ─── CONFIG: SET YOUR GITHUB REPO HERE ───────────────────────────────────────
// Replace with your own: “https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/entries.json”
const ENTRIES_URL = “https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/entries.json”;
// ─────────────────────────────────────────────────────────────────────────────

const CATEGORIES = [“Airstrike”, “Statement”, “Casualties”, “Movement”, “Missile/Drone”, “Naval”, “Diplomatic”, “Other”];
const SOURCES = [“CENTCOM”, “IDF”, “IRGC”, “Al Jazeera”, “PressTV”, “Tasnim News”, “Gulf News”, “Arab News”, “CGTN Europe”, “WAM UAE”, “Other”];

const CAT_COLORS = {
“Airstrike”:     “#ef4444”,
“Statement”:     “#4a9eff”,
“Casualties”:    “#f97316”,
“Movement”:      “#a78bfa”,
“Missile/Drone”: “#fb7185”,
“Naval”:         “#06b6d4”,
“Diplomatic”:    “#34d399”,
“Other”:         “#64748b”,
};

const SOURCE_BADGE = {
“CENTCOM”:      { bg: “#0f2d4a”, color: “#60a5fa” },
“IDF”:          { bg: “#0f2d4a”, color: “#93c5fd” },
“Al Jazeera”:   { bg: “#3b1a00”, color: “#fb923c” },
“PressTV”:      { bg: “#3b0000”, color: “#fca5a5” },
“Tasnim News”:  { bg: “#3b0000”, color: “#f87171” },
“Gulf News”:    { bg: “#1a2a00”, color: “#86efac” },
“Arab News”:    { bg: “#1a2a00”, color: “#6ee7b7” },
“WAM UAE”:      { bg: “#2a1a00”, color: “#fcd34d” },
“CGTN Europe”:  { bg: “#001a2a”, color: “#67e8f9” },
};

function fmt(iso) {
if (!iso) return “—”;
try {
return new Date(iso).toLocaleString(“en-GB”, {
day: “2-digit”, month: “short”, year: “numeric”,
hour: “2-digit”, minute: “2-digit”, hour12: false,
});
} catch { return iso; }
}

export default function IranTracker() {
const [entries,     setEntries]     = useState([]);
const [loading,     setLoading]     = useState(true);
const [lastFetch,   setLastFetch]   = useState(null);
const [error,       setError]       = useState(””);
const [filterCat,   setFilterCat]   = useState(“All”);
const [filterSrc,   setFilterSrc]   = useState(“All”);
const [search,      setSearch]      = useState(””);
const [expandedId,  setExpandedId]  = useState(null);
const [configured,  setConfigured]  = useState(!ENTRIES_URL.includes(“YOUR_USERNAME”));

async function fetchEntries(silent = false) {
if (!configured) return;
if (!silent) setLoading(true);
setError(””);
try {
const res = await fetch(ENTRIES_URL + “?t=” + Date.now());
if (!res.ok) throw new Error(`HTTP ${res.status}`);
const data = await res.json();
setEntries(Array.isArray(data) ? data : []);
setLastFetch(new Date());
} catch (e) {
setError(“Could not fetch entries. Check your ENTRIES_URL config.”);
}
setLoading(false);
}

useEffect(() => {
fetchEntries();
const interval = setInterval(() => fetchEntries(true), 15 * 60 * 1000);
return () => clearInterval(interval);
}, [configured]);

const filtered = entries.filter(e => {
const catOk = filterCat === “All” || e.category === filterCat;
const srcOk = filterSrc === “All” || e.source === filterSrc;
const q = search.toLowerCase();
const textOk = !q || (e.headline + e.excerpt + e.location + e.source).toLowerCase().includes(q);
return catOk && srcOk && textOk;
});

const catCounts = CATEGORIES.reduce((a, c) => ({ …a, [c]: entries.filter(e => e.category === c).length }), {});

return (
<div style={{
minHeight: “100vh”,
background: “#07090f”,
color: “#e2e8f0”,
fontFamily: “‘IBM Plex Mono’, monospace”,
}}>
{/* Top bar */}
<div style={{
position: “sticky”, top: 0, zIndex: 100,
background: “#080b14”,
borderBottom: “1px solid #1e293b”,
padding: “0 20px”,
display: “flex”, alignItems: “center”, justifyContent: “space-between”,
height: 52,
}}>
<div style={{ display: “flex”, alignItems: “center”, gap: 10 }}>
<div style={{ width: 7, height: 7, borderRadius: “50%”, background: “#ef4444”, boxShadow: “0 0 8px #ef4444”, animation: “blink 2s infinite” }} />
<span style={{ fontSize: 10, letterSpacing: 3, color: “#94a3b8” }}>IRAN / REGIONAL TENSIONS</span>
<span style={{ fontSize: 9, background: “#1e293b”, color: “#475569”, padding: “2px 7px”, borderRadius: 2, letterSpacing: 1 }}>AUTO TRACKER</span>
</div>
<div style={{ display: “flex”, alignItems: “center”, gap: 14 }}>
{lastFetch && (
<span style={{ fontSize: 9, color: “#334155”, letterSpacing: 1 }}>
UPDATED {lastFetch.toLocaleTimeString(“en-GB”, { hour: “2-digit”, minute: “2-digit” })}
</span>
)}
<button onClick={() => fetchEntries()} style={{
background: “#0f172a”, border: “1px solid #1e293b”, color: “#475569”,
fontSize: 9, padding: “4px 10px”, borderRadius: 2, cursor: “pointer”,
fontFamily: “inherit”, letterSpacing: 1,
}}>↻ REFRESH</button>
<span style={{ fontSize: 9, color: “#334155” }}>{entries.length} ENTRIES</span>
</div>
</div>

```
  <div style={{ maxWidth: 1100, margin: "0 auto", padding: "20px 16px" }}>

    {/* Setup notice */}
    {!configured && (
      <div style={{
        background: "#1a0f00", border: "1px solid #f97316", borderRadius: 4,
        padding: "16px 20px", marginBottom: 20, fontSize: 11, lineHeight: 1.8,
      }}>
        <div style={{ color: "#fb923c", letterSpacing: 1, marginBottom: 8 }}>⚠ SETUP REQUIRED</div>
        <div style={{ color: "#94a3b8" }}>
          Edit the <code style={{ color: "#fbbf24" }}>ENTRIES_URL</code> constant at the top of this file.<br />
          Replace <code style={{ color: "#fbbf24" }}>YOUR_USERNAME</code> and <code style={{ color: "#fbbf24" }}>YOUR_REPO</code> with your GitHub details.<br />
          Example: <code style={{ color: "#6ee7b7" }}>https://raw.githubusercontent.com/jsmith/iran-tracker/main/entries.json</code>
        </div>
      </div>
    )}

    {/* Error */}
    {error && (
      <div style={{ background: "#1a0000", border: "1px solid #ef4444", borderRadius: 3, padding: "10px 16px", marginBottom: 16, fontSize: 10, color: "#fca5a5", letterSpacing: 1 }}>
        ⚠ {error}
      </div>
    )}

    {/* Stat tiles */}
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(105px, 1fr))", gap: 6, marginBottom: 20 }}>
      {CATEGORIES.map(c => (
        <div key={c} onClick={() => setFilterCat(filterCat === c ? "All" : c)} style={{
          background: filterCat === c ? "#0f172a" : "#0a0e18",
          border: `1px solid ${filterCat === c ? CAT_COLORS[c] : "#1a2332"}`,
          borderRadius: 3, padding: "10px 12px", cursor: "pointer", transition: "all 0.15s",
          opacity: catCounts[c] === 0 ? 0.3 : 1,
        }}>
          <div style={{ fontSize: 20, fontWeight: 700, color: CAT_COLORS[c] }}>{catCounts[c]}</div>
          <div style={{ fontSize: 8, color: "#475569", letterSpacing: 1, marginTop: 2 }}>{c.toUpperCase()}</div>
        </div>
      ))}
    </div>

    {/* Filters + Search */}
    <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap", alignItems: "center" }}>
      <input
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="Search headlines, locations..."
        style={{
          background: "#0d1117", border: "1px solid #1e293b", color: "#94a3b8",
          padding: "6px 12px", fontSize: 10, fontFamily: "inherit", borderRadius: 3,
          outline: "none", width: 220, letterSpacing: 0.5,
        }}
      />
      <select value={filterSrc} onChange={e => setFilterSrc(e.target.value)} style={{
        background: "#0d1117", border: "1px solid #1e293b", color: "#94a3b8",
        padding: "6px 12px", fontSize: 10, fontFamily: "inherit", borderRadius: 3, outline: "none",
      }}>
        <option value="All">ALL SOURCES</option>
        {SOURCES.map(s => <option key={s}>{s}</option>)}
      </select>
      <select value={filterCat} onChange={e => setFilterCat(e.target.value)} style={{
        background: "#0d1117", border: "1px solid #1e293b", color: "#94a3b8",
        padding: "6px 12px", fontSize: 10, fontFamily: "inherit", borderRadius: 3, outline: "none",
      }}>
        <option value="All">ALL CATEGORIES</option>
        {CATEGORIES.map(c => <option key={c}>{c}</option>)}
      </select>
      {(filterCat !== "All" || filterSrc !== "All" || search) && (
        <button onClick={() => { setFilterCat("All"); setFilterSrc("All"); setSearch(""); }} style={{
          background: "none", border: "1px solid #1e293b", color: "#475569",
          padding: "6px 10px", fontSize: 9, fontFamily: "inherit", borderRadius: 3,
          cursor: "pointer", letterSpacing: 1,
        }}>✕ CLEAR</button>
      )}
      <span style={{ fontSize: 9, color: "#334155", marginLeft: "auto" }}>
        {filtered.length} of {entries.length} entries
      </span>
    </div>

    {/* Feed */}
    {loading ? (
      <div style={{ color: "#1e293b", fontSize: 11, letterSpacing: 2, padding: "40px 0", textAlign: "center" }}>
        ◌ LOADING INTELLIGENCE FEED...
      </div>
    ) : filtered.length === 0 ? (
      <div style={{ color: "#1e293b", fontSize: 11, letterSpacing: 1, padding: "40px 0" }}>
        {entries.length === 0 ? "NO ENTRIES YET — FETCHER MAY STILL BE RUNNING" : "NO ENTRIES MATCH FILTERS"}
      </div>
    ) : (
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {filtered.map(entry => {
          const badge = SOURCE_BADGE[entry.source] || { bg: "#1e293b", color: "#64748b" };
          return (
            <div key={entry.id} style={{
              background: "#090c15",
              border: "1px solid #141c2e",
              borderLeft: `3px solid ${CAT_COLORS[entry.category] || "#334155"}`,
              borderRadius: 3,
            }}>
              <div
                onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
                style={{
                  display: "grid",
                  gridTemplateColumns: "120px 1fr 110px 90px 24px",
                  gap: 10, padding: "11px 14px",
                  cursor: "pointer", alignItems: "center",
                }}
              >
                <div style={{ fontSize: 9, color: "#4b5563", letterSpacing: 0.3 }}>{fmt(entry.date)}</div>
                <div style={{ fontSize: 11, color: "#cbd5e1" }}>
                  {entry.headline}
                  {entry.location && entry.location !== "Unknown" && (
                    <span style={{ color: "#334155", fontSize: 9, marginLeft: 8 }}>⬡ {entry.location}</span>
                  )}
                </div>
                <div style={{
                  fontSize: 8, letterSpacing: 1,
                  color: CAT_COLORS[entry.category] || "#64748b",
                  background: `${CAT_COLORS[entry.category] || "#64748b"}15`,
                  padding: "2px 7px", borderRadius: 2, textAlign: "center", whiteSpace: "nowrap",
                }}>{(entry.category || "OTHER").toUpperCase()}</div>
                <div style={{
                  fontSize: 8, letterSpacing: 0.5, fontWeight: 700,
                  background: badge.bg, color: badge.color,
                  padding: "2px 7px", borderRadius: 2, textAlign: "center", whiteSpace: "nowrap",
                }}>{entry.source}</div>
                <div style={{ color: "#1e293b", fontSize: 9, textAlign: "center" }}>
                  {expandedId === entry.id ? "▲" : "▼"}
                </div>
              </div>

              {expandedId === entry.id && (
                <div style={{ borderTop: "1px solid #0f172a", padding: "12px 14px", background: "#060810" }}>
                  <div style={{ fontSize: 9, color: "#334155", letterSpacing: 1, marginBottom: 6 }}>SOURCE EXCERPT</div>
                  <div style={{
                    fontSize: 11, color: "#94a3b8", lineHeight: 1.7,
                    borderLeft: "2px solid #1e293b", paddingLeft: 12,
                    fontStyle: "italic",
                  }}>"{entry.excerpt}"</div>
                  <div style={{ marginTop: 10, fontSize: 9, color: "#1e293b", letterSpacing: 1 }}>
                    LOGGED: {fmt(entry.addedAt)}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    )}
  </div>

  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&display=swap');
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
    * { box-sizing: border-box; }
    ::-webkit-scrollbar { width: 3px; }
    ::-webkit-scrollbar-thumb { background: #1e293b; }
    select option { background: #0d1117; }
  `}</style>
</div>
```

);
}

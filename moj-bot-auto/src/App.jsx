import { useState, useRef, useEffect } from "react";

const CARS_PER_PAGE = 6;

const DAMAGE_COLORS = {
  none: { bg: "#dcfce7", text: "#15803d", label: "Bezwypadkowy" },
  hail: { bg: "#fef9c3", text: "#a16207", label: "Grad" },
  flood: { bg: "#dbeafe", text: "#1d4ed8", label: "Zalanie" },
  front_end: { bg: "#fee2e2", text: "#b91c1c", label: "Przód" },
  front_left: { bg: "#fee2e2", text: "#b91c1c", label: "Przód lewy" },
  front_right: { bg: "#fee2e2", text: "#b91c1c", label: "Przód prawy" },
  front_bumper: { bg: "#fee2e2", text: "#b91c1c", label: "Zderzak" },
  rear_end: { bg: "#ffe4e6", text: "#9f1239", label: "Tył" },
  rear_bumper: { bg: "#ffe4e6", text: "#9f1239", label: "Zderzak tył" },
  rear_dent: { bg: "#ffe4e6", text: "#9f1239", label: "Wgniecenie" },
  side_impact: { bg: "#fce7f3", text: "#9d174d", label: "Bok" },
  side_scrape: { bg: "#fce7f3", text: "#9d174d", label: "Zarysowanie" },
  side_mirror: { bg: "#f3e8ff", text: "#7e22ce", label: "Lusterko" },
  suspension: { bg: "#e0e7ff", text: "#4338ca", label: "Zawieszenie" },
  engine_issue: { bg: "#ffedd5", text: "#c2410c", label: "Silnik" },
  engine_failure: { bg: "#ffedd5", text: "#c2410c", label: "Awaria silnika" },
  engine_light: { bg: "#ffedd5", text: "#c2410c", label: "Kontrolka" },
  battery_issue: { bg: "#f0fdf4", text: "#166534", label: "Bateria" },
};

const COUNTRY_FLAGS = { USA: "🇺🇸", Germany: "🇩🇪", Canada: "🇨🇦", Japan: "🇯🇵" };

const SUGGESTIONS = [
  "BMW seria 5",
  "BMW 3 Series do 150 tysięcy",
  "Bezwypadkowe Tesla Model 3",
  "Ford Mustang najnowsze",
  "Audi Q5 z Niemiec",
  "Toyota RAV4 po 2020 od najtańszych",
  "Tesla Model Y z USA",
  "Pokaż 5 najtańszych BMW seria 5"
];

function DamageBadge({ value }) {
  const info = DAMAGE_COLORS[value?.toLowerCase()] || { bg: "#f1f5f9", text: "#64748b", label: value };
  return (
    <span style={{
      fontSize: 11, fontWeight: 700, padding: "3px 10px", borderRadius: 99,
      background: info.bg, color: info.text, whiteSpace: "nowrap"
    }}>
      {info.label}
    </span>
  );
}

function CarCard({ car, index }) {
  const flag = COUNTRY_FLAGS[car.kraj_pochodzenia] || "🌍";
  const price = car.cena_fmt || `${Number(car.cena).toLocaleString("pl-PL")} PLN`;
  const mileage = car.przebieg_fmt || `${Number(car.przebieg).toLocaleString("pl-PL")} km`;

  return (
    <div style={{
      background: "#fff",
      border: "2px solid #e2e8f0",
      borderRadius: 16,
      padding: "16px 18px",
      marginBottom: 10,
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      transition: "all 0.2s",
      animation: `slideIn 0.3s ease-out ${index * 0.05}s both`
    }}
      onMouseEnter={e => {
        e.currentTarget.style.boxShadow = "0 8px 20px rgba(0,0,0,0.12)";
        e.currentTarget.style.transform = "translateY(-2px)";
        e.currentTarget.style.borderColor = "#0f172a";
      }}
      onMouseLeave={e => {
        e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.05)";
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.borderColor = "#e2e8f0";
      }}
    >
      {/* Wiersz 1: Numer + Marka/Model + Badge */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8, background: "#0f172a",
            color: "white", display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 800, fontSize: 13, flexShrink: 0
          }}>
            {index + 1}
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, color: "#0f172a", lineHeight: 1.3 }}>
              {car.marka} {car.model}
            </div>
            <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 3 }}>
              {car.rocznik} • {mileage}
            </div>
          </div>
        </div>
        <DamageBadge value={car.uszkodzenie} />
      </div>

      {/* Wiersz 2: Kraj + Cena */}
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        paddingTop: 12, borderTop: "1px solid #f1f5f9"
      }}>
        <div style={{ fontSize: 13, color: "#64748b", fontWeight: 500 }}>
          {flag} {car.kraj_pochodzenia}
        </div>
        <div style={{ fontSize: 18, fontWeight: 900, color: "#0f172a", letterSpacing: "-0.02em" }}>
          {price}
        </div>
      </div>

      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

function TypingDots() {
  return (
    <div style={{ display: "flex", gap: 4, padding: "14px 18px", background: "white", borderRadius: 14, border: "2px solid #e2e8f0", width: "fit-content", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 8, height: 8, borderRadius: "50%", background: "#94a3b8",
          animation: "bounce 1.2s infinite",
          animationDelay: `${i * 0.2}s`
        }} />
      ))}
      <style>{`@keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-8px)} }`}</style>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([{
    role: "assistant",
    content: "Cześć! 👋 Jestem asystentem AutoImport Pro. Pytaj o konkretne modele (np. 'BMW seria 5', 'Tesla Model 3', 'Ford Mustang') lub kryteria wyszukiwania.",
    cars: [],
    currentPage: 0
  }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text) {
    const userText = (text || input).trim();
    if (!userText || loading) return;
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userText }]);
    setLoading(true);

    try {
      const res = await fetch(
  `http://192.168.1.107:8001/chat?query=${encodeURIComponent(userText)}`
);
      const data = await res.json();
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.text || "Oto wyniki:",
        cars: Array.isArray(data.cars) ? data.cars : [],
        currentPage: 0,
        count: data.count ?? 0,
        sorted_by: data.sorted_by,
        filters_applied: data.filters_applied
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "❌ Nie mogę połączyć się z serwerem. Upewnij się, że backend działa (python main.py).",
        cars: [], currentPage: 0
      }]);
    }
    setLoading(false);
  }

  const changePage = (msgIndex, direction) => {
    setMessages(prev => {
      const newMsgs = [...prev];
      const msg = { ...newMsgs[msgIndex] };
      const maxPages = Math.ceil(msg.cars.length / CARS_PER_PAGE);
      if (direction === "next" && msg.currentPage < maxPages - 1) msg.currentPage += 1;
      if (direction === "prev" && msg.currentPage > 0) msg.currentPage -= 1;
      newMsgs[msgIndex] = msg;
      return newMsgs;
    });
  };

  const showSuggestions = messages.length <= 1;

  return (
    <div style={{
      display: "flex", flexDirection: "column", height: "100vh",
      background: "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
      fontFamily: "'Inter', -apple-system, sans-serif"
    }}>

      {/* Header */}
      <div style={{
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        color: "white",
        padding: "18px 28px",
        display: "flex", alignItems: "center", gap: 14,
        boxShadow: "0 4px 12px rgba(0,0,0,0.3)"
      }}>
        <div style={{ fontSize: 26 }}>🚗</div>
        <div>
          <div style={{ fontWeight: 800, fontSize: 18, letterSpacing: "-0.02em" }}>AutoImport Pro</div>
          <div style={{ fontSize: 11, color: "#94a3b8", fontWeight: 500 }}>Inteligentny asystent wyszukiwania</div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 7, fontSize: 12, color: "#4ade80", fontWeight: 600 }}>
          <div style={{
            width: 8, height: 8, borderRadius: "50%", background: "#4ade80",
            boxShadow: "0 0 8px #4ade80", animation: "pulse 2s infinite"
          }} />
          Online
          <style>{`@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}`}</style>
        </div>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, overflowY: "auto", padding: "28px 20px" }}>
        <div style={{ maxWidth: 800, margin: "0 auto", display: "flex", flexDirection: "column", gap: 20 }}>

          {messages.map((msg, i) => {
            const cars = msg.cars || [];
            const totalPages = Math.ceil(cars.length / CARS_PER_PAGE);
            const current = msg.currentPage || 0;
            const visibleCars = cars.slice(current * CARS_PER_PAGE, (current + 1) * CARS_PER_PAGE);
            const isUser = msg.role === "user";
            const globalStartIndex = current * CARS_PER_PAGE;

            return (
              <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: isUser ? "flex-end" : "flex-start" }}>

                {/* Bubble */}
                <div style={{
                  background: isUser ? "#0f172a" : "white",
                  color: isUser ? "white" : "#0f172a",
                  padding: "14px 18px",
                  borderRadius: isUser ? "20px 20px 4px 20px" : "20px 20px 20px 4px",
                  maxWidth: "85%",
                  fontSize: 14,
                  lineHeight: 1.6,
                  border: isUser ? "none" : "2px solid #e2e8f0",
                  boxShadow: isUser ? "0 2px 8px rgba(15,23,42,0.2)" : "0 1px 4px rgba(0,0,0,0.06)",
                  fontWeight: isUser ? 500 : 400
                }}>
                  {msg.content}
                </div>

                {/* Debug info (tylko dla dev) */}
                {msg.filters_applied && Object.keys(msg.filters_applied).length > 0 && (
                  <div style={{
                    fontSize: 10, color: "#94a3b8", marginTop: 6, padding: "4px 10px",
                    background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0"
                  }}>
                    🔍 Filtry: {JSON.stringify(msg.filters_applied)}
                  </div>
                )}

                {/* Wyniki */}
                {visibleCars.length > 0 && (
                  <div style={{ marginTop: 14, width: "100%", maxWidth: "95%" }}>
                    <div style={{
                      fontSize: 11, color: "#64748b", fontWeight: 700, letterSpacing: 1.2,
                      marginBottom: 10, display: "flex", justifyContent: "space-between", alignItems: "center"
                    }}>
                      <span>
                        WYNIKI · {cars.length} {cars.length === 1 ? "auto" : "aut"}
                        {msg.sorted_by && ` · Sortowane wg ${msg.sorted_by}`}
                      </span>
                      {totalPages > 1 && <span style={{ fontWeight: 600 }}>Strona {current + 1} / {totalPages}</span>}
                    </div>

                    {visibleCars.map((car, idx) => (
                      <CarCard key={idx} car={car} index={globalStartIndex + idx} />
                    ))}

                    {totalPages > 1 && (
                      <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
                        <button
                          onClick={() => changePage(i, "prev")}
                          disabled={current === 0}
                          style={{
                            flex: 1, padding: "10px", cursor: current === 0 ? "not-allowed" : "pointer",
                            border: "2px solid #e2e8f0", borderRadius: 10,
                            background: current === 0 ? "#f8fafc" : "white",
                            color: current === 0 ? "#cbd5e1" : "#0f172a",
                            fontWeight: 700, fontSize: 13, transition: "all 0.15s"
                          }}
                          onMouseEnter={e => current > 0 && (e.target.style.background = "#f1f5f9")}
                          onMouseLeave={e => current > 0 && (e.target.style.background = "white")}
                        >
                          ← Poprzednie
                        </button>
                        <button
                          onClick={() => changePage(i, "next")}
                          disabled={current === totalPages - 1}
                          style={{
                            flex: 1, padding: "10px",
                            cursor: current === totalPages - 1 ? "not-allowed" : "pointer",
                            border: "2px solid " + (current === totalPages - 1 ? "#e2e8f0" : "#0f172a"),
                            borderRadius: 10,
                            background: current === totalPages - 1 ? "#f8fafc" : "#0f172a",
                            color: current === totalPages - 1 ? "#cbd5e1" : "white",
                            fontWeight: 700, fontSize: 13, transition: "all 0.15s"
                          }}
                          onMouseEnter={e => current < totalPages - 1 && (e.target.style.background = "#1e293b")}
                          onMouseLeave={e => current < totalPages - 1 && (e.target.style.background = "#0f172a")}
                        >
                          Następne →
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {loading && <TypingDots />}

          {showSuggestions && !loading && (
            <div style={{ marginTop: 10 }}>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 10, fontWeight: 700, letterSpacing: 0.8 }}>
                💡 PRZYKŁADY (konkretne modele!)
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {SUGGESTIONS.map((s, idx) => (
                  <button key={idx} onClick={() => sendMessage(s)} style={{
                    padding: "8px 16px", borderRadius: 24, border: "2px solid #e2e8f0",
                    background: "white", cursor: "pointer", fontSize: 13, color: "#475569",
                    transition: "all 0.2s", fontWeight: 500
                  }}
                    onMouseEnter={e => {
                      e.target.style.background = "#0f172a";
                      e.target.style.color = "white";
                      e.target.style.borderColor = "#0f172a";
                      e.target.style.transform = "translateY(-2px)";
                    }}
                    onMouseLeave={e => {
                      e.target.style.background = "white";
                      e.target.style.color = "#475569";
                      e.target.style.borderColor = "#e2e8f0";
                      e.target.style.transform = "translateY(0)";
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <div style={{
        background: "white",
        padding: "18px 20px",
        borderTop: "2px solid #e2e8f0",
        boxShadow: "0 -4px 12px rgba(0,0,0,0.05)"
      }}>
        <div style={{ maxWidth: 800, margin: "0 auto", display: "flex", gap: 12 }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendMessage()}
            placeholder="Np. 'BMW seria 5 do 200k z USA' lub 'Tesla Model 3 bezwypadkowe najnowsze'"
            disabled={loading}
            style={{
              flex: 1, padding: "14px 20px", borderRadius: 28,
              border: "2px solid #e2e8f0", fontSize: 14, outline: "none",
              background: loading ? "#f8fafc" : "white",
              boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
              transition: "all 0.2s",
              color: "black"
            }}
            onFocus={e => e.target.style.borderColor = "#0f172a"}
            onBlur={e => e.target.style.borderColor = "#e2e8f0"}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            style={{
              padding: "14px 28px", borderRadius: 28,
              background: loading || !input.trim() ? "#e2e8f0" : "#0f172a",
              color: loading || !input.trim() ? "#94a3b8" : "white",
              border: "none", cursor: loading || !input.trim() ? "not-allowed" : "pointer",
              fontWeight: 700, fontSize: 14, transition: "all 0.15s",
              boxShadow: loading || !input.trim() ? "none" : "0 2px 8px rgba(15,23,42,0.2)"
            }}
            onMouseEnter={e => !loading && input.trim() && (e.target.style.background = "#1e293b")}
            onMouseLeave={e => !loading && input.trim() && (e.target.style.background = "#0f172a")}
          >
            {loading ? "..." : "🔍 Szukaj"}
          </button>
        </div>
      </div>
    </div>
  );
}

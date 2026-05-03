// Variation 3 (v2): Full-bleed Product Preview — NBU brand colors
// Primary #003D7C, secondaries #0054A6 / #7FB5E6 / #93C5FD,
// Accents #059669 (emerald), #F59E0B (amber), #DC2626 (red).
// Right panel: richer dashboard with region map, KPI tiles, live AI feed.

const NBU = {
  primary: "#003D7C",
  primaryDeep: "#002855",
  primary2: "#0054A6",
  primary3: "#2563EB",
  skyLight: "#7FB5E6",
  skyFaint: "#93C5FD",
  emerald: "#059669",
  emeraldLight: "#10B981",
  amber: "#F59E0B",
  amberDeep: "#D97706",
  red: "#DC2626",
  bg: "#F5F8FC",
  card: "#FFFFFF",
  ink: "#0F1A2B",
  inkSoft: "#334155",
  muted: "#64748B",
  outline: "rgba(0,61,124,0.12)",
  fixed: "#E6EEF8",
};

// Tiny SVG silhouette of Uzbekistan regions (abstracted blobs, original).
function MiniMap({ highlight = "fergana" }) {
  const regions = [
    { k: "karakalpak", d: "M12,60 C18,40 35,28 55,30 C70,32 78,48 72,62 C66,78 48,88 28,82 C18,80 8,72 12,60Z", cx: 42, cy: 56 },
    { k: "khorezm",    d: "M60,48 C70,42 82,44 86,54 C88,62 82,70 72,68 C64,66 56,58 60,48Z", cx: 73, cy: 56 },
    { k: "navoi",      d: "M88,58 C104,50 130,54 138,68 C142,80 128,90 110,86 C94,82 82,72 88,58Z", cx: 113, cy: 70 },
    { k: "bukhara",    d: "M90,82 C102,78 120,82 124,92 C126,100 116,108 102,104 C90,100 84,90 90,82Z", cx: 106, cy: 92 },
    { k: "samarkand",  d: "M140,80 C152,74 168,78 170,88 C172,98 160,106 148,102 C138,98 132,88 140,80Z", cx: 154, cy: 90 },
    { k: "kashkadarya",d: "M158,104 C172,100 188,104 190,116 C192,126 178,132 164,128 C152,124 146,110 158,104Z", cx: 174, cy: 116 },
    { k: "surkhandarya",d:"M180,132 C192,128 206,134 208,144 C208,154 196,158 184,154 C176,150 170,138 180,132Z", cx: 194, cy: 144 },
    { k: "jizzakh",    d: "M172,70 C184,66 196,70 196,80 C196,88 186,92 176,88 C168,86 162,76 172,70Z", cx: 184, cy: 79 },
    { k: "syrdarya",   d: "M196,66 C206,62 216,64 218,72 C218,80 208,84 200,80 C192,78 188,70 196,66Z", cx: 207, cy: 72 },
    { k: "tashkent",   d: "M204,50 C218,46 236,52 238,64 C238,74 224,80 212,76 C200,72 192,58 204,50Z", cx: 221, cy: 62 },
    { k: "namangan",   d: "M238,56 C250,52 264,58 264,66 C264,74 252,78 242,76 C234,74 230,62 238,56Z", cx: 251, cy: 66 },
    { k: "andijan",    d: "M262,68 C272,66 280,70 280,78 C278,86 268,88 260,84 C254,80 254,72 262,68Z", cx: 270, cy: 77 },
    { k: "fergana",    d: "M254,82 C266,78 280,82 282,92 C282,100 270,104 260,100 C250,96 244,86 254,82Z", cx: 268, cy: 91 },
  ];
  return (
    <svg viewBox="0 0 292 170" style={{ width: "100%", height: "auto", display: "block" }} aria-hidden>
      {regions.map(r => {
        const active = r.k === highlight;
        return (
          <g key={r.k}>
            <path d={r.d}
              fill={active ? NBU.skyFaint : "rgba(255,255,255,0.08)"}
              stroke={active ? "#fff" : "rgba(255,255,255,0.25)"}
              strokeWidth={active ? 1.2 : 0.7}
            />
            {active && (
              <>
                <circle cx={r.cx} cy={r.cy} r="3.5" fill="#fff" />
                <circle cx={r.cx} cy={r.cy} r="8" fill="none" stroke="#fff" strokeWidth="1" opacity="0.6">
                  <animate attributeName="r" values="4;12;4" dur="2.4s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.8;0;0.8" dur="2.4s" repeatCount="indefinite" />
                </circle>
              </>
            )}
          </g>
        );
      })}
    </svg>
  );
}

function V3Product() {
  const { lang, setLang, t } = useLang();
  const f = useAuthForm();
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick(x => x + 1), 3000);
    return () => clearInterval(id);
  }, []);

  const aiFeed = [
    { t: "AI СОВЕТНИК", m: "Рост МСБ в Фергане +18% за квартал", c: NBU.emerald },
    { t: "АНАЛИТИКА", m: "Экспорт текстиля Намангана превысил план на 4.2%", c: NBU.primary2 },
    { t: "РЕКОМЕНДАЦИЯ", m: "Кредитная ёмкость региона Сурхандарья +12%", c: NBU.amber },
    { t: "AI СОВЕТНИК", m: "Предупреждение: отток рабочей силы в Хорезме", c: NBU.red },
  ];
  const aiNow = aiFeed[tick % aiFeed.length];

  return (
    <div style={{
      minHeight: "100vh",
      background: NBU.bg,
      color: NBU.ink,
      display: "grid",
      gridTemplateColumns: "minmax(480px, 1fr) minmax(540px, 1.15fr)",
      fontFamily: "Manrope, Inter, sans-serif",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* LEFT */}
      <div style={{
        padding: "40px 56px",
        display: "flex", flexDirection: "column",
        justifyContent: "space-between",
        position: "relative", zIndex: 2,
      }}>
        <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{
              width: 34, height: 34, borderRadius: 9,
              background: NBU.primary,
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#fff", fontWeight: 800, fontSize: 15, letterSpacing: -0.3,
              boxShadow: `0 6px 20px -6px ${NBU.primary}66`,
            }}>N</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 15, letterSpacing: -0.2, color: NBU.primary }}>NBU AI Platform</div>
              <div style={{ fontSize: 10.5, letterSpacing: 1.4, textTransform: "uppercase",
                color: NBU.muted, fontFamily: "'JetBrains Mono', monospace" }}>
                National Bank · Tashkent
              </div>
            </div>
          </div>
          <LangPill lang={lang} setLang={setLang} />
        </header>

        <div style={{ maxWidth: 520, width: "100%", position: "relative" }}>
          {f.success && <SuccessOverlay t={t} />}

          <h1 style={{
            fontSize: 54, lineHeight: 1.02, letterSpacing: -1.8,
            margin: 0, fontWeight: 800, color: NBU.ink,
          }}>
            Войдите в<br/>
            <span style={{ color: NBU.primary }}>интеллект</span><br/>
            вашего бизнеса.
          </h1>
          <p style={{ fontSize: 15, color: NBU.inkSoft, marginTop: 18, maxWidth: 460, lineHeight: 1.55 }}>
            Региональная аналитика, AI-советник и инструменты финансового планирования — в одной защищённой платформе Национального Банка.
          </p>

          {/* tabs */}
          <div style={{
            display: "inline-flex", marginTop: 32, marginBottom: 20,
            background: NBU.fixed, borderRadius: 10, padding: 4,
          }}>
            {[["signin", t("signin")], ["signup", t("signup")]].map(([k, label]) => (
              <button key={k} onClick={() => f.setMode(k)}
                style={{
                  padding: "9px 20px",
                  borderRadius: 7, border: "none",
                  background: f.mode === k ? NBU.primary : "transparent",
                  color: f.mode === k ? "#fff" : NBU.primary,
                  fontSize: 13, fontWeight: 700,
                  cursor: "pointer",
                  boxShadow: f.mode === k ? `0 6px 16px -6px ${NBU.primary}66` : "none",
                  transition: "all .18s",
                }}>{label}</button>
            ))}
          </div>

          {f.mode === "signup" && (
            <div style={{ marginBottom: 18, animation: "slideUp .3s" }}>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.8,
                color: NBU.muted, marginBottom: 10, fontWeight: 700 }}>{t("roleTitle")}</div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {[["sme", t("role_sme")], ["corp", t("role_corp")], ["individual", t("role_individual")]].map(([k, label]) => (
                  <button key={k} onClick={() => f.setRole(k)}
                    style={{
                      padding: "8px 14px", borderRadius: 999,
                      border: `1px solid ${f.role === k ? NBU.primary : NBU.outline}`,
                      background: f.role === k ? NBU.primary : "transparent",
                      color: f.role === k ? "#fff" : NBU.primary,
                      fontSize: 13, fontWeight: 600, cursor: "pointer", transition: "all .15s",
                    }}>{label}</button>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 14, maxWidth: 460 }}>
            <NbuField label={t("email")} value={f.email} onChange={f.setEmail} type="email" placeholder={t("emailPh")} />
            <NbuPassword value={f.password} onChange={f.setPassword} t={t} />
          </div>

          {f.error && (
            <div style={{ marginTop: 10, fontSize: 12, color: NBU.red, fontWeight: 600,
              display: "flex", alignItems: "center", gap: 6 }}>
              <span>▲</span>{f.error === "email" ? "Проверьте email" : "Пароль слишком короткий"}
            </div>
          )}

          {f.mode === "signin" && (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between",
              marginTop: 16, marginBottom: 22, maxWidth: 460 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: NBU.inkSoft, cursor: "pointer" }}>
                <input type="checkbox" checked={f.remember} onChange={(e) => f.setRemember(e.target.checked)}
                  style={{ width: 15, height: 15, accentColor: NBU.primary }} />
                {t("remember")}
              </label>
              <a href="#" onClick={(e) => e.preventDefault()} style={{ fontSize: 13, color: NBU.primary, fontWeight: 600 }}>{t("forgot")}</a>
            </div>
          )}
          {f.mode === "signup" && <div style={{ height: 22 }} />}

          <div style={{ maxWidth: 460 }}>
            <NbuSubmit onClick={f.submit} loading={f.loading}>
              {f.mode === "signin" ? t("submit") : t("submitRegister")}
            </NbuSubmit>

            <div style={{ marginTop: 16, fontSize: 13, color: NBU.muted }}>
              {f.mode === "signin" ? t("noAccount") : t("haveAccount")}{" "}
              <button onClick={() => f.setMode(f.mode === "signin" ? "signup" : "signin")}
                style={{ background: "transparent", border: "none", color: NBU.primary, cursor: "pointer",
                  fontWeight: 700, padding: 0, fontSize: 13 }}>
                {f.mode === "signin" ? t("signupCta") : t("signinCta")} →
              </button>
            </div>
          </div>
        </div>

        <div style={{
          fontSize: 11, letterSpacing: 0.4, color: NBU.muted,
          display: "flex", alignItems: "center", gap: 16,
        }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 6, height: 6, borderRadius: 999, background: NBU.emerald }} />
            {t("statusOk")}
          </span>
          <span>·</span>
          <span>{t("legal")}</span>
          <span>·</span>
          <span>{t("copyright")}</span>
        </div>
      </div>

      {/* RIGHT: rich dashboard */}
      <div style={{
        position: "relative", overflow: "hidden",
        background: `linear-gradient(155deg, ${NBU.primaryDeep} 0%, ${NBU.primary} 55%, ${NBU.primary2} 100%)`,
        padding: 48,
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        {/* subtle grid */}
        <div aria-hidden style={{
          position: "absolute", inset: 0,
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)
          `,
          backgroundSize: "36px 36px",
          maskImage: "radial-gradient(ellipse 80% 70% at 55% 40%, #000 50%, transparent 90%)",
        }} />

        {/* glowing orbs */}
        <div aria-hidden style={{
          position: "absolute", top: -140, right: -140,
          width: 460, height: 460, borderRadius: 999,
          background: `radial-gradient(circle, ${NBU.skyFaint}55, transparent 70%)`,
          filter: "blur(30px)", animation: "floaty 7s ease-in-out infinite",
        }} />
        <div aria-hidden style={{
          position: "absolute", bottom: -180, left: -80,
          width: 380, height: 380, borderRadius: 999,
          background: `radial-gradient(circle, ${NBU.primary2}66, transparent 70%)`,
          filter: "blur(30px)",
        }} />

        <div style={{
          position: "relative", zIndex: 2,
          width: "100%", maxWidth: 600,
          transform: "perspective(1400px) rotateY(-7deg) rotateX(3deg)",
          transformOrigin: "center center",
          display: "flex", flexDirection: "column", gap: 16,
        }}>
          {/* Main dashboard card */}
          <div style={{
            background: "rgba(255,255,255,0.08)",
            border: "1px solid rgba(255,255,255,0.18)",
            borderRadius: 18,
            padding: 22,
            backdropFilter: "blur(16px)",
            boxShadow: "0 50px 100px -40px rgba(0,0,0,0.6)",
            color: "#fff",
          }}>
            {/* window chrome */}
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 16 }}>
              <div style={{ width: 8, height: 8, borderRadius: 999, background: "rgba(255,255,255,0.25)" }} />
              <div style={{ width: 8, height: 8, borderRadius: 999, background: "rgba(255,255,255,0.25)" }} />
              <div style={{ width: 8, height: 8, borderRadius: 999, background: "rgba(255,255,255,0.25)" }} />
              <div style={{
                marginLeft: 10, flex: 1,
                fontSize: 10.5, color: "rgba(255,255,255,0.55)",
                fontFamily: "'JetBrains Mono', monospace", letterSpacing: 0.4,
              }}>
                platform.nbu.uz/dashboard
              </div>
              <div style={{
                fontSize: 10, color: NBU.skyFaint,
                fontFamily: "'JetBrains Mono', monospace", letterSpacing: 0.8,
                display: "flex", alignItems: "center", gap: 6,
              }}>
                <span style={{ width: 5, height: 5, borderRadius: 999, background: NBU.emeraldLight,
                  boxShadow: `0 0 8px ${NBU.emeraldLight}` }} />
                LIVE
              </div>
            </div>

            {/* header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <div style={{ fontSize: 10, letterSpacing: 1.6, textTransform: "uppercase",
                  color: NBU.skyFaint, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>
                  АНАЛИТИКА РЕГИОНОВ
                </div>
                <div style={{ fontSize: 20, fontWeight: 800, marginTop: 4, letterSpacing: -0.4 }}>
                  Ферганская область
                </div>
                <div style={{ fontSize: 11.5, color: "rgba(255,255,255,0.65)", marginTop: 3, fontWeight: 500 }}>
                  Q2 · 2026 · 15 районов
                </div>
              </div>
              <div style={{
                padding: "5px 10px", borderRadius: 6,
                background: "rgba(16,185,129,0.18)", border: "1px solid rgba(16,185,129,0.4)",
                fontSize: 11, fontWeight: 700, color: "#A7F3D0",
                fontFamily: "'JetBrains Mono', monospace",
              }}>+18.2% YoY</div>
            </div>

            {/* mini map + sidecar */}
            <div style={{
              display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 14,
              padding: "14px 0",
              borderTop: "1px solid rgba(255,255,255,0.12)",
              borderBottom: "1px solid rgba(255,255,255,0.12)",
              marginBottom: 14,
            }}>
              <div style={{
                background: "rgba(0,0,0,0.18)", borderRadius: 10, padding: 10,
                display: "flex", flexDirection: "column", justifyContent: "space-between",
              }}>
                <MiniMap highlight="fergana" />
                <div style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  fontSize: 10, fontFamily: "'JetBrains Mono', monospace",
                  color: "rgba(255,255,255,0.55)", letterSpacing: 0.4, marginTop: 4,
                }}>
                  <span>14 регионов</span>
                  <span>· 199 районов</span>
                </div>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {[
                  { l: "ВРП района", v: "14,240", u: "млрд сум", c: "#fff" },
                  { l: "Инвестиции", v: "2,820", u: "млрд сум", c: "#A7F3D0" },
                  { l: "Активных МСБ", v: "12,840", u: "+342 мес.", c: NBU.skyFaint },
                ].map((s, i) => (
                  <div key={i} style={{
                    padding: "9px 11px", background: "rgba(255,255,255,0.06)",
                    border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8,
                  }}>
                    <div style={{ fontSize: 9.5, color: "rgba(255,255,255,0.55)",
                      fontFamily: "'JetBrains Mono', monospace",
                      textTransform: "uppercase", letterSpacing: 0.8, fontWeight: 600 }}>{s.l}</div>
                    <div style={{ fontSize: 17, fontWeight: 800, marginTop: 1, letterSpacing: -0.3, color: s.c }}>{s.v}</div>
                    <div style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", marginTop: 1 }}>{s.u}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bar chart */}
            <div style={{ marginBottom: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: 0.4, textTransform: "uppercase", color: "rgba(255,255,255,0.7)" }}>
                  ВРП по кварталам
                </div>
                <div style={{ display: "flex", gap: 10, fontSize: 10, color: "rgba(255,255,255,0.6)",
                  fontFamily: "'JetBrains Mono', monospace" }}>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 2, background: NBU.skyFaint }} />2024
                  </span>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 2,
                      background: `linear-gradient(to top, ${NBU.emerald}, ${NBU.emeraldLight})` }} />2025
                  </span>
                </div>
              </div>
              <div style={{
                height: 110, display: "flex", alignItems: "flex-end", gap: 6,
                padding: "4px 0",
              }}>
                {Array.from({ length: 16 }).map((_, i) => {
                  const base = 30 + Math.abs(Math.sin(i * 0.55) * 55) + (i % 4) * 4;
                  const accent = i >= 12;
                  return (
                    <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", gap: 2, alignItems: "stretch" }}>
                      <div style={{
                        height: `${Math.min(base, 90)}px`,
                        background: accent
                          ? `linear-gradient(to top, ${NBU.emerald}, ${NBU.emeraldLight})`
                          : `linear-gradient(to top, ${NBU.skyLight}88, ${NBU.skyFaint})`,
                        borderRadius: 3,
                        boxShadow: accent ? `0 0 14px ${NBU.emeraldLight}55` : "none",
                        transition: "all .3s",
                      }} />
                    </div>
                  );
                })}
              </div>
              <div style={{ display: "flex", justifyContent: "space-between",
                fontSize: 9.5, color: "rgba(255,255,255,0.4)", marginTop: 4,
                fontFamily: "'JetBrains Mono', monospace" }}>
                <span>Q1</span><span>Q2</span><span>Q3</span><span>Q4</span>
              </div>
            </div>

            {/* AI rotating feed */}
            <div key={tick} style={{
              padding: "13px 14px",
              background: `linear-gradient(135deg, ${aiNow.c}33, rgba(255,255,255,0.05))`,
              border: `1px solid ${aiNow.c}55`,
              borderRadius: 10,
              display: "flex", alignItems: "center", gap: 12,
              animation: "fade .4s ease",
            }}>
              <div style={{
                width: 30, height: 30, borderRadius: 8,
                background: aiNow.c,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 15, color: "#fff", fontWeight: 800,
                boxShadow: `0 0 14px ${aiNow.c}88`,
              }}>✦</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 10, color: aiNow.c, fontFamily: "'JetBrains Mono', monospace",
                  letterSpacing: 1, fontWeight: 700 }}>{aiNow.t}</div>
                <div style={{ fontSize: 13, marginTop: 2, fontWeight: 500, color: "rgba(255,255,255,0.95)" }}>{aiNow.m}</div>
              </div>
              <div style={{ display: "flex", gap: 3 }}>
                {aiFeed.map((_, i) => (
                  <div key={i} style={{
                    width: 4, height: 4, borderRadius: 999,
                    background: i === tick % aiFeed.length ? "#fff" : "rgba(255,255,255,0.25)",
                  }} />
                ))}
              </div>
            </div>
          </div>

          {/* secondary row: tool tiles */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
            {[
              { n: "Аналитика", d: "14 регионов", c: NBU.skyFaint, i: "▦" },
              { n: "Советник", d: "AI · GPT", c: NBU.emeraldLight, i: "✦" },
              { n: "Обучение", d: "Курсы МСБ", c: "#FBBF24", i: "◐" },
              { n: "Финконтроль", d: "Потоки", c: "#A78BFA", i: "⬡" },
            ].map((x, i) => (
              <div key={i} style={{
                padding: 12,
                background: "rgba(255,255,255,0.07)",
                border: "1px solid rgba(255,255,255,0.13)",
                borderRadius: 10,
                backdropFilter: "blur(12px)",
                color: "#fff",
              }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                  <div style={{
                    width: 22, height: 22, borderRadius: 6,
                    background: `${x.c}33`, color: x.c,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 12, fontWeight: 700,
                  }}>{x.i}</div>
                  <div style={{ width: 5, height: 5, borderRadius: 999, background: x.c, boxShadow: `0 0 6px ${x.c}` }} />
                </div>
                <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: -0.1 }}>{x.n}</div>
                <div style={{ fontSize: 9.5, color: "rgba(255,255,255,0.55)",
                  fontFamily: "'JetBrains Mono', monospace", marginTop: 2, letterSpacing: 0.3 }}>{x.d}</div>
              </div>
            ))}
          </div>
        </div>

        {/* floating live badge */}
        <div style={{
          position: "absolute", bottom: 28, left: 28, zIndex: 3,
          padding: "10px 14px",
          background: "#fff", color: NBU.primary,
          borderRadius: 10,
          fontSize: 12, fontWeight: 700,
          boxShadow: "0 20px 50px -15px rgba(0,0,0,0.5)",
          display: "flex", alignItems: "center", gap: 10,
          transform: "rotate(-2deg)",
        }}>
          <div style={{
            width: 26, height: 26, borderRadius: 7, background: NBU.emerald,
            color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 800,
          }}>↑</div>
          <div>
            <div style={{ fontSize: 9, letterSpacing: 1, textTransform: "uppercase", color: NBU.muted, fontWeight: 700 }}>Доход платформы</div>
            <div style={{ fontSize: 14, letterSpacing: -0.3 }}>₽4.2B · +12.4%</div>
          </div>
        </div>

        {/* floating nodes badge top */}
        <div style={{
          position: "absolute", top: 32, right: 32, zIndex: 3,
          padding: "8px 12px",
          background: "rgba(255,255,255,0.1)",
          border: "1px solid rgba(255,255,255,0.2)",
          backdropFilter: "blur(12px)",
          borderRadius: 999,
          fontSize: 11, fontWeight: 600, color: "#fff",
          display: "flex", alignItems: "center", gap: 8,
          fontFamily: "'JetBrains Mono', monospace", letterSpacing: 0.4,
        }}>
          <span style={{ width: 6, height: 6, borderRadius: 999, background: NBU.emeraldLight,
            boxShadow: `0 0 8px ${NBU.emeraldLight}`, animation: "pulse 2s infinite" }} />
          3 узла · Tashkent · Fergana · Samarkand
        </div>
      </div>
    </div>
  );
}

// ---- NBU-themed field components (override shared look) ----
function NbuField({ label, value, onChange, type = "text", placeholder, right }) {
  const [focus, setFocus] = useState(false);
  return (
    <label style={{ display: "block" }}>
      <span style={{
        display: "block", fontSize: 11, letterSpacing: 0.6,
        textTransform: "uppercase", color: NBU.muted, marginBottom: 6, fontWeight: 700,
      }}>{label}</span>
      <div style={{
        position: "relative", display: "flex", alignItems: "center",
        background: "#fff",
        border: `1.5px solid ${focus ? NBU.primary : NBU.outline}`,
        borderRadius: 10,
        transition: "all .18s",
        boxShadow: focus ? `0 0 0 4px ${NBU.primary}18` : "none",
      }}>
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          placeholder={placeholder}
          style={{
            flex: 1, background: "transparent", border: "none",
            padding: "13px 16px", fontSize: 15, color: NBU.ink,
          }}
        />
        {right}
      </div>
    </label>
  );
}

function NbuPassword({ value, onChange, t }) {
  const [show, setShow] = useState(false);
  return (
    <NbuField
      label={t("password")}
      value={value}
      onChange={onChange}
      type={show ? "text" : "password"}
      placeholder={t("passwordPh")}
      right={
        <button type="button" onClick={() => setShow(s => !s)} style={{
          background: "transparent", border: "none",
          marginRight: 8, padding: "6px 10px", borderRadius: 6,
          fontSize: 12, color: NBU.muted, fontWeight: 600, cursor: "pointer",
        }}>{show ? t("passwordHide") : t("passwordShow")}</button>
      }
    />
  );
}

function NbuSubmit({ children, onClick, loading, disabled }) {
  return (
    <button type="button" onClick={onClick} disabled={disabled || loading}
      style={{
        width: "100%", padding: "15px 20px", borderRadius: 10, border: "none",
        background: `linear-gradient(135deg, ${NBU.primary}, ${NBU.primary2})`,
        color: "#fff", fontSize: 14, fontWeight: 700, letterSpacing: 0.2,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.4 : 1,
        display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
        boxShadow: `0 10px 28px -10px ${NBU.primary}88`,
        transition: "transform .1s, box-shadow .18s",
      }}
      onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.99)")}
      onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
    >
      {loading ? <Spinner variant="dark" /> : children}
      {!loading && <span style={{ opacity: 0.7 }}>→</span>}
    </button>
  );
}

window.V3Product = V3Product;

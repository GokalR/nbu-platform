// V5: Command Center — dark left, bright data right
// Flips V3: form sits on dark NBU navy (left), dashboard on light (right).

function V5Command() {
  const { lang, setLang, t } = useLang();
  const f = useAuthForm();
  const [live, setLive] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setLive(x => x + 1), 2200);
    return () => clearInterval(id);
  }, []);

  const C = {
    primary: "#003D7C", primaryDeep: "#001935", primary2: "#0054A6",
    sky: "#7FB5E6", skyFaint: "#93C5FD",
    emerald: "#059669", emeraldLight: "#10B981",
    amber: "#F59E0B", red: "#DC2626",
    ink: "#0F1A2B", inkSoft: "#334155", muted: "#64748B",
  };

  return (
    <div style={{
      minHeight: "100vh", display: "grid",
      gridTemplateColumns: "minmax(460px, 0.95fr) minmax(540px, 1.2fr)",
      fontFamily: "Manrope, Inter, sans-serif",
    }}>
      {/* LEFT: dark form */}
      <div className="dark-placeholder" style={{
        background: `linear-gradient(175deg, ${C.primaryDeep} 0%, ${C.primary} 100%)`,
        color: "#fff", padding: "40px 48px",
        display: "flex", flexDirection: "column", justifyContent: "space-between",
        position: "relative", overflow: "hidden",
      }}>
        <div aria-hidden style={{
          position: "absolute", inset: 0,
          backgroundImage: "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
          maskImage: "radial-gradient(ellipse 80% 70% at 50% 50%, #000 40%, transparent 85%)",
        }} />
        <div aria-hidden style={{
          position: "absolute", top: -120, right: -120, width: 380, height: 380, borderRadius: 999,
          background: `radial-gradient(circle, ${C.skyFaint}44, transparent 70%)`, filter: "blur(30px)",
        }} />

        <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", position: "relative", zIndex: 2 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{
              width: 34, height: 34, borderRadius: 9,
              background: "#fff", color: C.primary,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontWeight: 800, fontSize: 15,
            }}>N</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 15 }}>NBU AI Platform</div>
              <div style={{ fontSize: 10.5, letterSpacing: 1.4, textTransform: "uppercase",
                color: C.skyFaint, fontFamily: "'JetBrains Mono', monospace" }}>
                Command Center · v4.2
              </div>
            </div>
          </div>
          <LangPill lang={lang} setLang={setLang} variant="dark" />
        </header>

        <div style={{ position: "relative", zIndex: 2, maxWidth: 440 }}>
          {f.success && <SuccessOverlay t={t} variant="dark" />}

          <h1 style={{ fontSize: 46, fontWeight: 800, lineHeight: 1.02, letterSpacing: -1.4, margin: 0 }}>
            Вход в<br/>
            <span style={{ color: C.skyFaint }}>аналитику</span><br/>
            регионов.
          </h1>
          <p style={{ fontSize: 14.5, color: "rgba(255,255,255,0.7)", marginTop: 16, lineHeight: 1.55 }}>
            Защищённый доступ к AI-инструментам Национального Банка Узбекистана.
          </p>

          <div style={{
            display: "inline-flex", marginTop: 28, marginBottom: 20,
            background: "rgba(255,255,255,0.08)", borderRadius: 10, padding: 4,
          }}>
            {[["signin", t("signin")], ["signup", t("signup")]].map(([k, label]) => (
              <button key={k} onClick={() => f.setMode(k)}
                style={{
                  padding: "9px 20px", borderRadius: 7, border: "none",
                  background: f.mode === k ? "#fff" : "transparent",
                  color: f.mode === k ? C.primary : "rgba(255,255,255,0.7)",
                  fontSize: 13, fontWeight: 700, cursor: "pointer",
                }}>{label}</button>
            ))}
          </div>

          {f.mode === "signup" && (
            <div style={{ marginBottom: 16, animation: "slideUp .3s" }}>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.8,
                color: "rgba(255,255,255,0.55)", marginBottom: 8, fontWeight: 700 }}>{t("roleTitle")}</div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {[["sme", t("role_sme")], ["corp", t("role_corp")], ["individual", t("role_individual")]].map(([k, label]) => (
                  <button key={k} onClick={() => f.setRole(k)}
                    style={{
                      padding: "7px 13px", borderRadius: 999,
                      border: `1px solid ${f.role === k ? "#fff" : "rgba(255,255,255,0.2)"}`,
                      background: f.role === k ? "#fff" : "transparent",
                      color: f.role === k ? C.primary : "rgba(255,255,255,0.85)",
                      fontSize: 12.5, fontWeight: 600, cursor: "pointer",
                    }}>{label}</button>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <FloatField label={t("email")} value={f.email} onChange={f.setEmail} type="email" placeholder={t("emailPh")} variant="dark" />
            <PasswordField value={f.password} onChange={f.setPassword} t={t} variant="dark" />
          </div>

          {f.error && (
            <div style={{ marginTop: 10, fontSize: 12, color: "#FCA5A5", fontWeight: 600 }}>
              ▲ {f.error === "email" ? "Проверьте email" : "Пароль слишком короткий"}
            </div>
          )}

          {f.mode === "signin" && (
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 14, marginBottom: 20 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "rgba(255,255,255,0.7)", cursor: "pointer" }}>
                <input type="checkbox" checked={f.remember} onChange={e => f.setRemember(e.target.checked)}
                  style={{ width: 14, height: 14, accentColor: "#fff" }} />
                {t("remember")}
              </label>
              <a href="#" onClick={e => e.preventDefault()} style={{ fontSize: 13, color: C.skyFaint, fontWeight: 600 }}>{t("forgot")}</a>
            </div>
          )}
          {f.mode === "signup" && <div style={{ height: 20 }} />}

          <button type="button" onClick={f.submit} disabled={f.loading}
            style={{
              width: "100%", padding: "15px 20px", borderRadius: 10, border: "none",
              background: "#fff", color: C.primary,
              fontSize: 14, fontWeight: 700, cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
              boxShadow: "0 10px 28px -10px rgba(255,255,255,0.3)",
            }}>
            {f.loading ? <Spinner /> : (f.mode === "signin" ? t("submit") : t("submitRegister"))}
            {!f.loading && <span style={{ opacity: 0.5 }}>→</span>}
          </button>

          <div style={{ marginTop: 16, fontSize: 13, color: "rgba(255,255,255,0.6)" }}>
            {f.mode === "signin" ? t("noAccount") : t("haveAccount")}{" "}
            <button onClick={() => f.setMode(f.mode === "signin" ? "signup" : "signin")}
              style={{ background: "transparent", border: "none", color: "#fff", cursor: "pointer",
                fontWeight: 700, padding: 0, fontSize: 13, textDecoration: "underline", textUnderlineOffset: 3 }}>
              {f.mode === "signin" ? t("signupCta") : t("signinCta")}
            </button>
          </div>
        </div>

        <div style={{
          position: "relative", zIndex: 2,
          fontSize: 11, color: "rgba(255,255,255,0.5)",
          display: "flex", alignItems: "center", gap: 14,
        }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 6, height: 6, borderRadius: 999, background: C.emeraldLight, boxShadow: `0 0 6px ${C.emeraldLight}` }} />
            {t("statusOk")}
          </span>
          <span>·</span>
          <span>{t("copyright")}</span>
        </div>
      </div>

      {/* RIGHT: light dashboard — command view */}
      <div style={{
        background: "#F5F8FC", padding: 40,
        display: "flex", alignItems: "center", justifyContent: "center",
        position: "relative", overflow: "hidden",
      }}>
        <div aria-hidden style={{
          position: "absolute", inset: 0,
          backgroundImage: `radial-gradient(${C.primary}12 1px, transparent 1px)`,
          backgroundSize: "28px 28px",
          maskImage: "radial-gradient(ellipse 80% 70% at 50% 50%, #000 50%, transparent 85%)",
        }} />

        <div style={{
          position: "relative", zIndex: 2, width: "100%", maxWidth: 600,
          display: "flex", flexDirection: "column", gap: 14,
        }}>
          {/* KPI ribbon */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
            {[
              { l: "Активов", v: "₽4.2B", d: "+12.4%", c: C.emerald },
              { l: "Клиентов", v: "12,840", d: "+342", c: C.primary2 },
              { l: "Регионов", v: "14", d: "100%", c: C.amber },
              { l: "Точность", v: "94.2%", d: "+2.1pp", c: C.primary },
            ].map((k, i) => (
              <div key={i} style={{
                padding: "14px 14px", background: "#fff",
                border: `1px solid ${C.primary}15`, borderRadius: 12,
                boxShadow: "0 2px 8px -4px rgba(0,61,124,0.08)",
              }}>
                <div style={{ fontSize: 9.5, letterSpacing: 1, textTransform: "uppercase",
                  color: C.muted, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>{k.l}</div>
                <div style={{ fontSize: 22, fontWeight: 800, marginTop: 4, letterSpacing: -0.4, color: C.ink }}>{k.v}</div>
                <div style={{ fontSize: 11, color: k.c, fontWeight: 700, marginTop: 2 }}>↑ {k.d}</div>
              </div>
            ))}
          </div>

          {/* main chart card */}
          <div style={{
            background: "#fff", borderRadius: 14,
            border: `1px solid ${C.primary}15`, padding: 22,
            boxShadow: "0 8px 30px -10px rgba(0,61,124,0.12)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
              <div>
                <div style={{ fontSize: 10, letterSpacing: 1.4, textTransform: "uppercase",
                  color: C.primary, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>ВРП · 14 РЕГИОНОВ · 2025</div>
                <div style={{ fontSize: 18, fontWeight: 800, marginTop: 4, color: C.ink, letterSpacing: -0.3 }}>Экономическая активность</div>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                {["4К", "12М", "5Л"].map((p, i) => (
                  <div key={p} style={{
                    padding: "5px 10px", fontSize: 11, fontWeight: 700,
                    borderRadius: 6, background: i === 1 ? C.primary : `${C.primary}10`,
                    color: i === 1 ? "#fff" : C.primary,
                    fontFamily: "'JetBrains Mono', monospace",
                  }}>{p}</div>
                ))}
              </div>
            </div>

            {/* area chart */}
            <svg viewBox="0 0 600 180" style={{ width: "100%", height: 160 }}>
              <defs>
                <linearGradient id="v5grad" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor={C.primary} stopOpacity="0.35" />
                  <stop offset="100%" stopColor={C.primary} stopOpacity="0" />
                </linearGradient>
                <linearGradient id="v5grad2" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor={C.emerald} stopOpacity="0.25" />
                  <stop offset="100%" stopColor={C.emerald} stopOpacity="0" />
                </linearGradient>
              </defs>
              {/* grid */}
              {[0, 1, 2, 3].map(i => (
                <line key={i} x1="0" x2="600" y1={30 + i * 40} y2={30 + i * 40}
                  stroke={`${C.primary}12`} strokeDasharray="3 4" />
              ))}
              {/* primary area */}
              <path d="M0,130 C60,110 100,80 150,75 C200,70 240,90 300,70 C360,55 400,40 460,55 C520,70 560,45 600,35 L600,180 L0,180 Z"
                fill="url(#v5grad)" />
              <path d="M0,130 C60,110 100,80 150,75 C200,70 240,90 300,70 C360,55 400,40 460,55 C520,70 560,45 600,35"
                fill="none" stroke={C.primary} strokeWidth="2.5" />
              {/* secondary */}
              <path d="M0,150 C80,140 140,125 220,115 C280,108 340,115 420,100 C480,90 540,85 600,75 L600,180 L0,180 Z"
                fill="url(#v5grad2)" />
              <path d="M0,150 C80,140 140,125 220,115 C280,108 340,115 420,100 C480,90 540,85 600,75"
                fill="none" stroke={C.emerald} strokeWidth="2" strokeDasharray="4 3" />
              {/* marker */}
              <circle cx="600" cy="35" r="5" fill="#fff" stroke={C.primary} strokeWidth="2.5" />
              <circle cx="600" cy="35" r="11" fill="none" stroke={C.primary} strokeWidth="1" opacity="0.4">
                <animate attributeName="r" values="5;14;5" dur="2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite" />
              </circle>
            </svg>

            <div style={{ display: "flex", gap: 20, marginTop: 10, fontSize: 11,
              fontFamily: "'JetBrains Mono', monospace", color: C.muted }}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 10, height: 2.5, background: C.primary }} /> ВРП
              </span>
              <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 10, height: 2.5, background: C.emerald, borderStyle: "dashed" }} /> Инвестиции
              </span>
            </div>
          </div>

          {/* Region grid + alert */}
          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 14 }}>
            <div style={{
              background: "#fff", borderRadius: 14,
              border: `1px solid ${C.primary}15`, padding: 18,
              boxShadow: "0 8px 30px -10px rgba(0,61,124,0.08)",
            }}>
              <div style={{ fontSize: 10, letterSpacing: 1.4, textTransform: "uppercase",
                color: C.primary, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, marginBottom: 12 }}>
                Топ регионов
              </div>
              {[
                { n: "Фергана", v: "+18.2%", p: 92, c: C.emerald },
                { n: "Наманган", v: "+14.8%", p: 78, c: C.emerald },
                { n: "Самарканд", v: "+9.4%", p: 62, c: C.primary2 },
                { n: "Ташкент", v: "+6.1%", p: 48, c: C.primary2 },
                { n: "Хорезм", v: "−2.3%", p: 30, c: C.red },
              ].map((r, i) => (
                <div key={i} style={{ marginBottom: 9 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 3 }}>
                    <span style={{ fontWeight: 600, color: C.ink }}>{r.n}</span>
                    <span style={{ fontWeight: 700, color: r.c, fontFamily: "'JetBrains Mono', monospace" }}>{r.v}</span>
                  </div>
                  <div style={{ height: 4, borderRadius: 999, background: `${C.primary}10`, overflow: "hidden" }}>
                    <div style={{ width: `${r.p}%`, height: "100%", background: r.c, borderRadius: 999 }} />
                  </div>
                </div>
              ))}
            </div>

            <div style={{
              background: `linear-gradient(155deg, ${C.primary}, ${C.primary2})`,
              borderRadius: 14, padding: 18, color: "#fff",
              position: "relative", overflow: "hidden",
              display: "flex", flexDirection: "column", justifyContent: "space-between",
            }}>
              <div>
                <div style={{ fontSize: 10, letterSpacing: 1.4, textTransform: "uppercase",
                  color: C.skyFaint, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>AI СОВЕТНИК</div>
                <div style={{ fontSize: 14, fontWeight: 600, marginTop: 8, lineHeight: 1.4 }}>
                  Рост МСБ в Фергане превысил прогноз на 4.2% — рекомендуется расширение кредитной линии.
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 10 }}>
                <span key={live} style={{
                  fontSize: 10, fontFamily: "'JetBrains Mono', monospace",
                  padding: "3px 8px", borderRadius: 999,
                  background: "rgba(255,255,255,0.15)",
                  animation: "fade .3s",
                }}>обновлено · только что</span>
              </div>
              <div style={{
                position: "absolute", top: -20, right: -20,
                width: 120, height: 120, borderRadius: 999,
                background: `radial-gradient(circle, ${C.skyFaint}44, transparent 70%)`,
              }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

window.V5Command = V5Command;

// V7: Terminal — mono/technical, split with a terminal-style live feed on right

function V7Terminal() {
  const { lang, setLang, t } = useLang();
  const f = useAuthForm();
  const [log, setLog] = useState([]);

  const C = {
    primary: "#003D7C", primary2: "#0054A6",
    sky: "#7FB5E6", skyFaint: "#93C5FD",
    emerald: "#10B981", amber: "#FBBF24", red: "#F87171",
    bg: "#F5F8FC", ink: "#0F1A2B", inkSoft: "#334155", muted: "#64748B",
    outline: "rgba(0,61,124,0.1)", fixed: "#E6EEF8",
    terminalBg: "#0A1628", terminalHi: "#0D2240",
  };

  useEffect(() => {
    const events = [
      { t: "SYS", m: "nbu-platform.core booted", c: C.skyFaint },
      { t: "AUTH", m: "tls 1.3 handshake · KZ·TASH-01", c: C.sky },
      { t: "DATA", m: "ingest: 14 regions · 199 districts", c: C.sky },
      { t: "ML", m: "model.fergana.grp reloaded (acc=94.2%)", c: C.emerald },
      { t: "OK", m: "revenue stream +12.4% vs 2025", c: C.emerald },
      { t: "INFO", m: "12,840 merchants online · uz.national", c: C.skyFaint },
      { t: "WARN", m: "khorezm workforce outflow detected", c: C.amber },
      { t: "AI", m: "advisor.ready · latency 83ms", c: C.emerald },
      { t: "DATA", m: "exporters.namangan +4.2% (forecast +3%)", c: C.sky },
      { t: "SYS", m: "awaiting login · session.anonymous", c: C.skyFaint },
    ];
    let i = 0;
    const push = () => {
      setLog(prev => {
        const next = [...prev, { ...events[i % events.length], id: Date.now() + Math.random() }];
        return next.slice(-12);
      });
      i++;
    };
    push(); push(); push();
    const id = setInterval(push, 1500);
    return () => clearInterval(id);
  }, []);

  const stats = [
    { l: "uptime", v: "99.982%" },
    { l: "nodes", v: "14" },
    { l: "qps", v: "4.2K" },
    { l: "latency", v: "83ms" },
  ];

  return (
    <div style={{
      minHeight: "100vh", display: "grid",
      gridTemplateColumns: "minmax(460px, 0.9fr) minmax(540px, 1.2fr)",
      fontFamily: "Manrope, Inter, sans-serif",
      background: C.bg, color: C.ink,
    }}>
      {/* LEFT: form */}
      <div style={{
        padding: "40px 52px",
        display: "flex", flexDirection: "column", justifyContent: "space-between",
      }}>
        <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{
              width: 34, height: 34, borderRadius: 9,
              background: C.primary, color: "#fff",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontWeight: 800, fontSize: 15,
            }}>N</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 15, color: C.primary }}>NBU AI Platform</div>
              <div style={{ fontSize: 10.5, letterSpacing: 1.4, textTransform: "uppercase",
                color: C.muted, fontFamily: "'JetBrains Mono', monospace" }}>
                Developer Console
              </div>
            </div>
          </div>
          <LangPill lang={lang} setLang={setLang} />
        </header>

        <div style={{ maxWidth: 440, width: "100%", position: "relative" }}>
          {f.success && <SuccessOverlay t={t} />}

          <div style={{
            fontFamily: "'JetBrains Mono', monospace", fontSize: 11,
            color: C.primary, fontWeight: 700, letterSpacing: 1.4,
            textTransform: "uppercase", marginBottom: 16,
          }}>
            $ nbu auth --init
          </div>

          <h1 style={{ fontSize: 46, fontWeight: 800, lineHeight: 1.02, letterSpacing: -1.6, margin: 0 }}>
            Войдите<br/>
            в <span style={{
              background: `linear-gradient(90deg, ${C.primary}, ${C.primary2})`,
              WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
            }}>систему.</span>
          </h1>
          <p style={{ fontSize: 14.5, color: C.inkSoft, marginTop: 16, lineHeight: 1.55 }}>
            Доступ к API, моделям ML и региональным датасетам. Банковский уровень защиты.
          </p>

          <div style={{
            display: "inline-flex", marginTop: 28, marginBottom: 20,
            background: C.fixed, borderRadius: 10, padding: 4,
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            {[["signin", "> " + t("signin")], ["signup", "+ " + t("signup")]].map(([k, label]) => (
              <button key={k} onClick={() => f.setMode(k)}
                style={{
                  padding: "9px 18px", borderRadius: 7, border: "none",
                  background: f.mode === k ? "#fff" : "transparent",
                  color: f.mode === k ? C.primary : `${C.primary}99`,
                  fontSize: 12.5, fontWeight: 700, cursor: "pointer",
                  fontFamily: "inherit",
                  boxShadow: f.mode === k ? `0 2px 8px ${C.primary}22` : "none",
                }}>{label}</button>
            ))}
          </div>

          {f.mode === "signup" && (
            <div style={{ marginBottom: 16, animation: "slideUp .3s" }}>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.8,
                color: C.muted, marginBottom: 8, fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" }}>
                --role
              </div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {[["sme", t("role_sme")], ["corp", t("role_corp")], ["individual", t("role_individual")]].map(([k, label]) => (
                  <button key={k} onClick={() => f.setRole(k)}
                    style={{
                      padding: "7px 13px", borderRadius: 6,
                      border: `1px solid ${f.role === k ? C.primary : C.outline}`,
                      background: f.role === k ? C.primary : "transparent",
                      color: f.role === k ? "#fff" : C.primary,
                      fontSize: 12, fontWeight: 600, cursor: "pointer",
                      fontFamily: "'JetBrains Mono', monospace",
                    }}>{label}</button>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <MonoField label="--email" value={f.email} onChange={f.setEmail} type="email" placeholder={t("emailPh")} C={C} />
            <MonoField label="--password" value={f.password} onChange={f.setPassword} type="password" placeholder={t("passwordPh")} C={C} />
          </div>

          {f.error && (
            <div style={{ marginTop: 10, fontSize: 12, color: C.red, fontWeight: 600,
              fontFamily: "'JetBrains Mono', monospace" }}>
              err: {f.error === "email" ? "invalid_email_format" : "password_length_insufficient"}
            </div>
          )}

          {f.mode === "signin" && (
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 14, marginBottom: 20 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12.5,
                color: C.inkSoft, cursor: "pointer", fontFamily: "'JetBrains Mono', monospace" }}>
                <input type="checkbox" checked={f.remember} onChange={e => f.setRemember(e.target.checked)}
                  style={{ width: 14, height: 14, accentColor: C.primary }} />
                --persist
              </label>
              <a href="#" onClick={e => e.preventDefault()} style={{
                fontSize: 12.5, color: C.primary, fontWeight: 600,
                fontFamily: "'JetBrains Mono', monospace",
              }}>reset_password →</a>
            </div>
          )}
          {f.mode === "signup" && <div style={{ height: 20 }} />}

          <button type="button" onClick={f.submit} disabled={f.loading}
            style={{
              width: "100%", padding: "15px 20px", borderRadius: 10, border: "none",
              background: C.primary, color: "#fff",
              fontSize: 13, fontWeight: 700, cursor: "pointer",
              letterSpacing: 0.5,
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
              boxShadow: `0 10px 28px -10px ${C.primary}88`,
              fontFamily: "'JetBrains Mono', monospace",
            }}>
            {f.loading ? <Spinner variant="dark" /> : `> ${f.mode === "signin" ? "nbu login --submit" : "nbu register --submit"}`}
          </button>

          <div style={{ marginTop: 16, fontSize: 12.5, color: C.muted, fontFamily: "'JetBrains Mono', monospace" }}>
            # {f.mode === "signin" ? t("noAccount") : t("haveAccount")}{" "}
            <button onClick={() => f.setMode(f.mode === "signin" ? "signup" : "signin")}
              style={{ background: "transparent", border: "none", color: C.primary, cursor: "pointer",
                fontWeight: 700, padding: 0, fontSize: 12.5, fontFamily: "inherit" }}>
              {f.mode === "signin" ? t("signupCta") : t("signinCta")} →
            </button>
          </div>
        </div>

        <div style={{
          fontSize: 10.5, color: C.muted, display: "flex", alignItems: "center", gap: 14,
          fontFamily: "'JetBrains Mono', monospace", letterSpacing: 0.4,
        }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 6, height: 6, borderRadius: 999, background: C.emerald,
              boxShadow: `0 0 6px ${C.emerald}` }} />
            status.ok
          </span>
          <span>·</span>
          <span>tls_1.3</span>
          <span>·</span>
          <span>{t("copyright")}</span>
        </div>
      </div>

      {/* RIGHT: terminal */}
      <div style={{
        background: C.terminalBg, color: "#D6E6F5",
        padding: 40, overflow: "hidden",
        display: "flex", flexDirection: "column", justifyContent: "center",
        position: "relative",
      }}>
        <div aria-hidden style={{
          position: "absolute", inset: 0,
          background: `radial-gradient(ellipse 80% 60% at 50% 50%, ${C.primary2}22, transparent 70%)`,
        }} />
        {/* scanline */}
        <div aria-hidden style={{
          position: "absolute", inset: 0, pointerEvents: "none",
          backgroundImage: "repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0 1px, transparent 1px 3px)",
        }} />

        <div style={{ position: "relative", zIndex: 2, maxWidth: 560, margin: "0 auto", width: "100%" }}>
          {/* window chrome */}
          <div style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "12px 16px", background: C.terminalHi,
            border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px 12px 0 0",
            borderBottom: "none",
          }}>
            <div style={{ display: "flex", gap: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: 999, background: "#F87171" }} />
              <div style={{ width: 10, height: 10, borderRadius: 999, background: "#FBBF24" }} />
              <div style={{ width: 10, height: 10, borderRadius: 999, background: "#10B981" }} />
            </div>
            <div style={{
              marginLeft: 10, fontSize: 11, color: "rgba(214,230,245,0.65)",
              fontFamily: "'JetBrains Mono', monospace", letterSpacing: 0.4, flex: 1,
            }}>
              nbu@platform:~ — live stream
            </div>
            <div style={{
              display: "flex", alignItems: "center", gap: 6,
              fontSize: 10, color: C.emerald, fontFamily: "'JetBrains Mono', monospace",
            }}>
              <span style={{ width: 6, height: 6, borderRadius: 999, background: C.emerald,
                boxShadow: `0 0 8px ${C.emerald}`, animation: "pulse 1.5s infinite" }} />
              LIVE
            </div>
          </div>

          {/* terminal body */}
          <div style={{
            background: C.terminalBg, border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: "0 0 12px 12px", padding: 22,
            fontFamily: "'JetBrains Mono', monospace",
            height: 360, overflow: "hidden",
            boxShadow: `0 30px 80px -20px rgba(0,0,0,0.6), inset 0 0 60px ${C.primary}22`,
            display: "flex", flexDirection: "column",
          }}>
            <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column", justifyContent: "flex-end" }}>
              {log.map((l) => (
                <div key={l.id} style={{
                  fontSize: 12, padding: "3px 0", lineHeight: 1.5,
                  display: "flex", gap: 10, alignItems: "flex-start",
                  animation: "slideUp .25s",
                }}>
                  <span style={{ color: "rgba(214,230,245,0.4)", fontSize: 11 }}>
                    {new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                  </span>
                  <span style={{
                    color: l.c, fontWeight: 700, minWidth: 42,
                    fontSize: 11, letterSpacing: 0.3,
                  }}>[{l.t}]</span>
                  <span style={{ color: "#D6E6F5", flex: 1 }}>{l.m}</span>
                </div>
              ))}
            </div>
            <div style={{
              marginTop: 10, paddingTop: 10,
              borderTop: "1px solid rgba(255,255,255,0.08)",
              fontSize: 12, display: "flex", alignItems: "center", gap: 8,
            }}>
              <span style={{ color: C.emerald }}>$</span>
              <span style={{ color: "#D6E6F5" }}>nbu auth --status</span>
              <span style={{
                marginLeft: 4, width: 8, height: 14, background: "#D6E6F5",
                animation: "pulse 1s infinite",
              }} />
            </div>
          </div>

          {/* stat row */}
          <div style={{
            marginTop: 18, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10,
          }}>
            {stats.map((s, i) => (
              <div key={i} style={{
                padding: "11px 14px",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 10,
              }}>
                <div style={{ fontSize: 10, color: "rgba(214,230,245,0.5)",
                  fontFamily: "'JetBrains Mono', monospace", letterSpacing: 1,
                  textTransform: "uppercase", fontWeight: 700 }}>{s.l}</div>
                <div style={{ fontSize: 16, color: "#fff", fontWeight: 700,
                  fontFamily: "'JetBrains Mono', monospace", marginTop: 3, letterSpacing: -0.2 }}>{s.v}</div>
              </div>
            ))}
          </div>

          {/* footer */}
          <div style={{
            marginTop: 18, padding: "10px 14px",
            background: "rgba(16,185,129,0.08)",
            border: `1px solid ${C.emerald}33`, borderRadius: 10,
            display: "flex", alignItems: "center", gap: 10,
            fontSize: 11.5, color: C.emerald,
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            <span>✓</span>
            <span>all systems nominal · ml_models 3/3 ready · data_pipeline 14/14 streaming</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function MonoField({ label, value, onChange, type = "text", placeholder, C }) {
  const [focus, setFocus] = useState(false);
  const [show, setShow] = useState(false);
  const inputType = type === "password" ? (show ? "text" : "password") : type;
  return (
    <label style={{ display: "block" }}>
      <span style={{ display: "block", fontSize: 11, letterSpacing: 0.6,
        color: C.muted, marginBottom: 6, fontWeight: 600,
        fontFamily: "'JetBrains Mono', monospace" }}>{label}</span>
      <div style={{
        position: "relative", display: "flex", alignItems: "center",
        background: "#fff", border: `1.5px solid ${focus ? C.primary : C.outline}`,
        borderRadius: 10, boxShadow: focus ? `0 0 0 4px ${C.primary}18` : "none",
        transition: "all .18s",
      }}>
        <span style={{ padding: "0 0 0 14px", color: C.muted,
          fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}>›</span>
        <input type={inputType} value={value} onChange={e => onChange(e.target.value)}
          onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
          placeholder={placeholder}
          style={{
            flex: 1, background: "transparent", border: "none",
            padding: "13px 14px", fontSize: 14, color: C.ink,
            fontFamily: type === "password" ? "'JetBrains Mono', monospace" : "inherit",
          }} />
        {type === "password" && (
          <button type="button" onClick={() => setShow(s => !s)}
            style={{ background: "transparent", border: "none", marginRight: 8, padding: "6px 10px",
              borderRadius: 6, fontSize: 11, color: C.muted, fontWeight: 600, cursor: "pointer",
              fontFamily: "'JetBrains Mono', monospace" }}>
            {show ? "hide" : "show"}
          </button>
        )}
      </div>
    </label>
  );
}

window.V7Terminal = V7Terminal;

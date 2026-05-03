// V6: Regional Atlas — mosaic of region tiles on right
// Light everywhere, form on left, right panel is a big interactive map mosaic.

function V6Atlas() {
  const { lang, setLang, t } = useLang();
  const f = useAuthForm();
  const [hover, setHover] = useState("fergana");

  const C = {
    primary: "#003D7C", primary2: "#0054A6", primary3: "#2563EB",
    sky: "#7FB5E6", skyFaint: "#93C5FD", skyFixed: "#E6EEF8",
    emerald: "#059669", emeraldLight: "#10B981",
    amber: "#F59E0B", red: "#DC2626",
    bg: "#FAFCFE", ink: "#0F1A2B", inkSoft: "#334155", muted: "#64748B",
    outline: "rgba(0,61,124,0.1)",
  };

  const regions = [
    { k: "fergana", n: "Фергана", pop: "3.7M", d: "+18%", c: C.primary },
    { k: "tashkent", n: "Ташкент", pop: "3.0M", d: "+6%", c: C.primary2 },
    { k: "samarkand", n: "Самарканд", pop: "4.0M", d: "+9%", c: C.primary2 },
    { k: "andijan", n: "Андижан", pop: "3.2M", d: "+12%", c: C.sky },
    { k: "namangan", n: "Наманган", pop: "2.9M", d: "+15%", c: C.sky },
    { k: "kashkadarya", n: "Кашкадарья", pop: "3.4M", d: "+7%", c: C.skyFaint },
    { k: "surkhandarya", n: "Сурхандарья", pop: "2.7M", d: "+5%", c: C.skyFaint },
    { k: "bukhara", n: "Бухара", pop: "2.0M", d: "+8%", c: C.sky },
    { k: "khorezm", n: "Хорезм", pop: "1.9M", d: "−2%", c: C.red },
    { k: "navoi", n: "Навои", pop: "1.0M", d: "+4%", c: C.skyFaint },
    { k: "jizzakh", n: "Джизак", pop: "1.4M", d: "+3%", c: C.skyFaint },
    { k: "syrdarya", n: "Сырдарья", pop: "0.9M", d: "+6%", c: C.sky },
    { k: "karakalpak", n: "Каракалпакстан", pop: "2.0M", d: "+1%", c: C.amber },
    { k: "tashkentReg", n: "Ташкент обл.", pop: "3.0M", d: "+5%", c: C.sky },
  ];

  const activeRegion = regions.find(r => r.k === hover) || regions[0];

  return (
    <div style={{
      minHeight: "100vh", display: "grid",
      gridTemplateColumns: "minmax(460px, 0.85fr) minmax(560px, 1.25fr)",
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
                Regional Atlas
              </div>
            </div>
          </div>
          <LangPill lang={lang} setLang={setLang} />
        </header>

        <div style={{ maxWidth: 440, width: "100%", position: "relative" }}>
          {f.success && <SuccessOverlay t={t} />}

          <div style={{
            display: "inline-block", fontSize: 11, letterSpacing: 1.6,
            textTransform: "uppercase", color: C.primary, fontWeight: 700,
            marginBottom: 14, fontFamily: "'JetBrains Mono', monospace",
          }}>
            · 14 областей под наблюдением
          </div>

          <h1 style={{ fontSize: 48, fontWeight: 800, lineHeight: 1.02, letterSpacing: -1.6, margin: 0, color: C.ink }}>
            Весь<br/>
            <span style={{ color: C.primary }}>Узбекистан</span><br/>
            в одной<br/>платформе.
          </h1>
          <p style={{ fontSize: 14.5, color: C.inkSoft, marginTop: 16, lineHeight: 1.55 }}>
            Войдите, чтобы увидеть экономические показатели, AI-рекомендации и финансовую аналитику по всем 14 регионам страны.
          </p>

          <div style={{
            display: "inline-flex", marginTop: 28, marginBottom: 20,
            background: C.skyFixed, borderRadius: 10, padding: 4,
          }}>
            {[["signin", t("signin")], ["signup", t("signup")]].map(([k, label]) => (
              <button key={k} onClick={() => f.setMode(k)}
                style={{
                  padding: "9px 20px", borderRadius: 7, border: "none",
                  background: f.mode === k ? "#fff" : "transparent",
                  color: f.mode === k ? C.primary : `${C.primary}99`,
                  fontSize: 13, fontWeight: 700, cursor: "pointer",
                  boxShadow: f.mode === k ? `0 2px 8px ${C.primary}22` : "none",
                }}>{label}</button>
            ))}
          </div>

          {f.mode === "signup" && (
            <div style={{ marginBottom: 16, animation: "slideUp .3s" }}>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: 0.8,
                color: C.muted, marginBottom: 8, fontWeight: 700 }}>{t("roleTitle")}</div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {[["sme", t("role_sme")], ["corp", t("role_corp")], ["individual", t("role_individual")]].map(([k, label]) => (
                  <button key={k} onClick={() => f.setRole(k)}
                    style={{
                      padding: "7px 13px", borderRadius: 999,
                      border: `1px solid ${f.role === k ? C.primary : C.outline}`,
                      background: f.role === k ? C.primary : "transparent",
                      color: f.role === k ? "#fff" : C.primary,
                      fontSize: 12.5, fontWeight: 600, cursor: "pointer",
                    }}>{label}</button>
                ))}
              </div>
            </div>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <NbuFieldAtlas label={t("email")} value={f.email} onChange={f.setEmail} type="email" placeholder={t("emailPh")} C={C} />
            <NbuFieldAtlas label={t("password")} value={f.password} onChange={f.setPassword} type="password" placeholder={t("passwordPh")} C={C} />
          </div>

          {f.error && (
            <div style={{ marginTop: 10, fontSize: 12, color: C.red, fontWeight: 600 }}>
              ▲ {f.error === "email" ? "Проверьте email" : "Пароль слишком короткий"}
            </div>
          )}

          {f.mode === "signin" && (
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 14, marginBottom: 20 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: C.inkSoft, cursor: "pointer" }}>
                <input type="checkbox" checked={f.remember} onChange={e => f.setRemember(e.target.checked)}
                  style={{ width: 14, height: 14, accentColor: C.primary }} />
                {t("remember")}
              </label>
              <a href="#" onClick={e => e.preventDefault()} style={{ fontSize: 13, color: C.primary, fontWeight: 600 }}>{t("forgot")}</a>
            </div>
          )}
          {f.mode === "signup" && <div style={{ height: 20 }} />}

          <button type="button" onClick={f.submit} disabled={f.loading}
            style={{
              width: "100%", padding: "15px 20px", borderRadius: 10, border: "none",
              background: C.primary, color: "#fff",
              fontSize: 14, fontWeight: 700, cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
              boxShadow: `0 10px 28px -10px ${C.primary}88`,
            }}>
            {f.loading ? <Spinner variant="dark" /> : (f.mode === "signin" ? t("submit") : t("submitRegister"))}
            {!f.loading && <span style={{ opacity: 0.7 }}>→</span>}
          </button>

          <div style={{ marginTop: 16, fontSize: 13, color: C.muted }}>
            {f.mode === "signin" ? t("noAccount") : t("haveAccount")}{" "}
            <button onClick={() => f.setMode(f.mode === "signin" ? "signup" : "signin")}
              style={{ background: "transparent", border: "none", color: C.primary, cursor: "pointer",
                fontWeight: 700, padding: 0, fontSize: 13 }}>
              {f.mode === "signin" ? t("signupCta") : t("signinCta")} →
            </button>
          </div>
        </div>

        <div style={{ fontSize: 11, color: C.muted, display: "flex", alignItems: "center", gap: 14 }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 6, height: 6, borderRadius: 999, background: C.emerald }} />
            {t("statusOk")}
          </span>
          <span>·</span>
          <span>{t("copyright")}</span>
        </div>
      </div>

      {/* RIGHT: atlas mosaic */}
      <div style={{
        position: "relative", padding: 40,
        background: `linear-gradient(155deg, ${C.primary}, ${C.primary2})`,
        color: "#fff", overflow: "hidden",
        display: "flex", flexDirection: "column", justifyContent: "center",
      }}>
        <div aria-hidden style={{
          position: "absolute", inset: 0,
          backgroundImage: "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
          maskImage: "radial-gradient(ellipse 80% 70% at 50% 50%, #000 40%, transparent 85%)",
        }} />

        <div style={{ position: "relative", zIndex: 2 }}>
          {/* header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 22 }}>
            <div>
              <div style={{ fontSize: 10, letterSpacing: 2, textTransform: "uppercase",
                color: C.skyFaint, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>
                ATLAS · LIVE
              </div>
              <div style={{ fontSize: 26, fontWeight: 800, marginTop: 6, letterSpacing: -0.6 }}>
                Регионы Узбекистана
              </div>
              <div style={{ fontSize: 12.5, color: "rgba(255,255,255,0.6)", marginTop: 4 }}>
                Наведите на область, чтобы увидеть детали
              </div>
            </div>
            <div style={{
              padding: "8px 14px", background: "rgba(255,255,255,0.1)",
              border: "1px solid rgba(255,255,255,0.2)", borderRadius: 10,
              backdropFilter: "blur(12px)", minWidth: 160,
            }}>
              <div style={{ fontSize: 9.5, letterSpacing: 1.2, textTransform: "uppercase",
                color: C.skyFaint, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>{activeRegion.n}</div>
              <div style={{ fontSize: 16, fontWeight: 800, marginTop: 2 }}>{activeRegion.pop}</div>
              <div style={{ fontSize: 11, color: activeRegion.d.startsWith("−") ? "#FCA5A5" : "#A7F3D0",
                fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>
                ВРП {activeRegion.d}
              </div>
            </div>
          </div>

          {/* Voronoi-style tile mosaic */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(5, 1fr)",
            gridAutoRows: "66px",
            gap: 8,
          }}>
            {[
              // [k, colSpan, rowSpan]
              ["karakalpak", 2, 2],
              ["khorezm", 1, 1],
              ["navoi", 2, 1],
              ["khorezmX", 1, 1, "blank"],
              ["bukhara", 1, 1],
              ["samarkand", 1, 1],
              ["jizzakh", 1, 1],
              ["tashkentReg", 1, 1],
              ["syrdarya", 1, 1],
              ["tashkent", 1, 1],
              ["kashkadarya", 1, 1],
              ["namangan", 1, 1],
              ["andijan", 1, 1],
              ["surkhandarya", 1, 1],
              ["fergana", 2, 1],
            ].map(([k, cs, rs, kind]) => {
              if (kind === "blank") return <div key={k} style={{ gridColumn: `span ${cs}`, gridRow: `span ${rs}` }} />;
              const r = regions.find(x => x.k === k);
              if (!r) return null;
              const active = hover === k;
              return (
                <button key={k}
                  onMouseEnter={() => setHover(k)}
                  onFocus={() => setHover(k)}
                  style={{
                    gridColumn: `span ${cs}`, gridRow: `span ${rs}`,
                    background: active ? "rgba(255,255,255,0.95)" : "rgba(255,255,255,0.08)",
                    border: `1px solid ${active ? "#fff" : "rgba(255,255,255,0.18)"}`,
                    borderRadius: 10, padding: "8px 10px",
                    color: active ? C.primary : "#fff",
                    cursor: "pointer", transition: "all .18s",
                    textAlign: "left",
                    display: "flex", flexDirection: "column", justifyContent: "space-between",
                    backdropFilter: active ? "none" : "blur(10px)",
                    boxShadow: active ? "0 12px 30px -10px rgba(0,0,0,0.4)" : "none",
                    transform: active ? "scale(1.02)" : "scale(1)",
                    overflow: "hidden",
                    position: "relative",
                  }}>
                  <div style={{
                    fontSize: 11, fontWeight: 700, letterSpacing: -0.1,
                    color: active ? C.primary : "#fff",
                  }}>{r.n}</div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 4 }}>
                    <span style={{
                      fontSize: 10, fontFamily: "'JetBrains Mono', monospace",
                      color: active ? C.muted : "rgba(255,255,255,0.6)",
                    }}>{r.pop}</span>
                    <span style={{
                      fontSize: 9.5, fontWeight: 700,
                      fontFamily: "'JetBrains Mono', monospace",
                      color: r.d.startsWith("−")
                        ? (active ? C.red : "#FCA5A5")
                        : (active ? C.emerald : "#A7F3D0"),
                    }}>{r.d}</span>
                  </div>
                  {active && (
                    <div style={{
                      position: "absolute", top: 6, right: 6,
                      width: 6, height: 6, borderRadius: 999, background: C.emerald,
                      boxShadow: `0 0 8px ${C.emerald}`,
                    }} />
                  )}
                </button>
              );
            })}
          </div>

          {/* bottom stats */}
          <div style={{
            marginTop: 24, display: "grid", gridTemplateColumns: "repeat(4, 1fr)",
            gap: 10, padding: "16px 0 0 0",
            borderTop: "1px solid rgba(255,255,255,0.15)",
          }}>
            {[
              { l: "Население", v: "35.3M" },
              { l: "ВРП общий", v: "85.6 трлн" },
              { l: "Районов", v: "199" },
              { l: "Клиентов", v: "12.8K" },
            ].map((s, i) => (
              <div key={i}>
                <div style={{ fontSize: 9.5, letterSpacing: 1.2, textTransform: "uppercase",
                  color: C.skyFaint, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>{s.l}</div>
                <div style={{ fontSize: 19, fontWeight: 800, marginTop: 3, letterSpacing: -0.3 }}>{s.v}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function NbuFieldAtlas({ label, value, onChange, type = "text", placeholder, C }) {
  const [focus, setFocus] = useState(false);
  const [show, setShow] = useState(false);
  const inputType = type === "password" ? (show ? "text" : "password") : type;
  return (
    <label style={{ display: "block" }}>
      <span style={{ display: "block", fontSize: 11, letterSpacing: 0.6,
        textTransform: "uppercase", color: C.muted, marginBottom: 6, fontWeight: 700 }}>{label}</span>
      <div style={{
        position: "relative", display: "flex", alignItems: "center",
        background: "#fff", border: `1.5px solid ${focus ? C.primary : C.outline}`,
        borderRadius: 10, boxShadow: focus ? `0 0 0 4px ${C.primary}18` : "none",
        transition: "all .18s",
      }}>
        <input
          type={inputType} value={value}
          onChange={e => onChange(e.target.value)}
          onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
          placeholder={placeholder}
          style={{ flex: 1, background: "transparent", border: "none", padding: "13px 16px", fontSize: 15, color: C.ink }} />
        {type === "password" && (
          <button type="button" onClick={() => setShow(s => !s)}
            style={{ background: "transparent", border: "none", marginRight: 8, padding: "6px 10px",
              borderRadius: 6, fontSize: 12, color: C.muted, fontWeight: 600, cursor: "pointer" }}>
            {show ? "Скрыть" : "Показать"}
          </button>
        )}
      </div>
    </label>
  );
}

window.V6Atlas = V6Atlas;

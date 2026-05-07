// Variation 2: Centered Glass Console
// Dark technical aesthetic. Grid background. Single card with tabs + role chips.
// Monospace detailing, soft accent green.

function V2Console() {
  const { lang, setLang, t } = useLang();
  const f = useAuthForm();

  const stats = [
    { n: "12,840", l: t("stat1Label") },
    { n: "199", l: t("stat2Label") },
    { n: "94.2%", l: t("stat3Label") },
  ];

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0b0d10",
      color: "#f4efe6",
      display: "flex",
      flexDirection: "column",
      fontFamily: "Inter, system-ui, sans-serif",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* background: subtle grid + soft radial */}
      <div aria-hidden style={{
        position: "absolute", inset: 0, zIndex: 0,
        backgroundImage: `
          radial-gradient(ellipse 80% 60% at 50% 30%, rgba(120, 200, 160, 0.09), transparent 60%),
          radial-gradient(ellipse 70% 50% at 20% 80%, rgba(160, 140, 220, 0.06), transparent 60%),
          linear-gradient(rgba(244,239,230,0.04) 1px, transparent 1px),
          linear-gradient(90deg, rgba(244,239,230,0.04) 1px, transparent 1px)
        `,
        backgroundSize: "auto, auto, 42px 42px, 42px 42px",
        maskImage: "radial-gradient(ellipse 100% 80% at 50% 50%, #000 40%, transparent 85%)",
      }} />

      {/* top bar */}
      <header style={{
        position: "relative", zIndex: 2,
        padding: "24px 40px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        borderBottom: "1px solid rgba(244,239,230,0.06)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <BrandMark size={26} tone="cream" />
          <div>
            <div style={{ fontSize: 14, fontWeight: 600, letterSpacing: 0.2 }}>NBU AI Platform</div>
            <div style={{ fontSize: 10.5, letterSpacing: 1.4, textTransform: "uppercase",
              color: "rgba(244,239,230,0.45)", fontFamily: "'JetBrains Mono', monospace" }}>
              secure · v4.2.1
            </div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{
            fontFamily: "'JetBrains Mono', monospace", fontSize: 11,
            color: "rgba(244,239,230,0.5)", letterSpacing: 0.5,
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: 999, background: "#6ac28b", boxShadow: "0 0 8px rgba(106,194,139,0.7)" }} />
            {t("statusOk")}
          </div>
          <LangPill lang={lang} setLang={setLang} variant="dark" />
        </div>
      </header>

      {/* content */}
      <div style={{
        position: "relative", zIndex: 2,
        flex: 1,
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: "40px 24px",
      }}>
        <div className="dark-placeholder" style={{
          width: "100%", maxWidth: 460,
          position: "relative",
        }}>
          {/* card */}
          <div style={{
            background: "linear-gradient(180deg, rgba(244,239,230,0.05), rgba(244,239,230,0.02))",
            border: "1px solid rgba(244,239,230,0.1)",
            borderRadius: 20,
            padding: 32,
            position: "relative",
            backdropFilter: "blur(20px)",
            boxShadow: "0 20px 60px -20px rgba(0,0,0,0.6), inset 0 1px 0 rgba(244,239,230,0.06)",
          }}>
            {f.success && <SuccessOverlay t={t} variant="dark" />}

            {/* corner tick marks */}
            {["tl", "tr", "bl", "br"].map((pos) => (
              <div key={pos} style={{
                position: "absolute",
                [pos.includes("t") ? "top" : "bottom"]: -1,
                [pos.includes("l") ? "left" : "right"]: -1,
                width: 12, height: 12,
                borderColor: "rgba(244,239,230,0.35)",
                borderStyle: "solid",
                borderWidth: 0,
                [pos.includes("t") ? "borderTopWidth" : "borderBottomWidth"]: 1.5,
                [pos.includes("l") ? "borderLeftWidth" : "borderRightWidth"]: 1.5,
                borderRadius: pos === "tl" ? "6px 0 0 0" : pos === "tr" ? "0 6px 0 0" : pos === "bl" ? "0 0 0 6px" : "0 0 6px 0",
                pointerEvents: "none",
              }} />
            ))}

            <div style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 10.5, letterSpacing: 2, textTransform: "uppercase",
              color: "rgba(244,239,230,0.5)",
              display: "flex", alignItems: "center", gap: 8,
              marginBottom: 18,
            }}>
              <span>//</span> auth · node.tashkent-01
            </div>

            <h1 style={{
              fontFamily: "Manrope, Inter, sans-serif",
              fontSize: 30, letterSpacing: -0.6, lineHeight: 1.1,
              margin: 0, fontWeight: 700,
            }}>
              Enter the platform
            </h1>
            <p style={{ fontSize: 14, color: "rgba(244,239,230,0.6)", marginTop: 10, marginBottom: 24 }}>
              {t("sub")}
            </p>

            {/* segmented tabs */}
            <div style={{
              display: "grid", gridTemplateColumns: "1fr 1fr",
              background: "rgba(244,239,230,0.04)",
              border: "1px solid rgba(244,239,230,0.08)",
              borderRadius: 10,
              padding: 4,
              marginBottom: 22,
            }}>
              {[["signin", t("signin")], ["signup", t("signup")]].map(([k, label]) => (
                <button key={k} onClick={() => f.setMode(k)}
                  style={{
                    padding: "10px 14px",
                    borderRadius: 7,
                    border: "none",
                    background: f.mode === k ? "#f4efe6" : "transparent",
                    color: f.mode === k ? "#0b0d10" : "rgba(244,239,230,0.6)",
                    fontSize: 13, fontWeight: 600,
                    cursor: "pointer", transition: "all .18s ease",
                  }}>
                  {label}
                </button>
              ))}
            </div>

            {/* role chips — horizontal, compact */}
            {f.mode === "signup" && (
              <div style={{ marginBottom: 18, animation: "slideUp .3s" }}>
                <div style={{
                  fontSize: 10.5, textTransform: "uppercase", letterSpacing: 1.2,
                  color: "rgba(244,239,230,0.45)", marginBottom: 10,
                  fontFamily: "'JetBrains Mono', monospace",
                }}>{t("roleTitle")}</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6 }}>
                  {[
                    ["sme", t("role_sme")],
                    ["corp", t("role_corp")],
                    ["individual", t("role_individual")],
                  ].map(([k, label]) => (
                    <button key={k} onClick={() => f.setRole(k)}
                      style={{
                        padding: "10px 8px",
                        background: f.role === k ? "rgba(244,239,230,0.12)" : "transparent",
                        border: `1px solid ${f.role === k ? "rgba(244,239,230,0.35)" : "rgba(244,239,230,0.1)"}`,
                        borderRadius: 8,
                        color: f.role === k ? "#f4efe6" : "rgba(244,239,230,0.6)",
                        fontSize: 12, fontWeight: 500,
                        cursor: "pointer", transition: "all .15s",
                      }}>{label}</button>
                  ))}
                </div>
              </div>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <FloatField
                label={t("email")}
                value={f.email}
                onChange={f.setEmail}
                type="email"
                placeholder={t("emailPh")}
                variant="dark"
                autoComplete="email"
              />
              <PasswordField value={f.password} onChange={f.setPassword} t={t} variant="dark" />
            </div>

            {f.error && (
              <div style={{
                marginTop: 10, fontSize: 12,
                fontFamily: "'JetBrains Mono', monospace",
                color: "#e07b7b", animation: "slideUp .2s",
              }}>
                {f.error === "email" ? "▲ invalid_email" : "▲ password_too_short"}
              </div>
            )}

            {f.mode === "signin" && (
              <div style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                marginTop: 14, marginBottom: 22,
              }}>
                <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "rgba(244,239,230,0.6)", cursor: "pointer" }}>
                  <input type="checkbox" checked={f.remember} onChange={(e) => f.setRemember(e.target.checked)}
                    style={{ width: 14, height: 14, accentColor: "#f4efe6", cursor: "pointer" }} />
                  {t("remember")}
                </label>
                <a href="#" onClick={(e) => e.preventDefault()} style={{
                  fontSize: 12, color: "rgba(244,239,230,0.7)", textDecoration: "none",
                  fontFamily: "'JetBrains Mono', monospace",
                }}>{t("forgot")} →</a>
              </div>
            )}
            {f.mode === "signup" && <div style={{ height: 22 }} />}

            <SubmitButton onClick={f.submit} loading={f.loading} variant="light">
              {f.mode === "signin" ? t("submit") : t("submitRegister")}
            </SubmitButton>

            <div style={{
              marginTop: 20, fontSize: 12, textAlign: "center",
              color: "rgba(244,239,230,0.55)",
              fontFamily: "'JetBrains Mono', monospace", letterSpacing: 0.3,
            }}>
              {f.mode === "signin" ? t("noAccount") : t("haveAccount")}{" "}
              <button onClick={() => f.setMode(f.mode === "signin" ? "signup" : "signin")}
                style={{
                  background: "transparent", border: "none",
                  color: "#f4efe6", cursor: "pointer", textDecoration: "underline",
                  textUnderlineOffset: 3, padding: 0, fontSize: 12,
                  fontFamily: "inherit",
                }}>
                {f.mode === "signin" ? t("signupCta") : t("signinCta")}
              </button>
            </div>
          </div>

          {/* stats strip below */}
          <div style={{
            marginTop: 20,
            display: "grid", gridTemplateColumns: "repeat(3, 1fr)",
            border: "1px solid rgba(244,239,230,0.08)",
            borderRadius: 12,
            overflow: "hidden",
          }}>
            {stats.map((s, i) => (
              <div key={i} style={{
                padding: "14px 16px",
                borderRight: i < 2 ? "1px solid rgba(244,239,230,0.08)" : "none",
                background: "rgba(244,239,230,0.02)",
              }}>
                <div style={{ fontSize: 20, fontWeight: 600, fontFamily: "Manrope, sans-serif", letterSpacing: -0.3 }}>{s.n}</div>
                <div style={{
                  fontSize: 10.5, color: "rgba(244,239,230,0.5)",
                  fontFamily: "'JetBrains Mono', monospace",
                  textTransform: "uppercase", letterSpacing: 0.6,
                  marginTop: 3,
                }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <footer style={{
        position: "relative", zIndex: 2,
        padding: "18px 40px",
        borderTop: "1px solid rgba(244,239,230,0.06)",
        display: "flex", justifyContent: "space-between",
        fontSize: 10.5, letterSpacing: 1, textTransform: "uppercase",
        color: "rgba(244,239,230,0.35)",
        fontFamily: "'JetBrains Mono', monospace",
      }}>
        <span>{t("copyright")}</span>
        <span>{t("legal")}</span>
      </footer>
    </div>
  );
}

window.V2Console = V2Console;

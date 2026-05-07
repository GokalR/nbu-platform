// Variation 1: Split Editorial
// Cream paper + deep ink. Serif wordmark. Editorial typography.
// Left: big idea, quote, features. Right: warm paper form card.

function V1Editorial() {
  const { lang, setLang, t } = useLang();
  const f = useAuthForm();

  return (
    <div style={{
      minHeight: "100vh",
      background: "#f4efe6",
      color: "#0b0d10",
      display: "grid",
      gridTemplateColumns: "1.1fr 1fr",
      fontFamily: "Inter, system-ui, sans-serif",
      position: "relative",
    }}>
      {/* LEFT: editorial */}
      <div style={{
        padding: "48px 56px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        borderRight: "1px solid rgba(11,13,16,0.08)",
        position: "relative",
        overflow: "hidden",
      }}>
        {/* tiny diagonal stripe texture */}
        <div aria-hidden style={{
          position: "absolute", inset: 0,
          backgroundImage: "repeating-linear-gradient(135deg, rgba(11,13,16,0.018) 0 2px, transparent 2px 14px)",
          pointerEvents: "none",
        }} />

        <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", position: "relative" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <BrandMark size={30} />
            <span style={{ fontFamily: "'Instrument Serif', serif", fontSize: 22, letterSpacing: 0.3 }}>NBU AI</span>
          </div>
          <div style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 11,
            letterSpacing: 1.2,
            textTransform: "uppercase",
            color: "rgba(11,13,16,0.55)",
          }}>
            {t("kicker")}
          </div>
        </header>

        <div style={{ position: "relative", maxWidth: 560 }}>
          <div style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 11,
            letterSpacing: 2,
            textTransform: "uppercase",
            color: "rgba(11,13,16,0.5)",
            marginBottom: 24,
            display: "flex", alignItems: "center", gap: 10,
          }}>
            <span style={{ width: 24, height: 1, background: "rgba(11,13,16,0.4)" }} />
            Volume · 01
          </div>
          <h1 style={{
            fontFamily: "'Instrument Serif', serif",
            fontSize: 76,
            lineHeight: 0.98,
            letterSpacing: -1.5,
            margin: 0,
            fontWeight: 400,
          }}>
            {t("heroTitle").split(" ").map((w, i, arr) => (
              <span key={i} style={i === arr.length - 1 ? { fontStyle: "italic", color: "rgba(11,13,16,0.7)" } : {}}>
                {w}{i < arr.length - 1 ? " " : ""}
              </span>
            ))}
          </h1>
          <p style={{
            fontSize: 16,
            lineHeight: 1.55,
            color: "rgba(11,13,16,0.68)",
            marginTop: 28,
            maxWidth: 480,
          }}>
            {t("heroBody")}
          </p>

          {/* features list */}
          <ul style={{ listStyle: "none", padding: 0, margin: "36px 0 0 0", display: "flex", flexDirection: "column", gap: 10 }}>
            {[t("feat1"), t("feat2"), t("feat3")].map((f, i) => (
              <li key={i} style={{
                display: "flex", alignItems: "center", gap: 14,
                fontSize: 14, color: "rgba(11,13,16,0.75)",
                fontFamily: "'JetBrains Mono', monospace",
              }}>
                <span style={{
                  width: 18, textAlign: "center", fontSize: 11,
                  color: "rgba(11,13,16,0.5)",
                }}>0{i+1}</span>
                <span style={{ flex: 1 }}>{f}</span>
              </li>
            ))}
          </ul>
        </div>

        <div style={{ position: "relative", display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 32 }}>
          <blockquote style={{
            margin: 0,
            maxWidth: 380,
            fontFamily: "'Instrument Serif', serif",
            fontStyle: "italic",
            fontSize: 19,
            lineHeight: 1.35,
            color: "rgba(11,13,16,0.75)",
          }}>
            {t("quote")}
            <footer style={{
              fontStyle: "normal",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 11,
              letterSpacing: 0.5,
              color: "rgba(11,13,16,0.5)",
              marginTop: 10,
              textTransform: "uppercase",
            }}>
              {t("quoteBy")}
            </footer>
          </blockquote>

          <div style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 10.5,
            letterSpacing: 1.2,
            color: "rgba(11,13,16,0.45)",
            textAlign: "right",
            textTransform: "uppercase",
          }}>
            <div>{t("copyright")}</div>
            <div style={{ marginTop: 4 }}>{t("legal")}</div>
          </div>
        </div>
      </div>

      {/* RIGHT: form */}
      <div style={{
        padding: "48px 56px",
        display: "flex",
        flexDirection: "column",
        background: "#faf7f2",
        position: "relative",
      }}>
        <header style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 12 }}>
          <LangPill lang={lang} setLang={setLang} />
        </header>

        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: "100%", maxWidth: 420, position: "relative" }}>
            {f.success && <SuccessOverlay t={t} />}

            {/* tab switcher */}
            <div style={{
              display: "inline-flex",
              fontFamily: "'Instrument Serif', serif",
              fontSize: 15,
              marginBottom: 32,
              gap: 24,
            }}>
              {[["signin", t("signin")], ["signup", t("signup")]].map(([k, label]) => (
                <button key={k}
                  onClick={() => f.setMode(k)}
                  style={{
                    padding: "4px 0",
                    background: "transparent",
                    border: "none",
                    borderBottom: `1.5px solid ${f.mode === k ? "#0b0d10" : "transparent"}`,
                    color: f.mode === k ? "#0b0d10" : "rgba(11,13,16,0.4)",
                    fontSize: 22,
                    cursor: "pointer",
                    fontFamily: "inherit",
                  }}
                >
                  {label}
                </button>
              ))}
            </div>

            <h2 style={{
              fontFamily: "'Instrument Serif', serif",
              fontSize: 34,
              lineHeight: 1.05,
              margin: 0,
              fontWeight: 400,
              letterSpacing: -0.5,
            }}>
              {f.mode === "signin" ? "Добро пожаловать обратно." : "Откройте аккаунт."}
            </h2>
            <p style={{
              fontSize: 14, color: "rgba(11,13,16,0.6)", marginTop: 10, marginBottom: 28,
            }}>
              {t("sub")}
            </p>

            {/* role selector for signup */}
            {f.mode === "signup" && (
              <div style={{ marginBottom: 20, animation: "slideUp .3s ease" }}>
                <div style={{
                  fontSize: 12, textTransform: "uppercase", letterSpacing: 0.4,
                  color: "rgba(11,13,16,0.5)", marginBottom: 10, fontWeight: 500,
                }}>{t("roleTitle")}</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  <RoleChip active={f.role === "sme"} onClick={() => f.setRole("sme")} title={t("role_sme")} desc={t("role_smeDesc")} />
                  <RoleChip active={f.role === "corp"} onClick={() => f.setRole("corp")} title={t("role_corp")} desc={t("role_corpDesc")} />
                  <RoleChip active={f.role === "individual"} onClick={() => f.setRole("individual")} title={t("role_individual")} desc={t("role_individualDesc")} />
                </div>
              </div>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <FloatField
                label={t("email")}
                value={f.email}
                onChange={f.setEmail}
                type="email"
                placeholder={t("emailPh")}
                autoComplete="email"
              />
              <PasswordField value={f.password} onChange={f.setPassword} t={t} />
            </div>

            {f.error && (
              <div style={{
                marginTop: 12, fontSize: 12,
                fontFamily: "'JetBrains Mono', monospace",
                color: "#a03030",
                animation: "slideUp .2s",
              }}>
                {f.error === "email" ? "▲ Проверьте email" : "▲ Пароль слишком короткий"}
              </div>
            )}

            {f.mode === "signin" && (
              <div style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                marginTop: 16, marginBottom: 24,
              }}>
                <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "rgba(11,13,16,0.65)", cursor: "pointer" }}>
                  <input type="checkbox" checked={f.remember} onChange={(e) => f.setRemember(e.target.checked)}
                    style={{ width: 15, height: 15, accentColor: "#0b0d10", cursor: "pointer" }} />
                  {t("remember")}
                </label>
                <a href="#" onClick={(e) => e.preventDefault()} style={{
                  fontSize: 13, color: "#0b0d10", textDecoration: "underline", textUnderlineOffset: 3,
                }}>{t("forgot")}</a>
              </div>
            )}
            {f.mode === "signup" && <div style={{ height: 24 }} />}

            <SubmitButton onClick={f.submit} loading={f.loading} variant="dark">
              {f.mode === "signin" ? t("submit") : t("submitRegister")}
            </SubmitButton>

            <div style={{
              marginTop: 24, fontSize: 13, textAlign: "center",
              color: "rgba(11,13,16,0.6)",
            }}>
              {f.mode === "signin" ? t("noAccount") : t("haveAccount")}{" "}
              <button onClick={() => f.setMode(f.mode === "signin" ? "signup" : "signin")}
                style={{
                  background: "transparent", border: "none",
                  color: "#0b0d10", cursor: "pointer", textDecoration: "underline",
                  textUnderlineOffset: 3, padding: 0, fontSize: 13,
                }}>
                {f.mode === "signin" ? t("signupCta") : t("signinCta")}
              </button>
            </div>
          </div>
        </div>

        {/* footer status */}
        <div style={{
          display: "flex", alignItems: "center", gap: 8,
          fontSize: 11, letterSpacing: 0.5, textTransform: "uppercase",
          color: "rgba(11,13,16,0.45)",
          fontFamily: "'JetBrains Mono', monospace",
          justifyContent: "flex-end",
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: 999,
            background: "#2a8c4f", animation: "pulse 2s ease-in-out infinite",
          }} />
          {t("statusOk")}
        </div>
      </div>
    </div>
  );
}

window.V1Editorial = V1Editorial;

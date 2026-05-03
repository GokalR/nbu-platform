// Variation 4: Guided Stepper
// Multi-step flow with progress: role -> credentials -> confirm.
// Warm minimal, focus on guidance.

function V4Stepper() {
  const { lang, setLang, t } = useLang();
  const f = useAuthForm();
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const steps = [t("stepRole"), t("stepCreds"), t("stepReady")];

  const canNext = () => {
    if (step === 0) return !!f.role;
    if (step === 1) return f.email.includes("@") && f.password.length >= 6;
    return true;
  };

  const go = (dir) => {
    if (dir === 1) {
      if (step === steps.length - 1) { f.submit(); return; }
      if (canNext()) setStep((s) => s + 1);
    } else {
      if (step > 0) setStep((s) => s - 1);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#f4efe6",
      color: "#0b0d10",
      display: "flex", flexDirection: "column",
      fontFamily: "Inter, system-ui, sans-serif",
      position: "relative",
    }}>
      {/* decorative side rail */}
      <div aria-hidden style={{
        position: "absolute", left: 0, top: 0, bottom: 0, width: 280,
        backgroundImage: "repeating-linear-gradient(135deg, rgba(11,13,16,0.025) 0 2px, transparent 2px 10px)",
        pointerEvents: "none",
      }} />

      <header style={{
        padding: "24px 40px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "relative", zIndex: 2,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <BrandMark size={26} />
          <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: -0.2 }}>NBU AI Platform</span>
        </div>
        <LangPill lang={lang} setLang={setLang} />
      </header>

      <div style={{
        flex: 1,
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: "40px 24px", position: "relative", zIndex: 2,
      }}>
        <div style={{ width: "100%", maxWidth: 520, position: "relative" }}>
          {f.success && <SuccessOverlay t={t} />}

          {/* progress bar */}
          <div style={{ marginBottom: 36 }}>
            <div style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              fontSize: 11, letterSpacing: 1.2, textTransform: "uppercase",
              color: "rgba(11,13,16,0.5)", marginBottom: 10, fontWeight: 600,
              fontFamily: "'JetBrains Mono', monospace",
            }}>
              <span>{t("step")} {step + 1} {t("of")} {steps.length} · {steps[step]}</span>
              <span>{Math.round(((step + 1) / steps.length) * 100)}%</span>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              {steps.map((_, i) => (
                <div key={i} style={{
                  flex: 1, height: 3, borderRadius: 999,
                  background: i <= step ? "#0b0d10" : "rgba(11,13,16,0.12)",
                  transition: "background .3s ease",
                }} />
              ))}
            </div>
          </div>

          <div style={{
            background: "#faf7f2",
            border: "1px solid rgba(11,13,16,0.08)",
            borderRadius: 20,
            padding: 36,
            boxShadow: "0 30px 60px -30px rgba(11,13,16,0.15)",
            minHeight: 460,
            display: "flex", flexDirection: "column",
          }}>
            <div style={{ flex: 1 }}>
              {step === 0 && (
                <div style={{ animation: "slideUp .3s" }}>
                  <h2 style={{
                    fontSize: 30, letterSpacing: -0.6, lineHeight: 1.1,
                    margin: 0, fontWeight: 700,
                  }}>{t("roleTitle")}</h2>
                  <p style={{ fontSize: 14, color: "rgba(11,13,16,0.6)", marginTop: 10, marginBottom: 26 }}>
                    Это поможет нам показать правильные инструменты.
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    <RoleChip active={f.role === "sme"} onClick={() => f.setRole("sme")} title={t("role_sme")} desc={t("role_smeDesc")} />
                    <RoleChip active={f.role === "corp"} onClick={() => f.setRole("corp")} title={t("role_corp")} desc={t("role_corpDesc")} />
                    <RoleChip active={f.role === "individual"} onClick={() => f.setRole("individual")} title={t("role_individual")} desc={t("role_individualDesc")} />
                  </div>
                </div>
              )}

              {step === 1 && (
                <div style={{ animation: "slideUp .3s" }}>
                  <h2 style={{ fontSize: 30, letterSpacing: -0.6, lineHeight: 1.1, margin: 0, fontWeight: 700 }}>
                    {t("stepCreds")}
                  </h2>
                  <p style={{ fontSize: 14, color: "rgba(11,13,16,0.6)", marginTop: 10, marginBottom: 26 }}>
                    Используйте корпоративный email для доступа к расширенным функциям.
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    <FloatField label={t("email")} value={f.email} onChange={f.setEmail} type="email" placeholder={t("emailPh")} autoComplete="email" />
                    <PasswordField value={f.password} onChange={f.setPassword} t={t} />
                  </div>
                  <label style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 13,
                    color: "rgba(11,13,16,0.65)", cursor: "pointer", marginTop: 18 }}>
                    <input type="checkbox" checked={f.remember} onChange={(e) => f.setRemember(e.target.checked)}
                      style={{ width: 15, height: 15, accentColor: "#0b0d10" }} />
                    {t("remember")}
                  </label>
                </div>
              )}

              {step === 2 && (
                <div style={{ animation: "slideUp .3s" }}>
                  <h2 style={{ fontSize: 30, letterSpacing: -0.6, lineHeight: 1.1, margin: 0, fontWeight: 700 }}>
                    Всё готово.
                  </h2>
                  <p style={{ fontSize: 14, color: "rgba(11,13,16,0.6)", marginTop: 10, marginBottom: 26 }}>
                    Проверьте данные перед входом.
                  </p>
                  <div style={{
                    background: "rgba(11,13,16,0.03)",
                    border: "1px solid rgba(11,13,16,0.08)",
                    borderRadius: 12,
                    padding: 18,
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 13, lineHeight: 1.9,
                  }}>
                    <div><span style={{ color: "rgba(11,13,16,0.5)" }}>role:</span> {f.role}</div>
                    <div><span style={{ color: "rgba(11,13,16,0.5)" }}>email:</span> {f.email || "—"}</div>
                    <div><span style={{ color: "rgba(11,13,16,0.5)" }}>lang:</span> {lang}</div>
                    <div><span style={{ color: "rgba(11,13,16,0.5)" }}>remember:</span> {f.remember ? "true" : "false"}</div>
                  </div>
                  <div style={{
                    marginTop: 18, display: "flex", alignItems: "center", gap: 10,
                    fontSize: 12, color: "rgba(11,13,16,0.6)",
                  }}>
                    <span style={{ width: 6, height: 6, borderRadius: 999, background: "#2a8c4f" }} />
                    {t("legal")}
                  </div>
                </div>
              )}
            </div>

            {f.error && step === 1 && (
              <div style={{ fontSize: 12, color: "#a03030", fontWeight: 500, marginBottom: 10 }}>
                ▲ {f.error === "email" ? "Проверьте email" : "Пароль слишком короткий"}
              </div>
            )}

            <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
              {step > 0 && (
                <button onClick={() => go(-1)} style={{
                  padding: "14px 22px", borderRadius: 12,
                  background: "transparent", border: "1px solid rgba(11,13,16,0.15)",
                  color: "#0b0d10", fontSize: 14, fontWeight: 500, cursor: "pointer",
                }}>
                  ← {t("back")}
                </button>
              )}
              <div style={{ flex: 1 }}>
                <SubmitButton onClick={() => go(1)} disabled={!canNext()} loading={f.loading}>
                  {step === steps.length - 1 ? t("submit") : t("next")}
                </SubmitButton>
              </div>
            </div>
          </div>

          <div style={{
            marginTop: 20, textAlign: "center", fontSize: 13, color: "rgba(11,13,16,0.55)",
          }}>
            {t("noAccount")}{" "}
            <a href="#" onClick={(e) => e.preventDefault()} style={{ color: "#0b0d10", fontWeight: 600, textDecoration: "underline", textUnderlineOffset: 3 }}>
              {t("signupCta")}
            </a>
          </div>
        </div>
      </div>

      <footer style={{
        padding: "16px 40px",
        fontSize: 11, letterSpacing: 0.4, color: "rgba(11,13,16,0.45)",
        display: "flex", justifyContent: "space-between",
        position: "relative", zIndex: 2,
      }}>
        <span>{t("copyright")}</span>
        <span>{t("legal")}</span>
      </footer>
    </div>
  );
}

window.V4Stepper = V4Stepper;

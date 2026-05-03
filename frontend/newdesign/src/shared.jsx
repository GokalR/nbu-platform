// Shared utilities, hooks, and micro-components across the 4 variants.

const { useState, useEffect, useRef, useMemo, useCallback } = React;

// ---------- i18n ----------
const COPY = {
  ru: {
    brand: "NBU AI Platform",
    sub: "Доступ к AI-инструментам для анализа, обучения и управления бизнесом",
    kicker: "National Bank · AI Platform",
    signin: "Вход",
    signup: "Регистрация",
    email: "Email",
    emailPh: "you@company.uz",
    password: "Пароль",
    passwordPh: "Минимум 8 символов",
    passwordShow: "Показать",
    passwordHide: "Скрыть",
    remember: "Запомнить меня",
    forgot: "Забыли пароль?",
    submit: "Войти в платформу",
    submitRegister: "Создать аккаунт",
    roleTitle: "Я вхожу как",
    role_sme: "Малый бизнес",
    role_smeDesc: "ИП и МСБ, до 100 сотрудников",
    role_corp: "Корпоративный клиент",
    role_corpDesc: "Средний и крупный бизнес",
    role_individual: "Частное лицо",
    role_individualDesc: "Физические лица",
    noAccount: "Нет аккаунта?",
    haveAccount: "Уже есть аккаунт?",
    signupCta: "Зарегистрироваться",
    signinCta: "Войти",
    copyright: "© 2026 NBU AI Platform",
    legal: "Защищено end-to-end шифрованием",
    tools: "Инструменты",
    tool1: "Аналитика регионов",
    tool1d: "14 регионов, 199 районов",
    tool2: "AI Бизнес-советник",
    tool2d: "Персонализированный анализ",
    tool3: "Финансовая грамотность",
    tool3d: "Курсы и симуляции",
    tool4: "Финконтроль",
    tool4d: "Управление денежными потоками",
    step: "Шаг",
    of: "из",
    next: "Продолжить",
    back: "Назад",
    stepRole: "Выберите роль",
    stepCreds: "Введите данные",
    stepReady: "Готово",
    welcome: "Добро пожаловать",
    welcomeSub: "Перенаправляем в вашу панель…",
    stat1Label: "активных бизнесов",
    stat2Label: "районов Узбекистана",
    stat3Label: "моделей точности",
    statusOk: "Все системы работают",
    heroTitle: "Интеллект для вашего бизнеса.",
    heroBody: "Платформа объединяет аналитику регионов, AI-советника и инструменты финансового планирования в одном защищённом окружении.",
    feat1: "Региональная аналитика в реальном времени",
    feat2: "Персональные рекомендации AI-советника",
    feat3: "Шифрование и банковский уровень защиты",
    quote: "«Платформа сократила нам время на отчётность с трёх дней до получаса.»",
    quoteBy: "— Азиза К., финдиректор торговой сети",
  },
  uz: {
    brand: "NBU AI Platform",
    sub: "Biznesni tahlil qilish va boshqarish uchun AI vositalari",
    kicker: "Milliy Bank · AI Platforma",
    signin: "Kirish",
    signup: "Ro'yxatdan o'tish",
    email: "Email",
    emailPh: "you@company.uz",
    password: "Parol",
    passwordPh: "Kamida 8 ta belgi",
    passwordShow: "Ko'rsatish",
    passwordHide: "Yashirish",
    remember: "Meni eslab qol",
    forgot: "Parolni unutdingizmi?",
    submit: "Platformaga kirish",
    submitRegister: "Akkaunt yaratish",
    roleTitle: "Men quyidagi sifatida kiraman",
    role_sme: "Kichik biznes",
    role_smeDesc: "Yakka tartib va KOB, 100 gacha xodim",
    role_corp: "Korporativ mijoz",
    role_corpDesc: "O'rta va yirik biznes",
    role_individual: "Jismoniy shaxs",
    role_individualDesc: "Individual foydalanuvchilar",
    noAccount: "Akkauntingiz yo'qmi?",
    haveAccount: "Akkauntingiz bormi?",
    signupCta: "Ro'yxatdan o'tish",
    signinCta: "Kirish",
    copyright: "© 2026 NBU AI Platform",
    legal: "End-to-end shifrlash bilan himoyalangan",
    tools: "Vositalar",
    tool1: "Hududlar tahlili",
    tool1d: "14 viloyat, 199 tuman",
    tool2: "AI Biznes maslahatchi",
    tool2d: "Shaxsiy tahlil",
    tool3: "Moliyaviy savodxonlik",
    tool3d: "Kurslar va simulyatorlar",
    tool4: "Moliya nazorati",
    tool4d: "Pul oqimlarini boshqarish",
    step: "Qadam",
    of: "dan",
    next: "Davom etish",
    back: "Orqaga",
    stepRole: "Rolingizni tanlang",
    stepCreds: "Ma'lumotlarni kiriting",
    stepReady: "Tayyor",
    welcome: "Xush kelibsiz",
    welcomeSub: "Panelingizga yo'naltirilmoqda…",
    stat1Label: "faol bizneslar",
    stat2Label: "tumanlar",
    stat3Label: "modellar aniqligi",
    statusOk: "Barcha tizimlar ishlayapti",
    heroTitle: "Biznesingiz uchun intellekt.",
    heroBody: "Platforma hudud tahlili, AI maslahatchi va moliyaviy rejalashtirish vositalarini bitta himoyalangan muhitda birlashtiradi.",
    feat1: "Real vaqtda hududiy tahlil",
    feat2: "AI maslahatchining shaxsiy tavsiyalari",
    feat3: "Bank darajasidagi shifrlash",
    quote: "«Platforma hisobot vaqtimizni 3 kundan yarim soatga qisqartirdi.»",
    quoteBy: "— Aziza K., savdo tarmog'i moliya direktori",
  },
};

function useLang(initial = "ru") {
  const [lang, setLang] = useState(initial);
  const t = (k) => COPY[lang][k] ?? k;
  return { lang, setLang, t };
}

// ---------- Logo mark (abstract, original) ----------
function BrandMark({ size = 28, tone = "ink" }) {
  const fg = tone === "ink" ? "#0b0d10" : tone === "cream" ? "#f4efe6" : tone;
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
      <rect x="1.5" y="1.5" width="29" height="29" rx="8" stroke={fg} strokeWidth="1.5" fill="none" />
      <path d="M9 22 L9 10 L16 20 L23 10 L23 22" stroke={fg} strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="16" cy="16" r="1.5" fill={fg} />
    </svg>
  );
}

// ---------- Form input ----------
function FloatField({ label, value, onChange, type = "text", placeholder, right, variant = "light", autoComplete }) {
  const [focus, setFocus] = useState(false);
  const dark = variant === "dark";
  return (
    <label style={{ display: "block", position: "relative" }}>
      <span style={{
        display: "block",
        fontSize: 12,
        letterSpacing: 0.3,
        textTransform: "uppercase",
        color: dark ? "rgba(244,239,230,0.55)" : "rgba(11,13,16,0.55)",
        marginBottom: 8,
        fontWeight: 500,
      }}>{label}</span>
      <div style={{
        position: "relative",
        display: "flex",
        alignItems: "center",
        background: dark ? "rgba(255,255,255,0.04)" : "#fff",
        border: `1px solid ${focus ? (dark ? "rgba(244,239,230,0.4)" : "#0b0d10") : (dark ? "rgba(244,239,230,0.12)" : "rgba(11,13,16,0.12)")}`,
        borderRadius: 12,
        transition: "border-color .18s ease, background .18s ease",
      }}>
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          style={{
            flex: 1,
            background: "transparent",
            border: "none",
            padding: "14px 16px",
            fontSize: 15,
            color: dark ? "#f4efe6" : "#0b0d10",
          }}
        />
        {right}
      </div>
    </label>
  );
}

// ---------- Password field w/ show toggle ----------
function PasswordField({ value, onChange, t, variant, label, placeholder }) {
  const [show, setShow] = useState(false);
  const dark = variant === "dark";
  return (
    <FloatField
      label={label || t("password")}
      value={value}
      onChange={onChange}
      type={show ? "text" : "password"}
      placeholder={placeholder || t("passwordPh")}
      variant={variant}
      autoComplete="current-password"
      right={
        <button
          type="button"
          onClick={() => setShow((s) => !s)}
          style={{
            background: "transparent",
            border: "none",
            marginRight: 8,
            padding: "6px 10px",
            borderRadius: 8,
            fontSize: 12,
            letterSpacing: 0.2,
            color: dark ? "rgba(244,239,230,0.7)" : "rgba(11,13,16,0.6)",
            cursor: "pointer",
          }}
        >
          {show ? t("passwordHide") : t("passwordShow")}
        </button>
      }
    />
  );
}

// ---------- Language switcher ----------
function LangPill({ lang, setLang, variant = "light" }) {
  const dark = variant === "dark";
  const btn = (code, label) => (
    <button
      key={code}
      onClick={() => setLang(code)}
      style={{
        padding: "6px 12px",
        background: lang === code ? (dark ? "#f4efe6" : "#0b0d10") : "transparent",
        color: lang === code ? (dark ? "#0b0d10" : "#f4efe6") : (dark ? "rgba(244,239,230,0.7)" : "rgba(11,13,16,0.6)"),
        border: "none",
        borderRadius: 999,
        fontSize: 12,
        letterSpacing: 0.4,
        fontWeight: 600,
        cursor: "pointer",
      }}
    >
      {label}
    </button>
  );
  return (
    <div style={{
      display: "inline-flex",
      padding: 3,
      borderRadius: 999,
      border: `1px solid ${dark ? "rgba(244,239,230,0.15)" : "rgba(11,13,16,0.12)"}`,
      background: dark ? "rgba(255,255,255,0.03)" : "rgba(255,255,255,0.6)",
    }}>
      {btn("ru", "RU")}
      {btn("uz", "UZ")}
    </div>
  );
}

// ---------- Role chip ----------
function RoleChip({ active, onClick, title, desc, variant = "light" }) {
  const dark = variant === "dark";
  return (
    <button
      onClick={onClick}
      style={{
        textAlign: "left",
        padding: "14px 16px",
        borderRadius: 12,
        border: `1px solid ${active ? (dark ? "#f4efe6" : "#0b0d10") : (dark ? "rgba(244,239,230,0.12)" : "rgba(11,13,16,0.1)")}`,
        background: active ? (dark ? "rgba(244,239,230,0.06)" : "rgba(11,13,16,0.03)") : "transparent",
        cursor: "pointer",
        transition: "all .18s ease",
        display: "flex",
        alignItems: "center",
        gap: 12,
        width: "100%",
      }}
    >
      <div style={{
        width: 18, height: 18, borderRadius: 999,
        border: `1.5px solid ${active ? (dark ? "#f4efe6" : "#0b0d10") : (dark ? "rgba(244,239,230,0.3)" : "rgba(11,13,16,0.25)")}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        flexShrink: 0,
      }}>
        {active && <div style={{ width: 8, height: 8, borderRadius: 999, background: dark ? "#f4efe6" : "#0b0d10" }} />}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: dark ? "#f4efe6" : "#0b0d10" }}>{title}</div>
        <div style={{ fontSize: 12, color: dark ? "rgba(244,239,230,0.55)" : "rgba(11,13,16,0.55)", marginTop: 2 }}>{desc}</div>
      </div>
    </button>
  );
}

// ---------- Submit button ----------
function SubmitButton({ children, onClick, variant = "dark", loading, disabled }) {
  const dark = variant === "dark";
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        width: "100%",
        padding: "16px 20px",
        borderRadius: 12,
        border: "none",
        background: dark ? "#0b0d10" : "#f4efe6",
        color: dark ? "#f4efe6" : "#0b0d10",
        fontSize: 15,
        fontWeight: 600,
        letterSpacing: 0.1,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.4 : 1,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
        transition: "transform .1s ease, opacity .18s ease",
      }}
      onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.99)")}
      onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
    >
      {loading ? <Spinner variant={variant} /> : children}
      {!loading && <span style={{ opacity: 0.6, fontWeight: 400 }}>→</span>}
    </button>
  );
}

function Spinner({ variant = "dark" }) {
  const dark = variant === "dark";
  return (
    <span style={{
      width: 16, height: 16, borderRadius: 999,
      border: `2px solid ${dark ? "rgba(244,239,230,0.3)" : "rgba(11,13,16,0.3)"}`,
      borderTopColor: dark ? "#f4efe6" : "#0b0d10",
      animation: "spin 0.7s linear infinite",
      display: "inline-block",
    }} />
  );
}

// ---------- Success overlay ----------
function SuccessOverlay({ t, variant = "light" }) {
  const dark = variant === "dark";
  return (
    <div style={{
      position: "absolute", inset: 0,
      background: dark ? "rgba(11,13,16,0.92)" : "rgba(250,247,242,0.94)",
      backdropFilter: "blur(8px)",
      borderRadius: "inherit",
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      gap: 12,
      animation: "fade .25s ease",
      zIndex: 10,
    }}>
      <div style={{
        width: 44, height: 44, borderRadius: 999,
        background: dark ? "#f4efe6" : "#0b0d10",
        color: dark ? "#0b0d10" : "#f4efe6",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 20,
        animation: "pop .4s cubic-bezier(.2,.9,.3,1.3)",
      }}>✓</div>
      <div style={{ fontSize: 16, fontWeight: 600, color: dark ? "#f4efe6" : "#0b0d10" }}>{t("welcome")}</div>
      <div style={{ fontSize: 13, color: dark ? "rgba(244,239,230,0.6)" : "rgba(11,13,16,0.55)" }}>{t("welcomeSub")}</div>
    </div>
  );
}

// ---------- Keyframe styles (injected once) ----------
function KeyframeStyles() {
  return (
    <style>{`
      @keyframes spin { to { transform: rotate(360deg); } }
      @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
      @keyframes pop { 0% { transform: scale(0); } 100% { transform: scale(1); } }
      @keyframes slideUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.55; } }
      @keyframes floaty { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
      @keyframes shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }
      input::placeholder { color: rgba(11,13,16,0.3); }
      .dark-placeholder input::placeholder { color: rgba(244,239,230,0.3); }
      button, a { font-family: inherit; }
    `}</style>
  );
}

// ---------- Shared form hook ----------
function useAuthForm() {
  const [mode, setMode] = useState("signin"); // signin | signup
  const [role, setRole] = useState("sme"); // sme | corp | individual
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const submit = useCallback(() => {
    setError("");
    if (!email || !email.includes("@")) { setError("email"); return; }
    if (password.length < 6) { setError("password"); return; }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2200);
    }, 900);
  }, [email, password]);

  return { mode, setMode, role, setRole, email, setEmail, password, setPassword, remember, setRemember, loading, success, error, submit };
}

Object.assign(window, {
  COPY, useLang, BrandMark, FloatField, PasswordField, LangPill, RoleChip,
  SubmitButton, Spinner, SuccessOverlay, KeyframeStyles, useAuthForm,
});

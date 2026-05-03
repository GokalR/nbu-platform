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
    // V3 hero
    v3_hero_a: "Войдите в",
    v3_hero_b: "интеллект",
    v3_hero_c: "вашего бизнеса.",
    v3_sub: "Региональная аналитика, AI-советник и инструменты финансового планирования — в одной защищённой платформе.",
    err_email: "Проверьте email",
    err_password: "Пароль слишком короткий",
    // V3 dashboard
    v3_analytics: "АНАЛИТИКА РЕГИОНОВ",
    v3_region: "Ферганская область",
    v3_region_meta: "Q2 · 2026 · 15 районов",
    v3_map_kicker: "КАРТА · ФЕРГАНСКАЯ ДОЛИНА",
    v3_map_sub: "15 районов · 4 города",
    v3_stat_districts: "15 районов",
    v3_stat_cities: "4 города",
    v3_stat_pop: "3.7M чел.",
    v3_kpi1_l: "ВРП района",
    v3_kpi1_u: "млрд сум",
    v3_kpi2_l: "Инвестиции",
    v3_kpi2_u: "млрд сум",
    v3_kpi3_l: "Активных МСБ",
    v3_kpi3_u: "+342 мес.",
    v3_chart_title: "ВРП по кварталам",
    v3_tool1: "Аналитика",
    v3_tool1d: "14 регионов",
    v3_tool2: "Советник",
    v3_tool2d: "AI бот",
    v3_tool3: "Обучение",
    v3_tool3d: "Курсы МСБ",
    v3_tool4: "Финконтроль",
    v3_tool4d: "Потоки",
    v3_badge_l: "Покрытие платформы",
    v3_badge_v: "14 регионов · 650K+ бизнесов",
    v3_top_badge: "Данные обновлены · 14 мин назад",
    v3_ai_advisor: "AI СОВЕТНИК",
    v3_ai_analytics: "АНАЛИТИКА",
    v3_ai_rec: "РЕКОМЕНДАЦИЯ",
    v3_ai_msg1: "Рост МСБ в Фергане +18% за квартал",
    v3_ai_msg2: "Экспорт текстиля Намангана превысил план на 4.2%",
    v3_ai_msg3: "Кредитная ёмкость региона Сурхандарья +12%",
    v3_ai_msg4: "Предупреждение: отток рабочей силы в Хорезме",
    v3_yoy: "г/г",
    v3_grp_label: "ВРП",
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
    // V3 hero
    v3_hero_a: "Biznesingiz",
    v3_hero_b: "intellektiga",
    v3_hero_c: "kiring.",
    v3_sub: "Hududiy tahlil, AI maslahatchi va moliyaviy rejalashtirish vositalari — bitta himoyalangan platformada.",
    err_email: "Emailni tekshiring",
    err_password: "Parol juda qisqa",
    // V3 dashboard
    v3_analytics: "HUDUDLAR TAHLILI",
    v3_region: "Farg'ona viloyati",
    v3_region_meta: "Q2 · 2026 · 15 tuman",
    v3_map_kicker: "XARITA · FARG'ONA VODIYSI",
    v3_map_sub: "15 tuman · 4 shahar",
    v3_stat_districts: "15 tuman",
    v3_stat_cities: "4 shahar",
    v3_stat_pop: "3.7M kishi",
    v3_kpi1_l: "HMM (tuman)",
    v3_kpi1_u: "mlrd so'm",
    v3_kpi2_l: "Investitsiyalar",
    v3_kpi2_u: "mlrd so'm",
    v3_kpi3_l: "Faol KOB",
    v3_kpi3_u: "+342 oyiga",
    v3_chart_title: "HMM choraklar bo'yicha",
    v3_tool1: "Tahlil",
    v3_tool1d: "14 viloyat",
    v3_tool2: "Maslahatchi",
    v3_tool2d: "AI bot",
    v3_tool3: "Ta'lim",
    v3_tool3d: "KOB kurslari",
    v3_tool4: "Moliya nazorati",
    v3_tool4d: "Oqimlar",
    v3_badge_l: "Platforma qamrovi",
    v3_badge_v: "14 viloyat · 650K+ biznes",
    v3_top_badge: "Ma'lumotlar yangilangan · 14 daq. oldin",
    v3_ai_advisor: "AI MASLAHATCHI",
    v3_ai_analytics: "TAHLIL",
    v3_ai_rec: "TAVSIYA",
    v3_ai_msg1: "Farg'onada KOB o'sishi chorakda +18%",
    v3_ai_msg2: "Namangan to'qimachilik eksporti rejadan +4.2%",
    v3_ai_msg3: "Surxondaryo kredit sig'imi +12%",
    v3_ai_msg4: "Ogohlantirish: Xorazmda ishchi kuchi oqimi",
    v3_yoy: "y/y",
    v3_grp_label: "HMM",
  },
};

function useLang(initial = "uz") {
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

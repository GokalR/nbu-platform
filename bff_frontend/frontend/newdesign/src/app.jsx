// App shell: variant switcher + Tweaks panel + edit-mode protocol

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "variant": "v1",
  "showTweaks": true
}/*EDITMODE-END*/;

const VARIANTS = [
  { id: "v1", name: "Editorial", desc: "Cream + serif, split layout", Comp: () => <V1Editorial /> },
  { id: "v2", name: "Console",   desc: "Dark technical, glass card", Comp: () => <V2Console /> },
  { id: "v3", name: "Product",   desc: "Dashboard preview, light",   Comp: () => <V3Product /> },
  { id: "v4", name: "Stepper",   desc: "Guided multi-step flow",     Comp: () => <V4Stepper /> },
  { id: "v5", name: "Command",   desc: "Dark form, bright data",     Comp: () => <V5Command /> },
  { id: "v6", name: "Atlas",     desc: "14-region interactive mosaic", Comp: () => <V6Atlas /> },
  { id: "v7", name: "Terminal",  desc: "Dev-console + live log feed",  Comp: () => <V7Terminal /> },
];

function TweaksPanel({ visible, variant, setVariant }) {
  if (!visible) return null;
  return (
    <div style={{
      position: "fixed", bottom: 20, right: 20, zIndex: 1000,
      background: "#0b0d10", color: "#f4efe6",
      borderRadius: 14, padding: 14,
      border: "1px solid rgba(244,239,230,0.12)",
      boxShadow: "0 20px 50px -20px rgba(0,0,0,0.5)",
      width: 260,
      fontFamily: "Inter, system-ui, sans-serif",
    }}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        marginBottom: 12,
      }}>
        <span style={{
          fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase",
          color: "rgba(244,239,230,0.6)", fontFamily: "'JetBrains Mono', monospace",
        }}>Tweaks</span>
        <span style={{ fontSize: 10, color: "rgba(244,239,230,0.4)", fontFamily: "'JetBrains Mono', monospace" }}>
          {variant.toUpperCase()}
        </span>
      </div>
      <div style={{
        fontSize: 10.5, color: "rgba(244,239,230,0.5)", marginBottom: 8,
        letterSpacing: 0.4, textTransform: "uppercase",
      }}>Variant</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {VARIANTS.map((v) => (
          <button key={v.id} onClick={() => setVariant(v.id)} style={{
            padding: "10px 12px", textAlign: "left",
            background: variant === v.id ? "rgba(244,239,230,0.12)" : "transparent",
            border: `1px solid ${variant === v.id ? "rgba(244,239,230,0.3)" : "rgba(244,239,230,0.08)"}`,
            color: "#f4efe6", borderRadius: 9,
            cursor: "pointer", transition: "all .15s",
          }}>
            <div style={{ fontSize: 13, fontWeight: 600 }}>{v.name}</div>
            <div style={{ fontSize: 11, color: "rgba(244,239,230,0.55)", marginTop: 1 }}>{v.desc}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

function App() {
  const [tweaks, setTweaks] = useState(TWEAK_DEFAULTS);
  const [editMode, setEditMode] = useState(false);

  // restore from localStorage for quick iteration
  useEffect(() => {
    try {
      const saved = localStorage.getItem("nbu-auth-variant");
      if (saved && VARIANTS.find(v => v.id === saved)) {
        setTweaks(t => ({ ...t, variant: saved }));
      }
    } catch {}
  }, []);

  useEffect(() => {
    try { localStorage.setItem("nbu-auth-variant", tweaks.variant); } catch {}
  }, [tweaks.variant]);

  // edit-mode protocol: register listener FIRST, then announce
  useEffect(() => {
    const handler = (e) => {
      const d = e.data;
      if (!d || typeof d !== "object") return;
      if (d.type === "__activate_edit_mode") setEditMode(true);
      if (d.type === "__deactivate_edit_mode") setEditMode(false);
    };
    window.addEventListener("message", handler);
    try { window.parent.postMessage({ type: "__edit_mode_available" }, "*"); } catch {}
    return () => window.removeEventListener("message", handler);
  }, []);

  const setVariant = (id) => {
    setTweaks((t) => ({ ...t, variant: id }));
    try { window.parent.postMessage({ type: "__edit_mode_set_keys", edits: { variant: id } }, "*"); } catch {}
  };

  const current = VARIANTS.find(v => v.id === tweaks.variant) || VARIANTS[0];

  return (
    <>
      <KeyframeStyles />
      <div data-screen-label={`auth ${current.name}`}>
        <current.Comp />
      </div>
      <TweaksPanel visible={editMode} variant={tweaks.variant} setVariant={setVariant} />

      {/* Mini variant indicator when tweaks off — subtle */}
      {!editMode && (
        <div style={{
          position: "fixed", bottom: 14, left: 14, zIndex: 999,
          display: "flex", gap: 4, padding: "6px 8px",
          background: "rgba(11,13,16,0.55)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(244,239,230,0.15)",
          borderRadius: 999,
          fontFamily: "'JetBrains Mono', monospace",
        }}>
          {VARIANTS.map(v => (
            <button key={v.id} onClick={() => setVariant(v.id)} style={{
              padding: "4px 9px", fontSize: 10,
              border: "none", borderRadius: 999, cursor: "pointer",
              letterSpacing: 0.5, textTransform: "uppercase",
              background: tweaks.variant === v.id ? "#f4efe6" : "transparent",
              color: tweaks.variant === v.id ? "#0b0d10" : "rgba(244,239,230,0.7)",
              fontWeight: 600,
              fontFamily: "inherit",
            }} title={v.desc}>{v.id}</button>
          ))}
        </div>
      )}
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

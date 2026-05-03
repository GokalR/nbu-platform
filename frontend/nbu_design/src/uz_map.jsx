// Uzbekistan region map — hand-crafted SVG approximation of the 14 admin divisions.
// Authentic silhouette: Karakalpakstan west, the valley (Fergana/Namangan/Andijan)
// finger east, Tashkent city marker. Colors from NBU regionColors palette.

const UZ_REGIONS_DATA = [
  {
    k: "karakalpakstan", n: "Каракалпакстан", nLat: "Qoraqalpog'iston",
    // Huge western region, includes Aral Sea area
    d: "M 40,40 L 130,30 L 215,40 L 260,75 L 310,95 L 315,135 L 285,165 L 235,175 L 205,225 L 180,280 L 115,315 L 60,295 L 35,240 L 25,175 L 30,110 Z",
    cx: 150, cy: 160, color: "#C8D7E8",
  },
  {
    k: "khorezm", n: "Хорезм", nLat: "Xorazm",
    d: "M 225,220 L 280,205 L 310,215 L 315,245 L 285,265 L 240,260 L 220,240 Z",
    cx: 270, cy: 235, color: "#B4CFE5",
  },
  {
    k: "navoi", n: "Навои", nLat: "Navoiy",
    d: "M 240,265 L 315,250 L 395,240 L 470,245 L 495,290 L 475,340 L 410,355 L 340,335 L 280,305 Z",
    cx: 380, cy: 295, color: "#A8BFD9",
  },
  {
    k: "bukhara", n: "Бухара", nLat: "Buxoro",
    d: "M 285,310 L 345,340 L 410,360 L 425,405 L 390,440 L 340,430 L 295,395 L 280,345 Z",
    cx: 355, cy: 385, color: "#9BB5D3",
  },
  {
    k: "kashkadarya", n: "Кашкадарья", nLat: "Qashqadaryo",
    d: "M 430,410 L 495,385 L 565,395 L 590,440 L 570,480 L 500,495 L 440,470 L 420,435 Z",
    cx: 500, cy: 440, color: "#8FAACC",
  },
  {
    k: "surkhandarya", n: "Сурхандарья", nLat: "Surxondaryo",
    d: "M 510,500 L 575,490 L 600,530 L 595,580 L 560,615 L 530,595 L 515,555 Z",
    cx: 555, cy: 550, color: "#829EC4",
  },
  {
    k: "samarkand", n: "Самарканд", nLat: "Samarqand",
    d: "M 475,345 L 550,335 L 610,355 L 625,390 L 595,415 L 525,395 L 485,375 Z",
    cx: 555, cy: 375, color: "#7FB5E6",
  },
  {
    k: "jizzakh", n: "Джизак", nLat: "Jizzax",
    d: "M 580,300 L 650,290 L 700,310 L 705,345 L 665,365 L 615,355 L 590,335 Z",
    cx: 645, cy: 325, color: "#93C5FD",
  },
  {
    k: "syrdarya", n: "Сырдарья", nLat: "Sirdaryo",
    d: "M 670,270 L 715,265 L 740,285 L 735,315 L 705,320 L 680,300 Z",
    cx: 705, cy: 293, color: "#7FB5E6",
  },
  {
    k: "tashkent_reg", n: "Ташкентская обл.", nLat: "Toshkent",
    d: "M 700,205 L 765,195 L 820,205 L 850,230 L 855,270 L 820,290 L 770,285 L 735,265 L 710,240 Z",
    cx: 780, cy: 245, color: "#6BA3D9",
  },
  {
    k: "tashkent_city", n: "Ташкент", nLat: "Toshkent shahri",
    // tiny enclave
    d: "M 792,235 L 810,232 L 818,245 L 810,258 L 792,255 L 788,245 Z",
    cx: 802, cy: 245, color: "#003D7C", isCity: true,
  },
  {
    k: "namangan", n: "Наманган", nLat: "Namangan",
    d: "M 825,215 L 880,205 L 935,220 L 955,255 L 935,275 L 880,280 L 845,260 Z",
    cx: 890, cy: 242, color: "#0054A6",
  },
  {
    k: "andijan", n: "Андижан", nLat: "Andijon",
    d: "M 940,260 L 985,250 L 1010,275 L 1005,305 L 970,320 L 935,300 Z",
    cx: 975, cy: 285, color: "#2563EB",
  },
  {
    k: "fergana", n: "Фергана", nLat: "Farg'ona",
    d: "M 880,290 L 945,285 L 990,310 L 1000,345 L 960,370 L 895,365 L 860,340 L 855,315 Z",
    cx: 925, cy: 325, color: "#3B82F6", highlight: true,
  },
];

function UzMap({ highlight = "fergana", onHover }) {
  const [hov, setHov] = useState(null);
  const VIEW_W = 1030;
  const VIEW_H = 640;

  return (
    <svg
      viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
      style={{ width: "100%", height: "auto", display: "block", overflow: "visible" }}
      aria-hidden
    >
      <defs>
        <filter id="uz-shadow" x="-10%" y="-10%" width="120%" height="120%">
          <feDropShadow dx="0" dy="3" stdDeviation="4" floodColor="#000" floodOpacity="0.35" />
        </filter>
        <linearGradient id="uz-fergana-gradient" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#60A5FA" />
          <stop offset="100%" stopColor="#2563EB" />
        </linearGradient>
        <pattern id="uz-dots" x="0" y="0" width="6" height="6" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="0.6" fill="rgba(255,255,255,0.12)" />
        </pattern>
      </defs>

      {/* base subtle halo under country */}
      <path
        d={UZ_REGIONS_DATA.map(r => r.d).join(" ")}
        fill="rgba(255,255,255,0.02)"
        style={{ filter: "blur(8px)" }}
      />

      {/* regions */}
      {UZ_REGIONS_DATA.map(r => {
        const isActive = r.k === highlight;
        const isHover = r.k === hov;
        const dim = highlight && !isActive && !isHover;
        return (
          <g key={r.k}>
            <path
              d={r.d}
              fill={
                isActive
                  ? "url(#uz-fergana-gradient)"
                  : r.isCity
                    ? "#003D7C"
                    : "rgba(255,255,255,0.08)"
              }
              fillOpacity={isActive ? 1 : (isHover ? 0.85 : dim ? 0.35 : 0.7)}
              stroke="#fff"
              strokeWidth={isActive ? 2 : 0.9}
              strokeOpacity={isActive ? 1 : 0.4}
              strokeLinejoin="round"
              style={{
                filter: isActive ? "url(#uz-shadow)" : "none",
                transition: "fill-opacity .2s, stroke-width .2s",
                cursor: "pointer",
              }}
              onMouseEnter={() => { setHov(r.k); onHover && onHover(r.k); }}
              onMouseLeave={() => { setHov(null); onHover && onHover(null); }}
            />
            {isActive && (
              <>
                <circle cx={r.cx} cy={r.cy} r="5" fill="#fff" />
                <circle cx={r.cx} cy={r.cy} r="9" fill="none" stroke="#fff" strokeWidth="1.5" opacity="0.7">
                  <animate attributeName="r" values="5;18;5" dur="2.4s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.8;0;0.8" dur="2.4s" repeatCount="indefinite" />
                </circle>
              </>
            )}
          </g>
        );
      })}

      {/* dotted overlay on Fergana to make it feel active */}
      {UZ_REGIONS_DATA.filter(r => r.k === highlight).map(r => (
        <path key={`dot-${r.k}`} d={r.d} fill="url(#uz-dots)" pointerEvents="none" />
      ))}

      {/* labels - only for larger regions and active */}
      <g pointerEvents="none">
        {UZ_REGIONS_DATA.map(r => {
          if (r.isCity) return null;
          const isActive = r.k === highlight;
          const isHover = r.k === hov;
          const tiny = ["syrdarya"].includes(r.k);
          const fontSize = isActive ? 16 : tiny ? 10 : 12;
          const weight = isActive ? 800 : isHover ? 700 : 600;
          return (
            <text
              key={`l-${r.k}`}
              x={r.cx} y={r.cy}
              textAnchor="middle" dominantBaseline="middle"
              fontSize={fontSize} fontWeight={weight}
              fill="#fff"
              fillOpacity={isActive ? 1 : isHover ? 0.95 : 0.6}
              style={{
                fontFamily: "Manrope, Inter, sans-serif",
                letterSpacing: -0.1,
                textShadow: "0 1px 3px rgba(0,0,0,0.4)",
              }}
            >
              {r.n}
            </text>
          );
        })}
      </g>

      {/* Tashkent city marker */}
      {(() => {
        const tc = UZ_REGIONS_DATA.find(r => r.k === "tashkent_city");
        return (
          <g pointerEvents="none">
            <circle cx={tc.cx} cy={tc.cy} r="5" fill="#F59E0B" stroke="#fff" strokeWidth="1.5" />
            <text
              x={tc.cx + 12} y={tc.cy - 10}
              fontSize="11" fontWeight="700" fill="#FEF3C7"
              style={{ fontFamily: "Manrope, sans-serif", letterSpacing: 0.3, textShadow: "0 1px 3px rgba(0,0,0,0.5)" }}
            >
              ★ Ташкент
            </text>
          </g>
        );
      })()}

      {/* compass rose — bottom right */}
      <g transform="translate(60, 590)" opacity="0.7" pointerEvents="none">
        <circle r="18" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.25)" strokeWidth="0.8" />
        <path d="M 0,-14 L 3,0 L 0,14 L -3,0 Z" fill="rgba(255,255,255,0.9)" />
        <text y="-22" textAnchor="middle" fontSize="9" fill="rgba(255,255,255,0.7)" fontFamily="'JetBrains Mono', monospace">N</text>
      </g>

      {/* scale bar */}
      <g transform="translate(820, 595)" pointerEvents="none">
        <line x1="0" y1="0" x2="120" y2="0" stroke="rgba(255,255,255,0.4)" strokeWidth="1" />
        <line x1="0" y1="-3" x2="0" y2="3" stroke="rgba(255,255,255,0.6)" strokeWidth="1" />
        <line x1="60" y1="-3" x2="60" y2="3" stroke="rgba(255,255,255,0.6)" strokeWidth="1" />
        <line x1="120" y1="-3" x2="120" y2="3" stroke="rgba(255,255,255,0.6)" strokeWidth="1" />
        <text x="0" y="16" fontSize="8.5" fill="rgba(255,255,255,0.6)" fontFamily="'JetBrains Mono', monospace">0</text>
        <text x="60" y="16" fontSize="8.5" fill="rgba(255,255,255,0.6)" fontFamily="'JetBrains Mono', monospace" textAnchor="middle">250 км</text>
        <text x="120" y="16" fontSize="8.5" fill="rgba(255,255,255,0.6)" fontFamily="'JetBrains Mono', monospace" textAnchor="end">500</text>
      </g>
    </svg>
  );
}

window.UzMap = UzMap;
window.UZ_REGIONS_DATA = UZ_REGIONS_DATA;

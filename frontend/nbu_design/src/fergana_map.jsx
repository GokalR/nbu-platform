// Fergana region map — traced from user reference image.
// Elongated east-west valley, jagged internal district borders,
// Sokh exclave hanging south-center, tiny Shohimardon exclave SE.

const FERGANA_DATA = [
  // === West edge ===
  {
    k: "beshariq", n: "Бешарык",
    d: "M 40,230 L 90,195 L 145,205 L 160,255 L 150,310 L 110,335 L 70,320 L 45,290 L 30,260 Z",
    cx: 95, cy: 265,
  },
  {
    k: "furkat", n: "Фуркат",
    d: "M 145,205 L 205,195 L 225,240 L 215,275 L 165,280 L 150,255 Z",
    cx: 185, cy: 238,
  },
  {
    k: "dangara", n: "Дангара",
    d: "M 205,120 L 285,105 L 325,145 L 315,185 L 260,200 L 215,185 L 200,155 Z",
    cx: 260, cy: 155,
  },
  {
    k: "uzbekistan_r", n: "Узбекистан",
    d: "M 160,285 L 220,275 L 285,290 L 300,325 L 265,355 L 210,360 L 165,340 Z",
    cx: 230, cy: 320,
  },
  {
    k: "kokand", n: "Коканд", kind: "city",
    d: "M 247,190 L 288,180 L 308,215 L 290,245 L 255,245 L 235,215 Z",
    cx: 272, cy: 215,
  },
  {
    k: "uchkuprik", n: "Учкуприк",
    d: "M 305,170 L 360,160 L 378,205 L 360,240 L 305,245 L 290,210 Z",
    cx: 335, cy: 205,
  },
  {
    k: "buvayda", n: "Бувайда",
    d: "M 305,95 L 385,85 L 405,130 L 380,160 L 325,155 L 305,125 Z",
    cx: 350, cy: 125,
  },

  // === Center ===
  {
    k: "bagdod", n: "Багдад",
    d: "M 380,185 L 465,175 L 495,220 L 475,270 L 410,278 L 375,245 L 370,210 Z",
    cx: 430, cy: 225,
  },
  {
    k: "yazyavan", n: "Язъяван",
    d: "M 410,95 L 500,85 L 530,125 L 515,170 L 460,178 L 415,160 L 400,125 Z",
    cx: 465, cy: 130,
  },
  {
    k: "rishtan", n: "Риштан",
    d: "M 380,280 L 455,275 L 490,315 L 470,360 L 410,370 L 370,335 L 365,305 Z",
    cx: 420, cy: 320,
  },
  {
    k: "altiarik", n: "Алтыарык",
    d: "M 495,275 L 575,270 L 605,315 L 585,360 L 510,365 L 480,330 L 485,295 Z",
    cx: 540, cy: 320,
  },

  // === East cluster ===
  {
    k: "kushtepa", n: "Куштепа",
    d: "M 540,170 L 610,160 L 635,205 L 615,240 L 560,240 L 535,210 Z",
    cx: 580, cy: 205,
  },
  {
    k: "tashlak", n: "Ташлак",
    d: "M 635,155 L 710,145 L 735,190 L 720,230 L 655,235 L 630,195 Z",
    cx: 685, cy: 190,
  },
  {
    k: "margilan", n: "Маргилан", kind: "city",
    d: "M 615,205 L 660,195 L 680,225 L 660,250 L 620,250 L 600,230 Z",
    cx: 640, cy: 225,
  },
  {
    k: "kuva", n: "Кува",
    d: "M 740,150 L 820,140 L 855,185 L 840,235 L 770,245 L 735,200 Z",
    cx: 795, cy: 190,
  },
  {
    k: "fergana_city", n: "Фергана", kind: "city",
    d: "M 650,255 L 695,248 L 718,280 L 698,308 L 655,308 L 635,285 Z",
    cx: 675, cy: 280,
  },
  {
    k: "fergana_dist", n: "Фергана р-н",
    d: "M 570,305 L 650,315 L 720,320 L 740,355 L 700,390 L 625,390 L 565,365 Z",
    cx: 645, cy: 355,
  },
  {
    k: "kuvasay", n: "Кувасай",
    d: "M 725,240 L 815,235 L 850,275 L 830,325 L 745,330 L 715,290 Z",
    cx: 780, cy: 285,
  },

  // === Exclaves ===
  {
    k: "sokh", n: "Сох",
    d: "M 310,400 L 345,385 L 375,400 L 390,445 L 380,490 L 355,510 L 325,500 L 310,470 L 300,440 L 295,420 Z",
    cx: 345, cy: 450, exclave: true,
  },
  {
    k: "shohimardon", n: "",
    d: "M 690,425 L 725,420 L 740,445 L 728,465 L 700,465 L 685,445 Z",
    cx: 712, cy: 442, exclave: true, tiny: true,
  },
];

function FerganaMap({ highlight = "fergana_city", onHover }) {
  const [hov, setHov] = useState(null);
  const VIEW_W = 900;
  const VIEW_H = 560;
  const active = hov || highlight;

  return (
    <svg
      viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
      style={{ width: "100%", height: "auto", display: "block", overflow: "visible" }}
      aria-hidden
    >
      <defs>
        <filter id="fm-shadow" x="-10%" y="-10%" width="120%" height="120%">
          <feDropShadow dx="0" dy="3" stdDeviation="4" floodColor="#000" floodOpacity="0.4" />
        </filter>
      </defs>

      {FERGANA_DATA.map(r => {
        const isActive = r.k === active;
        const isCity = r.kind === "city";
        let fill;
        if (isActive && isCity) fill = "#001B3D";
        else if (isCity) fill = "#003D7C";
        else if (isActive) fill = "#0054A6";
        else fill = "#7FB5E6";

        return (
          <path
            key={r.k}
            d={r.d}
            fill={fill}
            fillOpacity={isActive ? 1 : 0.85}
            stroke="#ffffff"
            strokeWidth={isActive ? 2.5 : 1.3}
            strokeLinejoin="round"
            style={{
              filter: isActive ? "url(#fm-shadow)" : "none",
              transition: "all .18s",
              cursor: "pointer",
            }}
            onMouseEnter={() => { setHov(r.k); onHover && onHover(r.k); }}
            onMouseLeave={() => { setHov(null); onHover && onHover(null); }}
          />
        );
      })}

      {/* City pin markers */}
      {FERGANA_DATA.filter(r => r.kind === "city").map(r => (
        <g key={`pin-${r.k}`} pointerEvents="none">
          <path
            d={`M ${r.cx},${r.cy - 10} C ${r.cx - 8},${r.cy - 10} ${r.cx - 8},${r.cy + 3} ${r.cx},${r.cy + 11} C ${r.cx + 8},${r.cy + 3} ${r.cx + 8},${r.cy - 10} ${r.cx},${r.cy - 10} Z`}
            fill="#001B3D"
            stroke="#fff"
            strokeWidth="1.4"
          />
          <circle cx={r.cx} cy={r.cy - 4} r="2.8" fill="#fff" />
        </g>
      ))}

      {/* Labels */}
      <g pointerEvents="none">
        {FERGANA_DATA.filter(r => r.n && !r.tiny).map(r => {
          const isActive = r.k === active;
          const isCity = r.kind === "city";
          const fontSize = isCity ? 13 : (isActive ? 12 : 11);
          const weight = isCity ? 800 : (isActive ? 700 : 600);
          const yOff = isCity ? 22 : 0;
          return (
            <text
              key={`l-${r.k}`}
              x={r.cx} y={r.cy + yOff}
              textAnchor="middle" dominantBaseline="middle"
              fontSize={fontSize} fontWeight={weight}
              fill={isCity ? "#ffffff" : "#0b1a33"}
              style={{
                fontFamily: "Manrope, Inter, sans-serif",
                letterSpacing: 0.1,
                paintOrder: "stroke fill",
                stroke: isCity ? "rgba(0,27,61,0.9)" : "rgba(255,255,255,0.9)",
                strokeWidth: isCity ? 0 : 3,
                strokeLinejoin: "round",
              }}
            >
              {r.n}
            </text>
          );
        })}
      </g>
    </svg>
  );
}

window.FerganaMap = FerganaMap;
window.FERGANA_DATA = FERGANA_DATA;

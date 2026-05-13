// Icon set — clean line icons, 1.6 stroke. All accept { size, color, ... }
const Ic = ({ children, size = 18, color = "currentColor", ...rest }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
    strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...rest}>
    {children}
  </svg>
);

const IcPulse   = (p) => <Ic {...p}><path d="M3 12h3l2-7 4 14 3-9 2 5h4"/></Ic>;
const IcBrain   = (p) => <Ic {...p}><path d="M9 4a3 3 0 0 0-3 3v.5A2.5 2.5 0 0 0 4 10v.5A2.5 2.5 0 0 0 4 15v.5A2.5 2.5 0 0 0 6 18v.5A2.5 2.5 0 0 0 9 21V4Z"/><path d="M15 4a3 3 0 0 1 3 3v.5A2.5 2.5 0 0 1 20 10v.5A2.5 2.5 0 0 1 20 15v.5A2.5 2.5 0 0 1 18 18v.5A2.5 2.5 0 0 1 15 21V4Z"/></Ic>;
const IcUsers   = (p) => <Ic {...p}><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="8.5" r="3"/><path d="M16 14a5 5 0 0 1 5.5 6"/></Ic>;
const IcDB      = (p) => <Ic {...p}><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></Ic>;
const IcSteth   = (p) => <Ic {...p}><path d="M5 3v6a5 5 0 0 0 10 0V3"/><path d="M5 3h2"/><path d="M13 3h2"/><path d="M10 14v3a4 4 0 0 0 8 0v-1"/><circle cx="18" cy="11" r="2"/></Ic>;
const IcHand    = (p) => <Ic {...p}><path d="M9 11V5a1.5 1.5 0 0 1 3 0v6"/><path d="M12 11V4a1.5 1.5 0 0 1 3 0v7"/><path d="M15 11V5.5a1.5 1.5 0 0 1 3 0V14"/><path d="M9 11V7a1.5 1.5 0 0 0-3 0v7c0 4 3 7 6 7h1c3 0 5-2.5 5-5"/></Ic>;
const IcCheck   = (p) => <Ic {...p}><path d="M20 6 9 17l-5-5"/></Ic>;
const IcCheckCircle = (p) => <Ic {...p}><circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/></Ic>;
const IcTarget  = (p) => <Ic {...p}><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></Ic>;
const IcLayers  = (p) => <Ic {...p}><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/><path d="m3 18 9 5 9-5"/></Ic>;
const IcGit     = (p) => <Ic {...p}><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M6 8.5v3A2.5 2.5 0 0 0 8.5 14h7A2.5 2.5 0 0 0 18 11.5v-3"/><path d="M12 14v1.5"/></Ic>;
const IcClock   = (p) => <Ic {...p}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></Ic>;
const IcCal     = (p) => <Ic {...p}><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18"/><path d="M8 3v4M16 3v4"/></Ic>;
const IcTrend   = (p) => <Ic {...p}><path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/></Ic>;
const IcArrow   = (p) => <Ic {...p}><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></Ic>;
const IcArrowL  = (p) => <Ic {...p}><path d="M19 12H5"/><path d="m11 6-6 6 6 6"/></Ic>;
const IcChev    = (p) => <Ic {...p}><path d="m9 6 6 6-6 6"/></Ic>;
const IcChevL   = (p) => <Ic {...p}><path d="m15 6-6 6 6 6"/></Ic>;
const IcDl      = (p) => <Ic {...p}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></Ic>;
const IcUp      = (p) => <Ic {...p}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8 12 3 7 8"/><path d="M12 3v12"/></Ic>;
const IcSearch  = (p) => <Ic {...p}><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></Ic>;
const IcUser    = (p) => <Ic {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></Ic>;
const IcSettings= (p) => <Ic {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h0a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v0a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/></Ic>;
const IcLogout  = (p) => <Ic {...p}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/></Ic>;
const IcWifi    = (p) => <Ic {...p}><path d="M5 13a10 10 0 0 1 14 0"/><path d="M8.5 16.5a5 5 0 0 1 7 0"/><circle cx="12" cy="20" r="1" fill="currentColor"/></Ic>;
const IcShield  = (p) => <Ic {...p}><path d="M12 3 4 6v6c0 5 4 8 8 9 4-1 8-4 8-9V6l-8-3Z"/></Ic>;
const IcFolder  = (p) => <Ic {...p}><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z"/></Ic>;
const IcFile    = (p) => <Ic {...p}><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-6-6Z"/><path d="M14 3v6h6"/></Ic>;
const IcMore    = (p) => <Ic {...p}><circle cx="12" cy="5" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="19" r="1" fill="currentColor"/></Ic>;
const IcLock    = (p) => <Ic {...p}><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 1 1 8 0v4"/></Ic>;
const IcMail    = (p) => <Ic {...p}><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></Ic>;
const IcEye     = (p) => <Ic {...p}><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></Ic>;
const IcCpu     = (p) => <Ic {...p}><rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></Ic>;
const IcZap     = (p) => <Ic {...p}><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/></Ic>;
const IcCamera  = (p) => <Ic {...p}><path d="M3 8a2 2 0 0 1 2-2h2l2-2h6l2 2h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8Z"/><circle cx="12" cy="13" r="3.5"/></Ic>;
const IcPlus    = (p) => <Ic {...p}><path d="M12 5v14M5 12h14"/></Ic>;
const IcMinus   = (p) => <Ic {...p}><path d="M5 12h14"/></Ic>;
const IcInfo    = (p) => <Ic {...p}><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M12 12v5"/></Ic>;
const IcPlay    = (p) => <Ic {...p}><path d="M7 5v14l12-7L7 5Z" fill="currentColor"/></Ic>;
const IcRefresh = (p) => <Ic {...p}><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/></Ic>;
const IcAdjust  = (p) => <Ic {...p}><path d="M4 6h10M4 12h7M4 18h13"/><circle cx="18" cy="6" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="21" cy="18" r="2"/></Ic>;

Object.assign(window, {
  Ic, IcPulse, IcBrain, IcUsers, IcDB, IcSteth, IcHand, IcCheck, IcCheckCircle,
  IcTarget, IcLayers, IcGit, IcClock, IcCal, IcTrend, IcArrow, IcArrowL, IcChev, IcChevL,
  IcDl, IcUp, IcSearch, IcUser, IcSettings, IcLogout, IcWifi, IcShield, IcFolder, IcFile,
  IcMore, IcLock, IcMail, IcEye, IcCpu, IcZap, IcCamera, IcPlus, IcMinus, IcInfo, IcPlay,
  IcRefresh, IcAdjust,
});

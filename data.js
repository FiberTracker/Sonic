// data.js — Sonic Telecom Competitive Intelligence
// Sources cited inline. All metrics from public filings, press, FCC BDC, or labeled estimates.

const PROVIDERS = {
  sonic: {
    id: '190425',
    name: 'Sonic Telecom',
    color: '#0C7EC6',
    shortName: 'Sonic',
  },
  att: {
    id: '130077',
    name: 'AT&T Inc.',
    color: '#00759E',
    shortName: 'AT&T',
  },
  comcast: {
    id: '130317',
    name: 'Comcast (Xfinity)',
    color: '#4972AC',
    shortName: 'Comcast',
  },
  frontier: {
    id: '130258',
    name: 'Frontier Communications',
    color: '#469A6C',
    shortName: 'Frontier',
  },
  race: {
    id: '330062',
    name: 'Race Communications',
    color: '#879420',
    shortName: 'Race',
  },
};

const FOCUS_PROVIDER = 'sonic';

// Operator Profiles
const OPERATOR_PROFILES = {
  sonic: {
    name: 'Sonic Telecom, LLC',
    hq: 'Santa Rosa, CA (Sonoma County)',
    founded: '1994',
    founder: 'Dane Jasper & Scott Doty',
    ownership: 'Private, founder-controlled. No PE sponsor.',
    ceo: 'Nathan Patrick (CEO); Dane Jasper (Executive Chairman & Co-Founder)',
    cfo: 'Scott Son',
    employees: '~500-700',
    technology: 'GPON / XGS-PON (10G symmetrical) / 50G PON (Adtran partnership, Nov 2024)',
    speeds: 'Up to 10 Gbps symmetrical',
    pricing: '$49.99/mo (10 Gbps fiber, promo). No contracts, no data caps.',
    subscribers: '~150,000 customers (per press / calculated)',
    revenue: '$150-250M range (private — Getlatka: $158M Oct 2024; Comparably: $259M 2025)',
    ebitda: '~$80M (per market intel)',
    ebitdaSource: 'Market Intel / Chatter',
    homesPassedEst: '250K-500K owned fiber passings (UNVERIFIED — derived from subscriber/take-rate math)',
    fccBdcBsls: null, // populated from BDC data
    markets: 'San Francisco, North Bay/Sonoma, East Bay, Peninsula/South Bay, Sacramento, Los Angeles Basin, Dallas TX (new 2025)',
    keyDiff: 'Aggressive pricing ($49.99 for 10 Gbps), 50G PON tech leadership, copper-to-fiber migration strategy via AT&T wholesale lease, strong privacy/net neutrality brand',
    maActivity: 'Tracxn flagged M&A offer Apr 2025 (unconfirmed). Founder reportedly open to discussions.',
    absHistory: 'None on record.',
    beadStatus: 'CA received $1.86B BEAD. Sonic likely applicant — no confirmed awards as of Dec 2025.',
    growthStrategy: 'Dallas TX entry (2025) = first market outside CA. Land-and-expand via AT&T copper leasing ($40/mo wholesale) then overbuild with owned fiber. 50G PON deployment with Adtran.',
    valuation: {
      implied: '$475M (Getlatka, unverified)',
      ebitdaMultiple: '~6x at $475M / $80M EBITDA — below market (8-12x for scaled fiber)',
      note: 'If $80M EBITDA is real, 8-12x range implies $640M-$960M enterprise value.',
    },
    sources: [
      { text: 'Sonic Official Website', url: 'https://www.sonic.com/' },
      { text: 'Adtran 50G PON Partnership (Nov 2024)', url: 'https://investors.adtran.com/news/news-details/2024/Adtran-and-Sonic-Fiber-Internet-partner-to-deliver-50G-PON-connectivity-across-California/default.aspx' },
      { text: 'Broadband Breakfast — Copper Leasing Strategy', url: 'https://broadbandbreakfast.com/sonic-ceo-dane-jasper-says-copper-leasing-provides-foundation-for-expanding-broadband-fiber/' },
      { text: 'Allconnect Sonic Review 2025', url: 'https://www.allconnect.com/providers/sonic' },
      { text: 'FCC BDC J25 Filing (Jun 2025)', url: 'https://broadbandmap.fcc.gov/' },
      { text: 'Wikipedia — Sonic (ISP)', url: 'https://en.wikipedia.org/wiki/Sonic_(ISP)' },
    ],
  },
  att: {
    name: 'AT&T Inc.',
    hq: 'Dallas, TX',
    founded: '1885 (current incarnation 2005)',
    ownership: 'Public (NYSE: T)',
    ceo: 'John Stankey',
    technology: 'GPON / XGS-PON',
    speeds: 'Up to 5 Gbps (AT&T Fiber)',
    pricing: '$55-180/mo (varies by speed tier)',
    subscribers: '~9.1M fiber subs nationally (Q4 2025)',
    homesPassedEst: '~30M nationally, targeting 60M by 2030',
    markets: 'California (Bay Area, LA, Sacramento, Central Valley) + 21-state footprint',
    keyDiff: 'Largest fiber footprint in CA. NetworkCo seeking PE partner. Massive capex commitment to 60M HHP target.',
    sources: [
      { text: 'AT&T Investor Relations', url: 'https://investors.att.com/' },
      { text: 'FCC BDC J25 Filing', url: 'https://broadbandmap.fcc.gov/' },
    ],
  },
  comcast: {
    name: 'Comcast Corporation (Xfinity)',
    hq: 'Philadelphia, PA',
    founded: '1963',
    ownership: 'Public (NASDAQ: CMCSA)',
    ceo: 'Brian Roberts (Chairman); Mike Cavanagh (President)',
    technology: 'HFC (DOCSIS 3.1/4.0) + selective FTTH overbuild',
    speeds: 'Up to 6 Gbps (Xfinity Gigabit Pro)',
    pricing: '$35-300/mo (varies by speed/bundle)',
    subscribers: '~32M broadband subs nationally',
    markets: 'California-wide, dominant cable incumbent',
    keyDiff: 'Cable incumbent with massive Bay Area/LA footprint. Upload speed disadvantage vs fiber. DOCSIS 4.0 rollout in progress.',
    sources: [
      { text: 'Comcast Investor Relations', url: 'https://corporate.comcast.com/investors' },
      { text: 'FCC BDC J25 Filing', url: 'https://broadbandmap.fcc.gov/' },
    ],
  },
  frontier: {
    name: 'Frontier Communications',
    hq: 'Dallas, TX',
    founded: '1935 (emerged from bankruptcy 2021)',
    ownership: 'Public (NASDAQ: FYBR) — Verizon acquisition pending',
    ceo: 'Nick Jeffery',
    technology: 'GPON / XGS-PON',
    speeds: 'Up to 5 Gbps',
    pricing: '$49.99-154.99/mo',
    subscribers: '~2.4M fiber subs nationally',
    homesPassedEst: '~8.3M fiber passings nationally',
    markets: 'California (Bay Area suburbs, Central Valley, Southern CA) + 25 states',
    keyDiff: 'Aggressive post-bankruptcy fiber overbuild. Verizon deal at 26.6x EBITDA (Sep 2024). Strong CA presence in suburbs/exurbs.',
    sources: [
      { text: 'Frontier Investor Relations', url: 'https://investor.frontier.com/' },
      { text: 'FCC BDC J25 Filing', url: 'https://broadbandmap.fcc.gov/' },
    ],
  },
  race: {
    name: 'Race Communications, Inc.',
    hq: 'South San Francisco, CA',
    founded: '1994',
    ownership: 'Private. Sponsor: Oak Hill Capital.',
    ceo: 'Raul Alcaraz',
    technology: 'FTTH (GPON)',
    speeds: 'Up to 10 Gbps',
    pricing: '$59.95-149.95/mo',
    subscribers: 'Not disclosed',
    homesPassedEst: '~100K+ (estimated)',
    markets: 'Central Valley (Kern, Tulare, Kings, Fresno), Bay Area, rural CA',
    keyDiff: 'Rural CA specialist. Oak Hill-backed since 2023. Strong BEAD/RDOF funding position. Addresses underserved Central Valley markets.',
    sources: [
      { text: 'Race Communications Website', url: 'https://www.race.com/' },
      { text: 'FCC BDC J25 Filing', url: 'https://broadbandmap.fcc.gov/' },
    ],
  },
};

// Regions for navigation
const REGIONS = [
  { name: 'San Francisco', center: [37.7749, -122.4194], zoom: 12, desc: 'Core fiber market — Sonic 39% address coverage' },
  { name: 'North Bay / Sonoma', center: [38.4404, -122.7141], zoom: 11, desc: 'Home turf — Santa Rosa HQ, earliest builds' },
  { name: 'East Bay', center: [37.8044, -122.2712], zoom: 11, desc: 'Oakland, Berkeley, Fremont expansion' },
  { name: 'Peninsula', center: [37.4419, -122.1430], zoom: 11, desc: 'Palo Alto, San Mateo, Half Moon Bay' },
  { name: 'South Bay', center: [37.3382, -121.8863], zoom: 11, desc: 'San Jose, Santa Clara' },
  { name: 'Sacramento', center: [38.5816, -121.4944], zoom: 11, desc: 'Expanding presence' },
  { name: 'Los Angeles', center: [34.0522, -118.2437], zoom: 10, desc: 'Entered 2013 — broad SoCal footprint' },
  { name: 'All California', center: [37.2, -119.5], zoom: 6, desc: 'Statewide view' },
];

// Key executives for profile tab
const KEY_EXECUTIVES = [
  { name: 'Dane Jasper', title: 'Executive Chairman & Co-Founder', note: 'Founded Sonic 1994. Net neutrality/privacy advocate. Reportedly open to strategic discussions.' },
  { name: 'Nathan Patrick', title: 'CEO', note: 'Promoted from CTO. Runs day-to-day operations.' },
  { name: 'Scott Doty', title: 'CIO, VP & Co-Founder', note: 'Technical co-founder. Oversees infrastructure.' },
  { name: 'Scott Son', title: 'CFO', note: 'Previous CFO stints at HUBB Filters and Sunverge Energy.' },
  { name: 'William Greenlaw', title: 'Director of Regulatory & Gov Affairs', note: 'CPUC/FCC regulatory matters.' },
  { name: 'Stephen Bradley', title: 'VP of Sales & Marketing', note: 'Commercial go-to-market.' },
];

// Competitive positioning
const COMP_MATRIX = {
  headers: ['Metric', 'Sonic', 'AT&T Fiber', 'Comcast', 'Frontier', 'Race'],
  rows: [
    ['Max Speed', '10 Gbps sym', '5 Gbps', '6 Gbps (asym)', '5 Gbps', '10 Gbps'],
    ['Base Price', '$49.99/mo', '$55/mo', '$35-55/mo', '$49.99/mo', '$59.95/mo'],
    ['Technology', 'GPON/XGS/50G PON', 'GPON/XGS-PON', 'HFC + FTTH', 'GPON/XGS-PON', 'GPON'],
    ['Data Caps', 'None', '1 TB (varies)', '1.2 TB', 'None', 'None'],
    ['Contracts', 'No', 'No', 'Yes (most plans)', 'No', 'No'],
    ['Ownership', 'Private/Founder', 'Public (T)', 'Public (CMCSA)', 'Public (FYBR)', 'Private/Oak Hill'],
    ['CA Focus', 'Primary (+ TX)', '21-state national', 'National cable', '25-state national', 'CA only'],
  ],
};

// Valuation context
const VALUATION_CONTEXT = {
  sonicMetrics: {
    ebitda: 80,
    ebitdaSource: 'Market Intel / Chatter',
    revenueRange: '150-250',
    revenueSource: 'Third-party estimates (Getlatka/Comparably) — UNVERIFIED',
    impliedValue: 475,
    impliedSource: 'Getlatka — UNVERIFIED',
  },
  comps: [
    { deal: 'T-Mobile / MetroNet', dollarPerHhp: 4900, multiple: '25.0x', date: 'Jul 2024' },
    { deal: 'Verizon / Frontier', dollarPerHhp: null, multiple: '26.6x', date: 'Sep 2024' },
    { deal: 'Searchlight / Ziply', dollarPerHhp: 2600, multiple: '9.1x', date: 'Sep 2024' },
    { deal: 'Bell / Consolidated', dollarPerHhp: 3000, multiple: '14.3x', date: 'Nov 2024' },
    { deal: 'AT&T Fiber (May \'25)', dollarPerHhp: 3800, multiple: '16.5x', date: 'May 2025' },
  ],
  scenarioAnalysis: [
    { label: '8x EBITDA (low)', ev: 640 },
    { label: '10x EBITDA (mid)', ev: 800 },
    { label: '12x EBITDA (high)', ev: 960 },
  ],
};

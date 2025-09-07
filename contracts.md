# Regam Blockchain Website - API Contracts & Integration Guide

## Current Implementation Status
✅ **Frontend Complete** - Homepage with all core sections
- Hero section with CTAs
- Value proposition cards (5 features)
- RGM token information section
- Footer with community links and legal pages

## Mock Data Structure

### Hero Section
```javascript
hero: {
  headline: "Fast. Secure. Scalable. Eco-friendly.",
  subheadline: "Regam Blockchain powers low-fee payments and apps with 10B-supply RGM.",
  primaryCtas: [
    { text: "Get RGM", href: "#", variant: "primary" },
    { text: "Read the Docs", href: "#", variant: "secondary" }
  ],
  secondaryCta: { text: "Join the Community", href: "#" }
}
```

### Value Propositions
```javascript
valueProps: [
  { id: 1, title: "Speed", description: "Near-instant confirmation..." },
  { id: 2, title: "Security", description: "Battle-tested design..." },
  // ... 5 total cards
]
```

### Token Information
```javascript
token: {
  symbol: "RGM",
  name: "RegamCoin", 
  totalSupply: "10,000,000,000",
  useCases: ["gas", "staking", "governance", "payments"],
  description: "RGM is the native token of Regam Blockchain..."
}
```

### Statistics
```javascript
stats: [
  { label: "Block finality", value: "Fast" },
  { label: "Average fees", value: "Low" },
  { label: "Energy design", value: "Efficient" },
  { label: "Compatibility", value: "EVM-ready" }
]
```

### Community Links
```javascript
community: [
  { name: "Discord", href: "#", icon: "MessageCircle" },
  { name: "Telegram", href: "#", icon: "Send" },
  { name: "Twitter", href: "#", icon: "Twitter" },
  { name: "GitHub", href: "#", icon: "Github" }
]
```

## Future Backend Integration Plan

### API Endpoints Needed

#### 1. Homepage Content API
```
GET /api/homepage
Response: {
  hero: { headline, subheadline, ctas },
  valueProps: [...],
  token: { symbol, totalSupply, description, useCases },
  stats: [...],
  community: [...]
}
```

#### 2. Token Statistics API  
```
GET /api/token/stats
Response: {
  totalSupply: "10000000000",
  circulatingSupply: "8500000000",
  currentPrice: "$0.045",
  marketCap: "$382500000",
  volume24h: "$12300000",
  stakingAPR: "8.5%"
}
```

#### 3. Blockchain Statistics API
```
GET /api/blockchain/stats  
Response: {
  blockTime: "2.1s",
  transactions24h: "145678",
  activeValidators: "150",
  totalStaked: "2100000000",
  networkHashrate: "1.2 TH/s"
}
```

#### 4. Newsletter Subscription
```
POST /api/newsletter/subscribe
Body: { email: "user@example.com" }
Response: { success: true, message: "Subscribed successfully" }
```

### Database Schema

#### Content Management
```javascript
// Homepage content collection
{
  _id: ObjectId,
  section: "hero" | "valueProps" | "token" | "stats",
  content: Object, // Flexible schema for different content types
  isActive: Boolean,
  lastUpdated: Date,
  version: Number
}
```

#### Token Metrics
```javascript
{
  _id: ObjectId,
  timestamp: Date,
  totalSupply: Number,
  circulatingSupply: Number,
  price: Number,
  marketCap: Number,
  volume24h: Number,
  holders: Number
}
```

#### Blockchain Metrics
```javascript
{
  _id: ObjectId,
  timestamp: Date,
  blockHeight: Number,
  blockTime: Number,
  transactions24h: Number,
  activeValidators: Number,
  totalStaked: Number,
  networkHashrate: String
}
```

## Frontend-Backend Integration Steps

### Phase 1: Replace Mock Data
1. Create API service layer in `/src/services/api.js`
2. Replace static imports from `mock.js` with API calls
3. Add loading states and error handling
4. Implement data caching with React Query or SWR

### Phase 2: Real-time Updates
1. Add WebSocket connection for live stats
2. Implement auto-refresh for token metrics
3. Add update indicators for real-time data

### Phase 3: Content Management
1. Admin interface for updating homepage content
2. Version control for content changes
3. A/B testing capabilities for different messaging

## Current File Structure
```
/app/frontend/src/
├── components/
│   ├── Header.jsx           # Fixed header with navigation
│   ├── Hero.jsx            # Hero section with main CTAs  
│   ├── ValueProps.jsx      # 5 value proposition cards
│   ├── TokenSection.jsx    # RGM token info + stats grid
│   ├── Footer.jsx          # Footer with links and legal
│   └── ui/                 # Shadcn UI components
├── mock.js                 # All mock data (to be replaced)
├── App.js                  # Main app with routing
├── App.css                 # Custom styles with brand colors
└── index.css               # Base styles with Tailwind

```

## Brand Colors Implementation
- **Primary Royal Blue**: #0B3D91 (buttons, brand elements)
- **Accent Cyan**: #00FFD1 (hover states, highlights)  
- **Gold Accent**: #F4C430 (special highlights)
- **Background**: #000000 (main background)
- **Cards**: #121212 (secondary background)

## Technology Stack
- **Frontend**: React 19, Tailwind CSS, Shadcn UI
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **Future Backend**: FastAPI + MongoDB
- **Deployment**: Docker with supervisor

## Next Steps for Backend
1. Set up FastAPI endpoints matching the contract above
2. Create MongoDB collections for content and metrics
3. Implement data fetching service in frontend
4. Add environment-specific API URLs
5. Test integration with real data sources
// Mock data for Regam Blockchain website
export const mockData = {
  // Hero section
  hero: {
    headline: "Fast. Secure. Scalable. Eco-friendly.",
    subheadline: "Regam Blockchain powers low-fee payments and apps with 10B-supply RGM.",
    primaryCtas: [
      { text: "Get RGM", href: "#", variant: "primary" },
      { text: "Read the Docs", href: "#", variant: "secondary" }
    ],
    secondaryCta: { text: "Join the Community", href: "#" }
  },

  // Value proposition cards
  valueProps: [
    {
      id: 1,
      title: "Speed",
      description: "Near-instant confirmation for a smooth user experience."
    },
    {
      id: 2,
      title: "Security", 
      description: "Battle-tested design with strong validator rules."
    },
    {
      id: 3,
      title: "Scalability",
      description: "Built to handle heavy demand without congestion."
    },
    {
      id: 4,
      title: "Eco-friendly",
      description: "Efficient architecture that reduces energy use."
    },
    {
      id: 5,
      title: "Low fees",
      description: "Keep more of what you send and earn."
    }
  ],

  // Token information
  token: {
    symbol: "RGM",
    name: "RegamCoin",
    totalSupply: "10,000,000,000",
    useCases: ["gas", "staking", "governance", "payments"],
    description: "RGM is the native token of Regam Blockchain. It powers transactions, staking, governance, and incentives across the network."
  },

  // Quick stats
  stats: [
    { label: "Block finality", value: "Fast" },
    { label: "Average fees", value: "Low" },
    { label: "Energy design", value: "Efficient" },
    { label: "Compatibility", value: "EVM-ready" }
  ],

  // Community links
  community: [
    { name: "Discord", href: "#", icon: "MessageCircle" },
    { name: "Telegram", href: "#", icon: "Send" },
    { name: "Twitter", href: "#", icon: "Twitter" },
    { name: "GitHub", href: "#", icon: "Github" }
  ],

  // Navigation
  navigation: [
    { name: "Home", href: "/" },
    { name: "Technology", href: "/technology" },
    { name: "Token", href: "/token" },
    { name: "Developers", href: "/developers" },
    { name: "Roadmap", href: "/roadmap" },
    { name: "Blog", href: "/blog" },
    { name: "FAQ", href: "/faq" }
  ],

  // Footer
  footer: {
    legal: [
      { name: "Terms", href: "/terms" },
      { name: "Privacy", href: "/privacy" },
      { name: "Cookie Policy", href: "/cookies" }
    ],
    riskNote: "Digital assets carry risk. Do your own research. This site does not offer financial advice.",
    contact: "hello@regamblockchain.com"
  }
};
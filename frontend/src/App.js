import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Import UI components
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Input } from './components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Separator } from './components/ui/separator';
import { 
  Activity, 
  Blocks, 
  Zap, 
  Leaf, 
  Search, 
  Wallet, 
  Send, 
  QrCode,
  TrendingUp,
  Database,
  Users,
  Clock,
  ArrowUpRight,
  ArrowDownLeft,
  Copy,
  Plus,
  Settings
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  
  return (
    <nav className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-lg flex items-center justify-center">
                <Blocks className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                Regam Explorer
              </span>
            </Link>
            
            <div className="hidden md:flex space-x-6">
              <Link 
                to="/" 
                className={`px-3 py-2 rounded-lg transition-colors ${
                  location.pathname === '/' 
                    ? 'bg-emerald-100 text-emerald-700' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                Explorer
              </Link>
              <Link 
                to="/wallet" 
                className={`px-3 py-2 rounded-lg transition-colors ${
                  location.pathname === '/wallet' 
                    ? 'bg-emerald-100 text-emerald-700' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                Wallet
              </Link>
              <Link 
                to="/validators" 
                className={`px-3 py-2 rounded-lg transition-colors ${
                  location.pathname === '/validators' 
                    ? 'bg-emerald-100 text-emerald-700' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                Validators
              </Link>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="hidden sm:flex items-center space-x-2">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Live Network</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Real-time Metrics Hook
const useRealTimeMetrics = () => {
  const [metrics, setMetrics] = useState(null);
  
  useEffect(() => {
    // Initial fetch
    const fetchMetrics = async () => {
      try {
        const response = await axios.get(`${API}/system/info`);
        setMetrics(response.data);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    };
    
    fetchMetrics();
    
    // Set up periodic updates (mock real-time)
    const interval = setInterval(fetchMetrics, 3000);
    return () => clearInterval(interval);
  }, []);
  
  return metrics;
};

// Explorer Home Component
const ExplorerHome = () => {
  const [blocks, setBlocks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [tpsData, setTpsData] = useState(null);
  const metrics = useRealTimeMetrics();
  
  useEffect(() => {
    fetchBlocks();
    fetchTpsData();
  }, []);
  
  const fetchBlocks = async () => {
    try {
      const response = await axios.get(`${API}/blocks?limit=10`);
      setBlocks(response.data.blocks);
    } catch (error) {
      console.error('Error fetching blocks:', error);
    }
  };
  
  const fetchTpsData = async () => {
    try {
      const response = await axios.get(`${API}/metrics/tps?window=5m`);
      setTpsData(response.data);
    } catch (error) {
      console.error('Error fetching TPS data:', error);
    }
  };
  
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await axios.get(`${API}/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error searching:', error);
    }
  };
  
  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toFixed(0);
  };
  
  const formatHash = (hash) => {
    return `${hash.slice(0, 8)}...${hash.slice(-8)}`;
  };
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 to-blue-50"></div>
          <CardContent className="relative p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Live TPS</p>
                <p className="text-2xl font-bold text-emerald-600">
                  {tpsData ? formatNumber(tpsData.average_tps) : '2.0M'}
                </p>
              </div>
              <Activity className="w-8 h-8 text-emerald-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Ultra-high throughput</p>
          </CardContent>
        </Card>
        
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-purple-50"></div>
          <CardContent className="relative p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Latency</p>
                <p className="text-2xl font-bold text-blue-600">1.2ms</p>
              </div>
              <Zap className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Lightning fast</p>
          </CardContent>
        </Card>
        
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-green-50 to-emerald-50"></div>
          <CardContent className="relative p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Energy/Tx</p>
                <p className="text-2xl font-bold text-green-600">0.003kWh</p>
              </div>
              <Leaf className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Eco-friendly</p>
          </CardContent>
        </Card>
        
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-orange-50 to-red-50"></div>
          <CardContent className="relative p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Fee</p>
                <p className="text-2xl font-bold text-orange-600">0.0003 RGC</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
            <p className="text-xs text-gray-500 mt-2">Ultra-low fees</p>
          </CardContent>
        </Card>
      </div>
      
      {/* Search */}
      <Card className="mb-8">
        <CardContent className="p-6">
          <div className="flex space-x-4">
            <div className="flex-1">
              <Input
                placeholder="Search by block height, transaction hash, or address..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="text-base"
              />
            </div>
            <Button onClick={handleSearch} className="bg-emerald-600 hover:bg-emerald-700">
              <Search className="w-4 h-4 mr-2" />
              Search
            </Button>
          </div>
          
          {searchResults && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-3">Search Results</h3>
              {searchResults.results.length === 0 ? (
                <p className="text-gray-500">No results found</p>
              ) : (
                <div className="space-y-3">
                  {searchResults.results.map((result, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <Badge variant="secondary" className="mb-2">
                            {result.type}
                          </Badge>
                          <p className="font-mono text-sm">
                            {result.type === 'block' && `Block #${result.data.height}`}
                            {result.type === 'transaction' && formatHash(result.data.hash)}
                            {result.type === 'address' && formatHash(result.data.address)}
                          </p>
                        </div>
                        <Button variant="outline" size="sm">View Details</Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Recent Blocks */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="w-5 h-5" />
            <span>Recent Blocks</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {blocks.map((block, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                    <Blocks className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="font-semibold">Block #{block.height}</p>
                    <p className="text-sm text-gray-500 font-mono">{formatHash(block.hash)}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">{block.tx_count} transactions</p>
                  <p className="text-xs text-gray-500">{formatNumber(block.tps_window)} TPS</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Wallet Component
const WalletComponent = () => {
  const [activeWallet, setActiveWallet] = useState('regam1abcd...ef12');
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [sendAmount, setSendAmount] = useState('');
  const [sendAddress, setSendAddress] = useState('');
  const [showQR, setShowQR] = useState(false);
  
  useEffect(() => {
    fetchWalletData();
  }, [activeWallet]);
  
  const fetchWalletData = async () => {
    try {
      const [balanceRes, txRes] = await Promise.all([
        axios.get(`${API}/wallet/${activeWallet}/balance`),
        axios.get(`${API}/wallet/${activeWallet}/transactions?limit=10`)
      ]);
      
      setBalance(balanceRes.data);
      setTransactions(txRes.data.transactions);
    } catch (error) {
      console.error('Error fetching wallet data:', error);
    }
  };
  
  const handleSend = async () => {
    if (!sendAmount || !sendAddress) return;
    
    try {
      // Estimate fee first
      const feeRes = await axios.post(`${API}/wallet/estimateFee`, {
        from_address: activeWallet,
        to_address: sendAddress,
        amount: parseFloat(sendAmount)
      });
      
      // Send transaction
      const sendRes = await axios.post(`${API}/wallet/send`, {
        from_address: activeWallet,
        to_address: sendAddress,
        amount: parseFloat(sendAmount),
        fee_estimate: feeRes.data.total_fee
      });
      
      alert(`Transaction sent! Hash: ${sendRes.data.tx_hash}`);
      setSendAmount('');
      setSendAddress('');
      fetchWalletData(); // Refresh
    } catch (error) {
      console.error('Error sending transaction:', error);
      alert('Error sending transaction');
    }
  };
  
  const formatHash = (hash) => `${hash.slice(0, 8)}...${hash.slice(-8)}`;
  
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Regam Wallet</h1>
        <p className="text-gray-600">Manage your RegamCoin (RGC) securely</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Wallet Panel */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="send">Send</TabsTrigger>
              <TabsTrigger value="stake">Stake</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-6">
              {/* Balance Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Wallet Balance</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowQR(!showQR)}
                    >
                      <QrCode className="w-4 h-4 mr-2" />
                      {showQR ? 'Hide' : 'Show'} QR
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-emerald-600">
                      {balance ? balance.balance.toFixed(4) : '0.0000'} RGC
                    </p>
                    <p className="text-gray-500">≈ ${balance ? (balance.balance * 2.45).toFixed(2) : '0.00'} USD</p>
                  </div>
                  
                  {showQR && (
                    <div className="text-center">
                      <div className="w-32 h-32 bg-gray-200 rounded-lg mx-auto mb-2 flex items-center justify-center">
                        <QrCode className="w-16 h-16 text-gray-400" />
                      </div>
                      <p className="text-xs font-mono text-gray-600">{activeWallet}</p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Staked</p>
                      <p className="font-semibold">{balance ? balance.staked_balance.toFixed(4) : '0.0000'} RGC</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Rewards</p>
                      <p className="font-semibold text-emerald-600">+{balance ? balance.pending_rewards.toFixed(4) : '0.0000'} RGC</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              {/* Recent Transactions */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {transactions.slice(0, 5).map((tx, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            tx.direction === 'sent' ? 'bg-red-100' : 'bg-green-100'
                          }`}>
                            {tx.direction === 'sent' ? 
                              <ArrowUpRight className="w-4 h-4 text-red-600" /> :
                              <ArrowDownLeft className="w-4 h-4 text-green-600" />
                            }
                          </div>
                          <div>
                            <p className="font-medium capitalize">{tx.direction}</p>
                            <p className="text-sm text-gray-500 font-mono">{formatHash(tx.tx_hash)}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`font-semibold ${
                            tx.direction === 'sent' ? 'text-red-600' : 'text-green-600'
                          }`}>
                            {tx.direction === 'sent' ? '-' : '+'}{tx.amount.toFixed(4)} RGC
                          </p>
                          <Badge variant={tx.status === 'confirmed' ? 'default' : 'secondary'} className="text-xs">
                            {tx.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="send" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Send RegamCoin</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Recipient Address</label>
                    <Input
                      placeholder="regam1..."
                      value={sendAddress}
                      onChange={(e) => setSendAddress(e.target.value)}
                      className="font-mono"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Amount (RGC)</label>
                    <Input
                      type="number"
                      placeholder="0.0000"
                      value={sendAmount}
                      onChange={(e) => setSendAmount(e.target.value)}
                      step="0.0001"
                    />
                  </div>
                  
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between text-sm">
                      <span>Network Fee:</span>
                      <span>~0.0003 RGC</span>
                    </div>
                    <div className="flex justify-between text-sm font-medium mt-1">
                      <span>Total:</span>
                      <span>{sendAmount ? (parseFloat(sendAmount) + 0.0003).toFixed(4) : '0.0000'} RGC</span>
                    </div>
                  </div>
                  
                  <Button 
                    onClick={handleSend} 
                    className="w-full bg-emerald-600 hover:bg-emerald-700"
                    disabled={!sendAmount || !sendAddress}
                  >
                    <Send className="w-4 h-4 mr-2" />
                    Send Transaction
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="stake" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Staking</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Staking Coming Soon</h3>
                    <p className="text-gray-600 mb-4">
                      Earn rewards by staking your RGC with validators. 
                      Expected APY: 8-15%
                    </p>
                    <Button variant="outline" disabled>
                      Enable Staking
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Plus className="w-4 h-4 mr-2" />
                Add Wallet
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Copy className="w-4 h-4 mr-2" />
                Copy Address
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
            </CardContent>
          </Card>
          
          {/* Network Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Network Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Block Height:</span>
                <span className="text-sm font-medium">1,234,567</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Active Validators:</span>
                <span className="text-sm font-medium">2,341</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Staked:</span>
                <span className="text-sm font-medium">45.2M RGC</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Network Status:</span>
                <Badge className="bg-emerald-100 text-emerald-700">Healthy</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Validators Component
const ValidatorsComponent = () => {
  const [validators, setValidators] = useState([]);
  
  useEffect(() => {
    fetchValidators();
  }, []);
  
  const fetchValidators = async () => {
    try {
      const response = await axios.get(`${API}/validators`);
      setValidators(response.data.validators);
    } catch (error) {
      console.error('Error fetching validators:', error);
    }
  };
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Validators</h1>
        <p className="text-gray-600">Network validators securing the Regam blockchain</p>
      </div>
      
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left py-4 px-6 font-medium text-gray-900">Validator</th>
                  <th className="text-left py-4 px-6 font-medium text-gray-900">Voting Power</th>
                  <th className="text-left py-4 px-6 font-medium text-gray-900">Commission</th>
                  <th className="text-left py-4 px-6 font-medium text-gray-900">Uptime</th>
                  <th className="text-left py-4 px-6 font-medium text-gray-900">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {validators.slice(0, 20).map((validator, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                          <Users className="w-4 h-4 text-emerald-600" />
                        </div>
                        <div>
                          <p className="font-medium">Validator #{index + 1}</p>
                          <p className="text-sm text-gray-500 font-mono">
                            {validator.address.slice(0, 12)}...{validator.address.slice(-8)}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <p className="font-medium">{(validator.voting_power / 1000000).toFixed(1)}M</p>
                    </td>
                    <td className="py-4 px-6">
                      <p>{(validator.commission * 100).toFixed(1)}%</p>
                    </td>
                    <td className="py-4 px-6">
                      <p className="text-emerald-600 font-medium">{(validator.uptime_30d * 100).toFixed(1)}%</p>
                    </td>
                    <td className="py-4 px-6">
                      <Badge 
                        className={validator.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-700'}
                      >
                        {validator.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<ExplorerHome />} />
          <Route path="/wallet" element={<WalletComponent />} />
          <Route path="/validators" element={<ValidatorsComponent />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
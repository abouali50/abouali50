import React from 'react';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Coins, ArrowRight, PieChart } from 'lucide-react';
import { token } from '../data/mock';

export default function Token() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      
      <main className="pt-24">
        {/* Hero Section */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto text-center">
              <div className="flex items-center justify-center gap-4 mb-6">
                <Coins className="w-12 h-12 text-accent-cyan" />
                <h1 className="display-large text-accent-cyan">RegamCoin (RGM)</h1>
              </div>
              <p className="body-large text-text-secondary mb-8">
                Native token of Regam Blockchain. Total supply {token.totalSupply.toLocaleString()} RGM.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button className="btn-primary">
                  Get RGM
                  <ArrowRight className="w-5 h-5" />
                </Button>
                <Button className="btn-secondary">View Explorer</Button>
                <Button variant="outline" className="border-text-muted text-text-muted hover:text-white">
                  Read Docs
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Token Details */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-6xl mx-auto">
              <div className="grid lg:grid-cols-2 gap-12">
                {/* Essentials */}
                <Card className="token-card">
                  <CardHeader>
                    <CardTitle className="heading-2">Essentials</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="body-small text-text-muted mb-2">Symbol</p>
                        <p className="heading-3 text-royal-blue">{token.symbol}</p>
                      </div>
                      <div>
                        <p className="body-small text-text-muted mb-2">Total Supply</p>
                        <p className="heading-3">{token.totalSupply.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="body-small text-text-muted mb-2">Circulating</p>
                        <p className="heading-3">{token.circulating.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="body-small text-text-muted mb-2">Network</p>
                        <p className="heading-3">Regam</p>
                      </div>
                    </div>
                    
                    <div>
                      <p className="body-small text-text-muted mb-3">Use Cases</p>
                      <div className="flex flex-wrap gap-2">
                        {token.roles.map((role) => (
                          <Badge key={role} variant="secondary" className="token-badge">
                            {role}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Allocation */}
                <Card className="token-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <PieChart className="w-6 h-6 text-accent-cyan" />
                      <span className="heading-2">Token Allocation</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {token.allocation.map((allocation) => (
                        <div key={allocation.label} className="flex justify-between items-center p-3 rounded-lg bg-bg-primary">
                          <span className="body-medium">{allocation.label}</span>
                          <span className="heading-3 text-accent-cyan">{allocation.percent}%</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Token Economics */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="display-medium mb-6">Token Economics</h2>
              <p className="body-large text-text-secondary mb-12 max-w-2xl mx-auto">
                {token.description}
              </p>
              
              <div className="grid md:grid-cols-3 gap-8">
                <Card className="stat-card">
                  <CardContent className="p-6 text-center">
                    <p className="body-small text-text-muted mb-2">Market Cap</p>
                    <p className="heading-2 text-gold-accent">TBD</p>
                  </CardContent>
                </Card>
                <Card className="stat-card">
                  <CardContent className="p-6 text-center">
                    <p className="body-small text-text-muted mb-2">24h Volume</p>
                    <p className="heading-2 text-gold-accent">TBD</p>
                  </CardContent>
                </Card>
                <Card className="stat-card">
                  <CardContent className="p-6 text-center">
                    <p className="body-small text-text-muted mb-2">Holders</p>
                    <p className="heading-2 text-gold-accent">TBD</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
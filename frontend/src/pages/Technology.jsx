import React from 'react';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Zap, Shield, ArrowUp, Leaf, Network } from 'lucide-react';
import { tech } from '../data/mock';

export default function Technology() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      
      <main className="pt-24">
        {/* Hero Section */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="display-large mb-6">Technology</h1>
              <p className="body-large text-text-secondary mb-8 max-w-2xl mx-auto">
                Built with cutting-edge blockchain technology to deliver unmatched performance, 
                security, and sustainability for the future of decentralized applications.
              </p>
            </div>
          </div>
        </section>

        {/* Performance Stats */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-6xl mx-auto">
              <h2 className="display-medium text-center mb-12">Performance Overview</h2>
              <div className="grid md:grid-cols-3 gap-8">
                <Card className="stat-card">
                  <CardContent className="p-8 text-center">
                    <Zap className="w-12 h-12 text-accent-cyan mx-auto mb-4" />
                    <p className="body-small text-text-muted mb-2">TPS Target</p>
                    <p className="heading-1 text-accent-cyan">{tech.performance.tpsTarget}</p>
                  </CardContent>
                </Card>
                <Card className="stat-card">
                  <CardContent className="p-8 text-center">
                    <ArrowUp className="w-12 h-12 text-accent-cyan mx-auto mb-4" />
                    <p className="body-small text-text-muted mb-2">Block Finality</p>
                    <p className="heading-1 text-accent-cyan">{tech.performance.finality}</p>
                  </CardContent>
                </Card>
                <Card className="stat-card">
                  <CardContent className="p-8 text-center">
                    <Shield className="w-12 h-12 text-accent-cyan mx-auto mb-4" />
                    <p className="body-small text-text-muted mb-2">Average Fees</p>
                    <p className="heading-1 text-accent-cyan">{tech.performance.avgFee}</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Technology Features */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-6xl mx-auto">
              <div className="grid lg:grid-cols-2 gap-12">
                {/* Security */}
                <Card className="value-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <Shield className="w-8 h-8 text-accent-cyan" />
                      <span className="heading-2">Security</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="body-medium text-text-secondary">
                      Battle-tested security with {tech.security.validators} and comprehensive audit protocols.
                    </p>
                    <div>
                      <p className="body-small text-text-muted mb-2">Security Audits</p>
                      <div className="flex flex-wrap gap-2">
                        {tech.security.audits.map((audit) => (
                          <Badge key={audit} variant="secondary" className="token-badge">
                            {audit}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Scalability */}
                <Card className="value-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <ArrowUp className="w-8 h-8 text-accent-cyan" />
                      <span className="heading-2">Scalability</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="body-medium text-text-secondary">
                      Advanced scaling solutions through {tech.scalability.approach}.
                    </p>
                    <div>
                      <p className="body-small text-text-muted mb-2">Architecture</p>
                      <Badge variant="secondary" className="token-badge">
                        High Throughput
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                {/* Sustainability */}
                <Card className="value-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <Leaf className="w-8 h-8 text-accent-cyan" />
                      <span className="heading-2">Sustainability</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="body-medium text-text-secondary">
                      Environmental responsibility through {tech.sustainability.approach}.
                    </p>
                    <div>
                      <p className="body-small text-text-muted mb-2">Energy Efficiency</p>
                      <Badge variant="secondary" className="token-badge">
                        Low Carbon
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                {/* Interoperability */}
                <Card className="value-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <Network className="w-8 h-8 text-accent-cyan" />
                      <span className="heading-2">Interoperability</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="body-medium text-text-secondary">
                      EVM compatibility: {tech.interoperability.evmFriendly ? 'Yes' : 'No'}
                    </p>
                    <div>
                      <p className="body-small text-text-muted mb-2">Supported Wallets</p>
                      <div className="flex flex-wrap gap-2">
                        {tech.interoperability.wallets.map((wallet) => (
                          <Badge key={wallet} variant="secondary" className="token-badge">
                            {wallet}
                          </Badge>
                        ))}
                      </div>
                    </div>
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
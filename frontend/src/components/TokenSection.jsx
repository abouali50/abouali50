import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Coins, ArrowRight } from 'lucide-react';
import { homepage, token } from '../data/mock';

export const TokenSection = () => {
  const { token, stats } = mockData;

  return (
    <section className="py-24">
      <div className="dark-container">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="display-medium mb-6">RGM Token</h2>
            <p className="body-large text-text-secondary max-w-3xl mx-auto">
              {token.description}
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Token Info Card */}
            <Card className="token-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <Coins className="w-8 h-8 text-accent-cyan" />
                  <div>
                    <h3 className="heading-2">{token.name} ({token.symbol})</h3>
                    <p className="body-medium text-text-secondary">Native Token</p>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <p className="body-small text-text-muted mb-2">Total Supply</p>
                  <p className="heading-1 text-royal-blue">{token.totalSupply} {token.symbol}</p>
                </div>
                
                <div>
                  <p className="body-small text-text-muted mb-3">Use Cases</p>
                  <div className="flex flex-wrap gap-2">
                    {token.useCases.map((useCase) => (
                      <Badge key={useCase} variant="secondary" className="token-badge">
                        {useCase}
                      </Badge>
                    ))}
                  </div>
                </div>

                <Button className="btn-primary w-full">
                  View Tokenomics
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </CardContent>
            </Card>

            {/* Stats Grid */}
            <div className="space-y-6">
              <h3 className="heading-2 mb-6">At a Glance</h3>
              <div className="grid grid-cols-2 gap-4">
                {stats.map((stat, index) => (
                  <Card key={index} className="stat-card">
                    <CardContent className="p-6 text-center">
                      <p className="body-small text-text-muted mb-2">{stat.label}</p>
                      <p className="heading-3 text-accent-cyan">{stat.value}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
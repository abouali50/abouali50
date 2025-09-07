import React from 'react';
import { Card, CardContent } from './ui/card';
import { Zap, Shield, ArrowUp, Leaf, DollarSign } from 'lucide-react';
import { homepage } from '../data/mock';

const iconMap = {
  Speed: Zap,
  Security: Shield,
  Scalability: ArrowUp,
  'Eco-friendly': Leaf,
  'Low fees': DollarSign
};

export const ValueProps = () => {
  const { valueProps } = homepage;

  return (
    <section className="py-24">
      <div className="dark-container">
        <div className="text-center mb-16">
          <h2 className="display-medium mb-6">Why Regam</h2>
          <p className="body-medium text-text-secondary max-w-2xl mx-auto">
            Built for the future of decentralized applications with unmatched performance and sustainability.
          </p>
        </div>

        <div className="dark-grid">
          {valueProps.map((prop) => {
            const IconComponent = iconMap[prop.title];
            return (
              <Card key={prop.id} className="value-card">
                <CardContent className="p-8">
                  <div className="flex items-center mb-4">
                    <div className="icon-container">
                      <IconComponent className="w-6 h-6 text-accent-cyan" />
                    </div>
                    <h3 className="heading-3 ml-4">{prop.title}</h3>
                  </div>
                  <p className="body-medium text-text-secondary">
                    {prop.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};
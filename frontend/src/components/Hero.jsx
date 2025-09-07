import React from 'react';
import { Button } from './ui/button';
import { ArrowRight, ExternalLink } from 'lucide-react';
import { homepage } from '../data/mock';

export const Hero = () => {
  const { hero } = mockData;

  return (
    <section className="hero-section">
      <div className="dark-container">
        <div className="max-w-4xl mx-auto text-center py-32">
          <h1 className="display-huge mb-8">
            {hero.headline}
          </h1>
          
          <p className="body-large mb-12 text-text-secondary max-w-2xl mx-auto">
            {hero.subheadline}
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-8">
            {hero.primaryCtas.map((cta, index) => (
              <Button
                key={index}
                className={cta.variant === 'primary' ? 'btn-primary' : 'btn-secondary'}
                size="lg"
              >
                {cta.text}
                <ArrowRight className="w-5 h-5" />
              </Button>
            ))}
          </div>

          <Button variant="ghost" className="text-text-muted hover:text-text-primary">
            {hero.secondaryCta.text}
            <ExternalLink className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </section>
  );
};
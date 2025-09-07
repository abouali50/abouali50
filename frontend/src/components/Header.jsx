import React from 'react';
import { Button } from './ui/button';
import { mockData } from '../mock';

export const Header = () => {
  return (
    <header className="dark-header">
      <div className="flex items-center">
        <div className="dark-logo text-2xl font-bold text-white">
          <span className="text-royal-blue">Regam</span>
        </div>
      </div>
      
      <nav className="dark-nav hidden md:flex">
        {mockData.navigation.slice(0, 4).map((item) => (
          <a
            key={item.name}
            href={item.href}
            className="dark-nav-link"
          >
            {item.name}
          </a>
        ))}
      </nav>

      <div className="flex items-center gap-4">
        <Button variant="outline" className="btn-secondary hidden md:inline-flex">
          Read the Docs
        </Button>
        <Button className="btn-primary">
          Get RGM
        </Button>
      </div>
    </header>
  );
};
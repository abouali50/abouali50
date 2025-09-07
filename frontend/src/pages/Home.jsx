import React from 'react';
import { Header } from '../components/Header';
import { Hero } from '../components/Hero';
import { ValueProps } from '../components/ValueProps';
import { TokenSection } from '../components/TokenSection';
import { Footer } from '../components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      <main>
        <Hero />
        <ValueProps />
        <TokenSection />
      </main>
      <Footer />
    </div>
  );
}
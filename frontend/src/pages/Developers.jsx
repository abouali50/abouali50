import React from 'react';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Code, BookOpen, Gift, Github, ArrowRight, CheckCircle } from 'lucide-react';
import { dev } from '../data/mock';

export default function Developers() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      
      <main className="pt-24">
        {/* Hero Section */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="display-large mb-6">Developers</h1>
              <p className="body-large text-text-secondary mb-8 max-w-2xl mx-auto">
                Start fast with clear docs, templates, and examples. Ship payments, DeFi tools, 
                and consumer apps without the pain of high fees.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button className="btn-primary">
                  <Code className="w-5 h-5" />
                  Quick Start
                </Button>
                <Button className="btn-secondary">
                  <BookOpen className="w-5 h-5" />
                  Documentation
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Quickstart */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto">
              <h2 className="display-medium text-center mb-12">Get Started in Minutes</h2>
              
              <Card className="value-card mb-8">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <CheckCircle className="w-8 h-8 text-accent-cyan" />
                    <span className="heading-2">5-Step Quickstart</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {dev.quickstart.map((step, index) => (
                      <div key={index} className="flex items-center gap-4 p-4 rounded-lg bg-bg-primary">
                        <div className="w-8 h-8 rounded-full bg-royal-blue text-white flex items-center justify-center font-bold">
                          {index + 1}
                        </div>
                        <span className="body-medium">{step}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div className="text-center">
                <Button className="btn-primary">
                  Deploy Your First dApp
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Resources */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-6xl mx-auto">
              <h2 className="display-medium text-center mb-12">Developer Resources</h2>
              
              <div className="grid lg:grid-cols-3 gap-8">
                {/* Documentation */}
                <Card className="value-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <BookOpen className="w-8 h-8 text-accent-cyan" />
                      <span className="heading-3">Documentation</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="body-medium text-text-secondary">
                      Comprehensive guides, API references, and tutorials to get you building fast.
                    </p>
                    <div className="space-y-2">
                      <a href={dev.links.docs} className="block p-3 rounded-lg bg-bg-primary hover:bg-border-subtle transition-colors">
                        <p className="body-medium">📚 Full Documentation</p>
                      </a>
                      <a href={dev.links.sdk} className="block p-3 rounded-lg bg-bg-primary hover:bg-border-subtle transition-colors">
                        <p className="body-medium">🔧 SDK & Tools</p>
                      </a>
                    </div>
                  </CardContent>
                </Card>

                {/* GitHub */}
                <Card className="value-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <Github className="w-8 h-8 text-accent-cyan" />
                      <span className="heading-3">Open Source</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="body-medium text-text-secondary">
                      Explore our codebase, contribute to the ecosystem, and build on solid foundations.
                    </p>
                    <div className="space-y-2">
                      <a href={dev.links.github} className="block p-3 rounded-lg bg-bg-primary hover:bg-border-subtle transition-colors">
                        <p className="body-medium">💻 GitHub Repository</p>
                      </a>
                      <div className="p-3 rounded-lg bg-bg-primary">
                        <p className="body-medium">🌟 Example Projects</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Grants */}
                <Card className="value-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                      <Gift className="w-8 h-8 text-accent-cyan" />
                      <span className="heading-3">Grants Program</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="body-medium text-text-secondary">
                      Get funding for your innovative projects building on Regam Blockchain.
                    </p>
                    <div className="mb-4">
                      <Badge 
                        variant="secondary" 
                        className={`token-badge ${dev.grants.status === 'open' ? 'bg-green-900 text-green-300' : ''}`}
                      >
                        Status: {dev.grants.status}
                      </Badge>
                    </div>
                    <Button className="btn-secondary w-full">
                      Apply for Grant
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Community Support */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="display-medium mb-6">Join the Developer Community</h2>
              <p className="body-large text-text-secondary mb-8 max-w-2xl mx-auto">
                Connect with other builders, get help from the core team, and shape the future of Regam Blockchain.
              </p>
              
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="stat-card">
                  <CardContent className="p-6 text-center">
                    <p className="body-medium text-text-secondary mb-4">Join our Discord for real-time support</p>
                    <Button className="btn-primary">
                      Discord Community
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  </CardContent>
                </Card>
                <Card className="stat-card">
                  <CardContent className="p-6 text-center">
                    <p className="body-medium text-text-secondary mb-4">Weekly office hours with the team</p>
                    <Button className="btn-secondary">
                      Office Hours
                      <ArrowRight className="w-4 h-4" />
                    </Button>
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
import React from 'react';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';

export default function Terms() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      
      <main className="pt-24 pb-16">
        <div className="dark-container">
          <div className="max-w-4xl mx-auto">
            <h1 className="display-medium mb-8">Terms of Service</h1>
            <div className="prose prose-invert max-w-none">
              <p className="body-large text-text-secondary mb-8">
                Last updated: December 2024
              </p>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">1. Service Scope</h2>
                <p className="body-medium text-text-secondary mb-4">
                  Regam Blockchain provides blockchain infrastructure and related services. These terms govern your use of our website, documentation, tools, and network.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">2. No Financial Advice</h2>
                <p className="body-medium text-text-secondary mb-4">
                  The information provided on this website and through our services is for informational purposes only and does not constitute financial, investment, or legal advice. You should consult with qualified professionals before making any financial decisions.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">3. User Responsibilities</h2>
                <p className="body-medium text-text-secondary mb-4">
                  You are responsible for:
                </p>
                <ul className="list-disc list-inside space-y-2 text-text-secondary">
                  <li>Maintaining the security of your private keys and wallet credentials</li>
                  <li>Complying with applicable laws and regulations in your jurisdiction</li>
                  <li>Using our services in accordance with these terms</li>
                  <li>Conducting your own research before making any transactions</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">4. Intellectual Property</h2>
                <p className="body-medium text-text-secondary mb-4">
                  All content, trademarks, and intellectual property on this website are owned by Regam Blockchain or our licensors. You may not use our intellectual property without express written permission.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">5. Limitation of Liability</h2>
                <p className="body-medium text-text-secondary mb-4">
                  To the maximum extent permitted by law, Regam Blockchain shall not be liable for any indirect, incidental, special, or consequential damages arising from your use of our services.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">6. Governing Law</h2>
                <p className="body-medium text-text-secondary mb-4">
                  These terms are governed by and construed in accordance with applicable law. Any disputes shall be resolved through binding arbitration.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">7. Changes to Terms</h2>
                <p className="body-medium text-text-secondary mb-4">
                  We reserve the right to modify these terms at any time. Continued use of our services constitutes acceptance of any changes.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">Contact Us</h2>
                <p className="body-medium text-text-secondary">
                  If you have questions about these terms, please contact us at{' '}
                  <a href="mailto:legal@regamblockchain.com" className="text-accent-cyan hover:text-royal-blue">
                    legal@regamblockchain.com
                  </a>
                </p>
              </section>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
import React from 'react';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';

export default function Privacy() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      
      <main className="pt-24 pb-16">
        <div className="dark-container">
          <div className="max-w-4xl mx-auto">
            <h1 className="display-medium mb-8">Privacy Policy</h1>
            <div className="prose prose-invert max-w-none">
              <p className="body-large text-text-secondary mb-8">
                Last updated: December 2024
              </p>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">1. Information We Collect</h2>
                <p className="body-medium text-text-secondary mb-4">
                  We collect minimal information necessary to provide our services:
                </p>
                <ul className="list-disc list-inside space-y-2 text-text-secondary">
                  <li>Basic analytics data (page views, device type, general location)</li>
                  <li>Contact information when you voluntarily provide it</li>
                  <li>Technical data necessary for website functionality</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">2. How We Use Information</h2>
                <p className="body-medium text-text-secondary mb-4">
                  We use collected information for:
                </p>
                <ul className="list-disc list-inside space-y-2 text-text-secondary">
                  <li>Improving our website and services</li>
                  <li>Responding to your inquiries</li>
                  <li>Analytics and performance monitoring</li>
                  <li>Security and fraud prevention</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">3. Cookies</h2>
                <p className="body-medium text-text-secondary mb-4">
                  We use cookies and similar technologies to enhance your browsing experience. You can control cookie settings through your browser preferences. See our{' '}
                  <a href="/cookies" className="text-accent-cyan hover:text-royal-blue">
                    Cookie Policy
                  </a>{' '}
                  for more details.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">4. Third-Party Services</h2>
                <p className="body-medium text-text-secondary mb-4">
                  We may use third-party services for analytics and functionality. These services have their own privacy policies and terms of service.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">5. Data Security</h2>
                <p className="body-medium text-text-secondary mb-4">
                  We implement appropriate security measures to protect your information. However, no method of transmission over the internet is 100% secure.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">6. Your Rights</h2>
                <p className="body-medium text-text-secondary mb-4">
                  Depending on your jurisdiction, you may have rights regarding your personal data including access, correction, deletion, and portability.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">7. Changes to This Policy</h2>
                <p className="body-medium text-text-secondary mb-4">
                  We may update this privacy policy from time to time. We will notify you of any material changes by posting the new policy on this page.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">Contact Us</h2>
                <p className="body-medium text-text-secondary">
                  If you have questions about this privacy policy, please contact us at{' '}
                  <a href="mailto:privacy@regamblockchain.com" className="text-accent-cyan hover:text-royal-blue">
                    privacy@regamblockchain.com
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
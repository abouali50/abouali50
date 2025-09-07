import React from 'react';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';

export default function Cookies() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      
      <main className="pt-24 pb-16">
        <div className="dark-container">
          <div className="max-w-4xl mx-auto">
            <h1 className="display-medium mb-8">Cookie Policy</h1>
            <div className="prose prose-invert max-w-none">
              <p className="body-large text-text-secondary mb-8">
                Last updated: December 2024
              </p>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">What Are Cookies</h2>
                <p className="body-medium text-text-secondary mb-4">
                  Cookies are small text files that are stored on your device when you visit our website. They help us provide you with a better browsing experience and understand how our website is used.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">Types of Cookies We Use</h2>
                
                <div className="mb-6">
                  <h3 className="heading-3 mb-3">Essential Cookies</h3>
                  <p className="body-medium text-text-secondary mb-4">
                    These cookies are necessary for the website to function properly. They cannot be disabled.
                  </p>
                </div>

                <div className="mb-6">
                  <h3 className="heading-3 mb-3">Analytics Cookies</h3>
                  <p className="body-medium text-text-secondary mb-4">
                    These cookies help us understand how visitors interact with our website by collecting anonymous information.
                  </p>
                </div>

                <div className="mb-6">
                  <h3 className="heading-3 mb-3">Functional Cookies</h3>
                  <p className="body-medium text-text-secondary mb-4">
                    These cookies enable enhanced functionality and personalization, such as remembering your preferences.
                  </p>
                </div>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">How to Control Cookies</h2>
                <p className="body-medium text-text-secondary mb-4">
                  You can control and manage cookies in several ways:
                </p>
                <ul className="list-disc list-inside space-y-2 text-text-secondary">
                  <li>Through your browser settings - most browsers allow you to block or delete cookies</li>
                  <li>Through opt-out links provided by analytics services</li>
                  <li>By contacting us directly with your preferences</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">Browser Settings</h2>
                <p className="body-medium text-text-secondary mb-4">
                  Here's how to manage cookies in popular browsers:
                </p>
                <ul className="list-disc list-inside space-y-2 text-text-secondary">
                  <li><strong>Chrome:</strong> Settings → Privacy and security → Cookies and other site data</li>
                  <li><strong>Firefox:</strong> Options → Privacy & Security → Cookies and Site Data</li>
                  <li><strong>Safari:</strong> Preferences → Privacy → Cookies and website data</li>
                  <li><strong>Edge:</strong> Settings → Cookies and site permissions → Cookies and site data</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">Impact of Disabling Cookies</h2>
                <p className="body-medium text-text-secondary mb-4">
                  Disabling cookies may affect your browsing experience. Some features of our website may not function properly without cookies.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">Updates to This Policy</h2>
                <p className="body-medium text-text-secondary mb-4">
                  We may update this cookie policy from time to time. Please check this page regularly for any changes.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="heading-2 mb-4">Contact Us</h2>
                <p className="body-medium text-text-secondary">
                  If you have questions about our cookie policy, please contact us at{' '}
                  <a href="mailto:privacy@regamblockchain.com" className="text-accent-cyan hover:text-royal-blue">
                    privacy@regamblockchain.com
                  </a>
                </p>
                <p className="body-medium text-text-secondary mt-4">
                  For more information about our data practices, please see our{' '}
                  <a href="/privacy" className="text-accent-cyan hover:text-royal-blue">
                    Privacy Policy
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
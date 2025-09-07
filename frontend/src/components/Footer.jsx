import React from 'react';
import { Separator } from './ui/separator';
import { MessageCircle, Send, Twitter, Github } from 'lucide-react';
import { homepage } from '../data/mock';

const iconMap = {
  MessageCircle,
  Send, 
  Twitter,
  Github
};

export const Footer = () => {
  const { footer, community } = mockData;

  return (
    <footer className="py-16 border-t border-border-subtle">
      <div className="dark-container">
        <div className="max-w-6xl mx-auto">
          {/* Main Footer Content */}
          <div className="grid md:grid-cols-3 gap-12 mb-12">
            {/* Brand */}
            <div>
              <div className="text-2xl font-bold text-white mb-4">
                <span className="text-royal-blue">Regam</span> Blockchain
              </div>
              <p className="body-medium text-text-secondary mb-6">
                Fast, secure, scalable, and eco-friendly blockchain for the future.
              </p>
              
              {/* Community Links */}
              <div className="flex gap-4">
                {community.map((link) => {
                  const IconComponent = iconMap[link.icon];
                  return (
                    <a
                      key={link.name}
                      href={link.href}
                      className="community-link"
                      aria-label={link.name}
                    >
                      <IconComponent className="w-5 h-5" />
                    </a>
                  );
                })}
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="heading-3 mb-4">Quick Links</h4>
              <ul className="space-y-3">
                <li><a href="/technology" className="footer-link">Technology</a></li>
                <li><a href="/token" className="footer-link">RGM Token</a></li>
                <li><a href="/developers" className="footer-link">Developers</a></li>
                <li><a href="/roadmap" className="footer-link">Roadmap</a></li>
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h4 className="heading-3 mb-4">Get in Touch</h4>
              <p className="body-medium text-text-secondary mb-4">
                Questions? We're here to help.
              </p>
              <a href={`mailto:${footer.contact}`} className="footer-link">
                {footer.contact}
              </a>
            </div>
          </div>

          <Separator className="mb-8" />

          {/* Bottom Footer */}
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex flex-wrap gap-6">
              {footer.legal.map((link) => (
                <a key={link.name} href={link.href} className="footer-link">
                  {link.name}
                </a>
              ))}
            </div>
            
            <p className="body-small text-text-muted text-center md:text-right max-w-md">
              {footer.riskNote}
            </p>
          </div>

          <div className="text-center mt-8">
            <p className="body-small text-text-muted">
              © 2024 Regam Blockchain. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};
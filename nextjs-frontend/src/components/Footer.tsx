import React from 'react';
import Link from 'next/link';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <div className="text-xl font-bold text-blue-600 mb-2">
              Virtual Try-On
            </div>
            <p className="text-gray-600 text-sm">
              AI-powered virtual try-on for a faster, more confident fit check.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/try-on" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Try-On
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-gray-600 hover:text-blue-600 transition-colors">
                  About
                </Link>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Help & Support
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Technology</h3>
            <ul className="space-y-2 text-sm">
              <li className="text-gray-600">Powered by VITON-HD</li>
              <li className="text-gray-600">AI-Driven Pose Estimation</li>
              <li className="text-gray-600">Real-time Processing</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-center text-sm text-gray-500">
            © 2024 VirtualTryOn Fashion App. Built with modern web technologies.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

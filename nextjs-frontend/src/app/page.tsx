'use client';

import React from 'react';
import Link from 'next/link';

const HomePage: React.FC = () => {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-purple-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Try On Clothes
              <span className="block text-gradient">Virtually</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Experience the future of online shopping with our AI-powered virtual try-on technology. 
              See how clothes fit before you buy, powered by cutting-edge VITON-HD technology.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/try-on"
                className="bg-blue-600 text-white text-lg px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center justify-center"
              >
                Start Virtual Try-On →
              </Link>
              <button
                onClick={() => scrollToSection('about')}
                className="bg-white text-gray-700 border border-gray-300 text-lg px-8 py-3 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Learn More
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our advanced AI technology makes virtual try-on simple and realistic
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Upload Your Photo</h3>
              <p className="text-gray-600">
                Upload a clear, full-body photo of yourself in good lighting
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Choose Garment</h3>
              <p className="text-gray-600">
                Select the clothing item you want to try on from our examples or upload your own
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">See the Magic</h3>
              <p className="text-gray-600">
                Our AI processes your images and shows you how the clothes look on you
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              About Virtual Try-On
            </h2>
            <p className="text-xl text-gray-600">
              Revolutionizing online fashion shopping with cutting-edge AI technology
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">The Technology</h3>
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">VITON-HD</h4>
                <p className="text-gray-600 leading-relaxed">
                  Our virtual try-on system is powered by VITON-HD, a state-of-the-art deep learning model 
                  specifically designed for realistic clothing transfer. This advanced neural network understands 
                  human poses, body shapes, and clothing characteristics to generate highly realistic try-on results.
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Key Features:</h5>
                  <ul className="space-y-1 text-gray-600">
                    <li className="flex items-center">
                      <span className="text-green-500 mr-2">✓</span>
                      Pose-aware synthesis
                    </li>
                    <li className="flex items-center">
                      <span className="text-green-500 mr-2">✓</span>
                      High-resolution output
                    </li>
                    <li className="flex items-center">
                      <span className="text-green-500 mr-2">✓</span>
                      Realistic fitting
                    </li>
                    <li className="flex items-center">
                      <span className="text-green-500 mr-2">✓</span>
                      Preserves details
                    </li>
                  </ul>
                </div>
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Tech Stack:</h5>
                  <ul className="space-y-1 text-gray-600">
                    <li>• Next.js + TypeScript</li>
                    <li>• FastAPI + Python</li>
                    <li>• PyTorch + VITON-HD</li>
                    <li>• Standalone Services</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
            <div className="flex items-start">
              <svg className="w-6 h-6 text-blue-600 mt-1 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h4 className="text-lg font-semibold text-blue-900 mb-2">Demo Version</h4>
                <p className="text-blue-800">
                  This is a demonstration of the Virtual Try-On app. For full AI processing, 
                  the backend services need to be running with the VITON-HD model loaded. 
                  The complete codebase is available and ready to deploy!
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Try It Out?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Experience the future of online shopping today
          </p>
          <Link
            href="/try-on"
            className="inline-flex items-center bg-white text-blue-600 font-semibold px-8 py-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Get Started Now →
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;

import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            About Virtual Try-On
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Revolutionizing online fashion shopping with cutting-edge AI technology
          </p>
        </div>

        {/* Technology Section */}
        <section className="card p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">The Technology</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">VITON-HD</h3>
              <p className="text-gray-600 leading-relaxed">
                Our virtual try-on system is powered by VITON-HD (Virtual Try-On Networks - High Definition), 
                a state-of-the-art deep learning model specifically designed for realistic clothing transfer. 
                This advanced neural network understands human poses, body shapes, and clothing characteristics 
                to generate highly realistic try-on results.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Features</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span><strong>Pose-Aware Synthesis:</strong> Accurately handles different human poses and body positions</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span><strong>High-Resolution Output:</strong> Generates crisp, detailed images up to 1024x768 resolution</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span><strong>Realistic Fitting:</strong> Considers body shape and garment characteristics for natural results</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span><strong>Preserves Details:</strong> Maintains fabric textures, patterns, and styling elements</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Architecture Section */}
        <section className="card p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">System Architecture</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Frontend</h3>
              <p className="text-sm text-gray-600">React TypeScript application with modern UI components and real-time processing status</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h6m-2 10v6a2 2 0 01-2 2H6a2 2 0 01-2-2v-1m16-1a2 2 0 00-2-2V6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 00-2 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">API Service</h3>
              <p className="text-sm text-gray-600">FastAPI backend handling file uploads, job management, and service orchestration</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">ML Service</h3>
              <p className="text-sm text-gray-600">VITON-HD inference engine with pose estimation and image preprocessing</p>
            </div>
          </div>
        </section>

        {/* Development Info */}
        <section className="card p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Development Stack</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900">Frontend</h4>
              <p className="text-sm text-gray-600 mt-1">React, TypeScript, Tailwind CSS</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900">Backend</h4>
              <p className="text-sm text-gray-600 mt-1">FastAPI, Python, Redis</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900">ML</h4>
              <p className="text-sm text-gray-600 mt-1">PyTorch, OpenCV, MediaPipe</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900">Infrastructure</h4>
              <p className="text-sm text-gray-600 mt-1">Docker, Nginx, MinIO</p>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section className="card p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Get Involved</h2>
          <div className="text-center">
            <p className="text-gray-600 mb-6">
              This is an open-source project showcasing modern web development and AI integration. 
              Contributions and feedback are welcome!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="btn-primary px-6 py-3">
                View on GitHub
              </button>
              <button className="btn-secondary px-6 py-3">
                Documentation
              </button>
            </div>
          </div>
        </section>

        {/* Demo Notice */}
        <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-start">
            <svg className="w-6 h-6 text-blue-600 mt-1 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">Demo Version</h3>
              <p className="text-blue-800">
                This is a demonstration version of the Virtual Try-On application. The full functionality 
                requires the ML models to be downloaded and the backend services to be running. 
                See the README for setup instructions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
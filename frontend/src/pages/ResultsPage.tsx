import React from 'react';
import { useParams } from 'react-router-dom';

const ResultsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Try-On Results
          </h1>
          <p className="text-lg text-gray-600">
            Job ID: {jobId}
          </p>
        </div>

        {/* Demo Results */}
        <div className="card p-8 text-center">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Processing Complete!
            </h2>
            <p className="text-gray-600">
              Your virtual try-on has been processed successfully.
            </p>
          </div>

          {/* Demo Placeholder */}
          <div className="bg-gray-100 rounded-lg p-12 mb-6">
            <div className="text-gray-500 mb-4">
              <svg className="w-24 h-24 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="text-lg">Virtual Try-On Result</p>
              <p className="text-sm">
                This is a demo. In the full implementation, your processed image would appear here.
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="btn-primary px-6 py-3">
              Download Result
            </button>
            <button className="btn-secondary px-6 py-3">
              Try Another
            </button>
            <button className="btn-secondary px-6 py-3">
              Share Result
            </button>
          </div>

          {/* Info */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-800 text-sm">
              💡 <strong>Demo Mode:</strong> This is a demonstration of the Virtual Try-On app. 
              To see real results, the backend services need to be running with the VITON-HD model loaded.
            </p>
          </div>
        </div>

        {/* Processing Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card p-6 text-center">
            <div className="text-green-600 mb-2">
              <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">Status</h3>
            <p className="text-green-600">Completed</p>
          </div>

          <div className="card p-6 text-center">
            <div className="text-blue-600 mb-2">
              <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">Processing Time</h3>
            <p className="text-gray-600">~2.5 seconds</p>
          </div>

          <div className="card p-6 text-center">
            <div className="text-purple-600 mb-2">
              <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">AI Model</h3>
            <p className="text-gray-600">VITON-HD</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '../../utils/api';

const TryOnPage: React.FC = () => {
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [personImage, setPersonImage] = useState<File | null>(null);
  const [garmentImage, setGarmentImage] = useState<File | null>(null);
  const [personPreview, setPersonPreview] = useState<string | null>(null);
  const [garmentPreview, setGarmentPreview] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [resultImageUrl, setResultImageUrl] = useState<string | null>(null);
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);

  const addToast = (toast: { type: string; message: string }) => {
    // Simple alert for now, can be replaced with proper toast component
    alert(toast.message);
  };

  // Test API connection on component load
  useEffect(() => {
    const testApiConnection = async () => {
      try {
        console.log('Testing API connection...');
        const healthData = await apiClient.getHealth();
        console.log('API Health check successful:', healthData);
        setApiHealthy(true);
      } catch (error) {
        console.error('API Health check failed:', error);
        setApiHealthy(false);
      }
    };
    
    testApiConnection();
  }, []);

  const handlePersonImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        addToast({
          type: 'error',
          message: 'File size must be less than 10MB'
        });
        return;
      }

      // Validate file type
      if (!file.type.startsWith('image/')) {
        addToast({
          type: 'error',
          message: 'Please select a valid image file'
        });
        return;
      }

      setPersonImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setPersonPreview(e.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleGarmentImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        addToast({
          type: 'error',
          message: 'File size must be less than 10MB'
        });
        return;
      }

      // Validate file type
      if (!file.type.startsWith('image/')) {
        addToast({
          type: 'error',
          message: 'Please select a valid image file'
        });
        return;
      }

      setGarmentImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setGarmentPreview(e.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    console.log('Form submitted!'); // Debug log
    console.log('Person image:', personImage); // Debug log
    console.log('Garment image:', garmentImage); // Debug log
    
    if (!personImage || !garmentImage) {
      console.log('Missing images - validation failed'); // Debug log
      addToast({
        type: 'error',
        message: 'Please upload both person and garment images'
      });
      return;
    }

    console.log('Starting processing...'); // Debug log
    setIsProcessing(true);

    try {
      // Original hardcoded API calls (commented out)
      // const formData = new FormData();
      // formData.append('person_image', personImage);
      // formData.append('garment_image', garmentImage);
      // const response = await fetch('http://localhost:8000/api/v1/tryon', {
      //   method: 'POST',
      //   body: formData,
      // });

      // Updated to use apiClient with Railway backend
      console.log('About to call apiClient.virtualTryOn...'); // Debug log
      const data = await apiClient.virtualTryOn(personImage, garmentImage, true);
      console.log('Try-on job created:', data);

      // Poll for job completion
      const jobId = data.job_id;
      let jobCompleted = false;
      
      while (!jobCompleted) {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
        
        // Original hardcoded status check (commented out)
        // const statusResponse = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`);
        
        // Updated to use apiClient
        const jobData = await apiClient.getJobStatus(jobId);
        console.log('Job status:', jobData);
        
        if (jobData.status === 'completed') {
          jobCompleted = true;
          addToast({
            type: 'success',
            message: 'Processing completed! Your virtual try-on result is ready.'
          });
          
          // Set the result image URL (using Railway backend URL)
          if (jobData.result_url) {
            // Original localhost URL (commented out)
            // setResultImageUrl(`http://localhost:8000${jobData.result_url}`);
            
            // Updated for Railway backend
            setResultImageUrl(`https://backend-api-production-8f2f.up.railway.app${jobData.result_url}`);
          }
          
          // Show the result section
          setShowResult(true);
          
          // Scroll to result
          setTimeout(() => {
            const resultElement = document.getElementById('result');
            if (resultElement) {
              resultElement.scrollIntoView({ behavior: 'smooth' });
            }
          }, 100);
        } else if (jobData.status === 'failed') {
          throw new Error(jobData.message || 'Processing failed');
        }
      }

    } catch (error) {
      console.error('Try-on failed:', error);
      addToast({
        type: 'error',
        message: `Failed to process try-on: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const resetDemo = () => {
    setPersonImage(null);
    setGarmentImage(null);
    setPersonPreview(null);
    setGarmentPreview(null);
    setShowResult(false);
    setResultImageUrl(null);
    setIsProcessing(false);
    
    // Clear file inputs
    const personInput = document.getElementById('personImage') as HTMLInputElement;
    const garmentInput = document.getElementById('garmentImage') as HTMLInputElement;
    if (personInput) personInput.value = '';
    if (garmentInput) garmentInput.value = '';
  };

  const canSubmit = personImage && garmentImage && !isProcessing;
  
  // Debug logging for button state
  console.log('Button state - canSubmit:', canSubmit, 'personImage:', !!personImage, 'garmentImage:', !!garmentImage, 'isProcessing:', isProcessing);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Virtual Try-On Demo
          </h1>
          <p className="text-lg text-gray-600">
            Upload your photo and a garment to see how it looks on you
          </p>
          
          {/* API Status Indicator */}
          <div className="mt-4">
            {apiHealthy === null && (
              <div className="text-sm text-gray-500">
                🔍 Checking API connection...
              </div>
            )}
            {apiHealthy === true && (
              <div className="text-sm text-green-600">
                ✅ API connection healthy
              </div>
            )}
            {apiHealthy === false && (
              <div className="text-sm text-red-600">
                ❌ API connection failed - check console for details
              </div>
            )}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Image Upload Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Person Image Upload */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Your Photo
              </h3>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <input
                  id="personImage"
                  type="file"
                  accept="image/*"
                  onChange={handlePersonImageChange}
                  className="hidden"
                  disabled={isProcessing}
                />
                <label htmlFor="personImage" className="cursor-pointer">
                  {personPreview ? (
                    <div className="space-y-4">
                      <img
                        src={personPreview}
                        alt="Person preview"
                        className="max-w-full h-48 object-cover rounded mx-auto"
                      />
                      <p className="text-sm text-gray-500">Click to change image</p>
                    </div>
                  ) : (
                    <div>
                      <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="text-gray-600">Click to upload your photo</p>
                      <p className="text-sm text-gray-400">PNG, JPG, GIF up to 10MB</p>
                    </div>
                  )}
                </label>
              </div>
            </div>

            {/* Garment Image Upload */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Garment
              </h3>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <input
                  id="garmentImage"
                  type="file"
                  accept="image/*"
                  onChange={handleGarmentImageChange}
                  className="hidden"
                  disabled={isProcessing}
                />
                <label htmlFor="garmentImage" className="cursor-pointer">
                  {garmentPreview ? (
                    <div className="space-y-4">
                      <img
                        src={garmentPreview}
                        alt="Garment preview"
                        className="max-w-full h-48 object-cover rounded mx-auto"
                      />
                      <p className="text-sm text-gray-500">Click to change image</p>
                    </div>
                  ) : (
                    <div>
                      <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="text-gray-600">Click to upload garment</p>
                      <p className="text-sm text-gray-400">PNG, JPG, GIF up to 10MB</p>
                    </div>
                  )}
                </label>
              </div>
            </div>
          </div>

          {/* Try-On Button */}
          <div className="text-center">
            <button
              type="submit"
              disabled={!canSubmit}
              className={`px-8 py-3 rounded-lg font-semibold transition-colors ${
                canSubmit
                  ? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
                  : 'bg-gray-400 text-white cursor-not-allowed'
              }`}
            >
              {isProcessing ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : canSubmit ? (
                'Start Virtual Try-On'
              ) : (
                'Upload Both Images First'
              )}
            </button>
          </div>

          {/* Demo Result */}
          {showResult && (
            <div id="result" className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Try-On Result</h3>
              <div className="bg-gray-100 rounded-lg p-4 mb-6">
                {resultImageUrl ? (
                  <div>
                    <img
                      src={resultImageUrl}
                      alt="Virtual try-on result"
                      className="max-w-full max-h-96 mx-auto rounded-lg shadow"
                      onError={(e) => {
                        console.error('Failed to load result image');
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                    <p className="text-sm text-gray-500 mt-2">AI-Generated Virtual Try-On Result</p>
                  </div>
                ) : (
                  <div className="text-gray-500 p-8">
                    <svg className="w-24 h-24 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="text-lg">Processing Result...</p>
                    <p className="text-sm">Please wait while we generate your virtual try-on result</p>
                  </div>
                )}
              </div>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                  Download Result
                </button>
                <button 
                  onClick={resetDemo}
                  className="bg-white text-gray-700 border border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Try Another
                </button>
                <button className="bg-white text-gray-700 border border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors">
                  Share Result
                </button>
              </div>
            </div>
          )}
        </form>

        {/* Tips Section */}
        <div className="mt-12 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Tips for Best Results
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Person Photo:</h4>
              <ul className="space-y-1">
                <li>• Stand straight with arms slightly away from body</li>
                <li>• Use good lighting and plain background</li>
                <li>• Wear form-fitting clothes</li>
                <li>• Face the camera directly</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Garment Photo:</h4>
              <ul className="space-y-1">
                <li>• Use high-quality images</li>
                <li>• Ensure the garment is clearly visible</li>
                <li>• Avoid heavily wrinkled clothing</li>
                <li>• Plain backgrounds work best</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TryOnPage;
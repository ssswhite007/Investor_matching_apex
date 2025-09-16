'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import UploadForm from '@/components/UploadForm';
import AnalysisResults from '@/components/AnalysisResults';

interface FormData {
  companyName: string;
  stage: string;
  fundingGoal: string;
  continents: string[];
  countries: string[];
  pitchDeck: File | null;
}

export default function Home() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const handleSubmit = async (formData: FormData) => {
    setIsSubmitting(true);
    
    try {
      // Create FormData for file upload
      const submitData = new FormData();
      
      // Add file
      if (formData.pitchDeck) {
        submitData.append('pitchDeck', formData.pitchDeck);
      }
      
      // Add other form fields
      submitData.append('companyName', formData.companyName);
      submitData.append('stage', formData.stage);
      submitData.append('fundingGoal', formData.fundingGoal);
      submitData.append('continents', JSON.stringify(formData.continents));
      submitData.append('countries', JSON.stringify(formData.countries));
      
      // Submit to backend
      const response = await fetch('http://89.117.60.99:5000/api/upload-pitch-deck', {
        method: 'POST',
        body: submitData,
      });
      
      const result = await response.json();
      
      if (response.ok && result.success) {
        // Store the analysis result for display
        console.log('Analysis result received:', result.data);
        setAnalysisResult(result.data);
        setIsSubmitted(true);
      } else {
        throw new Error(result.error || 'Failed to analyze pitch deck');
      }
      
    } catch (error) {
      console.error('Submission error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit pitch deck';
      alert(`Error: ${errorMessage}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStartNew = () => {
    setIsSubmitted(false);
    setAnalysisResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 relative">
      <Header />
      
      {isSubmitted ? (
        <main className="relative mx-auto px-4 sm:px-6 lg:px-14 py-12">
          <div className="text-center">
            <div className="space-y-6">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
                Pitch Deck Analyzed Successfully!
              </h1>
              <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
                We've analyzed your pitch deck and found matching investment funds from our comprehensive database.
              </p>
              
              <AnalysisResults 
                analysisResult={analysisResult} 
                onStartNew={handleStartNew}
              />
            </div>
          </div>
        </main>
      ) : (
        <UploadForm 
          onSubmit={handleSubmit} 
          isSubmitting={isSubmitting} 
        />
      )}
    </div>
  );
}

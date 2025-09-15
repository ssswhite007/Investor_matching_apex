import { useState } from 'react';
import { Upload, CheckCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface FormData {
  companyName: string;
  stage: string;
  fundingGoal: string;
  continents: string[];
  countries: string[];
  pitchDeck: File | null;
}

interface UploadFormProps {
  onSubmit: (formData: FormData) => Promise<void>;
  isSubmitting: boolean;
}

export default function UploadForm({ onSubmit, isSubmitting }: UploadFormProps) {
  const [formData, setFormData] = useState<FormData>({
    companyName: '',
    stage: '',
    fundingGoal: '',
    continents: [],
    countries: [],
    pitchDeck: null,
  });
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
      setFormData(prev => ({ ...prev, pitchDeck: files[0] }));
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0 && files[0].type === 'application/pdf') {
      setFormData(prev => ({ ...prev, pitchDeck: files[0] }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  const isFormValid = !!formData.pitchDeck;

  return (
    <main className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pb-20 mt-20">
      <Card className="shadow-lg border border-gray-200 bg-white overflow-hidden">
        <CardHeader className="text-center pb-8 pt-12 bg-gradient-to-b from-blue-50 to-white">
          <CardTitle className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Start Your Journey
          </CardTitle>
          <CardDescription className="text-lg text-gray-600 max-w-lg mx-auto">
            Upload your pitch deck and get matched with relevant investment funds
          </CardDescription>
        </CardHeader>
        
        <CardContent className="p-8 md:p-12">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Pitch Deck Upload */}
            <div className="space-y-3">
              <Label className="text-lg font-semibold text-gray-900 flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Upload className="w-4 h-4 text-blue-600" />
                </div>
                Pitch Deck (PDF)
              </Label>
              <div
                className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
                  isDragOver
                    ? 'border-blue-400 bg-blue-50 scale-105'
                    : formData.pitchDeck
                    ? 'border-green-400 bg-green-50'
                    : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                
                {formData.pitchDeck ? (
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto shadow-lg">
                      <CheckCircle className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <p className="text-lg font-bold text-green-600">{formData.pitchDeck.name}</p>
                      <p className="text-sm text-green-600">
                        {(formData.pitchDeck.size / 1024 / 1024).toFixed(2)} MB • Ready to submit
                      </p>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setFormData(prev => ({ ...prev, pitchDeck: null }))}
                      className="bg-red-50 border-red-300 text-red-600 hover:bg-red-100 hover:border-red-400 rounded-lg"
                    >
                      Remove File
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto shadow-lg transition-all duration-300 ${
                      isDragOver 
                        ? 'bg-gradient-to-br from-blue-500 to-blue-600 scale-110' 
                        : 'bg-gradient-to-br from-blue-500 to-purple-600'
                    }`}>
                      <Upload className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <p className="text-xl font-bold text-gray-900 mb-2">
                        {isDragOver ? 'Drop your pitch deck here' : 'Upload Your Pitch Deck'}
                      </p>
                      <p className="text-gray-600">
                        Drag & drop your PDF here or click to browse
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        PDF files only • Maximum 25MB
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-8">
              <Button
                type="submit"
                disabled={!isFormValid || isSubmitting}
                className="w-full h-14 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold text-lg rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
              >
                <div className="flex items-center justify-center gap-3">
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Processing Application...
                    </>
                  ) : (
                    <>
                      Analyze Pitch Deck
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </div>
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}

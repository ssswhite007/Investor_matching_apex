import { Button } from '@/components/ui/button';
import FundMatchesTable from './FundMatchesTable';
import { Sparkles } from 'lucide-react';

interface AnalysisData {
  company_name?: string;
  company_email?: string;
  company_website?: string;
  stage?: string;
  sector?: string;
  location?: string;
  check_size?: string;
  investment_theme?: string;
  lead?: string;
  matching_funds?: any[];
  error?: string;
}

interface AnalysisResultsProps {
  analysisResult: AnalysisData;
  onStartNew: () => void;
}

export default function AnalysisResults({ analysisResult, onStartNew }: AnalysisResultsProps) {
  if (analysisResult.error) {
    return (
      <div className="space-y-8 mx-auto mt-12">
        <div className="bg-red-50 border border-red-200 rounded-xl p-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-red-600 text-2xl">⚠️</span>
            </div>
            <h3 className="text-2xl font-bold text-red-700 mb-4">Analysis Error</h3>
            <p className="text-gray-700 mb-4">
              There was an issue analyzing your pitch deck. Please check your OpenAI API key configuration.
            </p>
            <div className="bg-red-100 rounded-lg p-4 text-left">
              <p className="text-red-700 text-sm">
                <strong>Error:</strong> {analysisResult.error}
              </p>
            </div>
            <div className="mt-6 text-gray-600">
              <p className="text-sm">
                💡 <strong>Fix:</strong> Set your OpenAI API key in <code className="bg-gray-100 px-2 py-1 rounded">backend/.env</code>
              </p>
              <p className="text-sm mt-2">
                Get your API key at: <a href="https://platform.openai.com/account/api-keys" target="_blank" className="text-blue-600 hover:underline">platform.openai.com</a>
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-12">
          <Button 
            onClick={onStartNew}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200"
          >
            <Sparkles className="w-5 h-5 mr-2" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 mx-auto mt-12">
      {/* PDF Parsing Results */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-200 shadow-sm">
        <div className="flex items-center gap-4 mb-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">PDF Analysis Results</h3>
            <p className="text-gray-600">Information extracted from your pitch deck</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 px-6">
          <div className="bg-white rounded-xl p-4 border border-blue-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Company</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.company_name || 'N/A'}</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-blue-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Company Email</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.company_email || 'N/A'}</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-blue-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Company Website</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.company_website || 'N/A'}</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-purple-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Stage</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.stage || 'N/A'}</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-green-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Sector</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.sector || 'N/A'}</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-orange-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Location</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.location || 'N/A'}</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-yellow-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Check Size</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.check_size || 'N/A'}</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-indigo-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Investment Theme</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.investment_theme || 'N/A'}</p>
          </div>

          <div className="bg-white rounded-xl p-4 border border-indigo-100 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-semibold text-gray-700">Lead</span>
            </div>
            <p className="text-gray-900 font-medium">{analysisResult.lead || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Fund Matches Table */}
      {analysisResult.matching_funds && (
        <FundMatchesTable matches={analysisResult.matching_funds} />
      )}

      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-12">
        <Button 
          onClick={onStartNew}
          className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200"
        >
          <Sparkles className="w-5 h-5 mr-2" />
          Submit Another Application
        </Button>
      </div>
    </div>
  );
}

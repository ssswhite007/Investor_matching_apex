import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Star } from 'lucide-react';
import Pagination from './Pagination';

interface Fund {
  website?: string;
  email?: string;
  stage?: string;
  sector?: string;
  location?: string;
  check_size?: string;
  investment_theme?: string;
  lead?: string;
}

interface FundMatch {
  fund: Fund;
  confidence_rate?: number;
}

interface FundMatchesTableProps {
  matches: FundMatch[];
}

export default function FundMatchesTable({ matches }: FundMatchesTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);

  // Pagination logic
  const getPaginatedData = () => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return matches.slice(startIndex, endIndex);
  };

  const getTotalPages = () => {
    return Math.ceil(matches.length / itemsPerPage);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleItemsPerPageChange = (value: string) => {
    setItemsPerPage(parseInt(value));
    setCurrentPage(1); // Reset to first page when changing page size
  };

  if (!matches || matches.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-yellow-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-yellow-600 text-2xl">⚠️</span>
          </div>
          <h3 className="text-2xl font-bold text-yellow-700 mb-4">No Matching Funds Found</h3>
          <p className="text-gray-700 mb-4">
            We couldn't find any funds that match your criteria in our database.
          </p>
          <div className="text-gray-600 text-sm">
            <p>This might be because:</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Your pitch deck information is incomplete</li>
              <li>Your sector or stage is very niche</li>
              <li>Our fund database needs updating</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 className="text-2xl font-bold text-white">Fund Matches Found!</h3>
            <p className="text-blue-100">
              Found {matches.length} relevant investment funds from comprehensive database search
            </p>
          </div>
          
          {/* Page Size Selector */}
          <div className="flex items-center gap-3">
            <span className="text-blue-100 text-sm">Show:</span>
            <Select value={itemsPerPage.toString()} onValueChange={handleItemsPerPageChange}>
              <SelectTrigger className="w-20 h-9 bg-white/10 border-white/20 text-white focus:border-blue-300 focus:ring-blue-300/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
                <SelectItem value="50">50</SelectItem>
              </SelectContent>
            </Select>
            <span className="text-blue-100 text-sm">per page</span>
          </div>
        </div>
      </div>
      
      {/* Table */}
      <div className="overflow-x-auto px-6">
        <table className="w-full">
          <thead>
            <tr className="bg-gradient-to-r from-gray-50 to-blue-50 border-b border-gray-200">
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Rank</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Website</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Email</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Stage</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Sector</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Location</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Check Size</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Investment Theme</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Lead</th>
              <th className="py-4 px-6 text-gray-700 font-semibold text-sm">Score</th>
            </tr>
          </thead>
          <tbody>
            {getPaginatedData().map((match: FundMatch, index: number) => {
              const globalIndex = (currentPage - 1) * itemsPerPage + index;
              return (
                <tr 
                  key={index} 
                  className="border-b border-gray-100 hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-indigo-50/50 transition-all duration-200"
                >
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-3">
                      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold ${
                        globalIndex === 0 
                          ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white shadow-lg' 
                          : globalIndex === 1 
                          ? 'bg-gradient-to-r from-gray-300 to-gray-400 text-gray-800' 
                          : globalIndex === 2
                          ? 'bg-gradient-to-r from-amber-600 to-yellow-600 text-white'
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {index + 1}
                      </div>
                    </div>
                  </td>
                  
                  <td className="py-4 px-6">
                    {match.fund.website ? (
                      <div className="flex items-center justify-center gap-2">
                        <span className="font-medium text-blue-900"
                        onClick={() => window.open(`https://${match.fund.website?.replace(/^https?:\/\//, '')}`, '_blank')}
                        >
                          {match.fund.website.length > 20 ? `${match.fund.website.substring(0, 20)}...` : match.fund.website}
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                  </td>
                  
                  <td className="py-4 px-2">
                    {match.fund.email ? (
                      <a 
                        href={`mailto:${match.fund.email}`} 
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium hover:underline transition-colors"
                      >
                        {match.fund.email.length > 25 ? `${match.fund.email.substring(0, 25)}...` : match.fund.email}
                      </a>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                  </td>
                  
                  <td className="py-4 px-2">
                    {match.fund.stage ? (
                      <span className="inline-flex items-center gap-2 text-blue-800 px-3 py-1.5 rounded-full text-xs font-semibold">
                        {match.fund.stage}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                  </td>
                  
                  <td className="py-4 px-2">
                    {match.fund.sector ? (
                      <span className="inline-flex items-center gap-2 text-purple-800 px-3 py-1.5 rounded-full text-xs font-semibold">
                        {match.fund.sector}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                  </td>
                  
                  <td className="py-4 px-2">
                    {match.fund.location ? (
                      <span className="inline-flex items-center gap-2 text-green-800 px-3 py-1.5 rounded-full text-xs font-semibold">
                        {match.fund.location}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                  </td>
                  
                  <td className="py-4 px-2">
                    {match.fund.check_size ? (
                      <span className="inline-flex items-center gap-2 text-orange-800 px-3 py-1.5 rounded-full text-xs font-semibold">
                        {match.fund.check_size.length > 15 ? `${match.fund.check_size.substring(0, 15)}...` : match.fund.check_size}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                  </td>

                  <td className="py-4 px-2">
                    {match.fund.investment_theme ? (
                      <span className="inline-flex items-center gap-2 text-yellow-800 px-3 py-1.5 rounded-full text-xs font-semibold">
                        {match.fund.investment_theme.length > 20 ? `${match.fund.investment_theme.substring(0, 20)}...` : match.fund.investment_theme}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                  </td>

                  <td className="py-4 px-2">
                    {match.fund.lead ? (
                      <span className="inline-flex items-center gap-2 text-indigo-800 px-3 py-1.5 rounded-full text-xs font-semibold">
                        {match.fund.lead}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                  </td>
                  
                  <td className="py-4 px-2">
                    <div className="flex items-center justify-center">
                      <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-3 py-2 rounded-full shadow-sm">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm">{Math.round(match.confidence_rate || 0)}%</span>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      
      {/* Pagination */}
      <Pagination
        currentPage={currentPage}
        totalPages={getTotalPages()}
        totalItems={matches.length}
        itemsPerPage={itemsPerPage}
        onPageChange={handlePageChange}
      />
    </div>
  );
}

interface HeaderProps {}

export default function Header({}: HeaderProps) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">A</span>
            </div>
            <span className="text-3xl font-bold text-gray-900">APEX</span>
          </div>
          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors duration-300">
              Portfolio
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors duration-300">
              About
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors duration-300">
              Contact
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}

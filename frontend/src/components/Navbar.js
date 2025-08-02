import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MagnifyingGlassIcon, MapPinIcon, Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import SearchBar from './SearchBar';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserLocation();
  }, []);

  const fetchUserLocation = async () => {
    try {
      const response = await fetch('/api/user/location');
      if (response.ok) {
        const location = await response.json();
        setUserLocation(location);
      }
    } catch (error) {
      console.error('Error fetching user location:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (query) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
    setIsMenuOpen(false);
  };

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">P</span>
              </div>
              <span className="text-xl font-bold text-gray-900">PriceCompare</span>
            </Link>
          </div>

          {/* Desktop Search Bar */}
          <div className="hidden md:flex flex-1 max-w-2xl mx-8">
            <SearchBar onSearch={handleSearch} />
          </div>

          {/* User Location */}
          <div className="hidden md:flex items-center space-x-4">
            {isLoading ? (
              <div className="loading-spinner"></div>
            ) : userLocation ? (
              <div className="flex items-center space-x-1 text-sm text-gray-600">
                <MapPinIcon className="w-4 h-4" />
                <span>{userLocation.city}, {userLocation.country}</span>
              </div>
            ) : (
              <div className="flex items-center space-x-1 text-sm text-gray-500">
                <MapPinIcon className="w-4 h-4" />
                <span>Location unavailable</span>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-600 hover:text-gray-900 focus:outline-none focus:text-gray-900"
            >
              {isMenuOpen ? (
                <XMarkIcon className="w-6 h-6" />
              ) : (
                <Bars3Icon className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
              {/* Mobile Search Bar */}
              <div className="mb-4">
                <SearchBar onSearch={handleSearch} />
              </div>
              
              {/* Mobile User Location */}
              {userLocation && (
                <div className="flex items-center space-x-1 text-sm text-gray-600 px-3 py-2">
                  <MapPinIcon className="w-4 h-4" />
                  <span>{userLocation.city}, {userLocation.country}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar; 
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { StarIcon, ShoppingCartIcon, TrendingUpIcon } from '@heroicons/react/24/outline';
import SearchBar from '../components/SearchBar';
import ProductCard from '../components/ProductCard';

const HomePage = () => {
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [personalizedRecommendations, setPersonalizedRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTrendingProducts();
    fetchPersonalizedRecommendations();
  }, []);

  const fetchTrendingProducts = async () => {
    try {
      const response = await fetch('/api/recommendations/trending?limit=6');
      if (response.ok) {
        const data = await response.json();
        setTrendingProducts(data.products || []);
      }
    } catch (error) {
      console.error('Error fetching trending products:', error);
    }
  };

  const fetchPersonalizedRecommendations = async () => {
    try {
      const response = await fetch('/api/recommendations/personalized?limit=6');
      if (response.ok) {
        const data = await response.json();
        setPersonalizedRecommendations(data || []);
      }
    } catch (error) {
      console.error('Error fetching personalized recommendations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (query) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            Find the Best Prices
            <span className="text-primary-600"> Worldwide</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Compare prices from local and international e-commerce sites. 
            Get the best deals with our smart price comparison platform.
          </p>
          
          {/* Search Bar */}
          <div className="max-w-2xl mx-auto mb-8">
            <SearchBar onSearch={handleSearch} placeholder="What are you looking for?" />
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <ShoppingCartIcon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Comparison</h3>
              <p className="text-gray-600">Compare prices across multiple stores instantly</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <StarIcon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Best Deals</h3>
              <p className="text-gray-600">Find the lowest prices with our markup model</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <TrendingUpIcon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Trending Products</h3>
              <p className="text-gray-600">Discover what's popular in your area</p>
            </div>
          </div>
        </div>
      </div>

      {/* Trending Products */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Trending Products</h2>
          <button 
            onClick={() => navigate('/search')}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            View all →
          </button>
        </div>
        
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {trendingProducts.map((product, index) => (
              <ProductCard key={index} product={product} />
            ))}
          </div>
        )}
      </div>

      {/* Personalized Recommendations */}
      {personalizedRecommendations.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-gray-900">Recommended for You</h2>
            <button 
              onClick={() => navigate('/search')}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              View all →
            </button>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {personalizedRecommendations.map((product, index) => (
              <ProductCard key={index} product={product} />
            ))}
          </div>
        </div>
      )}

      {/* Call to Action */}
      <div className="bg-primary-600 text-white py-16">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold mb-4">Ready to Find Great Deals?</h2>
          <p className="text-xl mb-8 opacity-90">
            Start comparing prices across multiple stores and save money on your purchases.
          </p>
          <button
            onClick={() => navigate('/search')}
            className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Start Shopping
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 
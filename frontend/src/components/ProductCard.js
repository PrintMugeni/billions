import React from 'react';
import { Link } from 'react-router-dom';
import { StarIcon, ShoppingCartIcon } from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

const ProductCard = ({ product }) => {
  const handleBuyClick = (e) => {
    e.preventDefault();
    // Open product URL in new tab
    window.open(product.product_url, '_blank');
  };

  const formatPrice = (price, currency = 'USD') => {
    if (!price) return 'Price not available';
    
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
    });
    
    return formatter.format(price);
  };

  const renderRating = (rating, reviewCount) => {
    if (!rating) return null;
    
    return (
      <div className="flex items-center space-x-1">
        <div className="flex items-center">
          {[...Array(5)].map((_, i) => (
            <StarIcon
              key={i}
              className={`w-4 h-4 ${
                i < Math.floor(rating) 
                  ? 'text-yellow-400 fill-current' 
                  : 'text-gray-300'
              }`}
            />
          ))}
        </div>
        <span className="text-sm text-gray-600">
          {rating.toFixed(1)}
          {reviewCount && ` (${reviewCount})`}
        </span>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden product-card">
      {/* Product Image */}
      <div className="relative h-48 bg-gray-200">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div 
          className={`w-full h-full flex items-center justify-center text-gray-500 ${
            product.image_url ? 'hidden' : 'flex'
          }`}
        >
          <ShoppingCartIcon className="w-12 h-12" />
        </div>
        
        {/* Store Badge */}
        {product.store_name && (
          <div className="absolute top-2 left-2 bg-primary-600 text-white px-2 py-1 rounded text-xs font-medium">
            {product.store_name}
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4">
        {/* Product Name */}
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
          {product.name}
        </h3>

        {/* Rating */}
        {renderRating(product.rating, product.review_count)}

        {/* Price */}
        <div className="mt-3">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold text-gray-900">
              {formatPrice(product.price, product.currency)}
            </span>
            {product.original_price && product.original_price > product.price && (
              <span className="text-sm text-gray-500 line-through">
                {formatPrice(product.original_price, product.currency)}
              </span>
            )}
          </div>
        </div>

        {/* Category */}
        {product.category && (
          <div className="mt-2">
            <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
              {product.category}
            </span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-4 flex space-x-2">
          <button
            onClick={handleBuyClick}
            className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center justify-center space-x-2"
          >
            <ShoppingCartIcon className="w-4 h-4" />
            <span>Buy Now</span>
          </button>
          <Link
            to={`/product/${product.id}`}
            className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors text-center"
          >
            Details
          </Link>
        </div>

        {/* Additional Info */}
        <div className="mt-3 text-xs text-gray-500">
          <div className="flex justify-between">
            <span>Currency: {product.currency}</span>
            <span>Country: {product.country}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard; 
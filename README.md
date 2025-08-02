# Global Price Comparison Platform

A comprehensive price comparison platform that allows users to search for products and get the best prices from both local and international e-commerce websites.

## Features

- **User Location Detection**: Automatically detects user's country using IP geolocation
- **Real-time Web Scraping**: Pulls product data from multiple e-commerce sites
- **Smart Search**: Autocomplete search with product suggestions
- **Price Comparison**: Shows top 3 best deals for each product
- **Personalized Recommendations**: Learns from user search history
- **Revenue Model**: Small markup on cheapest prices
- **Admin Dashboard**: Analytics and scraper management

## Supported E-commerce Sites

### Uganda
- Jumia
- Jiji
- Ubuy
- Xente
- Dondolo

### International
- Amazon
- Walmart
- AliExpress

## Tech Stack

- **Frontend**: React + Tailwind CSS
- **Backend**: Python FastAPI
- **Scraping**: Playwright + BeautifulSoup
- **Database**: PostgreSQL
- **Hosting**: Railway/Heroku/Render

## Project Structure

```
price-comparison-platform/
├── frontend/                 # React frontend application
├── backend/                  # FastAPI backend application
├── scrapers/                 # Web scraping modules
├── database/                 # Database schemas and migrations
├── admin/                    # Admin dashboard
└── docs/                     # Documentation
```

## Quick Start

1. Clone the repository
2. Install dependencies for both frontend and backend
3. Set up environment variables
4. Run the development servers

## Environment Variables

Create `.env` files in both frontend and backend directories with:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
GEOIP_API_KEY=your_geoip_api_key
SCRAPER_TIMEOUT=30000
ADMIN_SECRET=your_admin_secret
```

## License

MIT License 
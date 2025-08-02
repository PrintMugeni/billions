import httpx
import asyncio
from typing import Optional
from app.schemas import UserLocation
from app.config import settings
import json

class GeoIPService:
    def __init__(self):
        self.api_key = settings.GEOIP_API_KEY
        self.fallback_apis = [
            "http://ip-api.com/json/",
            "https://ipapi.co/json/",
            "https://api.ipify.org?format=json"
        ]
    
    async def get_location_by_ip(self, ip_address: str) -> UserLocation:
        """Get location information for an IP address"""
        try:
            # Try primary API first (if configured)
            if self.api_key:
                location = await self._get_location_with_api_key(ip_address)
                if location:
                    return location
            
            # Fallback to free APIs
            location = await self._get_location_fallback(ip_address)
            if location:
                return location
            
            # Default fallback
            return UserLocation(
                country="Unknown",
                city="Unknown",
                ip_address=ip_address
            )
            
        except Exception as e:
            print(f"Error getting location for IP {ip_address}: {str(e)}")
            return UserLocation(
                country="Unknown",
                city="Unknown",
                ip_address=ip_address
            )
    
    async def _get_location_with_api_key(self, ip_address: str) -> Optional[UserLocation]:
        """Get location using API key (e.g., MaxMind, IP2Location)"""
        try:
            # Example with MaxMind GeoIP2
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://geoip-db.com/json/{ip_address}",
                    headers={"User-Agent": settings.SCRAPER_USER_AGENT}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return UserLocation(
                        country=data.get("country_name", "Unknown"),
                        city=data.get("city", "Unknown"),
                        region=data.get("state", "Unknown"),
                        ip_address=ip_address,
                        timezone=data.get("time_zone", "Unknown")
                    )
        except Exception as e:
            print(f"Error with API key location service: {str(e)}")
        
        return None
    
    async def _get_location_fallback(self, ip_address: str) -> Optional[UserLocation]:
        """Get location using free fallback APIs"""
        for api_url in self.fallback_apis:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        api_url,
                        headers={"User-Agent": settings.SCRAPER_USER_AGENT}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Parse different API response formats
                        if "ip-api.com" in api_url:
                            return UserLocation(
                                country=data.get("country", "Unknown"),
                                city=data.get("city", "Unknown"),
                                region=data.get("regionName", "Unknown"),
                                ip_address=data.get("query", ip_address),
                                timezone=data.get("timezone", "Unknown")
                            )
                        elif "ipapi.co" in api_url:
                            return UserLocation(
                                country=data.get("country_name", "Unknown"),
                                city=data.get("city", "Unknown"),
                                region=data.get("region", "Unknown"),
                                ip_address=data.get("ip", ip_address),
                                timezone=data.get("timezone", "Unknown")
                            )
                        elif "ipify.org" in api_url:
                            # This only gives IP, so we need to get location separately
                            return await self._get_location_for_ip(data.get("ip", ip_address))
                            
            except Exception as e:
                print(f"Error with fallback API {api_url}: {str(e)}")
                continue
        
        return None
    
    async def _get_location_for_ip(self, ip_address: str) -> UserLocation:
        """Get location for IP using a simple geolocation service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip_address}",
                    headers={"User-Agent": settings.SCRAPER_USER_AGENT}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return UserLocation(
                        country=data.get("country", "Unknown"),
                        city=data.get("city", "Unknown"),
                        region=data.get("regionName", "Unknown"),
                        ip_address=ip_address,
                        timezone=data.get("timezone", "Unknown")
                    )
        except Exception as e:
            print(f"Error getting location for IP {ip_address}: {str(e)}")
        
        return UserLocation(
            country="Unknown",
            city="Unknown",
            ip_address=ip_address
        )
    
    def get_relevant_sites_for_country(self, country: str) -> dict:
        """Get relevant e-commerce sites for a specific country"""
        country_lower = country.lower()
        
        # Map countries to their relevant sites
        country_sites = {
            "uganda": settings.ECOMMERCE_SITES["uganda"],
            "kenya": {
                "jumia": settings.ECOMMERCE_SITES["uganda"]["jumia"],
                "kilimall": {
                    "base_url": "https://www.kilimall.co.ke",
                    "search_url": "https://www.kilimall.co.ke/search?q={query}",
                    "enabled": True
                }
            },
            "nigeria": {
                "jumia": {
                    "base_url": "https://www.jumia.com.ng",
                    "search_url": "https://www.jumia.com.ng/catalog/?q={query}",
                    "enabled": True
                },
                "konga": {
                    "base_url": "https://www.konga.com",
                    "search_url": "https://www.konga.com/search?q={query}",
                    "enabled": True
                }
            }
        }
        
        # Return country-specific sites + international sites
        relevant_sites = country_sites.get(country_lower, {})
        international_sites = settings.ECOMMERCE_SITES["international"]
        
        return {
            "local": relevant_sites,
            "international": international_sites
        } 
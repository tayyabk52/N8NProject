#!/usr/bin/env python3
"""
Production server for optimized scraper
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any
from flask import Flask, request, jsonify

from utils.async_manager import AsyncEventLoopManager
from utils.file_saver import FileSaver
from scrapers.google_maps_scraper import OptimizedGoogleMapsScraper

logger = logging.getLogger(__name__)

class ProductionServer:
    """Production server for optimized scraper"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.scraper = None
        self.event_loop_manager = AsyncEventLoopManager()
        self._setup_routes()
        self._setup_error_handlers()
        self.result_cache = {}
        self.CACHE_DURATION = 15 * 60  # Cache results for 15 minutes
        
    def _make_docker_compatible_response(self, data, status_code=200):
        """Create Docker-compatible response with proper headers"""
        response = jsonify(data)
        response.status_code = status_code
        
        # Add headers for Docker networking compatibility
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Connection'] = 'close'  # Force connection close
        response.headers['Content-Type'] = 'application/json'
        
        return response
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return self._make_docker_compatible_response({
                "status": "healthy",
                "service": "Optimized Google Maps Scraper V6",
                "timestamp": datetime.now().isoformat(),
                "version": "6.0.0 - Smart Auto-Scroll + Two-Phase Extraction",
                "features": [
                    "Dynamic Scroll Container Detection",
                    "Viewport-Based Auto-Scroll",
                    "Two-Phase Extraction (List + Detail)",
                    "Enhanced Error Handling & Retry Logic",
                    "Regex-Based Data Parsing",
                    "Single Request Processing"
                ]
            })
        
        @self.app.route('/scrape-single', methods=['POST', 'OPTIONS'])
        def scrape_single():
            if request.method == 'OPTIONS':
                return self._handle_options_request()
            return self._handle_scrape_single()

    def _handle_options_request(self):
        """Handle CORS preflight OPTIONS requests"""
        response = self._make_docker_compatible_response({"status": "ok"})
        return response
    
    def _handle_scrape_single(self):
        """Handle single scraping request"""
        try:
            data = request.get_json()
            if not data:
                return self._make_docker_compatible_response({
                    "success": False,
                    "error": "No data provided",
                    "businesses": []
                }, 400)
            
            search_term = data.get('search_term', '')
            area_name = data.get('area_name', '')
            
            # Skip cache if explicitly requested
            bypass_cache = data.get('bypass_cache', False)
            
            # Check cache for existing result
            if not bypass_cache:
                cache_key = f"{search_term}_{area_name}"
                if cache_key in self.result_cache:
                    cache_entry = self.result_cache[cache_key]
                    if time.time() - cache_entry['timestamp'] < self.CACHE_DURATION:
                        logger.info(f"Returning cached result for '{search_term}' in '{area_name}'")
                        cache_entry['data']['from_cache'] = True
                        return self._make_docker_compatible_response(cache_entry['data'])
            
            logger.info(f"Processing single request: {search_term} in {area_name}")
            
            try:
                result = self.event_loop_manager.run_async(
                    self._process_single_async(data),
                    timeout=300.0  # 5 minute timeout
                )
                
                # Force immediate response - don't wait for file saving
                response_data = {
                    "success": result.get('success', False),
                    "businesses": result.get('businesses', []),
                    "total_found": result.get('total_found', 0),
                    "search_term": result.get('search_term', ''),
                    "area_name": result.get('area_name', ''),
                    "extraction_method": result.get('extraction_method', ''),
                    "timestamp": datetime.now().isoformat(),
                    "from_cache": False
                }
                
                # Cache successful results
                if response_data['success'] and search_term and area_name:
                    cache_key = f"{search_term}_{area_name}"
                    self.result_cache[cache_key] = {
                        'timestamp': time.time(),
                        'data': response_data
                    }
                    logger.info(f"Cached result for '{search_term}' in '{area_name}'")
                
                # Save files in background (don't block response)
                try:
                    FileSaver.save_results_to_json(result, 'single')
                    FileSaver.save_results_to_csv(result, 'single')
                except Exception as save_error:
                    logger.warning(f"Background save failed: {save_error}")
                
                return self._make_docker_compatible_response(response_data)
                
            except Exception as e:
                error_message = str(e)
                logger.error(f"Single processing failed: {error_message}")
                error_result = {
                    "success": False,
                    "error": error_message,
                    "search_term": search_term,
                    "area_name": area_name,
                    "businesses": [],
                    "timestamp": datetime.now().isoformat()
                }
                # Save error result
                try:
                    FileSaver.save_results_to_json(error_result, 'single_error')
                except:
                    pass
                
                return self._make_docker_compatible_response(error_result, 500)
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Request handling failed: {error_message}")
            return self._make_docker_compatible_response({
                "success": False,
                "error": error_message,
                "businesses": []
            }, 500)
    
    async def _process_single_async(self, request_data):
        """Process single request asynchronously with fresh browser approach"""
        # Create a new scraper for each request to ensure completely fresh state
        # This mimics the "first request after server restart" behavior
        scraper = OptimizedGoogleMapsScraper()
        
        try:
            return await scraper.scrape_single_search(request_data)
        except Exception as e:
            logger.error(f"Scraper error: {str(e)}")
            return {
                "success": False,
                "error": f"Scraper error: {str(e)}",
                "search_term": request_data.get('search_term', ''),
                "area_name": request_data.get('area_name', ''),
                "businesses": [],  # Return empty businesses list on error
                "timestamp": datetime.now().isoformat()
            }
    
    def _setup_error_handlers(self):
        """Setup error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return self._make_docker_compatible_response({"error": "Endpoint not found"}, 404)
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return self._make_docker_compatible_response({"error": "Internal server error"}, 500)
    
    def run(self, host='0.0.0.0', port=5000):
        """Run the server"""
        logger.info("🚀 Starting Optimized Google Maps Scraper V6...")
        logger.info("🎯 Features: Smart auto-scroll + Two-phase extraction")
        logger.info("🔬 Based on JavaScript testing insights")
        logger.info("📝 Simplified: Single request processing only")
        
        # Log caching configuration
        cache_minutes = self.CACHE_DURATION // 60
        logger.info(f"💾 Result caching ENABLED - Results cached for {cache_minutes} minutes")
        logger.info(f"💾 To bypass cache, include 'bypass_cache: true' in requests")
        
        logger.info("Available endpoints:")
        logger.info("  GET  /health - Health check")
        logger.info("  POST /scrape-single - Single search with optimized extraction")
        
        self.app.run(host=host, port=port, debug=False, threaded=True) 
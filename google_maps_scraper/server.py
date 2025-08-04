#!/usr/bin/env python3
"""
Production server for optimized scraper
"""

import os
import time
import logging
import threading
import requests
from datetime import datetime
from typing import Dict, Any
from flask import Flask, request, jsonify

# Add these imports for async functionality
from supabase import create_client, Client

from utils.async_manager import AsyncEventLoopManager
from utils.file_saver import FileSaver
from scrapers.google_maps_scraper import OptimizedGoogleMapsScraper

logger = logging.getLogger(__name__)

# Add Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://rchtpjzauzntftiqttqo.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')  # Add your key to environment
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

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
        
        @self.app.route('/scrape-job-async', methods=['POST', 'OPTIONS'])
        def scrape_job_async():
            if request.method == 'OPTIONS':
                return self._handle_options_request()
            return self._handle_scrape_job_async()

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
    
    def _handle_scrape_job_async(self):
        """Handle async scraping job request"""
        try:
            data = request.get_json()
            if not data:
                return self._make_docker_compatible_response({
                    "success": False,
                    "error": "No data provided"
                }, 400)
            
            job_id = data.get('job_id')
            completion_webhook = data.get('completion_webhook')
            
            if not job_id or not completion_webhook:
                return self._make_docker_compatible_response({
                    "success": False,
                    "error": "job_id and completion_webhook are required"
                }, 400)
            
            # Log the incoming request
            logger.info(f"Received async job request: job_id={job_id}, area={data.get('area_name')}, keyword={data.get('keyword')}")
            
            # Start scraping in background thread
            thread = threading.Thread(
                target=self._process_job_async,
                args=(data,),
                daemon=True
            )
            thread.start()
            
            # Return immediately
            return self._make_docker_compatible_response({
                "success": True,
                "message": f"Job {job_id} started successfully",
                "job_id": job_id,
                "status": "started"
            })
            
        except Exception as e:
            logger.error(f"Async job handler error: {str(e)}")
            return self._make_docker_compatible_response({
                "success": False,
                "error": str(e)
            }, 500)
    
    def _process_job_async(self, job_data):
        """Process scraping job asynchronously in background thread"""
        job_id = job_data.get('job_id')
        completion_webhook = job_data.get('completion_webhook')
        start_time = time.time()
        
        logger.info(f"Starting async processing for job {job_id}")
        
        try:
            # Update job status to running
            self._update_job_status(job_id, 'running')
            
            # Prepare scraping request
            scrape_request = {
                'search_term': job_data.get('search_term', job_data.get('keyword', '')),
                'area_name': job_data.get('area_name', ''),
                'max_results': job_data.get('max_results', 50),
                'max_retries': 2,
                'bypass_cache': True  # Always use fresh data for jobs
            }
            
            # Process the scraping
            result = self.event_loop_manager.run_async(
                self._process_single_async(scrape_request),
                timeout=300.0
            )
            
            # Calculate processing time
            processing_time = int(time.time() - start_time)
            
            # Insert businesses directly into Supabase
            businesses_inserted = 0
            if result.get('success') and result.get('businesses'):
                businesses_inserted = self._insert_businesses_to_supabase(
                    result['businesses'], 
                    job_data.get('area_id'),
                    job_id
                )
                logger.info(f"Job {job_id}: Inserted {businesses_inserted} businesses to database")
            
            # Prepare completion data
            completion_data = {
                "job_id": job_id,
                "success": result.get('success', False),
                "businesses_found": len(result.get('businesses', [])),
                "businesses_inserted": businesses_inserted,
                "processing_time": processing_time,
                "error_message": result.get('error'),
                "search_term": job_data.get('search_term', job_data.get('keyword', '')),
                "area_name": job_data.get('area_name', ''),
                "area_id": job_data.get('area_id'),
                "timestamp": datetime.now().isoformat()
            }
            
            # Send completion webhook
            self._send_completion_webhook(completion_webhook, completion_data, job_id)
            
        except Exception as e:
            logger.error(f"Async job {job_id} failed: {e}")
            # Send failure webhook
            self._send_completion_webhook(completion_webhook, {
                "job_id": job_id,
                "success": False,
                "error_message": str(e),
                "processing_time": int(time.time() - start_time),
                "timestamp": datetime.now().isoformat()
            }, job_id)
    
    def _update_job_status(self, job_id, status, error_message=None):
        """Update job status in Supabase"""
        if not supabase:
            logger.warning(f"Supabase not configured, cannot update job {job_id} status")
            return
        
        try:
            update_data = {
                "status": status,
            }
            
            if status == 'running':
                update_data["started_at"] = datetime.now().isoformat()
            elif status in ['completed', 'failed']:
                update_data["completed_at"] = datetime.now().isoformat()
            
            if error_message:
                update_data["error_message"] = error_message
            
            result = supabase.table('scrape_jobs').update(update_data).eq('id', job_id).execute()
            logger.info(f"Updated job {job_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id} status: {e}")
    
    def _insert_businesses_to_supabase(self, businesses, area_id, job_id):
        """Insert businesses directly into Supabase"""
        if not supabase or not businesses:
            return 0
        
        try:
            # Transform businesses for database
            db_businesses = []
            for business in businesses:
                # Prepare business record
                db_business = {
                    "area_id": area_id,
                    "scrape_job_id": job_id,
                    "name": business.get('name', '').strip()[:200] if business.get('name') else None,
                    "address": business.get('address', '').strip()[:500] if business.get('address') else None,
                    "phone": business.get('phone', '').strip()[:50] if business.get('phone') else None,
                    "website": business.get('website', '').strip()[:500] if business.get('website') else None,
                    "category": business.get('category', '').strip()[:100] if business.get('category') else None,
                    "rating": float(business['rating']) if business.get('rating') is not None else None,
                    "review_count": int(business['review_count']) if business.get('review_count') is not None else None,
                    "latitude": float(business['latitude']) if business.get('latitude') is not None else None,
                    "longitude": float(business['longitude']) if business.get('longitude') is not None else None,
                    "raw_info": business,  # Store complete raw data as JSONB
                    "status": "new",
                    "contact_status": "not_contacted",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Only add businesses with names
                if db_business['name']:
                    db_businesses.append(db_business)
            
            # Bulk insert with conflict resolution
            if db_businesses:
                # Insert in batches to avoid size limits
                batch_size = 50
                total_inserted = 0
                
                for i in range(0, len(db_businesses), batch_size):
                    batch = db_businesses[i:i + batch_size]
                    result = supabase.table('businesses').insert(batch).execute()
                    total_inserted += len(batch)
                    logger.info(f"Inserted batch of {len(batch)} businesses for job {job_id}")
                
                logger.info(f"✅ Total inserted {total_inserted} businesses for job {job_id}")
                return total_inserted
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to insert businesses: {e}")
            return 0
    
    def _send_completion_webhook(self, webhook_url, result, job_id):
        """Send completion notification to n8n webhook"""
        try:
            webhook_data = {
                "job_id": job_id,
                "success": result.get('success', False),
                "businesses_found": result.get('businesses_found', 0),
                "businesses_inserted": result.get('businesses_inserted', 0),
                "processing_time": result.get('processing_time'),
                "error_message": result.get('error_message'),
                "search_term": result.get('search_term'),
                "area_name": result.get('area_name'),
                "area_id": result.get('area_id'),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Sending completion webhook for job {job_id} to {webhook_url}")
            
            response = requests.post(webhook_url, json=webhook_data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Completion webhook sent successfully for job {job_id}")
            else:
                logger.warning(f"⚠️ Webhook failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to send completion webhook: {e}")
    
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
        logger.info("🔄 Async Job Support: ENABLED for n8n workflow integration")
        
        # Check if Supabase is configured
        if supabase:
            logger.info("✅ Supabase connection configured for direct database insertion")
        else:
            logger.warning("⚠️ Supabase not configured - job status updates and business insertion disabled")
        
        # Log caching configuration
        cache_minutes = self.CACHE_DURATION // 60
        logger.info(f"💾 Result caching ENABLED - Results cached for {cache_minutes} minutes")
        logger.info(f"💾 To bypass cache, include 'bypass_cache: true' in requests")
        
        logger.info("Available endpoints:")
        logger.info("  GET  /health - Health check")
        logger.info("  POST /scrape-single - Single search with optimized extraction")
        logger.info("  POST /scrape-job-async - Async job processing for n8n workflow")
        
        self.app.run(host=host, port=port, debug=False, threaded=True) 
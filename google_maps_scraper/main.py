#!/usr/bin/env python3
"""
Main entry point for the Optimized Google Maps Scraper
"""

import logging
from server import ProductionServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    server = ProductionServer()
    server.run() 
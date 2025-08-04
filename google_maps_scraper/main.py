#!/usr/bin/env python3
"""
Main entry point for the Optimized Google Maps Scraper
"""

import logging
import os
from dotenv import load_dotenv
from server import ProductionServer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    server = ProductionServer()
    server.run() 
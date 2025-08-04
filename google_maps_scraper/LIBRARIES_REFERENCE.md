# Libraries Reference Guide - Google Maps Scraper

## Core Libraries

### 1. Flask (`flask`)
**Purpose**: Web framework for the API server
**Usage in Scraper**:
- Creates RESTful API endpoints (`/health`, `/scrape-single`)
- Handles HTTP requests and responses
- Manages request validation and error handling
- Provides JSON responses with proper headers

**Key Features Used**:
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/scrape-single', methods=['POST'])
def scrape_single():
    data = request.get_json()
    return jsonify(result)
```

### 2. Playwright (`playwright.async_api`)
**Purpose**: Modern browser automation library
**Usage in Scraper**:
- Controls Chromium browser instances
- Navigates to Google Maps pages
- Interacts with page elements (click, scroll, type)
- Extracts data from web pages
- Implements stealth measures

**Key Features Used**:
```python
from playwright.async_api import async_playwright, Browser, Page

# Launch browser
playwright = await async_playwright().start()
browser = await playwright.chromium.launch(headless=True)

# Create page and navigate
page = await browser.new_page()
await page.goto(url)

# Extract data
elements = await page.query_selector_all('.Nv2PK')
text = await element.inner_text()
```

### 3. Asyncio (`asyncio`)
**Purpose**: Asynchronous programming support
**Usage in Scraper**:
- Manages concurrent browser operations
- Handles async event loops in Flask
- Enables non-blocking I/O operations
- Coordinates multiple async tasks

**Key Features Used**:
```python
import asyncio

# Run async functions
result = await scraper.scrape_single_search(request_data)

# Async loops
for i in range(cards_to_process):
    await self._extract_card_data(page, card)

# Async context managers
async with self._lock:
    # Critical section
```

### 4. Logging (`logging`)
**Purpose**: Structured logging system
**Usage in Scraper**:
- Debug information and error tracking
- Performance monitoring
- Request/response logging
- Error reporting

**Key Features Used**:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Starting scraping process")
logger.warning("No results found")
logger.error("Scraping failed: %s", error)
```

## Data Processing Libraries

### 5. Regular Expressions (`re`)
**Purpose**: Pattern matching for data extraction
**Usage in Scraper**:
- Extract phone numbers from text
- Parse coordinates from URLs
- Clean and validate data
- Extract ratings and review counts

**Key Patterns Used**:
```python
import re

# Phone number extraction
phone_pattern = r'\+?[\d\s\-\(\)]+'

# Coordinate extraction
coord_pattern = r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)'

# Rating extraction
rating_pattern = r'(\d+\.?\d*)'
```

### 6. Phonenumbers (`phonenumbers`)
**Purpose**: International phone number handling
**Usage in Scraper**:
- Validate phone number formats
- Format phone numbers internationally
- Parse different phone number formats
- Handle country-specific patterns

**Key Features Used**:
```python
import phonenumbers

# Parse and validate phone number
parsed = phonenumbers.parse(phone, None)
if phonenumbers.is_valid_number(parsed):
    formatted = phonenumbers.format_number(parsed, 
                                        phonenumbers.PhoneNumberFormat.INTERNATIONAL)
```

### 7. Random (`random`)
**Purpose**: Random number generation for anti-detection
**Usage in Scraper**:
- Random delays between actions
- Random viewport selection
- Random user agent selection
- Anti-detection timing

**Key Features Used**:
```python
import random

# Random delays
await asyncio.sleep(random.uniform(1.0, 3.0))

# Random viewport
viewport = random.choice([
    {'width': 1920, 'height': 1080},
    {'width': 1366, 'height': 768}
])

# Random user agent
user_agent = random.choice(user_agents)
```

## File Handling Libraries

### 8. JSON (`json`)
**Purpose**: JSON data handling
**Usage in Scraper**:
- API request/response formatting
- File export (JSON format)
- Configuration storage
- Error reporting

**Key Features Used**:
```python
import json

# Save results to JSON file
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

# Parse JSON request
data = request.get_json()
```

### 9. CSV (`csv`)
**Purpose**: CSV file export
**Usage in Scraper**:
- Export business data to spreadsheet format
- Create tabular data files
- Enable easy data analysis

**Key Features Used**:
```python
import csv

# Write CSV file
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for business in businesses:
        writer.writerow(business)
```

## System Libraries

### 10. Threading (`threading`)
**Purpose**: Thread management for async operations
**Usage in Scraper**:
- Event loop management in Flask
- Thread-safe operations
- Background task handling

**Key Features Used**:
```python
import threading

# Thread-safe locks
self._lock = threading.Lock()

# Background thread for event loop
thread = threading.Thread(target=run_loop, daemon=True)
```

### 11. Time (`time`)
**Purpose**: Time-related operations
**Usage in Scraper**:
- Cache timestamp management
- Performance timing
- Request timing

**Key Features Used**:
```python
import time

# Cache timestamps
timestamp = time.time()
if time.time() - cache_entry['timestamp'] < self.CACHE_DURATION:
    # Use cached result
```

### 12. Datetime (`datetime`)
**Purpose**: Date and time handling
**Usage in Scraper**:
- File naming with timestamps
- Request timestamping
- Log timestamps

**Key Features Used**:
```python
from datetime import datetime

# Create timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{search_term}_{timestamp}.json"
```

## Type Hints and Utilities

### 13. Typing (`typing`)
**Purpose**: Type hints for better code documentation
**Usage in Scraper**:
- Function parameter type hints
- Return type annotations
- Generic type support

**Key Features Used**:
```python
from typing import Dict, Any, List, Optional, Tuple

def scrape_single_search(self, search_request: Dict[str, Any]) -> Dict[str, Any]:
    pass

async def extract_business_data(self, page: Page) -> Optional[Dict[str, Any]]:
    pass
```

### 14. OS (`os`)
**Purpose**: Operating system interface
**Usage in Scraper**:
- File path operations
- Directory management
- Environment variable access

**Key Features Used**:
```python
import os

# File path operations
filepath = os.path.join(os.getcwd(), filename)

# Environment variables
debug_mode = os.getenv('DEBUG', 'False')
```

## Library Dependencies and Versions

### Required Dependencies:
```
Flask>=2.0.0
playwright>=1.30.0
phonenumbers>=8.12.0
```

### Optional Dependencies:
```
asyncio (built-in)
logging (built-in)
re (built-in)
json (built-in)
csv (built-in)
random (built-in)
threading (built-in)
time (built-in)
datetime (built-in)
typing (built-in)
os (built-in)
```

## Library Integration Patterns

### 1. Async/Await Pattern
```python
# Flask + Asyncio integration
class AsyncEventLoopManager:
    def run_async(self, coro, timeout=300.0):
        loop = self.get_loop()
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result(timeout=timeout)
```

### 2. Browser Automation Pattern
```python
# Playwright + Asyncio integration
async def scrape_with_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        # ... scraping logic
        await browser.close()
```

### 3. Data Processing Pattern
```python
# Regex + Validation pattern
def extract_phone_number(text: str) -> Optional[str]:
    # Use regex to find phone patterns
    match = re.search(phone_pattern, text)
    if match:
        phone = match.group(1)
        # Use phonenumbers library to validate
        if self._is_valid_phone(phone):
            return self._format_phone(phone)
    return None
```

### 4. File Export Pattern
```python
# JSON + CSV export pattern
def save_results(self, result: Dict[str, Any]):
    # Save as JSON
    with open(json_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Save as CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for business in result['businesses']:
            writer.writerow(business)
```

## Performance Considerations

### 1. Memory Management
- **Browser Cleanup**: Always close browser instances
- **Async Context**: Use async context managers
- **File Handles**: Properly close file handles

### 2. Concurrency
- **Async Operations**: Use asyncio for I/O operations
- **Thread Safety**: Use locks for shared resources
- **Event Loop**: Proper event loop management

### 3. Error Handling
- **Graceful Degradation**: Handle library-specific errors
- **Resource Cleanup**: Ensure cleanup in error cases
- **Logging**: Comprehensive error logging

## Best Practices

### 1. Library Usage
- **Import Organization**: Group imports by type
- **Type Hints**: Use typing for better documentation
- **Error Handling**: Handle library-specific exceptions

### 2. Performance
- **Async Operations**: Use async/await for I/O
- **Resource Management**: Proper cleanup of resources
- **Caching**: Implement appropriate caching strategies

### 3. Maintainability
- **Modular Design**: Separate concerns by library
- **Configuration**: Externalize library-specific configs
- **Documentation**: Document library usage patterns 
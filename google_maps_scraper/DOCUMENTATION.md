# Google Maps Scraper - Comprehensive Documentation

## Overview

This is a sophisticated Google Maps scraper built with Python that extracts business information from Google Maps search results. The system uses a modular architecture with advanced browser automation, smart scrolling, and two-phase data extraction.

## Architecture

### Modular Structure

```
├── main.py                 # Entry point
├── server.py              # Flask API server
├── config.py              # Configuration and selectors
├── browser_manager.py     # Browser pool and context management
├── scrapers/
│   ├── base_scraper.py   # Abstract base class
│   └── google_maps_scraper.py  # Main scraper implementation
├── extractors/
│   ├── scroll_manager.py  # Smart auto-scroll functionality
│   └── data_extractor.py # Data extraction logic
└── utils/
    ├── async_manager.py   # Async event loop management
    └── file_saver.py     # File saving utilities
```

## Core Libraries and Technologies

### Primary Libraries

1. **Flask** (`flask`)
   - Web framework for the API server
   - Handles HTTP requests and responses
   - Provides RESTful endpoints

2. **Playwright** (`playwright.async_api`)
   - Modern browser automation library
   - Supports Chromium, Firefox, and WebKit
   - Used for: Browser control, page navigation, element interaction
   - Key features: Headless browsing, stealth measures, async operations

3. **Asyncio** (`asyncio`)
   - Python's built-in asynchronous programming library
   - Enables concurrent operations without blocking
   - Used for: Browser operations, file I/O, API handling

4. **Logging** (`logging`)
   - Python's built-in logging system
   - Provides structured logging with different levels
   - Used for: Debugging, monitoring, error tracking

### Supporting Libraries

5. **Regular Expressions** (`re`)
   - Pattern matching for data extraction
   - Used for: Phone number parsing, coordinate extraction, rating parsing

6. **Phonenumbers** (`phonenumbers`)
   - International phone number parsing and formatting
   - Used for: Phone number validation and formatting

7. **CSV** (`csv`)
   - CSV file handling
   - Used for: Exporting results to CSV format

8. **JSON** (`json`)
   - JSON data handling
   - Used for: API responses, file exports, configuration

9. **Random** (`random`)
   - Random number generation
   - Used for: Anti-detection measures, timing randomization

10. **Threading** (`threading`)
    - Thread management for async operations
    - Used for: Event loop management in Flask

## How the Scraping Works

### 1. Request Processing Flow

```
Client Request → Flask Server → Async Manager → Scraper → Browser → Google Maps
```

1. **Client sends POST request** to `/scrape-single` endpoint
2. **Flask server** receives and validates the request
3. **Async manager** handles the asynchronous execution
4. **Scraper** processes the request with fresh browser instance
5. **Browser automation** navigates to Google Maps
6. **Data extraction** occurs in two phases
7. **Results** are returned to client and saved to files

### 2. Two-Phase Extraction Strategy

#### Phase 1: List View Extraction
- **Smart Auto-Scroll**: Dynamically finds scrollable container and loads all business cards
- **Container Detection**: Uses JavaScript to identify the correct scrollable element
- **Progressive Loading**: Scrolls until no new cards appear or target count reached
- **Anti-Detection**: Random delays and human-like scrolling behavior

#### Phase 2: Detail Pane Extraction
- **Sequential Processing**: Visits each business card one by one
- **Detail Pane Opening**: Clicks on each card to open detailed information
- **Comprehensive Data Extraction**: Extracts all available business information
- **Safe Navigation**: Returns to list view after each extraction

### 3. Data Extraction Process

#### Extracted Data Fields:
- **Name**: Business name
- **Address**: Physical address
- **Phone**: Contact number (formatted internationally)
- **Website**: Business website URL
- **Category**: Business category/type
- **Rating**: Star rating (1-5)
- **Review Count**: Number of reviews
- **Coordinates**: Latitude and longitude
- **Inferred Category**: Category derived from search term

#### Data Validation:
- **Phone Numbers**: Validated using `phonenumbers` library
- **Coordinates**: Range validation (-90 to 90 for lat, -180 to 180 for lng)
- **Websites**: URL validation and filtering of Google domains
- **Categories**: Filtering of rating-like text

### 4. Anti-Detection Measures

#### Browser Stealth:
```python
# Override webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
});

# Override automation properties
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
```

#### Human-like Behavior:
- **Random Delays**: Between 1-3 seconds between actions
- **Random Viewports**: Different screen sizes (1920x1080, 1366x768, etc.)
- **Random User Agents**: Different browser versions
- **Fresh Browser Instances**: New browser for each request
- **Progressive Scrolling**: Human-like scroll patterns

#### Request Patterns:
- **Single Request Processing**: No batch operations
- **Fresh Browser Approach**: Each request gets a completely new browser
- **Retry Logic**: Multiple attempts with different strategies
- **Search Variations**: Tries different search term formats

## Key Components Deep Dive

### 1. Browser Manager (`browser_manager.py`)

**Purpose**: Manages browser instances and context creation

**Key Features**:
- **Browser Pool**: Manages multiple browser instances
- **Stealth Context**: Creates browser contexts with anti-detection measures
- **Viewport Randomization**: Different screen sizes to avoid fingerprinting
- **User Agent Rotation**: Different browser versions
- **Block Detection**: Identifies when Google is blocking requests

**Stealth Measures**:
```python
# Random viewport selection
viewports = [
    {'width': 1920, 'height': 1080},
    {'width': 1366, 'height': 768},
    {'width': 1440, 'height': 900},
    {'width': 1536, 'height': 864},
]

# Random user agent selection
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...",
]
```

### 2. Scroll Manager (`extractors/scroll_manager.py`)

**Purpose**: Handles smart auto-scrolling to load all business cards

**Key Features**:
- **Dynamic Container Detection**: Uses JavaScript to find scrollable elements
- **Progressive Loading**: Scrolls until no new cards appear
- **Stability Detection**: Waits for 3 consecutive rounds without new cards
- **Fallback Strategies**: Multiple approaches if primary method fails

**JavaScript Integration**:
```javascript
// Find scrollable container
const card = document.querySelector('.Nv2PK');
let el = card.parentElement;
while (el && el !== document.body) {
    const sh = el.scrollHeight;
    const ch = el.clientHeight;
    if (sh > ch && (style.overflowY === 'auto' || style.overflowY === 'scroll')) {
        return el; // Found scrollable container
    }
    el = el.parentElement;
}
```

### 3. Data Extractor (`extractors/data_extractor.py`)

**Purpose**: Extracts and validates business data from Google Maps

**Key Features**:
- **Two-Phase Extraction**: List view + detail pane
- **Comprehensive Validation**: Phone, website, coordinate validation
- **Regex Patterns**: Advanced pattern matching for data extraction
- **Error Handling**: Graceful handling of extraction failures
- **Category Inference**: Smart category detection from search terms

**Data Validation Examples**:
```python
def _is_valid_phone(self, phone: str) -> bool:
    """Validate phone number - improved for Pakistani numbers"""
    digits = re.sub(r'[^\d\+]', '', phone)
    
    # Pakistani phone number patterns
    if digits.startswith('+92'):
        return len(digits) >= 12  # +92XXXXXXXXXX
    elif digits.startswith('03'):
        return len(digits) == 11  # 03XX-XXXXXXX
```

### 4. Configuration (`config.py`)

**Purpose**: Centralized configuration for selectors and patterns

**Key Components**:
- **CSS Selectors**: Precise selectors for different page elements
- **Regex Patterns**: Patterns for data extraction
- **Fallback Selectors**: Multiple selectors for reliability

**Selector Examples**:
```python
self.selectors = {
    "business_cards": ".Nv2PK",  # All business cards
    "detail_address": ".Io6YTe.fontBodyMedium.kR99db.fdkmkc",
    "detail_phone": "[href^='tel:'], .fontBodyMedium",
    "detail_website": "a[data-value='Website'], a[href^='http']",
}
```

## API Endpoints

### 1. Health Check (`GET /health`)
Returns system status and feature information.

**Response**:
```json
{
    "status": "healthy",
    "service": "Optimized Google Maps Scraper V6",
    "version": "6.0.0 - Smart Auto-Scroll + Two-Phase Extraction",
    "features": [
        "Dynamic Scroll Container Detection",
        "Viewport-Based Auto-Scroll",
        "Two-Phase Extraction (List + Detail)",
        "Enhanced Error Handling & Retry Logic",
        "Regex-Based Data Parsing",
        "Single Request Processing"
    ]
}
```

### 2. Single Scrape (`POST /scrape-single`)
Processes a single search request.

**Request Body**:
```json
{
    "search_term": "car rental",
    "area_name": "Lahore",
    "max_results": 20,
    "max_retries": 2,
    "bypass_cache": false
}
```

**Response**:
```json
{
    "success": true,
    "businesses": [
        {
            "name": "ABC Car Rental",
            "address": "123 Main Street, Lahore",
            "phone": "+92 300 1234567",
            "website": "https://abccarrental.com",
            "category": "Car Rental Agency",
            "rating": 4.5,
            "review_count": 127,
            "latitude": 31.4802937,
            "longitude": 74.3837626
        }
    ],
    "total_found": 15,
    "search_term": "car rental",
    "area_name": "Lahore",
    "extraction_method": "Two-Phase (Scroll + Sequential Detail Extraction)"
}
```

## Error Handling and Retry Logic

### 1. Retry Strategy
- **Multiple Attempts**: Up to 3 attempts per request
- **Fresh Browser**: Each retry uses a completely new browser instance
- **Search Variations**: Tries different search term formats
- **Progressive Delays**: Longer delays between retries

### 2. Error Types
- **Blocking Detection**: Google Maps blocking requests
- **No Results**: Search returns no businesses
- **Extraction Failures**: Individual business extraction fails
- **Network Issues**: Connection problems
- **Timeout Errors**: Page load timeouts

### 3. Fallback Mechanisms
- **Container Detection**: Multiple strategies to find scrollable elements
- **Data Extraction**: Multiple selectors for each data field
- **Navigation**: Multiple methods to return to list view
- **Search Variations**: Different search term formats

## Performance Optimizations

### 1. Caching
- **Result Caching**: 15-minute cache for identical requests
- **Cache Bypass**: Option to bypass cache for fresh results
- **Memory Management**: Automatic cache cleanup

### 2. Async Operations
- **Non-blocking I/O**: All browser operations are asynchronous
- **Concurrent Processing**: Multiple operations can run simultaneously
- **Event Loop Management**: Proper async event loop handling

### 3. Resource Management
- **Browser Pool**: Efficient browser instance management
- **Memory Cleanup**: Automatic cleanup of browser instances
- **File Handling**: Background file saving without blocking responses

## Security and Privacy

### 1. Anti-Detection Measures
- **Webdriver Override**: Hides automation indicators
- **Random Delays**: Human-like timing patterns
- **Viewport Randomization**: Different screen sizes
- **User Agent Rotation**: Different browser versions

### 2. Data Privacy
- **No Data Storage**: Results not stored permanently
- **Temporary Files**: Export files created on-demand
- **No Tracking**: No user tracking or analytics

### 3. Rate Limiting
- **Request Limits**: Single request processing only
- **Fresh Browser**: Each request gets new browser instance
- **Retry Limits**: Maximum 3 retries per request

## File Output

### 1. JSON Files
- **Format**: Structured JSON with all extracted data
- **Naming**: `{search_term}_{area_name}_{timestamp}.json`
- **Content**: Complete business data with metadata

### 2. CSV Files
- **Format**: Comma-separated values for spreadsheet import
- **Naming**: `{search_term}_{area_name}_{timestamp}.csv`
- **Content**: Business data in tabular format

### 3. Error Files
- **Format**: JSON files with error information
- **Naming**: `error_{search_term}_{area_name}_{timestamp}.json`
- **Content**: Error details and partial results

## Usage Examples

### 1. Basic Usage
```bash
# Start the server
python main.py

# Make a request
curl -X POST http://localhost:5000/scrape-single \
  -H "Content-Type: application/json" \
  -d '{
    "search_term": "restaurants",
    "area_name": "Karachi"
  }'
```

### 2. Advanced Usage
```bash
# Request with custom parameters
curl -X POST http://localhost:5000/scrape-single \
  -H "Content-Type: application/json" \
  -d '{
    "search_term": "hotels",
    "area_name": "Islamabad",
    "max_results": 50,
    "max_retries": 3,
    "bypass_cache": true
  }'
```

## Troubleshooting

### 1. Common Issues
- **No Results**: Try different search terms or areas
- **Blocking**: Wait and retry with different parameters
- **Timeout**: Increase timeout values or check network
- **Extraction Failures**: Check if Google Maps structure changed

### 2. Debug Information
- **Logs**: Check console output for detailed information
- **Error Files**: Generated files contain error details
- **Health Check**: Use `/health` endpoint to verify system status

### 3. Performance Tips
- **Cache Usage**: Use cache for repeated searches
- **Result Limits**: Set appropriate `max_results` values
- **Retry Strategy**: Use `max_retries` for reliability

## Future Enhancements

### 1. Planned Features
- **Multi-threading**: Parallel processing of multiple requests
- **Advanced Caching**: Redis-based caching system
- **API Rate Limiting**: Built-in rate limiting
- **Webhook Support**: Real-time result notifications

### 2. Scalability Improvements
- **Docker Support**: Containerized deployment
- **Load Balancing**: Multiple server instances
- **Database Integration**: Persistent storage options
- **Monitoring**: Advanced logging and metrics

## Conclusion

This Google Maps scraper represents a sophisticated approach to web scraping with:

- **Advanced Browser Automation**: Using Playwright for reliable browser control
- **Smart Data Extraction**: Two-phase extraction with comprehensive validation
- **Anti-Detection Measures**: Multiple strategies to avoid blocking
- **Modular Architecture**: Clean separation of concerns
- **Robust Error Handling**: Comprehensive retry and fallback mechanisms
- **Performance Optimization**: Caching and async operations

The system is designed for production use with enterprise-grade reliability and maintainability. 
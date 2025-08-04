# Google Maps Scraper

A sophisticated Google Maps scraper built with Python that extracts business information from Google Maps search results. The system uses a modular architecture with advanced browser automation, smart scrolling, and two-phase data extraction.

## 🚀 Quick Start

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd google_maps_scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Run the server:**
   ```bash
   python main.py
   ```

### Usage

The server will start on `http://localhost:5000` with the following endpoints:

- **Health Check:** `GET /health`
- **Single Scrape:** `POST /scrape-single`

#### Example Request:
```bash
curl -X POST http://localhost:5000/scrape-single \
  -H "Content-Type: application/json" \
  -d '{
    "search_term": "car rental",
    "area_name": "Lahore",
    "max_results": 20
  }'
```

## 📁 Project Structure

```
google_maps_scraper/
├── main.py                 # Entry point
├── server.py              # Flask API server
├── config.py              # Configuration and selectors
├── browser_manager.py     # Browser pool and context management
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── DOCUMENTATION.md      # Comprehensive documentation
├── LIBRARIES_REFERENCE.md # Library usage guide
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py   # Abstract base class
│   └── google_maps_scraper.py  # Main scraper implementation
├── extractors/
│   ├── __init__.py
│   ├── scroll_manager.py  # Smart auto-scroll functionality
│   └── data_extractor.py # Data extraction logic
└── utils/
    ├── __init__.py
    ├── async_manager.py   # Async event loop management
    └── file_saver.py     # File saving utilities
```

## 🔧 Key Features

- **Two-Phase Extraction**: Smart auto-scroll + sequential detail extraction
- **Anti-Detection Measures**: Fresh browser instances, random delays, stealth techniques
- **Comprehensive Data Extraction**: Name, address, phone, website, rating, coordinates
- **Robust Error Handling**: Multiple retry strategies and fallback mechanisms
- **Performance Optimization**: Caching and async operations
- **Modular Architecture**: Clean separation of concerns

## 📚 Documentation

- **DOCUMENTATION.md**: Complete system documentation
- **LIBRARIES_REFERENCE.md**: Detailed library usage guide

## 🛠️ Dependencies

### Core Libraries:
- **Flask**: Web framework for API server
- **Playwright**: Modern browser automation
- **Asyncio**: Asynchronous programming support
- **Phonenumbers**: International phone number handling

### Built-in Libraries:
- **Regex**: Pattern matching for data extraction
- **JSON/CSV**: File export formats
- **Logging**: System monitoring
- **Random**: Anti-detection measures

## 🎯 Extracted Data

- **Business Name**: Company name
- **Address**: Physical location
- **Phone**: Contact number (formatted internationally)
- **Website**: Business website URL
- **Category**: Business type/category
- **Rating**: Star rating (1-5)
- **Review Count**: Number of reviews
- **Coordinates**: Latitude and longitude

## 🔒 Security & Privacy

- **No Data Storage**: Results not stored permanently
- **Anti-Detection**: Multiple strategies to avoid blocking
- **Rate Limiting**: Single request processing with retry limits
- **Fresh Browser**: Each request gets new browser instance

## 📊 File Output

The scraper generates:
- **JSON files**: Complete data with metadata
- **CSV files**: Tabular format for analysis
- **Error files**: Detailed error information

## 🚨 Troubleshooting

### Common Issues:
- **No Results**: Try different search terms or areas
- **Blocking**: Wait and retry with different parameters
- **Timeout**: Check network connection
- **Extraction Failures**: Google Maps structure may have changed

### Debug Information:
- Check console logs for detailed information
- Generated error files contain specific error details
- Use `/health` endpoint to verify system status

## 🔄 API Endpoints

### Health Check
```http
GET /health
```

### Single Scrape
```http
POST /scrape-single
Content-Type: application/json

{
  "search_term": "restaurants",
  "area_name": "Karachi",
  "max_results": 20,
  "max_retries": 2,
  "bypass_cache": false
}
```

## 📈 Performance Tips

- **Cache Usage**: Use cache for repeated searches
- **Result Limits**: Set appropriate `max_results` values
- **Retry Strategy**: Use `max_retries` for reliability
- **Fresh Data**: Use `bypass_cache: true` for latest results

## 🤝 Contributing

This is a production-ready scraper with enterprise-grade reliability and maintainability. The modular architecture makes it easy to extend and modify.

## 📄 License

This project is for educational and research purposes. Please respect Google's terms of service when using this scraper. 
# Async Scraper Integration Guide

## Overview
This guide explains how to integrate your Google Maps scraper with the n8n async workflow for distributed scraping.

## Architecture Flow

```
n8n Job Polling → Claim Job → Start Async Scrape → Python Processes → Webhook Callback → Update Database
```

## Step-by-Step Integration

### 1. Install Additional Dependencies

```bash
cd google_maps_scraper
pip install -r requirements.txt
```

This will install:
- `supabase` - For direct database connection
- `requests` - For webhook callbacks
- `python-dotenv` - For environment variable management

### 2. Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
nano .env
```

Update these values:
- `SUPABASE_KEY`: Your actual Supabase anonymous key
- `COMPLETION_WEBHOOK`: Your n8n webhook URL

### 3. Database Setup

Ensure this PostgreSQL function exists in your Supabase database:

```sql
CREATE OR REPLACE FUNCTION claim_scrape_job(
    p_admin_id INTEGER,
    p_keywords TEXT[],
    p_max_jobs INTEGER
)
RETURNS TABLE (
    id INTEGER,
    area_id INTEGER,
    keyword VARCHAR,
    assigned_to INTEGER,
    area_name VARCHAR,
    city_name VARCHAR,
    country_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH claimed_jobs AS (
        UPDATE scrape_jobs sj
        SET 
            assigned_to = p_admin_id,
            status = 'claimed',
            started_at = NOW()
        FROM (
            SELECT sj.id
            FROM scrape_jobs sj
            JOIN areas a ON sj.area_id = a.id
            JOIN cities c ON a.city_id = c.id
            LEFT JOIN (
                SELECT assigned_to, COUNT(*) as active_count
                FROM scrape_jobs
                WHERE status IN ('claimed', 'running')
                AND assigned_to = p_admin_id
                GROUP BY assigned_to
            ) active ON TRUE
            WHERE sj.status = 'pending'
            AND sj.keyword = ANY(p_keywords)
            AND (active.active_count IS NULL OR active.active_count < p_max_jobs)
            ORDER BY sj.created_at ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        ) AS available_jobs
        WHERE sj.id = available_jobs.id
        RETURNING sj.*
    )
    SELECT 
        cj.id,
        cj.area_id,
        cj.keyword,
        cj.assigned_to,
        a.name as area_name,
        c.name as city_name,
        co.name as country_name
    FROM claimed_jobs cj
    JOIN areas a ON cj.area_id = a.id
    JOIN cities c ON a.city_id = c.id
    JOIN countries co ON c.country_id = co.id;
END;
$$ LANGUAGE plpgsql;
```

### 4. Start the Scraper

```bash
python main.py
```

You should see:
```
🚀 Starting Optimized Google Maps Scraper V6...
🔄 Async Job Support: ENABLED for n8n workflow integration
✅ Supabase connection configured for direct database insertion
Available endpoints:
  POST /scrape-job-async - Async job processing for n8n workflow
```

## How It Works

### 1. Job Request Flow

When n8n sends a job request to `/scrape-job-async`:

```json
{
  "job_id": 123,
  "area_id": 1,
  "area_name": "Downtown, New York, USA",
  "keyword": "restaurant",
  "completion_webhook": "https://n8n.com/webhook/job-completion"
}
```

The server:
1. Validates the request
2. Starts a background thread
3. Returns immediately with success response
4. Processes the job asynchronously

### 2. Background Processing

The background thread:
1. Updates job status to "running" in Supabase
2. Performs the actual scraping
3. Inserts businesses directly to database (bypassing n8n)
4. Sends completion webhook with results

### 3. Completion Webhook

When job completes, the server sends:

```json
{
  "job_id": 123,
  "success": true,
  "businesses_found": 45,
  "businesses_inserted": 45,
  "processing_time": 120,
  "area_id": 1,
  "timestamp": "2024-01-01T12:00:00"
}
```

## Testing

### 1. Test Async Job Creation

Use the n8n test webhook:

```bash
curl -X POST https://your-n8n.com/webhook/test-async-scraping \
  -H "Content-Type: application/json" \
  -d '{
    "area_id": 1,
    "keyword": "restaurant"
  }'
```

### 2. Direct API Test

Test the async endpoint directly:

```bash
curl -X POST http://localhost:5000/scrape-job-async \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 999,
    "area_id": 1,
    "area_name": "Downtown, New York, USA",
    "keyword": "restaurant",
    "completion_webhook": "https://webhook.site/your-test-url"
  }'
```

### 3. Monitor Logs

Watch both Python and n8n logs:

**Python Logs:**
```
Received async job request: job_id=123, area=Downtown, keyword=restaurant
Starting async processing for job 123
Job 123: Inserted 45 businesses to database
✅ Completion webhook sent successfully for job 123
```

**n8n Logs:**
```
✅ Processing claimed job: 123
✅ Job started successfully
📨 Received job completion webhook
✅ Job 123 completed successfully with 45 businesses
```

## Database Schema

Ensure these tables exist:

### scrape_jobs
```sql
CREATE TABLE scrape_jobs (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    keyword VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    assigned_to INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    businesses_found INTEGER,
    processing_time_seconds INTEGER,
    error_message TEXT,
    logs JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### businesses
```sql
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    scrape_job_id INTEGER REFERENCES scrape_jobs(id),
    name VARCHAR(200),
    address VARCHAR(500),
    phone VARCHAR(50),
    website VARCHAR(500),
    category VARCHAR(100),
    rating DECIMAL(2,1),
    review_count INTEGER,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    raw_info JSONB,
    status VARCHAR(20) DEFAULT 'new',
    contact_status VARCHAR(20) DEFAULT 'not_contacted',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Key Benefits

1. **No Timeouts**: Jobs can run for hours without n8n timing out
2. **Scalability**: Multiple scrapers can run simultaneously
3. **Direct Database Insertion**: Faster and more efficient than going through n8n
4. **Fault Tolerance**: Failed jobs don't block the queue
5. **Real-time Updates**: Webhook callbacks provide immediate status updates

## Troubleshooting

### Common Issues

1. **Supabase Connection Failed**
   ```
   ⚠️ Supabase not configured - job status updates and business insertion disabled
   ```
   - Check your SUPABASE_KEY is correct
   - Verify network connectivity to Supabase

2. **Webhook Not Received**
   - Check the COMPLETION_WEBHOOK URL is accessible from Python server
   - Verify n8n webhook is active and listening
   - Check firewall rules

3. **Jobs Not Being Claimed**
   - Check the claim_scrape_job function exists
   - Verify admin_id and keywords match
   - Check job status is 'pending'

4. **No Businesses Inserted**
   - Check scraper is returning valid data
   - Verify area_id exists in database
   - Check Supabase table permissions

### Debug Mode

Enable detailed logging:

```python
# In your main.py
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Performance Tuning

1. **Increase Concurrent Jobs**: Adjust MAX_CONCURRENT_JOBS based on server capacity
2. **Batch Size**: Modify business insertion batch size (default 50)
3. **Thread Pool**: Consider using ThreadPoolExecutor for multiple jobs
4. **Cache Duration**: Adjust CACHE_DURATION for better performance

## Security Considerations

1. **API Keys**: Never commit SUPABASE_KEY to version control
2. **Webhook Authentication**: Consider adding webhook signature verification
3. **Rate Limiting**: Implement rate limiting for the async endpoint
4. **Error Handling**: Sanitize error messages before sending to webhooks

## n8n Workflow Configuration

In your n8n instance, configure these variables:

```javascript
// n8n Environment Variables
ADMIN_ID=1
SUPPORTED_KEYWORDS=car rental,restaurant,hotel,pharmacy
MAX_CONCURRENT_JOBS=5
SCRAPER_ENDPOINT=http://your-scraper-host:5000
COMPLETION_WEBHOOK=https://your-n8n.com/webhook/job-completion
```

Import the provided n8n workflow JSON and update:
- Supabase credentials
- Webhook URLs
- Scraper endpoint

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure database schema matches requirements
4. Test with small jobs first before scaling up
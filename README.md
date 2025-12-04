# Airbnb Data Collection Pipeline

## Project Overview

This project is an automated data collection pipeline for scraping Airbnb listings from Almaty, Kazakhstan. The pipeline consists of three main stages: **scraping**, **cleaning**, and **loading** data into a SQLite database. The entire process can be orchestrated using Apache Airflow for scheduled, automated execution.

The project targets the Airbnb website (https://www.airbnb.com/), which is a dynamic React-based website requiring JavaScript rendering. The scraper handles infinite scrolling and pagination to extract listing information including titles, prices, and links.

## Features

- **Web Scraping**: Automated scraping using Playwright to handle dynamic content and JavaScript rendering
- **Data Cleaning**: Removes duplicates, handles missing values, and normalizes price data
- **Database Integration**: Automatically creates and populates a SQLite database with cleaned data
- **Airflow Orchestration**: Scheduled pipeline execution with Apache Airflow DAG
- **Error Handling**: Robust error handling for network issues and missing data
- **Scalable Design**: Modular code structure for easy maintenance and extension

## How It Works

The pipeline operates in three sequential stages:

1. **Scraping Stage** (`src/scraper.py`):
   - Uses Playwright to launch a Chromium browser
   - Navigates to Airbnb Almaty listings page
   - Handles infinite scrolling and pagination
   - Extracts listing data: title, price, and link
   - Saves raw data to `data/raw_data.csv`
   - Targets collection of 108+ listings

2. **Cleaning Stage** (`src/cleaner.py`):
   - Reads raw data from `data/raw_data.csv`
   - Removes duplicate entries based on listing links
   - Handles missing values (fills missing titles with "Unknown Title")
   - Normalizes price data by extracting numeric values
   - Filters out entries with invalid prices (price_cleaned = 0)
   - Saves cleaned data to `data/cleaned_data.csv`

3. **Loading Stage** (`src/loader.py`):
   - Reads cleaned data from `data/cleaned_data.csv`
   - Creates SQLite database at `data/output.db`
   - Creates `listings` table with proper schema
   - Loads cleaned data into the database
   - Provides row count confirmation

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium==4.38.0`
- `pandas==2.2.3`
- `beautifulsoup4==4.12.3`
- `webdriver-manager==4.0.2`
- `apache-airflow==2.10.3`

### Step 2: Install Playwright Browsers

The scraper uses Playwright, which requires browser binaries to be installed:

```bash
playwright install
```

Or if Playwright is not yet installed:

```bash
pip install playwright
playwright install chromium
```

### Step 3: Create Data Directory

Ensure the `data/` directory exists in the project root:

```bash
mkdir -p data
```

## Running the Scraper

### Manual Execution

You can run each stage of the pipeline manually:

**1. Run the Scraper:**
```bash
python src/scraper.py
```
This creates `data/raw_data.csv` with scraped listings.

**2. Run the Cleaner:**
```bash
python src/cleaner.py
```
This processes the raw data and creates `data/cleaned_data.csv`.

**3. Run the Loader:**
```bash
python src/loader.py
```
This loads the cleaned data into `data/output.db`.

## Database Initialization

The database is automatically initialized when you run the loader (`src/loader.py`). The loader will:

1. Check if `data/cleaned_data.csv` exists
2. Create or overwrite `data/output.db` SQLite database
3. Drop and recreate the `listings` table with the proper schema
4. Load all cleaned data into the database
5. Display the number of rows successfully loaded

**Note:** The database is recreated each time the loader runs, so existing data will be replaced.

## Airflow Pipeline

The project includes an Apache Airflow DAG (`dags/airflow_dag.py`) that orchestrates the entire pipeline.

### Setting Up Airflow

**1. Set Airflow Home Directory:**
```bash
export AIRFLOW_HOME=$(pwd)
```

For Windows PowerShell:
```powershell
$env:AIRFLOW_HOME = Get-Location
```

**2. Initialize Airflow Database:**
```bash
airflow db init
```

**3. Create Airflow User (first time only):**
```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

**4. Start Airflow Standalone:**
```bash
airflow standalone
```

Or start scheduler and webserver separately:
```bash
airflow scheduler &
airflow webserver
```

### Running the Pipeline via Airflow

1. **Access Airflow Web Interface:**
   - Open http://localhost:8080 in your browser
   - Login with the credentials you created (default: admin/admin)

2. **Enable and Trigger the DAG:**
   - Find `airbnb_project_dag` in the DAG list
   - Toggle the switch to **Unpause** (Blue)
   - Click the **Play ▶️** button -> **Trigger DAG**

3. **Monitor Execution:**
   - View the DAG graph to see task dependencies
   - Check task logs for detailed execution information
   - The pipeline runs: `scrape_data` → `clean_data` → `load_to_sqlite`

### Pipeline Configuration

The DAG is configured with:
- **Schedule**: Daily (`@daily`)
- **Start Date**: December 1, 2023
- **Retries**: 1 retry on failure
- **Retry Delay**: 1 minute
- **Catchup**: Disabled (won't backfill past dates)

## Database Schema

The `listings` table in `data/output.db` has the following structure:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary Key, Auto-increment |
| `title` | TEXT | Listing title/name |
| `price_original` | TEXT | Original price string (e.g., "$ 150", "₸ 50000") |
| `price_cleaned` | INTEGER | Normalized numeric price value |
| `link` | TEXT | Full URL to the Airbnb listing |

### Example Data

```
id | title                    | price_original | price_cleaned | link
---|--------------------------|----------------|---------------|----------------------------------
1  | Cozy Apartment in Center | $ 150          | 150           | https://www.airbnb.com/rooms/123
2  | Modern Studio            | ₸ 50000        | 50000         | https://www.airbnb.com/rooms/456
```

## Expected Output

After the pipeline completes successfully, the `data/` folder will contain:

1. **`raw_data.csv`**: 
   - Raw scraped data with all collected listings (target: 108+ records)
   - Columns: `title`, `price`, `link`
   - May contain duplicates and unprocessed price formats

2. **`cleaned_data.csv`**: 
   - Processed data without duplicates
   - Columns: `title`, `price` (renamed to `price_original`), `link`, `price_cleaned`
   - Missing values handled, prices normalized
   - Invalid entries (price_cleaned = 0) filtered out

3. **`output.db`**: 
   - SQLite database file
   - Contains `listings` table with final processed data
   - Ready for querying and analysis

### Verifying Output

You can verify the database contents using SQLite:

```bash
sqlite3 data/output.db "SELECT COUNT(*) FROM listings;"
sqlite3 data/output.db "SELECT * FROM listings LIMIT 5;"
```

## Project Members

- **Owners**: ganiya nursaliyeva, symbat bayanbayeva
- **Project**: Airbnb Data Collection Pipeline

---

## Additional Notes

- The scraper uses randomized delays (6-10 seconds) between page navigations to avoid being blocked
- Browser runs in non-headless mode by default for debugging (can be changed to `headless=True`)
- The pipeline handles common errors gracefully and continues processing
- All file paths are relative to the project root directory

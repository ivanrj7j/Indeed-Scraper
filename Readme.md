# Indeed Web Scraper App

## Description

This is an Indeed Web Scraper App designed to extract Company and Jobs data from Indeed.com. The application utilizes Scrapy for web scraping and Flask for creating a web interface.

## Features

- Scrapes job and company data from Indeed.com
- Uses Scrapy for efficient web crawling
- Flask-based web interface for user input
- Generates JSON output of crawled data
- Creates two CSV files: one for job data and one for company data

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/g-sree-jith/Indeed-Scraper
   cd indeed-web-scraper
   ```

2. Create a virtual environment and install the required packages:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

## Usage

1. Navigate to the Indeed_Flask folder:
   ```
   cd Indeed_Flask
   ```

2. Run the Flask application:
   ```
   python main.py
   ```

3. Open a web browser and go to the provided local URL (usually `http://127.0.0.1:5000`).

4. Use the web interface to input your search criteria for Indeed.com.

5. The scraper will run and save the output to a JSON file.

6. Two CSV files will be generated based on the JSON data:
   - One CSV file for job information
   - One CSV file for company information

7. To find the generated CSV files, look in the Indeed_Flask folder for files named after your job search keyword.

## File Structure

- `Indeed_Flask/`: Main application folder
  - `main.py`: Flask application script
  - `requirements.txt`: List of Python package dependencies
  - Output files:
    - `[keyword]_jobs.csv`: CSV file containing job data
    - `[keyword]_companies.csv`: CSV file containing company data
    - `[keyword]_output.json`: JSON file with raw scraped data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
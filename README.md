# Thomasnet Supplier Scraper

A Playwright-based web scraping project that collects supplier information from Thomasnet and exports the data to a CSV file.

## Features

* Extract supplier company names
* Extract supplier locations
* Collect company website URLs
* Collect Thomasnet profile URLs
* Retrieve publicly accessible phone numbers from supplier profile pages
* Export data to CSV format
* Basic error handling for failed requests

## Technologies Used

* Python 3
* Playwright
* CSV

## Installation

```bash
pip install playwright
playwright install
```

## Usage

```bash
python scraper.py
```

## Output

The scraper generates a CSV file containing:

* Company Name
* Location
* Phone Number
* Website URL
* Profile URL

## Project Structure

```text
thomasnet-supplier-scraper/
│
├── scraper.py
├── requirements.txt
├── README.md
├── sample_output.csv
└── .gitignore
```

## Notes

* This project is intended for educational and portfolio purposes.
* Data is collected from information made available through the website interface.
* Users are responsible for complying with the target website's terms and policies.

## License

MIT License

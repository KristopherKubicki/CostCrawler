# CostCrawler

CostCrawler is a Python3 application designed to streamline the collection and comparison of hospital rate cards. It features a Flask interface running on port 5000, making the process of gathering hospital pricing data efficient and user-friendly. CostCrawler enables users to make more informed healthcare decisions by comparing prices for different procedures across various facilities.

## Features
CostCrawler provides the following key functionalities:

1. **Facilities:** Manage a list of facilities to scan and monitor, including details like zip codes and postal locations.

2. **Procedures:** Track various procedures, with a particular emphasis on radiology.

3. **Locations:** View all available hospitals and procedures within a defined area, defaulting to a 30-mile radius from the center of a given location.

4. **Configurable API Keys:** The config.yaml file allows setting API keys for Azure and Google services, if required.

## Installation

CostCrawler has been tested on Ubuntu but it should work on other operating systems with minor modifications. Follow the steps below to install and run the project:

1. Clone the repo and navigate to it.
2. Create a Python virtual environment (e.g., `python3 -m venv env`).
3. Install the dependencies using the `requirements.txt` file (e.g., `python3 -m pip install -r requirements.txt`).
4. Install and set up a PostgreSQL database (version 10.12 recommended).
5. Edit the `config.yaml` file to add the path to the PostgreSQL database under `db:`, add `salt:`, and add `gv_key` and `mv_key` for Google and Microsoft scraping.
6. Load the initial schema from `data/schema.sql`.
7. Run the `load_facilities.py`, `load_procedures.py`, and `load_zones.py` scripts to load the initial data.
8. Run the web UI using the `run.web.sh` script located in the `bin` directory.
9. Scrape data using the `scrape_raw_charges.py` script.
10. Inspect the scraped data for integrity and load it using `load_raw_charges.py`.

You should now have a fully functional hospital charge list portal!

## Structure
The initial data for CostCrawler can be found in `CostCrawler/data/init`. The files include:

- `facilities.txt`: List of facilities
- `raw_charges.txt`: Raw collected charge data from 2021
- `schema.sql`: Initial database schema
- `true_proc.txt`: Procedure charge codes
- `zone.txt`: Facility locations (these are the Locations)

## Scripts
The `bin` directory contains scripts that handle various aspects of the project:

- `facade.py`: Runs the web interface on port 5000.
- `load_facilities.py`: Loads eligible facilities into the database from a formatted data file.
- `load_procedures.py`: Loads eligible procedures into the database from a formatted data file.
- `load_zones.py`: Loads all "Locations" into the database model from a formatted data file.
- `make_static_output.py`: Renders all content from the web UI into JSON blobs.
- `map_raw_procedures.py`: Performs data cleanup.
- `run.web.sh`: A helper script that runs the web services.
- `scrape_raw_charges.py`: A script that scrapes health care provider information from a list of domains.

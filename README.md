# Breaking Chains Sober Sundays League Tracker

A Flask app for tracking the Breaking Chains Sober Sundays disc golf league. It supports player sign-in, score entry, bag-tag tracking, league payouts, closest-to-pin entries, and player history.

## Features

- Register players and their payout, ace-pot, and CTP participation.
- Import round results from a UDisc event or enter placements manually.
- Calculate payouts and update bag-tag holders from round results.
- Review current tags, tag history, round results, CTPs, and handicaps.
- Suggest known player names during sign-in and fill in their latest recorded tag.
- Keep player and round data in the league's MySQL database.
- Scrape upcoming UDisc league events and update their scoreboard URLs.

## Project layout

```text
.
├── static/              # Images and other static assets
├── templates/           # Flask/Jinja templates
├── tests/               # Unit tests
├── cron_scrap_job.py    # Sync upcoming UDisc events to MySQL
├── db.py                # MySQL queries and persistence
├── flask_app.py         # Flask application and routes
├── payout.py            # League payout calculations
├── run_scraper.sh       # Scheduled-task entry point for the scraper
└── requirements.txt     # Python dependencies
```

## Requirements

- Python 3.10 (the deployed PythonAnywhere runtime)
- A reachable MySQL database with the BCSS league tables
- Chrome/Chromium and a compatible Selenium WebDriver to run the UDisc schedule scraper

## Configuration

Copy `.env.example` to `.env` and fill in the values for your environment. The Flask app uses `secret_key`, `site_user`, and `site_pw` for its Flask secret key and HTTP Basic Auth. Database access uses `host`, `user`, `password`, and `database`.

The scraper loads the same `.env` file from the directory containing `cron_scrap_job.py`. Keep real credentials only in `.env`; Git ignores it. Never commit credentials or paste them into source files.

## Local development

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`, enter local credentials, and ensure the configured MySQL database is reachable.
4. Start the development server:

   ```bash
   flask --app flask_app run --debug
   ```

5. Open <http://127.0.0.1:5000/>. The app uses HTTP Basic Auth; configure `site_user` and `site_pw` in `.env`.

The development server is for local use only. Use the existing WSGI configuration for deployment.

## Tests

Run the unit tests with the standard library:

```bash
python -m unittest discover -s tests -v
```

The tests cover payout totals and ties, tag-holder selection, and autocomplete/tag lookup queries. Database calls are stubbed; running the tests does not require the league database.

## Deploying on PythonAnywhere

This app shares the existing PythonAnywhere deployment with the Putting League app. BCSS stays at `/` and Putting League stays at `/puttingleague`. Keep the existing web app, WSGI configuration, routes, and static-file mappings intact.

1. Back up the current code and WSGI configuration.
2. Pull this repository into the existing BCSS app directory.
3. Install dependencies into the Python 3.10 environment used by the web app. Since packages are shared with the other app, review dependency changes before installing:

   ```bash
   python3.10 -m pip install --user -r requirements.txt
   ```

4. Keep the BCSS `.env` alongside `flask_app.py`, with the keys listed in `.env.example`. The existing WSGI configuration must load those values before importing the app.
5. Preserve the existing PythonAnywhere URL routes and static-file mappings, then reload the web app.
6. Confirm the league app and the Putting League app still load at their existing routes. Review the PythonAnywhere error log if the reload fails.

### Scheduled UDisc scraper

Configure the PythonAnywhere scheduled task to run `run_scraper.sh` from this repository. It invokes the scraper from the script's own directory, so the task does not depend on its starting directory. The scraper reads the same private `.env` file and writes upcoming event dates and scoreboard URLs to MySQL.

The scraper requires a working Chrome/Chromium and Selenium WebDriver installation. Verify those are available in the scheduled-task environment before enabling it.

## Roadmap

- Season reset and league setup.
- Bag-tag activity history endpoints for QR codes.
- Season points for round finishers.
- Additional player management and UDisc name-matching improvements.
- Ace-pot tracking and payout workflow.

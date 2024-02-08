```markdown
# Fastly NGWAF Request Feed Analyzer

This Python script fetches request feeds from the Fastly Next-Generation Web Application Firewall (NGWAF) API, stores the data in a CSV file, and performs an analysis on JA3 fingerprints (identified by `bot_j` values in the `summation` attribute) to find and display the top 10 occurrences.

## Features

- **Data Fetching:** Retrieves request feeds based on the specified corporation and site names.
- **CSV Storage:** Dynamically determines and writes all fields from the fetched data into a CSV file.
- **JA3 Analysis:** Extracts `bot_j` values from the `summation` column and identifies the top 10 JA3 fingerprints by their occurrence count.

## Requirements

- Python 3
- Requests library
- An active Fastly NGWAF API account with access credentials

## Setup

1. **Install Python 3** if you haven't already. You can download it from [python.org](https://www.python.org/downloads/).

2. **Install the Requests library** by running:

   ```shell
   pip install requests
   ```

3. **Set up environment variables** for your Fastly NGWAF API credentials and other parameters:

   - `SIGSCI_EMAIL`: Your Fastly NGWAF user email.
   - `SIGSCI_TOKEN`: Your Fastly NGWAF API token.
   - `CORP_NAME`: The name of your corporation as registered on Fastly NGWAF.
   - `SITE_NAME`: The name of your site as registered on Fastly NGWAF.

   You can set these variables in your terminal or include them in your script execution command.

## Usage

To run the script, navigate to the directory containing the script and execute it with Python, optionally specifying arguments for email, token, corporation name, site name, and output file name:

```shell
python fastly_ngwaf_analyzer.py --sigsci_email <your_email> --sigsci_token <your_token> --corp_name <your_corp_name> --site_name <your_site_name> --output_file <output.csv> -v
```

If you've set up environment variables for your credentials and identifiers, you can omit those arguments:

```shell
python fastly_ngwaf_analyzer.py --output_file output.csv -v
```

The `-v` or `--verbose` flag is optional and enables verbose output for debugging purposes.

## Output

After successful execution, the script will:

- Fetch the request feed data for the last 24 hours (excluding the most recent 5 minutes to account for data processing delays).
- Write the fetched data to the specified CSV file.
- Analyze the `bot_j` values extracted from the `summation` attribute in the CSV file.
- Print the top 10 JA3 fingerprints and their counts to the console.

## Note

This script is designed for use with Fastly NGWAF API and has been tested with Python 3.8+. Ensure your API credentials are correct and that you have the necessary permissions to access the request feed data.
```

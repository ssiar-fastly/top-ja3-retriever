import argparse
import requests
import csv
from datetime import datetime, timedelta
import os
import calendar
import time
import ast
from collections import Counter

# Constants
BASE_URL = "https://dashboard.signalsciences.net/api/v0"
MAX_RETRIES = 3
RETRY_WAIT = 10

def get_headers(sigsci_email, sigsci_token):
    """Generate headers for API requests."""
    return {
        "x-api-user": sigsci_email,
        "x-api-token": sigsci_token,
        "Content-Type": "application/json"
    }

def retry_api_call(func):
    """Decorator to retry API calls upon failure."""
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            response = func(*args, **kwargs)
            if response.status_code in [200, 201]:
                return response
            else:
                print(f"API call failed with status code {response.status_code}. Error message: {response.text}")
                if response.status_code == 401:
                    break  # No retry on authorization errors
                time.sleep(RETRY_WAIT)
                retries += 1
        return response
    return wrapper

@retry_api_call
def fetch_requests(email, token, corp_name, site_name, from_ts, until_ts, verbose=False):
    """Fetch requests with retry logic. Adjust the endpoint as needed."""
    url = f"{BASE_URL}/corps/{corp_name}/sites/{site_name}/feed/requests"
    params = {"from": from_ts, "until": until_ts}
    return requests.get(url, headers=get_headers(email, token), params=params)

def extract_bot_j_values(csv_file_path):
    """Extract bot_j values from the summation column."""
    bot_j_values = []
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            summation = row.get('summation')
            if summation:
                summation_dict = ast.literal_eval(summation)
                attrs = summation_dict.get('attrs', {})
                bot_j = attrs.get('bot_j')
                if bot_j:
                    bot_j_values.append(bot_j)
    return bot_j_values

def get_top_bot_j(bot_j_values, top_n=10):
    """Get the top n bot_j values."""
    bot_j_counts = Counter(bot_j_values)
    return bot_j_counts.most_common(top_n)

def main(args):
    # Calculate 'until' and 'from' timestamps
    until_time = datetime.utcnow().replace(second=0, microsecond=0) - timedelta(minutes=5)
    from_time = until_time - timedelta(hours=24)
    from_ts = calendar.timegm(from_time.timetuple())
    until_ts = calendar.timegm(until_time.timetuple())

    response = fetch_requests(args.sigsci_email, args.sigsci_token, args.corp_name, args.site_name, from_ts, until_ts, args.verbose)
    if response and response.status_code == 200:
        data = response.json()['data']
        with open(args.output_file, 'w', newline='') as csvfile:
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        if args.verbose:
            print(f"Data successfully written to {args.output_file}")

        # Extract and analyze bot_j values
        bot_j_values = extract_bot_j_values(args.output_file)
        top_bot_j = get_top_bot_j(bot_j_values)
        print("Top 10 JA3 values and their counts for last hour:")
        for bot_j, count in top_bot_j:
            print(f"JA3: {bot_j}, Count: {count}")
    else:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch request feed from Fastly NGWAF API and store in CSV, then analyze bot_j values.")
    parser.add_argument('--sigsci_email', default=os.environ.get('SIGSCI_EMAIL'), help='SIGSCI user email')
    parser.add_argument('--sigsci_token', default=os.environ.get('SIGSCI_TOKEN'), help='SIGSCI API token')
    parser.add_argument('--corp_name', default=os.environ.get('CORP_NAME'), help='Corporation name')
    parser.add_argument('--site_name', default=os.environ.get('SITE_NAME'), help='Site name')
    parser.add_argument('--output_file', default='output.csv', help='Output CSV file name')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output for debugging')

    args = parser.parse_args()

    main(args)

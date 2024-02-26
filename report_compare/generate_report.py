import os
import json
import argparse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def read_roster(file_path):
    with open(file_path, "r") as read_file:
        data = json.load(read_file)
    return data

def calculate_age(birthDate, date_string):
    birthDate = datetime.strptime(birthDate, '%Y-%m-%d')
    d = datetime.strptime(date_string, '%Y-%m-%d')
    return d.year - birthDate.year - ((d.month, d.day) < (birthDate.month, birthDate.day))

def get_credit_score(consumer, age):
    score = 0
    if consumer['is_deceased']:
        return score

    if age >= 22 and age <= 30:
        score = 650
    elif age > 30 and age <= 40:
        score = 750
    else:
        score = 800

    score = score - round(2.25 * consumer['hard_enquiries'])

    return score


def create_monthly_report(consumer_roster, date_string):
    release_version = os.getenv('RELEASE_VERSION', '0.0.0')
    last_day = datetime.strptime(date_string, '%Y%m') + relativedelta(day=31)
    last_day_str = last_day.strftime('%Y-%m-%d')

    for consumer in consumer_roster:
        age = calculate_age(consumer['dob'], last_day_str)
        if age > 89:
            consumer['is_deceased'] = True
        credit_report = {
            'report_date': last_day_str,
            'consumer': consumer,
            'release_version': release_version,
            'credit_score': get_credit_score(consumer, age),
            'age': age
        }
        path = f"data/{date_string[:4]}/{date_string[4:]}/"
        os.makedirs(path, exist_ok=True)
        with open(path + f"rpt_{consumer['SSN']}_{date_string}.json", 'w') as f:
            json.dump(credit_report, f)

def main():
    parser = argparse.ArgumentParser(description="Generate Monthly Credit Report")
    parser.add_argument("report_month", help="Report Month in the format yyyymm")
    args = parser.parse_args()
    consumer_roster = read_roster("data/consumer_roster.json")
    create_monthly_report(consumer_roster, args.report_month)

if __name__ == "__main__":
    main()

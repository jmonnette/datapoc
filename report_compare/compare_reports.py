import argparse
import json
import os
import statistics
import glob
from collections import Counter

def get_file_names(dir_path):
    file_names = glob.glob(f"{dir_path}/*.json")
    return {os.path.basename(f).split('_')[1]: f for f in file_names}

def get_diff(file_1, file_2):
    with open(file_1, 'r') as f1, open(file_2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
        score_diff = data2['credit_score'] - data1['credit_score']
        age_diff = data2['age'] - data1['age']
        is_deceased_diff = data2['consumer']['is_deceased'] != data1['consumer']['is_deceased']
        return (score_diff, data1['credit_score'], data2['credit_score'],
                age_diff, data1['age'], data2['age'],
                is_deceased_diff, data1['consumer']['is_deceased'], data2['consumer']['is_deceased'])

def compare_reports(month1, month2):
    directory1 = f'data/{month1[:4]}/{month1[4:]}/'
    directory2 = f'data/{month2[:4]}/{month2[4:]}/'
    files1_dic = get_file_names(directory1)
    files2_dic = get_file_names(directory2)
    files_intersection = set(files1_dic.keys()) & set(files2_dic.keys())

    score_diffs = []
    scores1 = []
    scores2 = []
    age_diffs = []
    age1 = []
    age2 = []
    deceased1 = {"<25": 0, "25-40": 0, "40-60": 0, ">60": 0}
    deceased2 = {"<25": 0, "25-40": 0, "40-60": 0, ">60": 0}
    deceased_diff = 0

    for ssn in files_intersection:
        score_diff, score_before, score_after, age_diff, age_before, age_after, is_deceased_diff, deceased_before, deceased_after = get_diff(files1_dic[ssn], files2_dic[ssn])

        if score_diff != 0:
            score_diffs.append(ssn)
        if age_diff > 1:
            age_diffs.append(ssn)
        if is_deceased_diff:
            deceased_diff +=1

        scores1.append(score_before)
        scores2.append(score_after)
        age1.append(age_before)
        age2.append(age_after)

        if deceased_before: deceased1 = deceased_bucket(age_before, deceased1)
        if deceased_after: deceased2 = deceased_bucket(age_after, deceased2)

    return (get_statistics(scores1), get_statistics(scores2), len(score_diffs),
            get_statistics(age1), get_statistics(age2), len(age_diffs),
            deceased_diff, deceased1, deceased2)

def deceased_bucket(age, deceased_dic):
    if age < 25:
        deceased_dic["<25"] += 1
    elif age < 40:
        deceased_dic["25-40"] += 1
    elif age < 60:
        deceased_dic["40-60"] += 1
    else:
        deceased_dic[">60"] += 1
    return deceased_dic

def get_statistics(data):
    return {
        "Mean" : statistics.fmean(data),
        "Median" : statistics.median(data),
        "Mode(s)" : statistics.multimode(data),
        "5 Most Frequent" : Counter(data).most_common(5)
    }

def main():
    parser = argparse.ArgumentParser(description="Compare Monthly Credit Reports")
    parser.add_argument("month1", help="First month in the format yyyymm")
    parser.add_argument("month2", help="Second month in the format yyyymm")
    args = parser.parse_args()

    stats_score1, stats_score2, score_diffs, stats_age1, stats_age2, age_diffs, deceased_diff, deceased1, deceased2 = compare_reports(args.month1, args.month2)

    print(f'Credit Score Info (Set 1): {stats_score1}')
    print(f'Credit Score Info (Set 2): {stats_score2}')
    print(f'Number of people whose credit_score changed: {score_diffs}')

    print(f'Age Info (Set 1): {stats_age1}')
    print(f'Age Info (Set 2): {stats_age2}')
    print(f'Number of people whose age increased by more than 1 year: {age_diffs}')

    print(f'Number of people whose deceased status changed: {deceased_diff}')
    print(f'Set 1 Deceased Info: {deceased1}')
    print(f'Set 2 Deceased Info: {deceased2}')

if __name__ == "__main__":
    main()

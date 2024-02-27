# Report Comparer Documentation

This shell script (written in Zsh), enables you to generate a roster, check out different versions of code, generate reports, and compare the generated reports.

## Requirements
1. zsh
2. Python3
3. Git
4. A Python script named `generate_roster.py`.
5. A Python script named `generate_report.py`.
6. A Python script named `compare_reports.py`.
7. python script located in `../github_helper/diff_github.py`.

## How to Run
1. Save the shell script to your local machine.
2. Make sure you have the required permissions to execute the script. If not, run `chmod +x script.sh`.
3. Run `./script.sh` or `zsh script.sh` in your terminal.

## How it works

The flow of this shell script is as follows:

1. Using Python, it runs `generate_roster.py` to generate a roster with 10,000 records.

2. It then checks out version v0.0.1 of the current Git repository and generates a report for year 2023 month 04 with `generate_report.py`.

3. After generating the report for v0.0.1, it checks out to version v0.0.4 and generates another report for year 2023 month 05.

4. The script then returns to the 'main' branch and calls the Python script `diff_github.py` to show the differences between the v0.0.1 and v0.0.4 versions for a given GitHub repository, specifically for the repository 'datapoc' under the username 'jmonnette'.

5. Lastly, it runs `compare_reports.py`, which presumably compares the reports generated in steps 2 and 3.

Note: Please ensure that you have the appropriate permissions to checkout different branches or tags. This script won't work properly if you are in the middle of a merge conflict or rebase.

## Caution
During the execution of this shell script, it leaves the current Git repository in the 'main' branch. If you had any uncommitted changes before running this script they could be lost. So, it is recommended to check the status of the repository by verifying that you have committed all the changes before running the script.   

This script makes use of an environment variable (`RELEASE_VERSION`). A change in this shell variable won't affect your shell session outside the runtime of this script.

## Dependencies

This script depends on both the presence of the Python files `generate_roster.py`, `generate_report.py`, `compare_reports.py` and `../github_helper/diff_github.py`, and their correct functioning. If any of these scripts fail or are not present, this script will also fail.

Also, this script assumes the presence of specific git tags (v0.0.1 and v0.0.4) in the repository where it's running. Make sure that those tags exist in your repository.
import difflib

file1_content = open("code/v0.0.4/generate_report_v0.0.4.py").readlines()
file2_content = open("code/v0.0.3/generate_report_v0.0.3.py").readlines()

diff = difflib.unified_diff(file1_content, file2_content)

print("".join(diff))

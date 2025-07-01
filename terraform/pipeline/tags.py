import os
import re

COMMIT_SHA = os.environ["COMMIT_SHA"]
REASON = os.environ["REASON"]
# use variable corresponding to tag triggers
SOURCE = os.environ["INDIVIDUAL_SOURCE"]

SOURCE_BRANCH = os.environ["SOURCE_BRANCH"]
IS_TAG = SOURCE_BRANCH.startswith("refs/tags/") is True

tag_type = None

if REASON in ["IndividualCI", "Manual"] and IS_TAG:
    if re.fullmatch(r"20\d\d.\d\d.\d+-rc\d+", SOURCE):
        tag_type = "test"
    elif re.fullmatch(r"20\d\d.\d\d.\d+", SOURCE):
        tag_type = "prod"

print(f"REASON: {REASON}")
print(f"INDIVIDUAL_SOURCE: {SOURCE}")
print(f"SOURCE_BRANCH: {SOURCE_BRANCH}")
print(f"COMMIT_SHA: {COMMIT_SHA}")
print(f"tag_type: {tag_type}")

# https://learn.microsoft.com/en-us/azure/devops/pipelines/process/set-variables-scripts?view=azure-devops&tabs=bash#about-tasksetvariable
print(f"##vso[task.setvariable variable=container_tag]{COMMIT_SHA}")
print(f"##vso[task.setvariable variable=tag_type]{tag_type}")

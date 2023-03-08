import json
import os
import magic

import requests

print('🚀Starting uploading coverage report to Asuna')
print('🔑Checking environment variables...')
print('🔑Checking upload key...')
if os.getenv('ASUNA_UPLOAD_KEY') is None:
    print('❌Failed: ASUNA_UPLOAD_KEY is not set')
    exit(1)

print('🧑‍💻Checking action environment variables to get name and description')
if os.getenv('EVENT_NAME') == 'pull_request':
    name = f"(#{os.getenv('PULL_REQUEST_NUMBER')}) {os.getenv('PULL_REQUEST_TITLE')}"
    description = f"Pull request #{os.getenv('PULL_REQUEST_NUMBER')} from {os.getenv('PULL_REQUEST_HEAD')}"
elif os.getenv('EVENT_NAME') == 'push':
    name = f"{os.getenv('PUSH_BRANCH')}@{os.getenv('PUSH_COMMIT')}"
    description = f"Push to {os.getenv('PUSH_BRANCH')}@{os.getenv('PUSH_COMMIT')}"
else:
    print('❌Failed: EVENT_NAME is not set')
    exit(1)

print('📈Preparing coverage report...')
# open coverage.json file, read and store as a dict
with open('coverage/coverage-summary.json', 'r') as f:
    coverage = f.read()
coverage_json = json.loads(coverage)

url = os.getenv('ASUNA_ENDPOINT')
print(f'⬆️Start uploading report to {url}')
form_data = {
    'key': os.getenv('ASUNA_UPLOAD_KEY'),
    'name': name,
    'description': description,
    # it's float in coverage.json
    'percentage': coverage_json['total']['statements']['pct'],
    'coverage': coverage
}

# Prepare the file for upload
all_files = []
for root, dirs, files in os.walk('coverage'):
    for file in files:
        file_type = magic.from_file(os.path.join(root, file), mime=True)
        all_files.append(('file', (file, open(os.path.join(root, file), 'rb'), file_type)))

# Send the request
server = requests.post(url, data=form_data, files=all_files)
output = server.text
# if status is not 201, print error message
if server.status_code != 201:
    print(f'❌Failed: {server.text}')
    exit(1)
else:
    output = json.loads(output)
    print(f'✅Success')
    print(f'📝Project: {output["project"]}')
    print(f'📝Project URL: {output["project_url"]}')
    print(f'🔗Full report URL: {output["url"]}')

    # Write markdown file
    with open('asuna.md', 'w') as f:
        f.writelines(f'[📔Go to project]({output["project_url"]}) | [🔗Full report]({output["url"]})')

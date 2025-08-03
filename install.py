import requests
import os

RAW_URL = "https://raw.githubusercontent.com/OftenNotKnown/OftenNotKnown.github.io/main/main.py"
OUTPUT_FILE = "main.py"

def download_file(url, output):
    print(f"📥 Downloading {output}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(output, 'wb') as f:
            f.write(response.content)
        print(f"✅ Saved as {output}")
    else:
        print(f"❌ Failed to download file. Status code: {response.status_code}")
        exit(1)

def run_file(filename):
    print(f"🚀 Running {filename}...")
    os.system(f'python "{filename}"')

if __name__ == "__main__":
    download_file(RAW_URL, OUTPUT_FILE)
    run_file(OUTPUT_FILE)

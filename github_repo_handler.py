import os
import requests
import zipfile
import io

def clean_github_url(repo_url):
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]
    if 'github.com' in repo_url and not repo_url.endswith('.git'):
        repo_url = repo_url.split('?')[0]
    return repo_url

def download_and_extract_github_repo(repo_url, run_dir):
    repo_url = clean_github_url(repo_url)
    repo_name = repo_url.rstrip('/').split('/')[-1]
    zip_url = f"{repo_url}/archive/refs/heads/master.zip"
    print(f"Downloading {zip_url}...")

    response = requests.get(zip_url)
    print(f"HTTP response status: {response.status_code}")
    if response.status_code == 200:
        print(f"Extracting {repo_name}.zip...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(run_dir)
        extracted_folder = os.path.join(run_dir, f"{repo_name}-main")
        if os.path.exists(extracted_folder):
            print(f"Extraction successful. Folder exists: {extracted_folder}")
        else:
            print(f"Extraction failed. Folder does not exist: {extracted_folder}")
        return extracted_folder
    else:
        raise Exception(f"Failed to download {repo_name}.zip from {zip_url}")

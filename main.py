import os
import requests
import zipfile
import io
from html import escape
from tokencost import calculate_prompt_cost, count_string_tokens
from decimal import Decimal

# Define the model to be used for cost and token calculation
MODEL = "gpt-4o"

def clean_github_url(repo_url):
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]
    if 'github.com' in repo_url and not repo_url.endswith('.git'):
        repo_url = repo_url.split('?')[0]
    return repo_url

def download_and_extract_github_repo(repo_url, download_dir):
    repo_url = clean_github_url(repo_url)
    repo_name = repo_url.rstrip('/').split('/')[-1]
    zip_url = f"{repo_url}/archive/refs/heads/master.zip"
    print(f"Downloading {zip_url}...")

    # Create download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Download the repo as a zip file
    response = requests.get(zip_url)
    if response.status_code == 200:
        print(f"Extracting {repo_name}.zip...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(download_dir)
        extracted_folder = os.path.join(download_dir, f"{repo_name}-master")
        return extracted_folder
    else:
        raise Exception(f"Failed to download {repo_name}.zip from {zip_url}")

def is_binary(file_path):
    """
    Check if a file is binary.
    """
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)
            if b'\0' in chunk:
                return True
        return False
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return True

def process_files(folder_path, output_txt, html_file):
    file_list = []
    max_depth = 0
    total_tokens = 0
    total_cost = Decimal(0)

    # Write to the text file
    with open(output_txt, 'w', encoding='utf-8') as txt_file:
        # Collect file information and determine max folder depth
        for root, dirs, files in os.walk(folder_path):
            for name in files:
                file_path = os.path.join(root, name)
                if is_excluded(name):
                    continue

                relative_path = os.path.relpath(file_path, folder_path)
                parts = relative_path.split(os.sep)
                depth = len(parts) - 1
                max_depth = max(max_depth, depth)

                if is_binary(file_path):
                    tokens = 0
                    cost = Decimal(0)
                    content = "<binary file content not included>"
                else:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        tokens = count_string_tokens(prompt=content, model=MODEL)
                        cost = calculate_prompt_cost(content, model=MODEL)
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        tokens = 0
                        cost = Decimal(0)
                        content = "<error reading content>"

                total_tokens += tokens
                total_cost += cost
                file_list.append((parts, tokens, cost, file_path))

                # Write file path and content to the text file
                txt_file.write(f"Path: {file_path}\n")
                txt_file.write("Content:\n")
                txt_file.write(content + "\n")
                txt_file.write("\n" + "-"*50 + "\n\n")

    # Create the HTML report
    create_html_report(html_file, file_list, max_depth, total_tokens, total_cost)

def create_html_report(html_file, file_list, max_depth, total_tokens, total_cost):
    with open(html_file, 'w') as html:
        html.write("<html><head><style>")
        html.write("body {font-family: Arial, sans-serif;}")
        html.write("table {border-collapse: collapse; margin-left: auto; margin-right: auto;}")
        html.write("th, td {border: 1px solid black; padding: 8px; text-align: left;}")
        html.write("th {background-color: #f2f2f2;}")
        html.write("section {display: flex; justify-content: center;}")
        html.write("table {max-width: 80%; width: 100%;}")
        html.write("</style></head><body>")
        html.write("<h1 style='text-align:center;'>File Report</h1>")
        html.write(f"<p style='text-align:center;'>Total Tokens: {total_tokens}</p>")
        html.write(f"<p style='text-align:center;'>Total Cost: ${float(total_cost):.10f}</p>")
        html.write("<section><table>")
        html.write("<tr>")
        
        # Create header
        for i in range(max_depth):
            html.write(f"<th>Folder {i+1}</th>")
        html.write("<th>File Name</th><th>Tokens</th><th>Cost</th><th>Link</th></tr>")
        
        # Create rows for each file
        for parts, tokens, cost, file_path in file_list:
            html.write("<tr>")
            depth = len(parts) - 1

            # Write folder columns
            for i in range(max_depth):
                if i < depth:
                    html.write(f"<td>{escape(parts[i])}</td>")
                elif i == depth:
                    html.write(f"<td>{escape(parts[i])}</td>")
                else:
                    html.write(f"<td></td>")
            
            # Write file name, tokens, cost, and link
            file_name = escape(parts[-1])
            cost_info = f"${float(cost):.10f}"  # Formatting cost for clarity
            link = f"<a href='file:///{escape(os.path.abspath(file_path))}'>link</a>"
            html.write(f"<td>{file_name}</td><td>{tokens}</td><td>{cost_info}</td><td>{link}</td>")
            html.write("</tr>")
        
        html.write("</table></section></body></html>")

def is_excluded(file_name):
    exclude_patterns = ["package-lock.json", ".DS_Store", "node_modules", "__pycache__", "*.log"]
    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern in file_name:
            return True
    return False

# Example usage
repo_url = input("Enter the GitHub repo URL: ")
download_dir = "downloaded_repos"
extracted_folder = download_and_extract_github_repo(repo_url, download_dir)

# Set output files next to the extracted folder
output_txt = os.path.join(download_dir, f"{os.path.basename(extracted_folder)}_file_paths_and_contents.txt")
html_file = os.path.join(download_dir, f"{os.path.basename(extracted_folder)}_file_report.html")

process_files(extracted_folder, output_txt, html_file)
print(f"Processing complete. Files saved in: {os.path.dirname(output_txt)}")

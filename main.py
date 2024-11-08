import sys
import os
import pyperclip

from datetime import datetime
from github_repo_handler import download_and_extract_github_repo
from file_processor import process_files
from utils import load_exclude_patterns

if __name__ == "__main__":
        
    # Fetch repo_url from command-line argument
    if len(sys.argv) > 1:
        repo_url = sys.argv[1]
    else:
        raise ValueError("Repository URL not provided. Usage: python script_name.py <repo_url>")

    # Load exclusion patterns from JSON
    exclude_patterns = load_exclude_patterns()

    # Set up the run directory structure
    run_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    repo_name = repo_url.rstrip('/').split('/')[-1]
    run_dir = os.path.join("runs", f"{run_time}_{repo_name}")
    os.makedirs(run_dir, exist_ok=True)

    # Download and extract the repository
    extracted_folder = download_and_extract_github_repo(repo_url, run_dir)

    if extracted_folder:
        # Set output files in the run directory
        output_txt = os.path.join(run_dir, f"{repo_name}_file_paths_and_contents.txt")
        html_file = os.path.join(run_dir, f"{repo_name}_file_report.html")

        process_files(extracted_folder, output_txt, html_file, exclude_patterns)

        # Prepare the success message
        completion_message = f"Processing complete. Files saved in: {run_dir}"

        # Print and copy to clipboard
        print(completion_message)
        
        try:
            pyperclip.copy(completion_message)  # Copy to clipboard
        except pyperclip.PyperclipException:
            print("Could not copy to clipboard. Please manually copy the path if needed.")
    else:
        print("Download or extraction failed. No files processed.")
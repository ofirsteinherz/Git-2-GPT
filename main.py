import os
from datetime import datetime
from github_repo_handler import download_and_extract_github_repo
from file_processor import process_files
from utils import load_exclude_patterns

# Example usage
if __name__ == "__main__":
    repo_url = input("Enter the GitHub repo URL: ")

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
        print(f"Processing complete. Files saved in: {run_dir}")
    else:
        print("Download or extraction failed. No files processed.")
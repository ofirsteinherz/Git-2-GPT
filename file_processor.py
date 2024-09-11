import os
from decimal import Decimal
from tokencost import calculate_prompt_cost, count_string_tokens
from utils import is_binary, is_excluded
from report_generator import create_html_report
import pandas as pd

MODEL = "gpt-4o"

def process_files(folder_path, output_txt, html_file, exclude_patterns):
    file_list = []
    total_tokens = 0
    total_cost = Decimal(0)

    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return

    print(f"Processing files in folder: {folder_path}")

    with open(output_txt, 'w', encoding='utf-8') as txt_file:
        for root, dirs, files in os.walk(folder_path):
            for name in files:
                file_path = os.path.join(root, name)
                print(f"Processing file: {file_path}")

                if is_excluded(name, exclude_patterns):
                    print(f"Excluded file: {file_path}")
                    continue

                relative_path = os.path.relpath(file_path, folder_path)
                parts = relative_path.split(os.sep)

                if is_binary(file_path):
                    tokens = 0
                    cost = Decimal(0)
                    content = "<binary file content not included>"
                elif file_path.endswith('.csv'):
                    try:
                        # Load only the first 100 rows of the CSV
                        df = pd.read_csv(file_path, nrows=100)
                        content = df.to_csv(index=False)  # Convert back to CSV string format for token counting
                        tokens = count_string_tokens(prompt=content, model=MODEL)
                        cost = calculate_prompt_cost(content, model=MODEL)
                        if tokens > 100000:
                            print(f"Skipping file {file_path} due to token count: {tokens}")
                            continue
                    except Exception as e:
                        print(f"Error processing CSV file {file_path}: {e}")
                        tokens = 0
                        cost = Decimal(0)
                        content = "<error reading CSV content>"
                else:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        tokens = count_string_tokens(prompt=content, model=MODEL)
                        cost = calculate_prompt_cost(content, model=MODEL)
                        if tokens > 100000:
                            print(f"Skipping file {file_path} due to token count: {tokens}")
                            continue
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        tokens = 0
                        cost = Decimal(0)
                        content = "<error reading content>"

                total_tokens += tokens
                total_cost += cost
                file_list.append((parts, tokens, cost, file_path))

                txt_file.write(f"Path: {file_path}\n")
                txt_file.write("Content:\n")
                txt_file.write(content + "\n")
                txt_file.write("\n" + "-"*50 + "\n\n")

    print(f"Total tokens processed: {total_tokens}")
    print(f"Total cost calculated: {total_cost}")

    create_html_report(html_file, file_list, total_tokens, total_cost)

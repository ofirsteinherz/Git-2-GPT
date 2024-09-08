import json
import os

def load_exclude_patterns(json_file="exclude_patterns.json"):
    with open(json_file, "r") as file:
        data = json.load(file)
    return data.get("exclude_patterns", [])

def is_excluded(file_name, exclude_patterns):
    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern in file_name:
            return True
    return False

def is_binary(file_path):
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)
            if b'\0' in chunk:
                return True
        return False
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return True

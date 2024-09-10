import os
import requests
import json
import time
from tokencost import calculate_prompt_cost, count_string_tokens
import pandas as pd

class OpenAIGPTClient:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API key is not set. Please set the OPENAI_API_KEY environment variable.")
        self.endpoint = "https://api.openai.com/v1/chat/completions"
        self.token_limit_per_minute = 450000  # Token per minute limit (TPM)
        self.requests_per_minute = 5000       # Requests per minute limit (RPM)
        self.daily_token_limit = 1350000      # Token per day limit (TPD)
        self.model = "gpt-4o"
        self.time_interval = 60  # Time window for the rate limit (1 minute)

        self.tokens_used_in_current_minute = 0
        self.requests_in_current_minute = 0
        self.current_minute_start = time.time()

    def reset_minute_counters(self):
        """Reset token and request counters after each minute."""
        current_time = time.time()
        if current_time - self.current_minute_start >= self.time_interval:
            self.tokens_used_in_current_minute = 0
            self.requests_in_current_minute = 0
            self.current_minute_start = current_time

    def llm_call(self, messages, model="gpt-4o", temperature=0.3, max_tokens=500, json_format=False, seed=42):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed
        }

        if json_format:
            data["response_format"] = { "type": "json_object" }

        self.reset_minute_counters()

        # Calculate the total number of tokens in this request
        input_tokens = sum(count_string_tokens(prompt=msg["content"], model=self.model) for msg in messages if "content" in msg)

        if self.tokens_used_in_current_minute + input_tokens > self.token_limit_per_minute or self.requests_in_current_minute >= self.requests_per_minute:
            # If sending this request would exceed the rate limits, wait until the next minute
            wait_time = self.time_interval - (time.time() - self.current_minute_start)
            print(f"Rate limit reached. Waiting {wait_time:.2f} seconds before sending the next request.")
            time.sleep(wait_time)
            self.reset_minute_counters()

        response = requests.post(self.endpoint, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise HTTPError for bad responses
        self.tokens_used_in_current_minute += input_tokens + count_string_tokens(response.text, model=self.model)
        self.requests_in_current_minute += 1

        return response.json()['choices'][0]['message']['content'].strip()

    def process_dataframe(self, df: pd.DataFrame, text_column: str):
        all_responses = []

        for _, row in df.iterrows():
            content = row[text_column]
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content}
            ]

            response = self.llm_call(messages)
            all_responses.append(response)

        return all_responses

# # Example usage of `OpenAIGPTClient`
# client = OpenAIGPTClient()
# # Assuming df is your DataFrame and 'text' is the column containing the text
# responses = client.process_dataframe(df, text_column='text')

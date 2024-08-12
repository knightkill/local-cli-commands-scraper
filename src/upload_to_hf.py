import os
import json
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi, Repository
from dotenv import load_dotenv

#load env
load_dotenv()
# Set your Hugging Face credentials
hf_token = os.getenv('HUGGINGFACE_TOKEN')
hf_username = os.getenv('HUGGINGFACE_USERNAME')
hf_dataset_name = os.getenv('HUGGINGFACE_DATASET_NAME')

if not hf_token or not hf_username or not hf_dataset_name:
    raise ValueError("Hugging Face token, username or dataset name not set in environment variables.")

hf_repo_id = f"{hf_username}/{hf_dataset_name}"
# Load the JSONL file
output_file = './output/scrapped.jsonl'

# Read the JSONL file
data = []
with open(output_file, 'r') as file:
    for line in file:
        data.append(json.loads(line))

# Create a Hugging Face dataset
dataset = Dataset.from_dict({
    "command": [item["command"] for item in data],
    "description": [item["description"] for item in data],
    "name": [item["name"] for item in data],
    "synopsis": [item["synopsis"] for item in data],
    "options": [item["options"] for item in data],
    "examples": [item["examples"] for item in data],
})

# Save dataset locally
dataset_folder = output_file.replace(".jsonl", "_dataset")
dataset.save_to_disk(dataset_folder)

# Initialize HfApi object
api = HfApi()

# Check if the repository already exists
try:
    repo_url = api.create_repo(
        repo_id=hf_repo_id,
        token=hf_token,
        repo_type='dataset',
        private=False,  # or True if you want it to be private
        exist_ok=True  # Pass True to avoid raising an error if the repo exists
    )
except Exception as e:
    print(f"Failed to create or retrieve repository: {str(e)}")
    exit(1)

# Upload the dataset to Hugging Face
dataset.push_to_hub(hf_repo_id, token=hf_token)

print(f"Dataset uploaded to Hugging Face: {hf_repo_id}")

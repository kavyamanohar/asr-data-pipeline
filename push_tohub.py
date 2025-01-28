from datasets import load_dataset

dataset = load_dataset("audiofolder", data_dir="./data/processed/corpus")
dataset.push_to_hub("kavyamanohar/court-hearings-ctc-nltk")

import pandas as pd


# Caveat: This file must be ran from root directory.
# Assumption: A seeded CSV file already exists ("dummy_data/dummy_students.csv").

def csv_to_parquet():
    csv_path = "dummy_data/dummy_students.csv"
    parquet_path = "dummy_data/dummy_students.parquet"
    df = pd.read_csv(csv_path)
    df.to_parquet(parquet_path, engine="pyarrow", index=False)
    print(f"✅ Successfully wrote {len(df)} rows to {parquet_path}")

def csv_to_json():
    csv_path = "dummy_data/dummy_students.csv"
    json_path = "dummy_data/dummy_students.json"
    df = pd.read_csv(csv_path)
    df.to_json(json_path, orient="records", indent=2)
    print(f"✅ Successfully wrote {len(df)} rows to {json_path}")

if __name__ == "__main__":
    pass # Replace with the required function
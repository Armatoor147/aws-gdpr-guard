import pandas as pd
import csv
import random
from datetime import datetime, timedelta


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

def create_1MB_csv_file():
    courses = ["Software", "Data"]
    cohort_dates = ["2024-11-02", "2024-09-01", "2025-01-15"]
    first_names = ["John", "Mia", "David", "Sarah", "Robert", "Emily", "Michael", "Olivia", "Chris", "Jessica", "Andrew", "Megan", "Daniel", "Laura", "James", "Anna", "Kevin", "Nicole", "Ryan", "Maria"]
    last_names = ["Smith", "Johnson", "Lee", "Chen", "Brown", "Green", "Davis", "Wilson", "Garcia", "Martinez", "Rodriguez", "Harris", "Clark", "King", "White", "Baker", "Scott", "Adams", "Murphy", "Lopez"]

    def random_graduation_date(cohort_date):
        cohort = datetime.strptime(cohort_date, "%Y-%m-%d")
        graduation = cohort + timedelta(days=random.randint(90, 365))
        return graduation.strftime("%Y-%m-%d")

    def generate_email(first_name, last_name):
        return f"{first_name.lower()}.{last_name.lower()}@email.com"

    with open('dummy_data/big_dummy_students.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["student_id", "name", "course", "cohort", "graduation_date", "email_address"])

        # Generate and write 21,000 rows (1KB * 1000 ≈ 1MB)
        for i in range(1, 21001):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            course = random.choice(courses)
            cohort = random.choice(cohort_dates)
            graduation_date = random_graduation_date(cohort)
            email = generate_email(first_name, last_name)
            writer.writerow([1233 + i, name, course, cohort, graduation_date, email])

if __name__ == "__main__":
    create_1MB_csv_file()
    pass # Replace with the required function
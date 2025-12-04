import pandas as pd
import os

def run_cleaner():
    input_path = 'data/raw_data.csv'
    output_path = 'data/cleaned_data.csv'

    if not os.path.exists(input_path):
        print("raw_data.csv is not founded")
        return

    df = pd.read_csv(input_path)
    print(f"Original Data collected {len(df)}")

    #removing duplicates
    df.drop_duplicates(subset=['link'], inplace=True)
    print(f"Data collected after removing duplicates {len(df)}")

    #handling missing values
    df['title'] = df['title'].fillna('Unknown Title')

    # normalizing
    def clean_price(value):
        if pd.isna(value) or value == "No Price":
            return 0
        digits_only = ''.join(filter(str.isdigit, str(value)))
        if digits_only:
            return int(digits_only)
        return 0

    df['price_cleaned'] = df['price'].apply(clean_price)
    df = df[df['price_cleaned'] > 0]

    #type conversions
    df['title'] = df['title'].astype(str)
    

    df.to_csv(output_path, index=False)
    print(f"Dataset size = {len(df)}")
  
if __name__ == "__main__":
    run_cleaner()
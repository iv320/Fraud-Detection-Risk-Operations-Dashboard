import pandas as pd
import numpy as np
import os

def run_fraud_pipeline(input_path='data/transactions.csv', output_path='data/processed_transactions.csv'):
    print("--- Starting Fraud Detection Pipeline ---")
    
    # 1. Data Ingestion
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
    
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} transactions.")
    
    # 2. Data Cleaning & Validation
    # Fix types
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['transaction_amount'] = pd.to_numeric(df['transaction_amount'], errors='coerce')
    
    # Drop rows with null/negative amounts
    initial_count = len(df)
    df = df.dropna(subset=['transaction_amount'])
    df = df[df['transaction_amount'] > 0]
    
    # Handle duplicates
    df = df.drop_duplicates(subset=['transaction_id'], keep='last')
    
    dropped_rows = initial_count - len(df)
    print(f"Cleaned data. Dropped {dropped_rows} rows.")
    
    # 3. Rule-Based Fraud Flags
    df['flag_high_amount'] = (df['transaction_amount'] > (3 * df['avg_txn_amount_30d'])).astype(int)
    df['flag_velocity'] = (df['txn_count_last_24h'] > 10).astype(int)
    df['flag_foreign_txn'] = ((df['is_foreign_txn'] == 1) & (df['transaction_amount'] > 5000)).astype(int)
    
    # 4. Outlier Detection (IQR)
    Q1 = df['transaction_amount'].quantile(0.25)
    Q3 = df['transaction_amount'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df['flag_outlier'] = ((df['transaction_amount'] < lower_bound) | (df['transaction_amount'] > upper_bound)).astype(int)
    
    # 5. Risk Scoring Engine
    # Condition Scores: High amount +30, Velocity breach +25, Foreign txn +20, Outlier detected +25
    df['risk_score'] = (
        df['flag_high_amount'] * 30 +
        df['flag_velocity'] * 25 +
        df['flag_foreign_txn'] * 20 +
        df['flag_outlier'] * 25
    )
    
    # Risk Buckets
    def get_risk_level(score):
        if score <= 30: return 'Low'
        elif score <= 60: return 'Medium'
        else: return 'High'
        
    df['risk_level'] = df['risk_score'].apply(get_risk_level)
    
    # 6. Final Fraud Flag
    df['fraud_flag'] = df['risk_score'].apply(lambda x: 'Yes' if x >= 60 else 'No')
    
    # Save processed data
    df.to_csv(output_path, index=False)
    print(f"Pipeline complete. Processed data saved to {output_path}")
    
    # Summary Table for review
    print("\nProcessing Summary:")
    print(df['risk_level'].value_counts())
    print("\nFraud Flag Counts:")
    print(df['fraud_flag'].value_counts())

if __name__ == "__main__":
    run_fraud_pipeline()

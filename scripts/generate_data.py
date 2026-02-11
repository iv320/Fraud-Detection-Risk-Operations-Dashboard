import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_synthetic_data(num_rows=100000):
    np.random.seed(42)
    
    # Categories and Countries
    categories = ['electronics', 'food', 'travel', 'grocery', 'health', 'entertainment']
    methods = ['Card', 'UPI', 'Wallet']
    countries = ['India', 'USA', 'UK', 'UAE', 'Canada', 'Singapore']
    
    # Generate Base Data
    data = {
        'transaction_id': [f'TXN_{i:06d}' for i in range(num_rows)],
        'customer_id': [f'CUS_{random.randint(1000, 5000)}' for _ in range(num_rows)],
        'transaction_amount': np.random.uniform(10, 50000, num_rows).round(2),
        'transaction_date': [datetime(2025, 1, 1) + timedelta(minutes=random.randint(0, 44640)) for _ in range(num_rows)],
        'merchant_category': [random.choice(categories) for _ in range(num_rows)],
        'payment_method': [random.choice(methods) for _ in range(num_rows)],
        'transaction_country': [random.choice(countries) for _ in range(num_rows)],
        'is_foreign_txn': [random.randint(0, 1) for _ in range(num_rows)],
        'txn_count_last_24h': np.random.randint(1, 15, num_rows),
        'avg_txn_amount_30d': np.random.uniform(100, 10000, num_rows).round(2),
        'chargeback_flag': [1 if random.random() < 0.02 else 0 for _ in range(num_rows)] # 2% chargeback rate
    }
    
    df = pd.DataFrame(data)
    
    # Inject some "fraudulent" patterns for demonstration
    # 1. High Velocity
    fraud_indices = df.sample(frac=0.01).index
    df.loc[fraud_indices, 'txn_count_last_24h'] = np.random.randint(11, 50, len(fraud_indices))
    
    # 2. High Amount relative to average
    df.loc[fraud_indices[:len(fraud_indices)//2], 'transaction_amount'] = df.loc[fraud_indices[:len(fraud_indices)//2], 'avg_txn_amount_30d'] * 4
    
    df.to_csv('data/transactions.csv', index=False)
    print(f"Generated {num_rows} transactions in data/transactions.csv")

if __name__ == "__main__":
    generate_synthetic_data()

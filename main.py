import pandas as pd

def convert_to_vertical_format(df):
    pass

def generate_frequent_itemsets(vertical_data, min_support):
    pass

def generate_association_rules(frequent_itemsets):
    pass

def extract_strong_rules(association_rules, min_confidence):
    pass

def calculate_lift(association_rules, frequent_itemsets, total_transactions):
    pass

min_support = 0.6
min_confidence = 0.6
file_name = "Horizontal_Format.xlsx"

def main():
    df = pd.read_excel(file_name)
    total_transactions = df.shape[0]

    vertical_data = convert_to_vertical_format(df)
    frequent_itemsets = generate_frequent_itemsets(vertical_data, min_support)
    association_rules = generate_association_rules(frequent_itemsets)
    extract_strong_rules(association_rules, min_confidence)
    calculate_lift(association_rules, frequent_itemsets, total_transactions)

main()
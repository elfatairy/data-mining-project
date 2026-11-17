import pandas as pd
import math

def convert_to_vertical_format(df):
    vv = {}

    for i in range(len(df)):
        tid = int(df.iloc[i, 0])
        itemsss = df.iloc[i, 1]



        
        listofitemss = itemsss.split(",")

        for j in listofitemss:

            if j not in vv:
                vv[j] = set()

     
            vv[j].add(tid)



    print("Vertical format:")
    for z in vv:
        print(z, ":", vv[z], "    support count =", len( vv[z]   ))



    return vv


def generate_frequent_itemsets(vertical_data, min_support,total_transactions):
   
    min_support_count = math.ceil(min_support * total_transactions)

    frequent_itemsets = {}
    items = sorted(vertical_data.items())

    # inner function of eclat
    def eclat(prefix, items):

        for i in range(len(items)):

            item, tids = items[i]

            # Extend the current prefix
            new_itemset = prefix + (item,)

            support_count = len(tids)

            # Save the frequent itemset
            frequent_itemsets[frozenset(new_itemset)] = {
                "tids": tids,
                "support_count": support_count
            }

            # Generate possible extensions
            extensions = []

            for j in range(i + 1, len(items)):
                
                next_item, next_tids = items[j]
                intersection = tids & next_tids

                # Keep only frequent extensions
                if len(intersection) >= min_support_count:
                    extensions.append((next_item, intersection))

            #  generate larger itemsets using recursion
            if extensions:
                eclat(new_itemset, extensions)

    # Start the algorithm for items with the min support only
    eclat((), [
        (item, tids)
        for item, tids in items
        if len(tids) >= min_support_count
    ])

    print("\nFrequent Itemsets:")

    max_length = max(
        (len(itemset) for itemset in frequent_itemsets),
        default=0
    )

    for k in range(1, max_length + 1):

        print(f"\nL{k}:")

        for itemset, data in frequent_itemsets.items():

            if len(itemset) == k:
                print(
                    set(itemset),
                    ":", data["tids"],
                    "Support count =", data["support_count"]
                )

    return frequent_itemsets

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
    frequent_itemsets = generate_frequent_itemsets(vertical_data, min_support,total_transactions)
    association_rules = generate_association_rules(frequent_itemsets)
    extract_strong_rules(association_rules, min_confidence)
    calculate_lift(association_rules, frequent_itemsets, total_transactions)

main()

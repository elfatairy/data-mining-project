import pandas as pd
import math

def convert_to_vertical_format(df):
    vv = {}

    for i in range(len(df)):
        raw_tid = df.iloc[i, 0]
        tid = raw_tid.item() if hasattr(raw_tid, "item") else str(raw_tid).strip()
        itemsss = df.iloc[i, 1]

        if pd.isna(itemsss):
            continue

        listofitemss = str(itemsss).split(",")

        for j in listofitemss:
            j = j.strip()
            if not j:
                continue
            if j not in vv:
                vv[j] = set()
     
            vv[j].add(tid)

    print("Vertical format: ")
    for z in vv:
        print(z, ": ", vv[z], "    support count = ", len(vv[z]))

    return vv


def generate_frequent_itemsets(vertical_data, min_support,total_transactions):
   
    min_support_count = math.ceil(round(min_support * total_transactions, 10))

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

def my_combinations(items, r):
    result = []
    def pick(start, current):
        if len(current) == r:
            result.append(tuple(current))
            return

        # test from start of the list
        for i in range(start, len(items)):
            current.append(items[i])      # get element
            pick(i + 1, current)          # the next element
            current.pop()                 # backtracking

    pick(0, [])
    return result

def generate_association_rules(frequent_itemsets):
    # Will Start from L2
    rules = []
    print(f"\nAssociation Rules:\n")
    for itemset, data in frequent_itemsets.items():
        # if L1 ignore
        if len(itemset) < 2:
            continue
        # L2 or more
        for n in range(1 , len(itemset)):
            for l in my_combinations(sorted(itemset), n):         # Take Combinations from the item set at size n
                antecedent = frozenset(l)                      # convert to set to make subtraction
                consequent = itemset - antecedent              # antecedent - > Condition      consequent -> result
                print(set(antecedent), "->", set(consequent))
                rules.append({"antecedent": antecedent, "consequent": consequent , "support": data["support_count"]}) # association rules antecedent given that consequent
    return rules


def extract_strong_rules(association_rules, frequent_itemsets, min_confidence):
    strong_rules = []
    print("\nStrong rules:")
    for rule in association_rules:
        confidence = rule["support"] / frequent_itemsets[rule["antecedent"]]["support_count"]
        if confidence >= min_confidence:
            strong_rules.append(rule)
            print(set(rule["antecedent"]), "->", set(rule["consequent"]), "with confidence =", confidence)
    return strong_rules

def calculate_lift(association_rules, frequent_itemsets, total_transactions):
    print("\nLift:")

    for rule in association_rules:
        antecedent = rule["antecedent"]
        consequent = rule["consequent"]

        p_union = rule["support"] / total_transactions
        p_a = frequent_itemsets[antecedent]["support_count"] / total_transactions
        p_b = frequent_itemsets[consequent]["support_count"] / total_transactions

        lift = p_union / (p_a * p_b) 
        status = ""
        if math.isclose(lift, 1.0):
            status = "Independent"
        elif lift < 1:
            status = "Negative Dependent"
        else:
            status = "Positive Dependent"
            
        print(set(antecedent), "->", set(consequent),"with lift =", lift,"(",status,")")
        


file_name = "Horizontal_Format.xlsx"

def main():
    df = pd.read_excel(file_name)
    total_transactions = df.shape[0]
    vertical_data = convert_to_vertical_format(df)

    while True:
        min_support = float(input("\nEnter minimum support (0 to 1, e.g. 0.6): "))
        min_confidence = float(input("Enter minimum confidence (0 to 1, e.g. 0.6): "))

        frequent_itemsets = generate_frequent_itemsets(vertical_data, min_support, total_transactions)
        association_rules = generate_association_rules(frequent_itemsets)
        strong_rules = extract_strong_rules(association_rules, frequent_itemsets, min_confidence)
        calculate_lift(association_rules, frequent_itemsets, total_transactions)

        again = input("\nRun again with different values? (y/n): ").strip().lower()
        if again != "y":
            break

main()
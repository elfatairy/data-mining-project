import pandas as pd
import math
import re

def clean_cell(value):
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)           # Change 1.0 to 1
    return str(value).strip()


def split_cell(text):       # Ex.:- ' I1, I2,,I5, ' => ['I1', 'I2', 'I5']
    pieces = text.split(",")
    parts = []
    for p in pieces:
        clean = p.strip()
        parts.append(clean)
    result = []
    for p in parts:
        if p:
            result.append(p)
    return result


def convert_tids_to_numbers(tids):
    matches = []
    for tid in tids:
        result = re.fullmatch(r"(\D*)(\d+)", tid)
        matches.append(result)

    if all(matches):                   
        letters = set()                
        for m in matches:
            letters.add(m.group(1))    
        if len(letters) == 1:
              numbers = []
              for m in matches:
                  numbers.append(int(m.group(2)))
              if len(set(numbers)) == len(numbers):
                 return numbers

    numbers = list(range(1, len(tids) + 1))
    print("TIDs were replaced with numbers:", dict(zip(tids, numbers)))
    return numbers


def clean_data(df):
    if df.shape[1] < 2:
        raise ValueError("The file needs two columns: TiD and items.")
    
    transactions = {}

    for i in range(len(df)):
        tid = clean_cell(df.iloc[i, 0])
        text = clean_cell(df.iloc[i, 1])

        if not tid and not text:        
            continue
        if not tid:
            raise ValueError(f"A row has an empty Transaction ID: {text}")

        items = transactions.setdefault(tid, [])
        items.extend(split_cell(text))

    if not transactions:
        raise ValueError("The file has no transactions.")

    numbers = convert_tids_to_numbers(list(transactions))

    rows = [(number, ",".join(items))
            for number, items in zip(numbers, transactions.values()) if items]

    return pd.DataFrame(rows, columns=["TiD", "items"]), len(transactions)


def calc_min_support_count(min_support, total_transactions):
    return max(1, math.ceil(round(min_support * total_transactions, 9)))


def ask_ratio(message):
    while True:
        text = input(message).strip()
        try:
            value = float(text.rstrip("%"))
        except ValueError:
            value = 0
        if text.endswith("%") or value > 1:
            value /= 100
        if 0 < value <= 1:
            return value
        print("Enter a value such as 0.6 or 60%.")


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

    print("Vertical format: ")
    for z in vv:
        print(z, ": ", vv[z], "    support count = ", len(vv[z]))

    return vv


def generate_frequent_itemsets(vertical_data, min_support_count,total_transactions):
    frequent_itemsets = {}
    items = sorted(vertical_data.items())

    def eclat(prefix, items):
        for i in range(len(items)):
            item, tids = items[i]
            new_itemset = prefix + (item,)
            support_count = len(tids)

            frequent_itemsets[frozenset(new_itemset)] = {
                "tids": tids, 
                "support_count": support_count
            }

            extensions = []
            for j in range(i + 1, len(items)):                
                next_item, next_tids = items[j]
                intersection = tids & next_tids

                if len(intersection) >= min_support_count:
                    extensions.append((next_item, intersection))

            if extensions:
                eclat(new_itemset, extensions)

    eclat((), [
        (item, tids)
        for item, tids in items
        if len(tids) >= min_support_count
    ])

    print("\nFrequent Itemsets:")
    max_length = max((len(itemset) for itemset in frequent_itemsets),default=0)

    for k in range(1, max_length + 1):
        print(f"\nL{k}:")

        for itemset, data in frequent_itemsets.items():
            if len(itemset) == k:
                print(set(itemset),":", data["tids"],"Support count =", data["support_count"])

    return frequent_itemsets

def my_combinations(items, r):
    result = []
    def pick(start, current):
        if len(current) == r:
            result.append(tuple(current))
            return

        for i in range(start, len(items)):
            current.append(items[i])
            pick(i + 1, current)      
            current.pop()

    pick(0, [])
    return result

def generate_association_rules(frequent_itemsets):
    rules = []
    print(f"\nAssociation Rules:\n")
    for itemset, data in frequent_itemsets.items():
        if len(itemset) < 2:
            continue
        
        for n in range(1 , len(itemset)):
            for l in my_combinations(sorted(itemset), n):
                antecedent = frozenset(l)
                consequent = itemset - antecedent
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
    try:
        df, total_transactions = clean_data(pd.read_excel(file_name))
    except (OSError, ValueError, ImportError) as error:
        print("Error:", error)
        return

    vertical_data = convert_to_vertical_format(df)
    while True:
        min_support = ask_ratio("\nMinimum support (example 0.6 or 60%): ")
        min_support_count = calc_min_support_count(min_support, total_transactions)
        min_confidence = ask_ratio("Minimum confidence (example 0.6 or 60%): ")

        frequent_itemsets = generate_frequent_itemsets(vertical_data, min_support_count, total_transactions)
        association_rules = generate_association_rules(frequent_itemsets)
        strong_rules = extract_strong_rules(association_rules, frequent_itemsets, min_confidence)
        calculate_lift(association_rules, frequent_itemsets, total_transactions)

        if input("\nTry other values? (y/n): ").strip().lower() != "y":
            break

main()
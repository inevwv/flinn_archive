import pandas as pd
from collections import defaultdict

# === File paths ===
COMPARE_CSV = "group_comparison_results.csv"
INVENTORY_XLSX = "D:/workspace/working_inventory - Copy.xlsx"
OUTPUT_XLSX = "working_inventory_with_actions.xlsx"

# === Step 1: Load data ===
compare_df = pd.read_csv(COMPARE_CSV)
inventory_df = pd.read_excel(INVENTORY_XLSX, engine="openpyxl")

# === Step 2: Filter for exact matches and collect file groups ===
exact_matches = compare_df[compare_df["Result"] == "Exact match"]

group_to_files = defaultdict(set)

for _, row in exact_matches.iterrows():
    group = row["Group_ID"]
    group_to_files[group].add(row["File_1"])
    group_to_files[group].add(row["File_2"])

# === Step 3: Build action map using File_1 as canonical ===
action_map = {}

for _, row in exact_matches.iterrows():
    file_1 = str(row["File_1"]).strip().replace("/", "\\")
    file_2 = str(row["File_2"]).strip().replace("/", "\\")

    action_map[file_1] = "Keep"  # always keep File_1
    if file_2 != file_1:
        action_map[file_2] = "Delete"  # delete duplicates

# Normalize paths in Full_Path to match the keys
inventory_df["Normalized_Path"] = inventory_df["Full_Path"].str.strip().replace("/", "\\", regex=False)
inventory_df["Action"] = inventory_df["Normalized_Path"].map(action_map).fillna("")
inventory_df.drop(columns=["Normalized_Path"], inplace=True)

missing_paths = set(action_map.keys()) - set(inventory_df["Full_Path"].str.strip().replace("/", "\\", regex=False))
if missing_paths:
    print("⚠️ These paths from the comparison results weren't found in the inventory:")
    for path in sorted(missing_paths):
        print("-", path)


# === Step 5: Save updated inventory as XLSX ===
inventory_df.to_excel(OUTPUT_XLSX, index=False)

print(f"✅ Done. Output saved to: {OUTPUT_XLSX}")
print(f"📊 Summary: {list(action_map.values()).count('Keep')} kept, {list(action_map.values()).count('Delete')} marked for deletion.")

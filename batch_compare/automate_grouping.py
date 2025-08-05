import pandas as pd
from pathlib import Path
from collections import defaultdict

# === CONFIGURATION ===
INPUT_PATH = "D:/workspace/xls_to_convert.csv"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "batch_compare" / "comparison_groups.xlsx"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# === LOAD AND PARSE PATHS ===
df = pd.read_csv(INPUT_PATH, header=None, names=["File_Path"], encoding="latin1")
df["File_Path"] = df["File_Path"].astype(str)

def extract_parts(path_str):
    p = Path(path_str)
    return {
        "Base_Name": p.name.strip().lower(),
        "Parent": p.parent.name.strip().lower(),
        "Grandparent": p.parent.parent.name.strip().lower()
    }

df_parts = df["File_Path"].apply(extract_parts).apply(pd.Series)
df = pd.concat([df, df_parts], axis=1)

# === GROUPING ===
rows = []
group_counter = 1

for base_name, group_df in df.groupby("Base_Name"):
    # Create (Grandparent, Parent) mapping
    parent_map = defaultdict(list)
    for _, row in group_df.iterrows():
        parent_map[(row["Grandparent"], row["Parent"])].append(row["File_Path"])

    # Now merge groups that have different grandparents but same parent name
    merged_groups = defaultdict(list)

    for (grandparent, parent), files in parent_map.items():
        merged_groups[parent].extend(files)

    for file_group in merged_groups.values():
        if len(file_group) > 1:
            group_id = f"grp_{group_counter:04d}"
            for f in file_group:
                rows.append({"Group_ID": group_id, "File_Path": f})
            group_counter += 1

# === SAVE ===
grouped_df = pd.DataFrame(rows)
grouped_df.to_excel(OUTPUT_PATH, index=False)
print(f"✅ Grouping complete. Saved to: {OUTPUT_PATH}")
print(f"🔢 Total groups: {len(grouped_df['Group_ID'].unique())}")

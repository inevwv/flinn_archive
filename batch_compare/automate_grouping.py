import pandas as pd
from pathlib import Path
from collections import defaultdict

# === CONFIGURATION ===
INPUT_PATH = "D:/workspace/xls_to_convert.csv"  # CSV with one column of full file paths
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "batch_compare" / "comparison_groups.xlsx"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# === LOAD PATHS ===
df = pd.read_csv(INPUT_PATH, header=None, names=["File_Path"], encoding="latin1")
df["File_Path"] = df["File_Path"].astype(str)

# === EXTRACT FILENAMES AND GROUP ===
df["Base_Name"] = df["File_Path"].apply(lambda x: Path(x).name.strip().lower())
group_dict = defaultdict(list)

for _, row in df.iterrows():
    group_dict[row["Base_Name"]].append(row["File_Path"])

# === CONSTRUCT GROUPED DATAFRAME ===
rows = []
for i, (basename, paths) in enumerate(group_dict.items(), start=1):
    if len(paths) > 1:  # Only include actual duplicates
        group_id = f"grp_{i:04d}"
        for p in paths:
            rows.append({"Group_ID": group_id, "File_Path": p})

grouped_df = pd.DataFrame(rows)

# === SAVE OUTPUT ===
grouped_df.to_excel(OUTPUT_PATH, index=False)
print(f"✅ Written grouped duplicates to: {OUTPUT_PATH}")

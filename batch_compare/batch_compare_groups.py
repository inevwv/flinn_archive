import pandas as pd
import itertools
from pathlib import Path
from compare_spreadsheets import load_excel, exact_comparison, sorted_comparison, similarity_score

INPUT_PATH = Path(__file__).resolve().parent / "comparison_groups.xlsx"
OUTPUT_CSV = Path(__file__).resolve().parent / "group_comparison_results.csv"

df = pd.read_excel(INPUT_PATH)

results = []

# Group by Group_ID
for group_id, group_df in df.groupby("Group_ID"):
    print(f"\n🔎 Processing group: {group_id}")
    file_paths = group_df["File_Path"].tolist()

    # Compare all pairs in the group
    for file1, file2 in itertools.combinations(file_paths, 2):
        try:
            df1 = load_excel(file1)
            df2 = load_excel(file2)

            if exact_comparison(df1, df2):
                result = "Exact match"
            elif sorted_comparison(df1, df2):
                result = "Same data, different order"
            else:
                score = similarity_score(df1, df2)
                result = f"Fuzzy match: {score:.2f}%"

        except Exception as e:
            result = f"Error: {e}"

        print(f"📝 {file1} ↔ {file2}: {result}")
        results.append({
            "Group_ID": group_id,
            "File_1": file1,
            "File_2": file2,
            "Result": result
        })

# Save results
pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ Summary saved to: {OUTPUT_CSV}")

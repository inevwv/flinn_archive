import pandas as pd
import numpy as np
import argparse
import sys

def load_excel(path):
    """Load an Excel file and fill NaNs for cleaner comparisons."""
    try:
        if path.endswith(".xls"):
            return pd.read_excel(path, engine="xlrd").fillna("")
        else:
            return pd.read_excel(path).fillna("")
    except Exception as e:
        print(f"❌ Failed to read '{path}': {e}")
        sys.exit(1)

def exact_comparison(df1, df2):
    return df1.equals(df2)

def sorted_comparison(df1, df2):
    df1_sorted = df1.sort_index(axis=0).sort_index(axis=1)
    df2_sorted = df2.sort_index(axis=0).sort_index(axis=1)
    return df1_sorted.equals(df2_sorted)

def similarity_score(df1, df2):
    if df1.shape != df2.shape:
        print(f"⚠️ Shape mismatch: {df1.shape} vs {df2.shape}")
        return 0.0
    comparison_array = df1.values == df2.values
    score = np.sum(comparison_array) / comparison_array.size * 100
    return score

def difference_report(df1, df2):
    try:
        return df1.compare(df2)
    except ValueError as e:
        return f"❌ Cannot compare: {e}"

def main():
    parser = argparse.ArgumentParser(description="Compare two Excel spreadsheets for duplication.")
    parser.add_argument("file1", help="Path to first spreadsheet")
    parser.add_argument("file2", help="Path to second spreadsheet")
    args = parser.parse_args()

    file1, file2 = args.file1, args.file2
    print(f"\n📂 Comparing: {file1} ↔ {file2}")

    df1 = load_excel(file1)
    df2 = load_excel(file2)

    print("\n🔍 Checking exact match...")
    if exact_comparison(df1, df2):
        print("✅ Files are exactly the same (same order, same values).")
        return

    print("❌ Files differ (at least some values or order).")

    print("\n🔁 Checking sorted comparison (ignoring row/column order)...")
    if sorted_comparison(df1, df2):
        print("✅ Files have the same data but in different order.")
    else:
        print("❌ Files still differ even after sorting.")

    print("\n📊 Computing fuzzy similarity score...")
    score = similarity_score(df1, df2)
    print(f"🔢 Similarity: {score:.2f}% of cells match")

    print("\n📄 Differences:")
    diff = difference_report(df1, df2)
    print(diff)

if __name__ == "__main__":
    main()

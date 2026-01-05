import pandas as pd

df = pd.read_csv("/dsl/libbot/data/text_full_libguide.csv", encoding='utf-8')

print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Search more broadly for CMN
print("\n=== Searching for 'CMN' in titles ===")
cmn_in_title = df[df['libguide_title'].str.contains('CMN', case=False, na=False)]
print(f"Found {len(cmn_in_title)} rows with 'CMN' in title")
if len(cmn_in_title) > 0:
    print(cmn_in_title[['libguide_title', 'text']].head(10))

# Search in text content too
print("\n=== Searching for 'CMN' in text ===")
cmn_in_text = df[df['text'].str.contains('CMN', case=False, na=False)]
print(f"Found {len(cmn_in_text)} rows with 'CMN' in text")
if len(cmn_in_text) > 0:
    print(cmn_in_text[['libguide_title', 'text']].head(10).to_string())

# Check for "Communication" related content
print("\n=== Searching for 'Communication' ===")
comm_rows = df[df['text'].str.contains('Communication', case=False, na=False)]
print(f"Found {len(comm_rows)} rows with 'Communication'")
if len(comm_rows) > 0:
    print(comm_rows[['libguide_title', 'text']].head(5).to_string())
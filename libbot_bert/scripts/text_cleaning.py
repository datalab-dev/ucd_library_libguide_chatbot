import pandas as pd
import re

# ---------- CONFIG ----------
CSV_PATH = "/dsl/libbot/data/text_full_libguide.csv"
TEXT_COL = "text"
# ----------------------------

print(f"Reading CSV from: {CSV_PATH}")
df = pd.read_csv(CSV_PATH, encoding='utf-8')

print(f"Original shape: {df.shape}")
print(f"Cleaning column: '{TEXT_COL}'")

# Store original for comparison
original_sample = df[TEXT_COL].iloc[99]

# Clean the text column; had Claude help me find specific formatting issues/cases
def clean_text(text):
    
    text = str(text)
    
    # Replace non-breaking spaces with regular spaces
    text = text.replace('\xa0', ' ')
    
    # Normalize different types of quotes to standard ASCII
    text = text.replace('"', '"').replace('"', '"')  # Smart quotes -> regular
    text = text.replace(''', "'").replace(''', "'")  # Smart apostrophes -> regular
    
    # Normalize different types of dashes
    text = text.replace('—', '-').replace('–', '-')  # Em/en dash -> hyphen
    
    # Normalize line breaks (keep them, just standardize)
    text = text.replace('\r\n', '\n')  # Windows -> Unix
    text = text.replace('\r', '\n')    # Old Mac -> Unix
    
    # Replace multiple spaces with single space (but preserve newlines)
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs -> single space
    
    # Remove leading/trailing whitespace from each line
    text = '\n'.join(line.strip() for line in text.split('\n'))
    
    # Remove multiple consecutive newlines (keep max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Final strip
    text = text.strip()
    
    return text

# Apply cleaning
df[TEXT_COL] = df[TEXT_COL].apply(clean_text)

# Show before/after comparison
print("\n" + "="*60)
print("BEFORE (first 200 chars):")
print(repr(original_sample[:200]))
print("\n" + "="*60)
print("AFTER (first 200 chars):")
print(repr(df[TEXT_COL].iloc[99][:200]))
print("="*60 + "\n")

# Count how many rows were affected
changes = sum(df[TEXT_COL].iloc[i] != original_sample if i == 0 else True for i in range(len(df)))
print(f"Rows processed: {len(df)}")

# Save back to same path
print(f"\nSaving cleaned CSV to: {CSV_PATH}")
df.to_csv(CSV_PATH, index=False, encoding='utf-8')

print("CSV has been cleaned and saved.")
print("\nCleaning operations performed:")
print("  - Replaced non-breaking spaces (\\xa0) with regular spaces")
print("  - Normalized smart quotes to regular ASCII quotes")
print("  - Normalized em/en dashes to hyphens")
print("  - Standardized line breaks to Unix format (\\n)")
print("  - Collapsed multiple spaces into single spaces")
print("  - Removed leading/trailing whitespace from lines")
print("  - Reduced multiple blank lines to max 2")

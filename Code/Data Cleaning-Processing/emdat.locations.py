import re
import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
input_file = project_root / 'data' / 'raw' / 'emdat_data.csv'
output_file = project_root / 'data' / 'processed' / 'states_extracted.csv'

if not input_file.exists():
    raise FileNotFoundError(
        f"EM-DAT input file not found: {input_file}. "
        "See data/README.md for authorized data setup instructions."
    )

df = pd.read_csv(input_file)

# Dictionary: Full name → Abbreviation
state_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
}

# List of full state names (same order as above)
states = list(state_abbrev.keys())

# Function to extract full state names from messy location strings
def extract_states(text):
    found = []
    for state in states:
        if re.search(rf'\b{re.escape(state)}\b', str(text), re.IGNORECASE):
            found.append(state)
    return sorted(set(found), key=lambda x: states.index(x))

# Extract states and convert to abbreviations
states_list = []

for idx, location in df["Location"].items():
    found_states = extract_states(location)
    abbrevs = [state_abbrev[state] for state in found_states]
    states_list.append({
        "ID": (idx + 1),
        "States": ", ".join(abbrevs)
    })

# Create and export final DataFrame
result_df = pd.DataFrame(states_list)
output_file.parent.mkdir(parents=True, exist_ok=True)
result_df.to_csv(output_file, index=False)
print(f"Saved to: {output_file}")

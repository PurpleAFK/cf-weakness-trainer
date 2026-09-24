import json

import pandas as pd

with open("data/raw/2026-09-24_user.status_PurpleAFK.json") as f:
    status = json.load(f)

df = pd.DataFrame(status)
print(df.shape)
print(df["verdict"].value_counts())

# normalize the data cuz it seems like normal json array
df_flat = pd.json_normalize(status)
extracted_df = df_flat[["problem.contestId", "problem.index", "problem.rating"]].copy()

extracted_df = extracted_df.drop_duplicates(
    subset=[
        "problem.contestId",
        "problem.index",
    ]
)


print(extracted_df)
print(extracted_df["problem.rating"].isna().sum())

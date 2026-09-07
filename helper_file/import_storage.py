# import pandas as pd

# file_path = "dataset/rigbuilder_storage.xlsx"

# df = pd.read_excel(file_path)

# print(df.head())

# print("\nColumns:")
# print(df.columns.tolist())

# print("\nData Types:")
# print(df.dtypes)

# print("\nShape:")
# print(df.shape)



import pandas as pd
from app import app, db, Storage

file_path = "dataset/rigbuilder_storage.xlsx"

df = pd.read_excel(file_path)

with app.app_context():

    for _, row in df.iterrows():

        storage = Storage(
            storage_id=row["storage_id"],
            company_brand=row["company_brand"],
            model_name=row["model_name"],
            storage_type=row["storage_type"],
            form_factor=row["form_factor"],
            interface=row["interface"],
            storage_capacity=row["storage_capacity"],
            read_speed_MBs=row["read_speed_MBs"],
            write_speed_MBs=row["write_speed_MBs"],
            heatsink=row["heatsink"],
            dram_cache=row["dram_cache"],
            endurance_tbw=row["endurance_tbw"],
            warranty_period=row["warranty_period"],
            price=row["price"]
        )

        db.session.add(storage)

    db.session.commit()

print(f"{len(df)} Storage records imported successfully!")
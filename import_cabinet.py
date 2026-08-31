# import pandas as pd

# file_path = "dataset/rigbuilder_cabinet.xlsx"
# df = pd.read_excel(file_path)

# df["Price"] = (
#     df[" Price"]
#     .astype(str)
#     .str.replace("₹", "", regex=False)
#     .str.replace("?", "", regex=False)
#     .str.replace(",", "", regex=False)
#     .str.strip()
# )

# df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

# print(df.head())

# print("\nColumns:")
# print(df.columns.tolist())

# print("\nData Types:")
# print(df.dtypes)

# print("\nShape:")
# print(df.shape)




import pandas as pd
from app import app, db, Cabinet

file_path = "dataset/rigbuilder_cabinet.xlsx"

df = pd.read_excel(file_path)

with app.app_context():

    for _, row in df.iterrows():

        cabinet = Cabinet(
            cabinet_id=row["Cabinet ID"],
            brand=row["Brand"],
            cabinet_name=row["Cabinet Name"],
            cabinet_form_factor=row["Cabinet Form Factor"],
            cabinet_build_type=row["Cabinet Build Type"],
            colors_available=row["Colors Available"],
            max_cooler_height=row["Max Cooler Height"],
            max_gpu_length=row["Max GPU Length"],
            cabinet_dimensions=row["Cabinet Dimensions (L x W x H)"],
            motherboard_support=row["Motherboard Support"],
            prebuilt_fans_included=row["Prebuilt Fans Included"],
            max_fans_supported=row["Max Fans Supported"],
            fan_lighting_type=row["Fan Lighting Type"],
            psu_dimension_allowed=row["PSU Dimension Allowed"],
            price=row["Price"]
        )

        db.session.add(cabinet)

    db.session.commit()

print(f"{len(df)} Cabinet records imported successfully!")
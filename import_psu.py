# import pandas as pd

# file_path = "dataset/rigbuilder_psu.xlsx"
# df = pd.read_excel(file_path)

# print(df.head())

# print("\nColumns:")
# print(df.columns.tolist())

# print("\nData Types:")
# print(df.dtypes)

# print("\nShape:")
# print(df.shape)






import pandas as pd
from app import app, db, PSU

file_path = "dataset/rigbuilder_psu.xlsx"

df = pd.read_excel(file_path)

with app.app_context():

    for _, row in df.iterrows():

        psu = PSU(
            psu_id=row["PSU ID"],
            brand_model=row["Brand & Model"],
            modularity=row["Modularity"],
            wattage=row["Wattage (W)"],
            max_output=row["Max Output "],
            certification=row["Certification"],
            atx_pcie_version=row["ATX / PCIe Ver."],
            size_form_factor=row["Size / Form Factor"],
            major_protections=row["Major Protections"],
            recommended_cpu_gpu_pairing=row["Recommended CPU + GPU Pairing"],
            approx_price=row["Approx Price (INR)"]
        )

        db.session.add(psu)

    db.session.commit()

print(f"{len(df)} PSU records imported successfully!")
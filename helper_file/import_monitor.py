# import pandas as pd

# file_path = "dataset/rigbuilder_monitor.xlsx"
# df = pd.read_excel(file_path)

# print(df.head())

# print("\nColumns:")
# print(df.columns.tolist())

# print("\nData Types:")
# print(df.dtypes)

# print("\nShape:")
# print(df.shape)





import pandas as pd
from app import app, db, Monitor

file_path = "dataset/rigbuilder_monitor.xlsx"

df = pd.read_excel(file_path)

with app.app_context():

    for _, row in df.iterrows():

        monitor = Monitor(
            monitor_id=row["Monitor ID"],
            brand_model=row["Brand & Model"],
            resolution=row["Resolution"],
            refresh_rate=row["Refresh Rate"],
            tilt_adjustment=row["Tilt Adjustment"],
            height_adjustment=row["Height Adjustment"],
            vesa_compatibility=row["VESA Compatibility"],
            screen_size=row["Screen Size"],
            response_time=row["Response Time"],
            price=row["Price "]
        )

        db.session.add(monitor)

    db.session.commit()

print(f"{len(df)} Monitor records imported successfully!")
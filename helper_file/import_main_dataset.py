# import pandas as pd

# file_path = "dataset/rigbuilder_main_dataset.xlsx"
# df = pd.read_excel(file_path)

# print(df.head())

# print("\nColumns:")
# print(df.columns.tolist())

# print("\nData Types:")
# print(df.dtypes)

# print("\nShape:")
# print(df.shape)





import pandas as pd

from app import app, db, MainDataset


file_path = "dataset/rigbuilder_main_dataset.xlsx"

df = pd.read_excel(file_path)

# Remove accidental spaces from column names
# df.columns = df.columns.str.strip()


with app.app_context():

    for _, row in df.iterrows():

        main_data = MainDataset(
            budget=row["budget"],
            used_parts=row["used_parts"],
            usage_scenario=row[" usage_scenario"],
            colour_theme=row["colour_theme"],
            monitor_required=row["monitor_required"],
            monitor_size=row["monitor_size"],
            monitor_resolution=row["monitor_resolution"],
            build_type=row["build_type"],
            upgrade_path=row["upgrade_path"],
            cpu=row["cpu"],
            gpu=row["gpu"],
            mobo=row["mobo"],
            cpu_cooler=row["cpu_cooler"],
            psu=row["psu"],
            storage=row["storage"],
            ram=row["ram"],
            cabinet=row["cabinet"],
            monitor=row["monitor"]
        )

        db.session.add(main_data)

    db.session.commit()

    print(f"{len(df)} Main Dataset records imported successfully!")
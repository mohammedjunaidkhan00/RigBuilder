import pandas as pd
from app import app, db, CPUCooler

file_path = "dataset/rigbuilder_cpu_cooler.xlsx"

df = pd.read_excel(file_path)

with app.app_context():

    # Existing cooler records remove
    CPUCooler.query.delete()
    db.session.commit()

    for _, row in df.iterrows():

        cooler = CPUCooler(
            cooler_id=row["Cooler ID"],
            cooler_brand=row["Cooler Brand"],
            cooler_name=row["Cooler Name"],
            cooler_type=row["Cooler Type"],
            cooler_height=row["Cooler Height"],
            fan_max_rpm=row["Fan Max RPM"],
            max_rated_tdp=row["Max Rated TDP"],
            aio_length=row["AIO Length"],
            fans_included=row["Fans Included"],
            lighting_type=row["Lighting Type"],
            aio_cooler_display=row["AIO/Cooler Display"],
            compatible_socket=row["Compatible Socket "],
            price=row[" Price"]
        )

        db.session.add(cooler)

    db.session.commit()

print(f"{len(df)} CPU Cooler records imported successfully!")
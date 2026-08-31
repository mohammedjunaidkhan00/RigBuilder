import pandas as pd
from app import app, db, RAM

file_path = "dataset/rigbuilder_ram.xlsx"

df = pd.read_excel(file_path)

with app.app_context():

    for _, row in df.iterrows():

        ram = RAM(
            ram_id=row["ram_id"],
            company_brand=row["company_brand"],
            model_name=row["model_name"],
            ram_generation=row["ram_generation"],
            capacity=row["capacity"],
            kit_configuration=row["kit_configuration"],
            base_frequency_mhz=row["base_frequency_mhz"],
            boost_frequency_mhz=row["boost_frequency_mhz"],
            cas_latency_cl=row["cas_latency_cl"],
            mobo_socket_compatibility=row["mobo_socket_compatibility"],
            overclock_profile=row["overclock_profile"],
            heatsink_available=row["heatsink_available"],
            rgb_lighting=row["rgb_lighting"],
            module_height_mm=row["module_height_mm"],
            approx_price=row["approx_price"],
            good_for_use_case=row["good_for_use_case"]
        )

        db.session.add(ram)

    db.session.commit()

print(f"{len(df)} RAM records imported successfully!")






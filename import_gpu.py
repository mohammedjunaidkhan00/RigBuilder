import pandas as pd
from app import app, db, GPU

file_path = "dataset/rigbuilder_gpu.xlsx"

df = pd.read_excel(file_path)

with app.app_context():

    # Import fresh data
    for _, row in df.iterrows():

        gpu = GPU(
            gpu_id=row["gpu id"],
            gpu_name=row["gpu name"],
            cuda_cores=row["cuda cores "],
            gpu_tdp=row["gpu tdp"],
            tensor_cores=row["tensor cores "],
            rt_cores=row["rt cores"],
            vram=row[" vram"],
            memory_bus=row["Memory Bus"],
            manufacturer_name=row["manufacturer name  "],
            brand=row["brand"],
            gpu_length=row["gpu length"],
            gpu_width=row["gpu width "],
            psu_required=row["psu required"],
            power_cable=row["power cable"],
            psu_type=row["psu type "],
            pcie_version=row["pcie version"],
            gpu_cooler=row["gpu cooler"],
            gpu_price=row["gpu price "],
            gpu_tier=row["gpu tier "]
        )

        db.session.add(gpu)

    db.session.commit()

print(f"{len(df)} GPU records imported successfully!")
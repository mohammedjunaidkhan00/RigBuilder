import pandas as pd

from app import app, db, CPU


file_path = "dataset/rigbuilder_cpu.xlsx"

df = pd.read_excel(file_path)


with app.app_context():

    for _, row in df.iterrows():

        cpu = CPU(
            cpu_id=row["cpu_id"],
            cpu_model=row["cpu_model"],
            manufacturer=row["manufacturer"],
            socket_no=row["socket_no"],
            compatible_socket=row["compatible_socket"],
            cores=row["cores"],
            thread=row["thread"],
            base_clock=row["base_clock"],
            boost_clock=row["boost_clock"],
            chache_memory=row["chache_memory"],
            tdp_wattage=row["tdp_wattage"],
            ram_support=row["ram_support"],
            integrated_gpu=row["integrated_gpu"],
            integrated_gpu_name=row["integrated_gpu_name"],
            cooler_recommended=row["cooler_recommended"],
            cpu_tier=row["cpu_tier"],
            price=row["price"]
        )

        db.session.add(cpu)

    db.session.commit()

    print(f"{len(df)} CPU records imported successfully!")
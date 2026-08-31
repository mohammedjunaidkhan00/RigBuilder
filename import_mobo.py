import pandas as pd
from app import app, db, Motherboard

file_path = "dataset/rigbuilder_mobo.xlsx"

df = pd.read_excel(file_path)

with app.app_context():

    # Existing motherboard records remove
    Motherboard.query.delete()
    db.session.commit()

    for _, row in df.iterrows():

        motherboard = Motherboard(
            model_id=row["model_id"],
            motherboard_name=row["motherboard_name"],
            socket_no=row["socket_no"],
            chipset=row["chipset"],
            pcie_version=row["pcie_version"],
            vrm_count=row["vrm_count"],
            vrm_amperage=row["vrm_amperage"],
            wireless_connectivity=row["wireless_connectivity"],
            ram_type=row["ram_type"],
            form_factor=row["form_factor"],
            price=row["price"]
        )

        db.session.add(motherboard)

    db.session.commit()

print(f"{len(df)} Motherboard records imported successfully!")
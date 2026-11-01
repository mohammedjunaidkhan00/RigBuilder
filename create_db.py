from app import app, db

import os
import pandas as pd
from app import app, db, CPU, GPU, Motherboard, CPUCooler, PSU, Storage, RAM, Cabinet, Monitor



# with app.app_context():
#     db.create_all()

# print("DB done")


 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
 
 
# with app.app_context():
 
#     # STEP 1: SAARI PURANI COMPONENT TABLES KHAALI KARO
#     print("Clearing old component tables...")
 
#     CPU.query.delete()
#     GPU.query.delete()
#     Motherboard.query.delete()
#     CPUCooler.query.delete()
#     PSU.query.delete()
#     Storage.query.delete()
#     RAM.query.delete()
#     Cabinet.query.delete()
#     Monitor.query.delete()
 
#     db.session.commit()
#     print("Old data cleared.\n")













BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")


with app.app_context():

    # STEP 2: CPU

    cpu_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_cpu.xlsx"))
    cpu_df.columns = cpu_df.columns.str.strip()
    cpu_df['cpu_id'] = cpu_df['cpu_id'].astype(str).str.strip()
    cpu_df['socket_no'] = cpu_df['socket_no'].astype(str).str.strip()
    
    cpu_df['price'] = pd.to_numeric(cpu_df['price'], errors='coerce')
    cpu_df = cpu_df.dropna(subset=['price'])
    cpu_df.reset_index(drop=True, inplace=True)
    
    # cores column se sirf number nikaalo (jaise "24 (8P+16E)" -> 24)
    cpu_df['cores'] = cpu_df['cores'].astype(str).str.extract(r'(\d+)')[0].astype(float)
    
    # print("CPU rows after cleaning:", cpu_df.shape)
    
    for _, row in cpu_df.iterrows():
        db.session.add(CPU(
            cpu_id=row["cpu_id"],
            cpu_model=row.get("cpu_model"),
            manufacturer=row.get("manufacturer"),
            socket_no=row.get("socket_no"),
            compatible_socket=row.get("compatible_socket"),
            cores=row.get("cores"),
            thread=row.get("thread"),
            base_clock=row.get("base_clock"),
            boost_clock=row.get("boost_clock"),
            chache_memory=row.get("chache_memory"),
            tdp_wattage=str(row.get("tdp_wattage")),
            ram_support=row.get("ram_support"),
            integrated_gpu=row.get("integrated_gpu"),
            integrated_gpu_name=row.get("integrated_gpu_name"),
            cooler_recommended=row.get("cooler_recommended"),
            cpu_tier=row.get("cpu_tier"),
            price=row.get("price"),
        ))
    db.session.commit()
    print(f"1 CPU table seeded. Rows: {len(cpu_df)}")
    

    # ============================================
    # STEP 3: Motherboard
    # ============================================
    mobo_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_mobo.xlsx"))
    mobo_df.columns = mobo_df.columns.str.strip()
    mobo_df['model_id'] = mobo_df['model_id'].astype(str).str.strip()
    mobo_df['socket_no'] = mobo_df['socket_no'].astype(str).str.strip()

    for _, row in mobo_df.iterrows():
        db.session.add(Motherboard(
            model_id=row["model_id"],
            motherboard_name=row.get("motherboard_name"),
            socket_no=row.get("socket_no"),
            chipset=row.get("chipset"),
            pcie_version=row.get("pcie_version"),
            vrm_count=str(row.get("vrm_count")),
            vrm_amperage=str(row.get("vrm_amperage")),
            wireless_connectivity=row.get("wireless_connectivity"),
            ram_type=row.get("ram_type"),
            form_factor=row.get("form_factor"),
            price=row.get("price"),
        ))
    db.session.commit()
    print(f"2 Motherboard table seeded. Rows: {len(mobo_df)}")


    # ============================================
    # STEP 4: GPU
    # ============================================
    gpu_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_gpu.xlsx"))
    gpu_df.columns = gpu_df.columns.str.strip()
    gpu_df['gpu id'] = gpu_df['gpu id'].astype(str).str.strip()

    for _, row in gpu_df.iterrows():
        db.session.add(GPU(
            gpu_id=row["gpu id"],
            gpu_name=str(row.get("gpu name")),
            cuda_cores=row.get("cuda cores"),
            gpu_tdp=str(row.get("gpu tdp")),
            tensor_cores=row.get("tensor cores"),
            rt_cores=row.get("rt cores"),
            vram=str(row.get("vram")),
            memory_bus=str(row.get("Memory Bus")),
            manufacturer_name=str(row.get("manufacturer name")),
            brand=str(row.get("brand")),
            gpu_length=str(row.get("gpu length")),
            gpu_width=str(row.get("gpu width")),
            psu_required=str(row.get("psu required")),
            power_cable=str(row.get("power cable")),
            psu_type=str(row.get("psu type")),
            pcie_version=str(row.get("pcie version")),
            gpu_cooler=str(row.get("gpu cooler")),
            gpu_price=row.get("gpu price"),
            gpu_tier=row.get("gpu tier"),
        ))

    db.session.commit()
    print(f"3 GPU table seeded. Rows: {len(gpu_df)}")



    # ============================================
    # STEP 5: CPU Cooler
    # ============================================
    cooler_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_cpu_cooler.xlsx"))
    cooler_df.columns = cooler_df.columns.str.strip()
    cooler_df['Cooler ID'] = cooler_df['Cooler ID'].astype(str).str.strip()

    for _, row in cooler_df.iterrows():
        db.session.add(CPUCooler(
            cooler_id=row["Cooler ID"],
            cooler_brand=str(row.get("Cooler Brand")),
            cooler_name=str(row.get("Cooler Name")),
            cooler_type=str(row.get("Cooler Type")),
            cooler_height=str(row.get("Cooler Height")),
            fan_max_rpm=str(row.get("Fan Max RPM")),
            max_rated_tdp=str(row.get("Max Rated TDP")),
            aio_length=str(row.get("AIO Length")),
            fans_included=str(row.get("Fans Included")),
            lighting_type=str(row.get("Lighting Type")),
            aio_cooler_display=str(row.get("AIO/Cooler Display")),
            compatible_socket=str(row.get("Compatible Socket")),
            price=row.get("Price"),
        ))

    db.session.commit()
    print(f"4 CPU Cooler table seeded. Rows: {len(cooler_df)}")


    # ============================================
    # STEP 6: PSU
    # ============================================
    psu_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_psu.xlsx"))
    psu_df.columns = psu_df.columns.str.strip()
    psu_df['PSU ID'] = psu_df['PSU ID'].astype(str).str.strip()

    for _, row in psu_df.iterrows():
        db.session.add(PSU(
            psu_id=row["PSU ID"],
            brand_model=row.get("Brand & Model"),
            modularity=row.get("Modularity"),
            wattage=row.get("Wattage (W)"),
            max_output=row.get("Max Output"),
            certification=row.get("Certification"),
            atx_pcie_version=row.get("ATX / PCIe Ver."),
            size_form_factor=row.get("Size / Form Factor"),
            major_protections=row.get("Major Protections"),
            recommended_cpu_gpu_pairing=row.get("Recommended CPU + GPU Pairing"),
            approx_price=row.get("Approx Price (INR)"),
        ))

    db.session.commit()
    print(f"5 PSU table seeded. Rows: {len(psu_df)}")


        # ============================================
    # STEP 7: Storage
    # ============================================
    storage_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_storage.xlsx"))
    storage_df.columns = storage_df.columns.str.strip()
    storage_df['storage_id'] = storage_df['storage_id'].astype(str).str.strip()

    for _, row in storage_df.iterrows():
        db.session.add(Storage(
            storage_id=row["storage_id"],
            company_brand=str(row.get("company_brand")),
            model_name=str(row.get("model_name")),
            storage_type=str(row.get("storage_type")),
            form_factor=str(row.get("form_factor")),
            interface=str(row.get("interface")),
            storage_capacity=str(row.get("storage_capacity")),
            read_speed_MBs=row.get("read_speed_MBs"),
            write_speed_MBs=row.get("write_speed_MBs"),
            heatsink=str(row.get("heatsink")),
            dram_cache=str(row.get("dram_cache")),
            endurance_tbw=str(row.get("endurance_tbw")),
            warranty_period=str(row.get("warranty_period")),
            price=row.get("price"),
        ))

    db.session.commit()
    print(f"6 Storage table seeded. Rows: {len(storage_df)}")


    # ============================================
    # STEP 8: RAM
    # ============================================
    ram_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_ram.xlsx"))
    ram_df.columns = ram_df.columns.str.strip()
    ram_df['ram_id'] = ram_df['ram_id'].astype(str).str.strip()

    for _, row in ram_df.iterrows():
        db.session.add(RAM(
            ram_id=row["ram_id"],
            company_brand=row.get("company_brand"),
            model_name=row.get("model_name"),
            ram_generation=row.get("ram_generation"),
            capacity=row.get("capacity"),
            kit_configuration=row.get("kit_configuration"),
            base_frequency_mhz=row.get("base_frequency_mhz"),
            boost_frequency_mhz=row.get("boost_frequency_mhz"),
            cas_latency_cl=row.get("cas_latency_cl"),
            mobo_socket_compatibility=row.get("mobo_socket_compatibility"),
            overclock_profile=row.get("overclock_profile"),
            heatsink_available=row.get("heatsink_available"),
            rgb_lighting=row.get("rgb_lighting"),
            module_height_mm=row.get("module_height_mm"),
            approx_price=row.get("approx_price"),
            good_for_use_case=row.get("good_for_use_case"),
        ))

    db.session.commit()
    print(f"7 RAM table seeded. Rows: {len(ram_df)}")


    # ============================================
    # STEP 9: Cabinet
    # ============================================
    cabinet_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_cabinet.xlsx"))
    cabinet_df.columns = cabinet_df.columns.str.strip()
    cabinet_df['Cabinet ID'] = cabinet_df['Cabinet ID'].astype(str).str.strip()

    for _, row in cabinet_df.iterrows():
        db.session.add(Cabinet(
            cabinet_id=row["Cabinet ID"],
            brand=row.get("Brand"),
            cabinet_name=row.get("Cabinet Name"),
            cabinet_form_factor=row.get("Cabinet Form Factor"),
            cabinet_build_type=row.get("Cabinet Build Type"),
            colors_available=row.get("Colors Available"),
            max_cooler_height=str(row.get("Max Cooler Height")),
            max_gpu_length=str(row.get("Max GPU Length")),
            cabinet_dimensions=row.get("Cabinet Dimensions (L x W x H)"),
            motherboard_support=row.get("Motherboard Support"),
            prebuilt_fans_included=row.get("Prebuilt Fans Included"),
            max_fans_supported=str(row.get("Max Fans Supported")),
            fan_lighting_type=row.get("Fan Lighting Type"),
            psu_dimension_allowed=str(row.get("PSU Dimension Allowed")),
            price=row.get("Price"),
        ))
    db.session.commit()
    print(f"8 Cabinet table seeded. Rows: {len(cabinet_df)}")


    # ============================================
    # STEP 10: Monitor
    # ============================================
    monitor_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_monitor.xlsx"))
    monitor_df.columns = monitor_df.columns.str.strip()
    monitor_df['Monitor ID'] = monitor_df['Monitor ID'].astype(str).str.strip()

    for _, row in monitor_df.iterrows():
        db.session.add(Monitor(
            monitor_id=row["Monitor ID"],
            brand_model=row.get("Brand & Model"),
            resolution=row.get("Resolution"),
            refresh_rate=row.get("Refresh Rate"),
            tilt_adjustment=row.get("Tilt Adjustment"),
            height_adjustment=row.get("Height Adjustment"),
            vesa_compatibility=row.get("VESA Compatibility"),
            screen_size=row.get("Screen Size"),
            response_time=row.get("Response Time"),
            price=row.get("Approx Price"),
        ))
    db.session.commit()
    print(f"9 Monitor table seeded. Rows: {len(monitor_df)}")

    print("\n✅ All tables cleared and reseeded successfully!")
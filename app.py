from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from huggingface_hub import hf_hub_download
import os
import joblib
import re
import numpy as np
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# Hugging Face repository
HF_REPO_ID = "mohammedjunaidkhan/rigbuilder-models"


# Download models from Hugging Face
cat_model_path = hf_hub_download(repo_id=HF_REPO_ID, filename="cat_model.pkl")

# Load ML models
cat_model = joblib.load(cat_model_path)
# random_forest_model = joblib.load(random_forest_model_path)


# LOAD PREPROCESSING FILES
feature_columns = joblib.load(os.path.join(MODEL_DIR, "feature_columns.pkl"))
target_encoders = joblib.load(os.path.join(MODEL_DIR, "target_encoders.pkl"))
ohe = joblib.load(os.path.join(MODEL_DIR, "ohe.pkl"))

# LOAD DATASETS
cpu_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_cpu.xlsx"))
gpu_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_gpu.xlsx"))
mobo_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_mobo.xlsx"))
cooler_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_cpu_cooler.xlsx"))
psu_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_psu.xlsx"))
storage_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_storage.xlsx"))
ram_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_ram.xlsx"))
cabinet_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_cabinet.xlsx"))
monitor_df = pd.read_excel(os.path.join(DATASET_DIR, "rigbuilder_monitor.xlsx"))

datasets = [cpu_df, gpu_df, mobo_df, cooler_df, psu_df, storage_df, ram_df, cabinet_df, monitor_df]
for df in datasets:df.columns = df.columns.str.strip()


# RAM type format fix (DDR-4 -> DDR4)
mobo_df['ram_type'] = mobo_df['ram_type'].replace({
    'DDR-3': 'DDR3', 'DDR-4': 'DDR4', 'DDR-5': 'DDR5'})

# Socket format consistent karo (space hatao, uppercase)
mobo_df['socket_no'] = mobo_df['socket_no'].astype(str).str.replace(' ', '', regex=False).str.upper()
cpu_df['socket_no'] = cpu_df['socket_no'].astype(str).str.replace(' ', '', regex=False).str.upper()
ram_df['mobo_socket_compatibility'] = ram_df['mobo_socket_compatibility'].astype(str).str.replace(' ', '', regex=False).str.upper()
cooler_df['Compatible Socket'] = cooler_df['Compatible Socket'].astype(str).str.replace(' ', '', regex=False).str.upper()

# ID columns se whitespace hatao (component lookup ke liye)
cpu_df['cpu_id'] = cpu_df['cpu_id'].astype(str).str.strip()
gpu_df['gpu id'] = gpu_df['gpu id'].astype(str).str.strip()
mobo_df['model_id'] = mobo_df['model_id'].astype(str).str.strip()
cooler_df['Cooler ID'] = cooler_df['Cooler ID'].astype(str).str.strip()
psu_df['PSU ID'] = psu_df['PSU ID'].astype(str).str.strip()
storage_df['storage_id'] = storage_df['storage_id'].astype(str).str.strip()
ram_df['ram_id'] = ram_df['ram_id'].astype(str).str.strip()
cabinet_df['Cabinet ID'] = cabinet_df['Cabinet ID'].astype(str).str.strip()
monitor_df['Monitor ID'] = monitor_df['Monitor ID'].astype(str).str.strip()


categorical_cols = ["usage_scenario", "colour_theme", "monitor_resolution","upgrade_path"]


# Component ID columns
components_id_col_name = {
    "CPU": "cpu_id",
    "GPU": "gpu id",
    "Mother Board": "model_id",
    "Cooler": "Cooler ID",
    "PSU": "PSU ID",
    "Storage": "storage_id",
    "RAM": "ram_id",
    "Cabinet": "Cabinet ID",
    "Monitor": "Monitor ID"}

# Target columns
target_columns = [
    "cpu",
    "gpu",
    "mobo",
    "cpu_cooler",
    "psu",
    "storage",
    "ram",
    "cabinet",
    "monitor"]

# Price columns
price_columns = {
    "GPU": "gpu price",
    "Mother Board": "price",
    "Cooler": "Price",
    "PSU": "Approx Price (INR)",
    "Storage": "price",
    "RAM": "approx_price",
    "Cabinet": "Price",
    "Monitor": "Price",}

# Component DataFrames
component_dataframes = {
    "CPU": cpu_df,
    "GPU": gpu_df,
    "Mother Board": mobo_df,
    "Cooler": cooler_df,
    "PSU": psu_df,
    "Storage": storage_df,
    "RAM": ram_df,
    "Cabinet": cabinet_df,
    "Monitor": monitor_df}




### **1. User input preprocessing**
def preprocess_user_input(budget,
                        used_parts,
                        usage_scenario,
                        colour_theme,
                        monitor_required,
                        monitor_size,
                        monitor_resolution,
                        # build_type,
                        upgrade_path):

    user_input = pd.DataFrame([{
        "budget": budget,
        "used_parts": used_parts,
        "usage_scenario": usage_scenario,
        "colour_theme": colour_theme,
        "monitor_required": monitor_required,
        "monitor_size": monitor_size,
        "monitor_resolution": monitor_resolution,
        # "build_type": build_type,
        "upgrade_path": upgrade_path}])

    encoded_data = ohe.transform(
        user_input[categorical_cols])

    encoded_df = pd.DataFrame(
        encoded_data,
        columns=ohe.get_feature_names_out(categorical_cols))

    user_input = user_input.drop(columns=categorical_cols)

    user_input = pd.concat([user_input, encoded_df], axis=1)

    return user_input



 ### **compatibility Text**
def get_compatible_chipsets(compatible_socket):
    if pd.isna(compatible_socket):return []
    return re.findall(r'\b[A-Z]\d{3}\b', str(compatible_socket))


def check_cpu_mobo(cpu, mobo):
    cpu_socket = str(cpu["socket_no"]).strip().upper()
    mobo_socket = str(mobo["socket_no"]).strip().upper()

    # Sirf socket match karo — compatible_socket column corrupt hai (Excel references leak hue hain)
    return cpu_socket == mobo_socket


def check_ram_mobo(ram, mobo):

    ram_generation = str(ram["ram_generation"]).strip().upper()

    mobo_ram_type = str(mobo["ram_type"]).strip().upper()

    ram_compatible_sockets = [
        socket.strip().upper()
        for socket in str(ram["mobo_socket_compatibility"]).split("/")]

    mobo_socket = str(mobo["socket_no"]).strip().upper()

    if ram_generation != mobo_ram_type:
        return False

    if mobo_socket not in ram_compatible_sockets:
        return False

    return True


def check_gpu_psu(gpu, psu):
    gpu_required = int(str(gpu["psu required"]).replace("W", "").strip())
    psu_wattage = float(psu["Wattage (W)"])
    return psu_wattage >= gpu_required


def check_gpu_cabinet(gpu, cabinet):

    gpu_length = float(str(gpu["gpu length"]).replace("mm", "").strip())
    max_gpu_length = float(str(cabinet["Max GPU Length"]).replace("mm", "").strip())

    return gpu_length <= max_gpu_length


def get_watt(value):
    match = re.search(r'\d+(\.\d+)?', str(value))
    if match:
        return float(match.group())
    return float('inf')


def check_cpu_cooler(cpu, cooler):

    cpu_socket = str(cpu["socket_no"]).strip().upper()

    compatible_sockets = [
        socket.strip().upper()
        for socket in str(cooler["Compatible Socket"]).split(",")]

    cpu_tdp = get_watt(cpu["tdp_wattage"])
    cooler_tdp = get_watt(cooler["Max Rated TDP"])
    socket_ok = (cpu_socket in compatible_sockets)
    tdp_ok = (cpu_tdp <= cooler_tdp)
    return socket_ok and tdp_ok


def get_mm(value):
    match = re.search(r'\d+(\.\d+)?', str(value))
    if match:
        return float(match.group())
    return None


def check_cooler_cabinet(cooler, cabinet):

    cooler_height = get_mm(cooler["Cooler Height"])
    max_cooler_height = get_mm(cabinet["Max Cooler Height"])
    return cooler_height <= max_cooler_height

 


### **check compatibility**
#new
def check_compatibility(build):

    results = {
        "CPU ↔ Motherboard": check_cpu_mobo(build["CPU"], build["Mother Board"]),
        "RAM ↔ Motherboard": check_ram_mobo(build["RAM"], build["Mother Board"]),
        "GPU ↔ PSU": check_gpu_psu(build["GPU"], build["PSU"]),
        "GPU ↔ Cabinet": check_gpu_cabinet(build["GPU"], build["Cabinet"]),
        "CPU ↔ Cooler": check_cpu_cooler(build["CPU"], build["Cooler"]),
        "Cooler ↔ Cabinet": check_cooler_cabinet(build["Cooler"], build["Cabinet"])}

    return results

#new
def is_build_compatible(compatibility_results):
    return all(compatibility_results.values())




### **Find Compatible Component**
# new
def find_compatible_mobos(cpu, mobo_df):
    compatible = []
    for _, mobo in mobo_df.iterrows():
        if check_cpu_mobo(cpu, mobo):
            compatible.append(mobo)
    return compatible


def find_compatible_rams(mobo, ram_df):
    compatible = []
    for _, ram in ram_df.iterrows():
        if check_ram_mobo(ram, mobo):
            compatible.append(ram)
    return compatible


def find_compatible_coolers(cpu, cooler_df):
    compatible = []
    for _, cooler in cooler_df.iterrows():
        if check_cpu_cooler(cpu, cooler):
            compatible.append(cooler)
    return compatible


def find_compatible_psus(gpu, psu_df):
    compatible = []
    for _, psu in psu_df.iterrows():
        if check_gpu_psu(gpu, psu):
            compatible.append(psu)
    return compatible


def find_compatible_cabinets(gpu, cooler, cabinet_df):
    compatible = []
    for _, cabinet in cabinet_df.iterrows():
        if check_gpu_cabinet(gpu, cabinet) and check_cooler_cabinet(cooler, cabinet):
            compatible.append(cabinet)
    return compatible


def pick_closest_by_price(candidates, target_price, price_col):
    if not candidates:
        return None

    def price_diff(item):
        price = pd.to_numeric(item[price_col], errors="coerce")
        if pd.isna(price):
            return float("inf")
        return abs(price - target_price)

    return min(candidates, key=price_diff)


### **Resolve Compatible Build**
def resolve_compatible_build(cpu, gpu, budget, component_dataframes, price_columns):
    build = {"CPU": cpu, "GPU": gpu}

    mobo_candidates = find_compatible_mobos(cpu, component_dataframes["Mother Board"])
    if not mobo_candidates:
        raise ValueError(f"No compatible motherboard found for CPU {cpu.get('cpu_id')}")

    # Motherboards ko price-closeness ke hisaab se sort karo
    target_mobo_price = budget * 0.15
    mobo_candidates.sort(
        key=lambda m: abs(pd.to_numeric(m[price_columns["Mother Board"]], errors="coerce") - target_mobo_price)
        if pd.notna(pd.to_numeric(m[price_columns["Mother Board"]], errors="coerce")) else float("inf"))

    # Har motherboard try karo jab tak RAM na mile
    selected_mobo = None
    selected_ram = None
    for mobo in mobo_candidates:
        ram_candidates = find_compatible_rams(mobo, component_dataframes["RAM"])
        if ram_candidates:
            selected_mobo = mobo
            selected_ram = pick_closest_by_price(ram_candidates, budget * 0.1, price_columns["RAM"])
            break

    if selected_mobo is None:
        raise ValueError("Koi bhi compatible motherboard RAM ke saath nahi mila")

    build["Mother Board"] = selected_mobo
    build["RAM"] = selected_ram

    # Cooler
    cooler_candidates = find_compatible_coolers(cpu, component_dataframes["Cooler"])
    if not cooler_candidates:
        raise ValueError("No compatible cooler found for CPU")
    build["Cooler"] = pick_closest_by_price(cooler_candidates, budget * 0.05, price_columns["Cooler"])

    # PSU
    psu_candidates = find_compatible_psus(gpu, component_dataframes["PSU"])
    if not psu_candidates:
        raise ValueError("No compatible PSU found for GPU")
    build["PSU"] = pick_closest_by_price(psu_candidates, budget * 0.1, price_columns["PSU"])

    # Cabinet
    cabinet_candidates = find_compatible_cabinets(gpu, build["Cooler"], component_dataframes["Cabinet"])
    if not cabinet_candidates:
        raise ValueError("No compatible cabinet found for GPU + Cooler combo")
    build["Cabinet"] = pick_closest_by_price(cabinet_candidates, budget * 0.05, price_columns["Cabinet"])

    return build




### **Get Compatibility Summary**
def get_compatibility_summary(compatibility_results):

    issues = [component for component, result in compatibility_results.items() if not result]

    return {"is_compatible": len(issues) == 0,
            "issues": issues}


### **2. Model prediction**
def predict_components(user_input, model):
    prediction = model.predict(user_input)
    prediction = np.squeeze(prediction)
    return prediction


### **3. Encoded predictions ko actual IDs mein decode karna**
def decode_predictions(prediction):
    decoded_prediction = {}
    for col, encoded_value in zip(target_columns, prediction):
        decoded_value = target_encoders[col].inverse_transform([encoded_value])[0]
        decoded_prediction[col] = decoded_value
    return decoded_prediction


### **4. Actual component lookup**
def get_component(df, column_name, component_id):
    result = df[df[column_name] == component_id]
    if result.empty:
        raise ValueError(f"Component {component_id} not found in column {column_name}")
    return result.iloc[0]



def get_component_details(decoded_prediction):
    build = {}

    for component_name, df in component_dataframes.items():

        target_column = {
            "CPU": "cpu",
            "GPU": "gpu",
            "Mother Board": "mobo",
            "Cooler": "cpu_cooler",
            "PSU": "psu",
            "Storage": "storage",
            "RAM": "ram",
            "Cabinet": "cabinet",
            "Monitor": "monitor"}[component_name]

        component_id = decoded_prediction[target_column]

        id_column = components_id_col_name[
            component_name]

        build[component_name] = get_component(
            df,
            id_column,
            component_id)
    return build


### **5. Price calculation**
def calculate_build_price(build):

    price_columns = {
        "CPU": "price",
        "GPU": "gpu price",
        "Mother Board": "price",
        "Cooler": "Price",
        "PSU": "Approx Price (INR)",
        "Storage": "price",
        "RAM": "approx_price",
        "Cabinet": "Price",
        "Monitor": "Approx Price"}

    total = 0

    for component, item in build.items():

        price_column = price_columns[component]

        price = pd.to_numeric(
            item[price_column],
            errors="coerce")

        if pd.notna(price):
            total += price
    return total


### **6. Final recommendation function**
def recommend_pc(
    budget,
    used_parts,
    usage_scenario,
    colour_theme,
    monitor_required,
    monitor_size,
    monitor_resolution,
    upgrade_path,
    model):

    # 1. Prepare user input
    user_input = preprocess_user_input(
        budget,
        used_parts,
        usage_scenario,
        colour_theme,
        monitor_required,
        monitor_size,
        monitor_resolution,
        upgrade_path)


    # 2. Predict component classes
    prediction = predict_components(user_input, model)


    # 3. Decode classes → component IDs
    decoded_prediction = decode_predictions(prediction)


    # 4. Component IDs → actual component rows
    # build = get_component_details(decoded_prediction)
    # new
        # 4. CPU & GPU seedha ML prediction se lo (anchors)
    cpu = get_component(cpu_df, "cpu_id", decoded_prediction["cpu"])
    gpu = get_component(gpu_df, "gpu id", decoded_prediction["gpu"])

    # 4a. Baaki components resolver se guaranteed-compatible milenge
    build = resolve_compatible_build(cpu, gpu, budget, component_dataframes, price_columns)

    # 4b. Storage/Monitor pe hard compatibility rule nahi hai, ML se hi lo
    # 4b. Storage pe hard compatibility rule nahi hai, ML se hi lo
    build["Storage"] = get_component(storage_df, "storage_id", decoded_prediction["storage"])

    # Monitor sirf tab lo jab user ko monitor chahiye ho
    if monitor_required == 1:
        build["Monitor"] = get_component(monitor_df, "Monitor ID", decoded_prediction["monitor"])
    else:build["Monitor"] = None


    # 6. Compatibility validation
    compatibility = check_compatibility(build)
    build_compatible = is_build_compatible(compatibility) #new

    summary = get_compatibility_summary(compatibility) #new

    # 5. Calculate total price
    total_price = calculate_build_price(build)

    return {
        "components": build,
        "total_price": total_price,
        "compatibility": compatibility,
        "build_compatible": build_compatible, #new
        "issues": summary["issues"] #new
}





app = Flask(__name__)
app.secret_key = "rigbuilder-secret-key"



# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///rigbuilder.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create database object
db = SQLAlchemy(app)


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class CPU(db.Model):

    cpu_id = db.Column(db.String(50), primary_key=True)
    cpu_model = db.Column(db.String(150), nullable=False)
    manufacturer = db.Column(db.String(50))
    socket_no = db.Column(db.String(50))
    compatible_socket = db.Column(db.String(100))
    cores = db.Column(db.Integer)
    thread = db.Column(db.Integer)
    base_clock = db.Column(db.Float)
    boost_clock = db.Column(db.Float)
    chache_memory = db.Column(db.String(50))
    tdp_wattage = db.Column(db.String(50))
    ram_support = db.Column(db.String(100))
    integrated_gpu = db.Column(db.String(20))
    integrated_gpu_name = db.Column(db.String(100))
    cooler_recommended = db.Column(db.String(100))
    cpu_tier = db.Column(db.String(50))
    price = db.Column(db.Float)



class GPU(db.Model):
    __tablename__ = "gpu"

    id = db.Column(db.Integer, primary_key=True)

    gpu_id = db.Column(db.String(50), unique=True, nullable=False)
    gpu_name = db.Column(db.String(100), nullable=False)
    cuda_cores = db.Column(db.Integer)
    gpu_tdp = db.Column(db.String(50))
    tensor_cores = db.Column(db.Integer)
    rt_cores = db.Column(db.Integer)
    vram = db.Column(db.String(50))
    memory_bus = db.Column(db.String(50))
    manufacturer_name = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    gpu_length = db.Column(db.String(50))
    gpu_width = db.Column(db.String(50))
    psu_required = db.Column(db.String(50))
    power_cable = db.Column(db.String(100))
    psu_type = db.Column(db.String(100))
    pcie_version = db.Column(db.String(50))
    gpu_cooler = db.Column(db.String(100))
    gpu_price = db.Column(db.Integer)
    gpu_tier = db.Column(db.Integer)



class CPUCooler(db.Model):
    __tablename__ = "cpu_cooler"

    id = db.Column(db.Integer, primary_key=True)

    cooler_id = db.Column(db.String(50), unique=True, nullable=False)
    cooler_brand = db.Column(db.String(100))
    cooler_name = db.Column(db.String(150))
    cooler_type = db.Column(db.String(100))
    cooler_height = db.Column(db.String(50))
    fan_max_rpm = db.Column(db.String(50))
    max_rated_tdp = db.Column(db.String(50))
    aio_length = db.Column(db.String(50))
    fans_included = db.Column(db.String(50))
    lighting_type = db.Column(db.String(100))
    aio_cooler_display = db.Column(db.String(100))
    compatible_socket = db.Column(db.String(200))
    price = db.Column(db.Integer)



class Motherboard(db.Model):
    __tablename__ = "motherboard"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.String(50), unique=True, nullable=False)
    motherboard_name = db.Column(db.String(150))
    socket_no = db.Column(db.String(50))
    chipset = db.Column(db.String(100))
    pcie_version = db.Column(db.String(50))
    vrm_count = db.Column(db.String(50))
    vrm_amperage = db.Column(db.String(50))
    wireless_connectivity = db.Column(db.String(20))
    ram_type = db.Column(db.String(50))
    form_factor = db.Column(db.String(50))
    price = db.Column(db.Integer)




class RAM(db.Model):
    __tablename__ = "ram"

    id = db.Column(db.Integer, primary_key=True)
    ram_id = db.Column(db.String(20), unique=True, nullable=False)
    company_brand = db.Column(db.String(100))
    model_name = db.Column(db.String(100))
    ram_generation = db.Column(db.String(50))
    capacity = db.Column(db.String(50))
    kit_configuration = db.Column(db.String(100))
    base_frequency_mhz = db.Column(db.Integer)
    boost_frequency_mhz = db.Column(db.Integer)
    cas_latency_cl = db.Column(db.String(50))
    mobo_socket_compatibility = db.Column(db.String(200))
    overclock_profile = db.Column(db.String(100))
    heatsink_available = db.Column(db.String(20))
    rgb_lighting = db.Column(db.String(20))
    module_height_mm = db.Column(db.Float)
    approx_price = db.Column(db.Integer)
    good_for_use_case = db.Column(db.Text)



class Storage(db.Model):
    __tablename__ = "storage"

    id = db.Column(db.Integer, primary_key=True)
    storage_id = db.Column(db.String(20), unique=True, nullable=False)
    company_brand = db.Column(db.String(100))
    model_name = db.Column(db.String(100))
    storage_type = db.Column(db.String(50))
    form_factor = db.Column(db.String(50))
    interface = db.Column(db.String(100))
    storage_capacity = db.Column(db.String(50))
    read_speed_MBs = db.Column(db.Integer)
    write_speed_MBs = db.Column(db.Integer)
    heatsink = db.Column(db.String(20))
    dram_cache = db.Column(db.String(50))
    endurance_tbw = db.Column(db.String(50))
    warranty_period = db.Column(db.String(50))
    price = db.Column(db.Integer)



class PSU(db.Model):
    __tablename__ = "psu"

    id = db.Column(db.Integer, primary_key=True)
    psu_id = db.Column(db.String(20), unique=True, nullable=False)
    brand_model = db.Column(db.String(150))
    modularity = db.Column(db.String(50))
    wattage = db.Column(db.Integer)
    max_output = db.Column(db.Integer)
    certification = db.Column(db.String(100))
    atx_pcie_version = db.Column(db.String(100))
    size_form_factor = db.Column(db.String(100))
    major_protections = db.Column(db.Text)
    recommended_cpu_gpu_pairing = db.Column(db.Text)
    approx_price = db.Column(db.Integer)



class Cabinet(db.Model):
    __tablename__ = "cabinet"

    id = db.Column(db.Integer, primary_key=True)
    cabinet_id = db.Column(db.String(20), unique=True, nullable=False)
    brand = db.Column(db.String(100))
    cabinet_name = db.Column(db.String(150))
    cabinet_form_factor = db.Column(db.String(100))
    cabinet_build_type = db.Column(db.String(100))
    colors_available = db.Column(db.String(200))
    max_cooler_height = db.Column(db.String(100))
    max_gpu_length = db.Column(db.String(100))
    cabinet_dimensions = db.Column(db.String(150))
    motherboard_support = db.Column(db.String(200))
    prebuilt_fans_included = db.Column(db.String(100))
    max_fans_supported = db.Column(db.String(100))
    fan_lighting_type = db.Column(db.String(100))
    psu_dimension_allowed = db.Column(db.String(100))
    price = db.Column(db.Integer)



class Monitor(db.Model):
    __tablename__ = "monitor"

    id = db.Column(db.Integer, primary_key=True)
    monitor_id = db.Column(db.String(20), unique=True, nullable=False)
    brand_model = db.Column(db.String(150))
    resolution = db.Column(db.String(50))
    refresh_rate = db.Column(db.String(50))
    tilt_adjustment = db.Column(db.String(50))
    height_adjustment = db.Column(db.String(50))
    vesa_compatibility = db.Column(db.String(50))
    screen_size = db.Column(db.String(50))
    response_time = db.Column(db.String(50))
    price = db.Column(db.Integer)




class MainDataset(db.Model):
    __tablename__ = "main_dataset"

    id = db.Column(db.Integer, primary_key=True)

    budget = db.Column(db.Integer)
    used_parts = db.Column(db.String(20))
    usage_scenario = db.Column(db.String(100))
    colour_theme = db.Column(db.String(50))
    monitor_required = db.Column(db.String(20))
    monitor_size = db.Column(db.String(50))
    monitor_resolution = db.Column(db.String(50))
    build_type = db.Column(db.String(50))
    upgrade_path = db.Column(db.String(50))

    cpu = db.Column(db.String(50))
    gpu = db.Column(db.String(50))
    mobo = db.Column(db.String(50))
    cpu_cooler = db.Column(db.String(50))
    psu = db.Column(db.String(50))
    storage = db.Column(db.String(50))
    ram = db.Column(db.String(50))
    cabinet = db.Column(db.String(50))
    monitor = db.Column(db.String(50))



# Cart db
class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    cpu_id = db.Column(db.String(50))
    gpu_id = db.Column(db.String(50))
    motherboard_id = db.Column(db.String(50))
    cooler_id = db.Column(db.String(50))
    psu_id = db.Column(db.String(50))
    storage_id = db.Column(db.String(50))
    ram_id = db.Column(db.String(50))
    cabinet_id = db.Column(db.String(50))
    monitor_id = db.Column(db.String(50))
    total_price = db.Column(db.Integer, nullable=False)



# Order db
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    cpu_id = db.Column(db.String(50))
    gpu_id = db.Column(db.String(50))
    motherboard_id = db.Column(db.String(50))
    cooler_id = db.Column(db.String(50))
    psu_id = db.Column(db.String(50))
    storage_id = db.Column(db.String(50))
    ram_id = db.Column(db.String(50))
    cabinet_id = db.Column(db.String(50))
    monitor_id = db.Column(db.String(50))

    total_price = db.Column(db.Integer, nullable=False)





@app.route("/")
def home():
    return render_template("home.html")



@app.route("/products")
def products():
    return render_template("products.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form["password"]

        # print("LOGIN EMAIL:", email)
        # print("LOGIN PASSWORD:", password) 

        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Invalid email or password", "error")
            return render_template("login.html")

        if not check_password_hash(user.password, password):
            flash("Invalid email or password", "error")
            return render_template("login.html")

        # Login successful
        session["user_id"] = user.id
        session["user_name"] = user.name

        return redirect(url_for("home"))


    return render_template("login.html")




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))




@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check password
        if password != confirm_password:return "Passwords do not match"

        # Check existing email
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:return "Email already registered"

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create user
        user = User(
            name=name,
            email=email,
            password=hashed_password)

        # Save user
        db.session.add(user)
        db.session.commit()

        # Redirect to login
        return redirect(url_for("login"))

    return render_template("signup.html")




# Recommendation
@app.route("/recommendation", methods=["GET", "POST"])
def recommendation():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    result_cb = None

    if request.method == "POST":

        budget = request.form.get("budget")
        used_parts = request.form.get("used_parts")
        usage_scenario = request.form.get("usage_scenario")
        colour_theme = request.form.get("colour_theme")
        monitor_required = int(request.form.get("monitor_required"))
        if monitor_required == 1:
            monitor_size = float(request.form.get("monitor_size"))
            monitor_resolution = request.form.get("monitor_resolution")
        else:
            monitor_size = 0
            monitor_resolution = "none"  # ya jo bhi tumhare dataset mein "no monitor" ke liye placeholder value hai

        # build_type = request.form.get("build_type")
        upgrade_path = request.form.get("upgrade_path")


        # Convert numeric values
        budget = int(budget)
        used_parts = int(used_parts)
        monitor_required = int(monitor_required)
        monitor_size = float(monitor_size)
        
        result_cb = recommend_pc(
            budget=budget,
            used_parts=used_parts,
            usage_scenario=usage_scenario,
            colour_theme=colour_theme,
            monitor_required=monitor_required,
            monitor_size=monitor_size,
            monitor_resolution=monitor_resolution,
            upgrade_path=upgrade_path, model=cat_model)

        # Add budget information
        result_cb["user_budget"] = budget
        result_cb["remaining_budget"] = (
            budget - int(result_cb["total_price"]))

        print("\nCATBOOST RESULT:")
        print(result_cb)

    return render_template("recommendation.html", result_cb=result_cb)




# Add to Cart
@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():

    # User must be logged in
    if not session.get("user_id"):
        return redirect(url_for("login"))

    
    # Create cart record
    cart_item = Cart(

        user_id=session.get("user_id"),
        cpu_id=request.form.get("cpu_id"),
        gpu_id=request.form.get("gpu_id"),
        motherboard_id=request.form.get("motherboard_id"),
        cooler_id=request.form.get("cooler_id"),
        psu_id=request.form.get("psu_id"),
        storage_id=request.form.get("storage_id"),
        ram_id=request.form.get("ram_id"),
        cabinet_id=request.form.get("cabinet_id"),
        monitor_id=request.form.get("monitor_id"),
        total_price=int(request.form.get("total_price")))

    print(f"All component: \n{cart_item}")
    
    db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    # User must be logged in
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Get current user's saved builds
    cart_items = Cart.query.filter_by(user_id=session.get("user_id")).all()

    # Store complete component details
    builds = []
    for item in cart_items:
        cpu = CPU.query.filter_by(cpu_id=item.cpu_id).first()
        gpu = GPU.query.filter_by(gpu_id=item.gpu_id).first()
        motherboard = Motherboard.query.filter_by(model_id=item.motherboard_id).first()
        cooler = CPUCooler.query.filter_by(cooler_id=item.cooler_id).first()
        psu = PSU.query.filter_by(psu_id=item.psu_id).first()
        storage = Storage.query.filter_by(storage_id=item.storage_id).first()
        ram = RAM.query.filter_by(ram_id=item.ram_id).first()
        cabinet = Cabinet.query.filter_by(cabinet_id=item.cabinet_id).first()
        monitor = Monitor.query.filter_by(monitor_id=item.monitor_id).first()
        print(cpu)
        build = {
            "cart": item,
            "cpu": cpu,
            "gpu": gpu,
            "motherboard": motherboard,
            "cooler": cooler,
            "psu": psu,
            "storage": storage,
            "ram": ram,
            "cabinet": cabinet,
            "monitor": monitor}
        builds.append(build)

    print(f"All user build: \n{builds}")

    return render_template("cart.html", builds=builds)



# Remove Build route
@app.route("/remove-from-cart/<int:cart_id>", methods=["POST"])
def remove_from_cart(cart_id):

    # User must be logged in
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Get the cart item
    cart_item = Cart.query.filter_by(
        id=cart_id,
        user_id=session.get("user_id")
    ).first()

    # If cart item does not exist
    if not cart_item:
        return redirect(url_for("cart"))

    db.session.delete(cart_item)
    db.session.commit()

    flash("Order has been Removed", "success")
    return redirect(url_for("cart"))




@app.route("/place-order/<int:cart_id>", methods=["POST"])
def place_order(cart_id):

    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Get the cart item of the current user
    cart_item = Cart.query.filter_by(
        id=cart_id,
        user_id=session.get("user_id")).first()

    # If cart item does not exist
    if not cart_item:
        return redirect(url_for("cart"))


    # Create order from cart item
    order = Order(

        user_id=cart_item.user_id,
        cpu_id=cart_item.cpu_id,
        gpu_id=cart_item.gpu_id,
        motherboard_id=cart_item.motherboard_id,
        cooler_id=cart_item.cooler_id,
        psu_id=cart_item.psu_id,
        storage_id=cart_item.storage_id,
        ram_id=cart_item.ram_id,
        cabinet_id=cart_item.cabinet_id,
        monitor_id=cart_item.monitor_id,
        total_price=cart_item.total_price)

    db.session.add(order)
    db.session.delete(cart_item)
    db.session.commit()

    flash("Order has been placed successfully!", "success")
    return redirect(url_for("cart"))




# About Page
@app.route("/about")
def about():
    return render_template("about.html")




with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
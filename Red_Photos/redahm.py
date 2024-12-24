for state, filename in file_mapping.items():
    try:
        df = pd.read_csv(filename)
        if "Route_name" in df.columns:
            slt.success(f"Loaded routes for {state}")
        else:
            slt.error(f"Column 'Route_name' not found in {filename}")
    except FileNotFoundError:
        slt.error(f"File {filename} not found for {state}")
    except Exception as e:
        slt.error(f"Error loading {filename}: {e}")

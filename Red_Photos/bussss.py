# Importing libraries
import pandas as pd
import pymysql
import streamlit as slt
from streamlit_option_menu import option_menu
import time

# Title Section
slt.image("bus_banner.jpg", caption="Travel with RedBus", width=700)  # Replace with your banner image path

slt.title("RedBus")
slt.write("## India's No. 1 Online Bus Ticket Booking Site")
slt.markdown("""
### Why Choose RedBus?
- **Extensive Network:** Covering over 20 states and 10,000+ bus routes.
- **Ease of Use:** Simple booking with real-time seat availability.
- **Secure Payments:** Multiple payment options with 100% security.
- **Customer Support:** 24/7 assistance for your travel needs.
""")
slt.divider()
slt.image("bus_banner.jpg", caption="Travel with RedBus", width=700)  # Replace with your banner image path

# Load Routes from CSV files
def load_routes(filename):
    try:
        df = pd.read_csv(filename)
        if "Route_name" in df.columns:
            return df["Route_name"].tolist()
        else:
            slt.error(f"'Route_name' column not found in {filename}")
            return []
    except FileNotFoundError:
        slt.error(f"File {filename} not found.")
        return []

# Route files and state mapping
files = {
    "Kerala": "df_kerala.csv",
    "Andhra Pradesh": "df_Andhra.csv",
    "Telangana": "df_Telangana.csv",
    "Goa": "df_Goa.csv",
    "Rajasthan": "df_R.csv",
    "South Bengal": "df_South_Bengal.csv",
    "Haryana": "df_H.csv",
    "Assam": "df_AS.csv",
    "Uttar Pradesh": "df_UP.csv",
    "West Bengal": "df_WB.csv"
}

routes = {state: load_routes(filename) for state, filename in files.items()}

# Navigation Menu
web = option_menu(
    menu_title="🚌 OnlineBus",
    options=["Home", "📍 States and Routes"],
    icons=["house", "info-circle"],
    orientation="horizontal"
)

# Home Page
if web == "Home":
    slt.image("aa_.jpg", width=200)
    slt.markdown("""
    ## Overview:
    The 'Redbus Data Scraping and Filtering with Streamlit Application' automates the extraction of bus details and provides dynamic filtering tools.
    
    ### Tools Used:
    - **Selenium**: For web scraping.
    - **Pandas**: For data transformation and cleaning.
    - **MySQL**: For storing and retrieving data.
    - **Streamlit**: For building this application.
    """)

# States and Routes Page
if web == "📍States and Routes":
    # Select State
    state = slt.selectbox("Select State", list(routes.keys()))
    
    if state in routes:
        route_list = routes[state]
        route_name = slt.selectbox("Select Route", route_list)

        # Input Filters
        col1, col2 = slt.columns(2)
        with col1:
            bus_type = slt.radio("Choose Bus Type", ["Sleeper", "Semi-Sleeper", "Others"])
        with col2:
            fare_range = slt.radio("Fare Range", ["50-1000", "1000-2000", "2000 and above"])

        time_input = slt.time_input("Select Departure Time")

        # Database Query Function
        def fetch_bus_data(route, bus_type, fare_range, time_input):
            try:
                conn = pymysql.connect(
                    host="localhost",
                    user="root",
                    password="12345",
                    database="RED_BUS_DETAILS"
                )
                cursor = conn.cursor()

                # Fare Range Filter
                if fare_range == "50-1000":
                    fare_min, fare_max = 50, 1000
                elif fare_range == "1000-2000":
                    fare_min, fare_max = 1000, 2000
                else:
                    fare_min, fare_max = 2000, 100000

                # Bus Type Filter
                if bus_type == "Sleeper":
                    bus_type_condition = "Bus_type LIKE '%Sleeper%'"
                elif bus_type == "Semi-Sleeper":
                    bus_type_condition = "Bus_type LIKE '%Semi Sleeper%'"
                else:
                    bus_type_condition = "Bus_type NOT LIKE '%Sleeper%' AND Bus_type NOT LIKE '%Semi Sleeper%'"

                # Time Formatting
                time_filter = time_input.strftime("%H:%M:%S")

                # SQL Query
                query = f"""
                    SELECT * FROM bus_details
                    WHERE Route_name = '{route}'
                    AND {bus_type_condition}
                    AND Price BETWEEN {fare_min} AND {fare_max}
                    AND Start_time >= '{time_filter}'
                    ORDER BY Price ASC, Start_time ASC
                """
                cursor.execute(query)
                result = cursor.fetchall()
                conn.close()

                # Return as DataFrame
                if result:
                    columns = [
                        "ID", "Bus_name", "Bus_type", "Start_time", "End_time",
                        "Total_duration", "Price", "Seats_Available", "Ratings",
                        "Route_link", "Route_name"
                    ]
                    return pd.DataFrame(result, columns=columns)
                else:
                    return pd.DataFrame()
            except pymysql.Error as e:
                slt.error(f"Database Error: {e}")
                return pd.DataFrame()

        # Fetch and Display Results
        df = fetch_bus_data(route_name, bus_type, fare_range, time_input)
        if not df.empty:
            slt.dataframe(df)
        else:
            slt.warning("No buses found for the selected filters.")

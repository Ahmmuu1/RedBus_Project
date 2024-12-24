# Importing libraries
import pandas as pd
import mysql.connector
import streamlit as slt
from streamlit_option_menu import option_menu
import plotly.express as px
import time

# Streamlit title
slt.title("Hello Streamlit!")
slt.write("If you see this, Streamlit is working correctly.")

# Define file paths and state-specific CSV mappings
file_mapping = {
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

# Load route lists dynamically from CSV files
route_lists = {}
for state, filename in file_mapping.items():
    try:
        df = pd.read_csv(filename)
        if "Route_name" in df.columns:
            route_lists[state] = df["Route_name"].tolist()
        else:
            slt.warning(f"Column 'Route_name' not found in {filename}.")
    except FileNotFoundError:
        slt.error(f"File {filename} not found.")
    except Exception as e:
        slt.error(f"Error loading {filename}: {e}")

# Streamlit option menu
web = option_menu(
    menu_title="🚌 OnlineBus",
    options=["Home", "📍 States and Routes"],
    icons=["house", "info-circle"],
    orientation="horizontal"
)

# Home page settings
if web == "Home":
    try:
        slt.image("aa_.jpg", width=200)
    except FileNotFoundError:
        slt.warning("Image 'aa_.jpg' not found. Please upload the image.")
    
    slt.title("Redbus Data Scraping with Selenium & Dynamic Filtering using Streamlit")
    slt.subheader(":blue[Domain:]  Transportation")
    slt.subheader(":blue[Objective:] ")
    slt.markdown(
        "The 'Redbus Data Scraping and Filtering with Streamlit Application' aims to revolutionize the transportation industry "
        "by providing a comprehensive solution for collecting, analyzing, and visualizing bus travel data. By utilizing Selenium for web scraping, "
        "this project automates the extraction of detailed information from Redbus, including bus routes, schedules, prices, and seat availability. "
        "By streamlining data collection and providing powerful tools for data-driven decision-making, this project can significantly improve "
        "operational efficiency and strategic planning in the transportation industry."
    )
    slt.subheader(":blue[Overview:]") 
    slt.markdown(
        """
        - **Selenium**: Automates web scraping to fetch bus details.
        - **Pandas**: Cleans and transforms the data into structured formats.
        - **MySQL**: Stores and retrieves data efficiently for analysis.
        - **Streamlit**: Builds this dynamic and interactive web application.
        """
    )
    slt.subheader(":blue[Skill-take:]")
    slt.markdown("Selenium, Python, Pandas, MySQL, mysql-connector-python, Streamlit.")
    slt.subheader(":blue[Developed-by:] Khatalahmed")

# States and Routes settings
if web == "📍 States and Routes":
    S = slt.selectbox("Select a State", list(route_lists.keys()))

    col1, col2 = slt.columns(2)
    with col1:
        bus_type = slt.radio("Choose bus type", ["Sleeper", "Semi-Sleeper", "Others"])
    with col2:
        fare_range = slt.radio("Choose bus fare range", ["50-1000", "1000-2000", "2000 and above"])
    time_filter = slt.time_input("Select departure time")

    # Display available routes for the selected state
    if S in route_lists:
        route_name = slt.selectbox("List of Routes", route_lists[S])

        # Function to filter bus details
        def filter_bus_details(state, route_name, bus_type, fare_range, time_filter):
            try:
                conn = mysql.connector.connect(
                    host="localhost", user="root", password="12345", database="RED_BUS_DETAILS"
                )
                cursor = conn.cursor()
                # Parse fare range
                if fare_range == "50-1000":
                    fare_min, fare_max = 50, 1000
                elif fare_range == "1000-2000":
                    fare_min, fare_max = 1000, 2000
                else:
                    fare_min, fare_max = 2000, 100000

                # Define bus type conditions
                if bus_type == "Sleeper":
                    bus_type_condition = "Bus_type LIKE '%Sleeper%'"
                elif bus_type == "Semi-Sleeper":
                    bus_type_condition = "Bus_type LIKE '%Semi Sleeper%'"
                else:
                    bus_type_condition = "Bus_type NOT LIKE '%Sleeper%' AND Bus_type NOT LIKE '%Semi Sleeper%'"

                formatted_time = time_filter.strftime("%H:%M:%S")

                # Query for filtering
                query = f"""
                SELECT * FROM bus_details
                WHERE Price BETWEEN {fare_min} AND {fare_max}
                AND Route_name = "{route_name}"
                AND {bus_type_condition}
                AND Start_time >= '{formatted_time}'
                ORDER BY Price, Start_time DESC
                """
                cursor.execute(query)
                results = cursor.fetchall()
                conn.close()

                # Convert to DataFrame
                columns = [
                    "ID", "Bus_name", "Bus_type", "Start_time", "End_time",
                    "Total_duration", "Price", "Seats_Available", "Ratings",
                    "Route_link", "Route_name"
                ]
                return pd.DataFrame(results, columns=columns)
            except mysql.connector.Error as e:
                slt.error(f"Database error: {e}")
                return pd.DataFrame()
            except Exception as e:
                slt.error(f"Error fetching bus details: {e}")
                return pd.DataFrame()

        # Display filtered results
        filtered_data = filter_bus_details(S, route_name, bus_type, fare_range, time_filter)
        if not filtered_data.empty:
            slt.dataframe(filtered_data)
        else:
            slt.warning("No data found for the selected filters.")

# 🏨 Hotel Booking Analytics & ETL Dashboard

> A full-stack desktop application that analyzes hotel booking data, visualizes business KPIs and persists results into a MySQL database.

![Python](https://img.shields.io/badge/Language-Python%203-3776AB)
![GUI](https://img.shields.io/badge/Interface-Tkinter-green)
![Database](https://img.shields.io/badge/DB-MySQL-orange)
![Analysis](https://img.shields.io/badge/Library-Pandas%20%7C%20Matplotlib-blue)

## 📊 Project Overview
This project is an end-to-end data analysis tool developed to derive actionable insights from a "Hotel Booking" dataset (119k+ records). 

Unlike standard analysis scripts, this is a fully interactive **Desktop Application** built with `tkinter`. It functions as an **ETL (Extract, Transform, Load)** pipeline:
1.  **Extract:** Ingests raw CSV data.
2.  **Transform:** Uses `pandas` for data cleaning, seasonality calculation, and demographic segmentation.
3.  **Load:** Persists processed insights into a **MySQL Database**.
4.  **Visualize:** Generates interactive Matplotlib charts for business intelligence.
5.  **Export:** Allows users to query the SQL database and export specific reports back to CSV.

## 🎯 Key Features

### 📈 Business Intelligence Modules
The application provides a GUI menu to visualize the following metrics:
* **KPI Dashboard:** Calculates Average Daily Rate (ADR), Mean Length of Stay and Cancellation Rates per hotel.
* **Customer Segmentation:** Algorithmic classification of guests into *Solo, Couples, Families or Groups* based on adult/child counts.
* **Seasonal Trends:** Time-series analysis of booking spikes across Winter, Spring, Summer and Autumn.
* **Cancellation Risk:** Correlates seasonality with cancellation rates to identify high-risk periods.
* **Room Inventory:** Distribution analysis of reserved room types.

### 💾 Data Persistence & ETL
* **SQL Integration:** The app connects to a local MySQL instance (`Hotel_booking_analysis`) and updates tables using `INSERT ... ON DUPLICATE KEY UPDATE` logic to ensure data integrity.
* **CSV Export Engine:** A dedicated menu allows users to fetch processed data from SQL and dump it into standardized CSV reports.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Data Processing:** Pandas, NumPy
* **Visualization:** Matplotlib
* **GUI Framework:** Tkinter
* **Database:** MySQL (via `mysql-connector-python`)

## 📸 Screenshots
![Main Menu](screenshots/main_menu.png)

![Seasonality Chart](/screenshots/booking_trends.png)

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have Python installed along with a local MySQL server.
```bash
pip install pandas matplotlib mysql-connector-python
```

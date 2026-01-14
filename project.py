import pandas as pd
import matplotlib.pyplot as plt
import csv
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import sys
import mysql.connector

# Insert data from csv into a DataFrame
data = pd.read_csv('hotel_booking.csv')
pd.set_option('display.max_columns', None)

month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
               'September', 'October', 'November', 'December']


def get_season(month):
    seasons = {
        'Winter': ['December', 'January', 'February'],
        'Spring': ['March', 'April', 'May'],
        'Summer': ['June', 'July', 'August'],
        'Autumn': ['September', 'October', 'November']
    }
    for season, months in seasons.items():
        if month in months:
            return season
    return None


def center_window(window, width, height):
    scr_width = window.winfo_screenwidth()
    scr_height = window.winfo_screenheight()
    x_pos = (scr_width - width) // 2
    y_pos = (scr_height - height) // 2
    window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")


# Connection with MySQL
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    port='3306',
    database='Hotel_booking_analysis'
)

mycursor = mydb.cursor()


def basic_statistics(input_data):

    statistics = input_data.groupby('hotel').agg(
        {'stays_in_weekend_nights': 'mean', 'stays_in_week_nights': 'mean', 'is_canceled': 'mean'})

    total_nights_mean = (statistics['stays_in_weekend_nights'] + statistics['stays_in_week_nights'])
    statistics.insert(0, 'Mean Total Nights', total_nights_mean)

    statistics['is_canceled'] = (statistics['is_canceled'] * 100).round(2)
    statistics['stays_in_weekend_nights'] = statistics['stays_in_weekend_nights'].round(2)
    statistics['stays_in_week_nights'] = statistics['stays_in_week_nights'].round(2)
    statistics['Mean Total Nights'] = statistics['Mean Total Nights'].round(2)

    formatted_statistics = statistics.rename(columns={'stays_in_weekend_nights': 'Mean Weekend Nights',
                                                      'stays_in_week_nights': 'Mean Week Nights',
                                                      'is_canceled': 'Cancellation Rate (%)'})

    return formatted_statistics


def monthly_seasonal_distribution():
    data['arrival_date_month'] = data['arrival_date_month'].astype('category')
    data['arrival_date_month'] = data['arrival_date_month'].cat.set_categories(month_order)

    monthly_data_sorted = data.groupby(['arrival_date_year', 'arrival_date_month'],
                                       observed=False).size().unstack().sort_index()

    monthly_data_sorted.plot(kind='bar', figsize=(10, 6))
    plt.title('Reservations distribution by month')
    plt.xlabel('Year')
    plt.ylabel('Number of reservations')
    plt.legend(title='Month')
    plt.xticks(rotation=45)
    plt.tight_layout()

    data['season'] = data['arrival_date_month'].apply(get_season)

    seasonal_data = data.groupby(['arrival_date_year', 'season']).size().unstack().sort_index()
    seasonal_data = seasonal_data.reindex(columns=["Winter", "Spring", "Summer", "Autumn"])

    seasonal_data.plot(kind='bar', figsize=(10, 6))
    plt.title('Reservations distribution by season')
    plt.xlabel('Year')
    plt.ylabel('Number of reservations')
    plt.legend(title='Season')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

    monthly_values = []
    for year, data_row in monthly_data_sorted.iterrows():
        for month, total_bookings in data_row.items():
            monthly_values.append((year, month, total_bookings))

    seasonal_values = []
    for year, data_row in monthly_data_sorted.iterrows():
        winter_bookings = data_row[['December', 'January', 'February']].sum().astype(int)
        spring_bookings = data_row[['March', 'April', 'May']].sum().astype(int)
        summer_bookings = data_row[['June', 'July', 'August']].sum().astype(int)
        autumn_bookings = data_row[['September', 'October', 'November']].sum().astype(int)

        seasonal_values.append((year, 'Winter', int(winter_bookings)))
        seasonal_values.append((year, 'Spring', int(spring_bookings)))
        seasonal_values.append((year, 'Summer', int(summer_bookings)))
        seasonal_values.append((year, 'Autumn', int(autumn_bookings)))

    # Define and execute SQL queries
    sql1 = "INSERT INTO monthly_distribution (cur_year, cur_month, total_bookings)\
                VALUES (%s, %s, %s)\
                ON DUPLICATE KEY UPDATE\
                total_bookings = VALUES(total_bookings)"

    sql2 = "INSERT INTO seasonal_distribution (cur_year, season, total_bookings)\
                    VALUES (%s, %s, %s)\
                    ON DUPLICATE KEY UPDATE\
                    total_bookings = VALUES(total_bookings)"

    mycursor.executemany(sql1, monthly_values)
    mycursor.executemany(sql2, seasonal_values)

    mydb.commit()


def room_type_distribution():

    room_type_data = data['reserved_room_type'].value_counts()

    explode_values = {'B': 0.2, 'C': 0.4, 'H': 0.6, 'L': 0.8, 'P': 1}
    explode = [explode_values.get(category, 0.0) for category in room_type_data.index]

    room_type_data.plot(kind='pie', autopct='%1.1f%%', explode=explode)
    plt.title('Reservations distribution by room type')
    plt.ylabel('')
    plt.show()

    values = [(room_type, count) for room_type, count in room_type_data.items()]

    sql = "INSERT INTO room_type_distribution (room_type, counter)\
            VALUES (%s, %s)\
            ON DUPLICATE KEY UPDATE\
            counter = VALUES(counter)"

    mycursor.executemany(sql, values)
    mydb.commit()


def customer_types():
    solo_traveller = len(data[(data['adults'] == 1) & (data['children'] == 0) & (data['babies'] == 0)])
    family = len(data[(data['adults'].between(1, 9)) & ((data['children'] >= 1) | (data['babies'] >= 1))])
    couple = len(data[(data['adults'] == 2) & (data['children'] == 0) & (data['babies'] == 0)])
    group_of_friends = len(data[(data['adults'].between(3, 9)) & (data['children'] == 0) & (data['babies'] == 0)])
    group = len(data[data['adults'] >= 10])
    children_only = len(data[(data['adults'] == 0) & (data['children'] > 0)])

    # Create new window
    customer_types_window = tk.Toplevel(root)
    customer_types_window.title("Customer Types")
    customer_types_window.geometry("800x450")
    center_window(customer_types_window, 800, 450)

    customer_types_text = tk.Text(customer_types_window)
    customer_types_text.pack(fill=tk.BOTH, expand=True)

    customer_types_data = {
        "Reservations by solo travellers": solo_traveller,
        "Reservations by families": family,
        "Reservations by couples": couple,
        "Reservations by group of friends": group_of_friends,
        "Reservations by larger groups": group,
        "Reservations by children": children_only
    }

    # Insert data into the text widget
    for customer_type, count in customer_types_data.items():
        customer_types_text.insert(tk.END, f"{customer_type}: {count}\n")

    customer_types_text.config(state=tk.DISABLED)

    sql = "INSERT INTO customer_types (cust_type, counter) \
               VALUES (%s, %s) \
               ON DUPLICATE KEY UPDATE \
               counter = VALUES(counter)"

    values = [("Solo traveler", solo_traveller),
              ("Family", family),
              ("Couple", couple),
              ("Group of friends", group_of_friends),
              ("Group", group),
              ("Children only", children_only)]

    mycursor.executemany(sql, values)
    mydb.commit()


def booking_trends():

    booking_trends_data = data.groupby(['arrival_date_year', 'arrival_date_month'],
                                       observed=False).size().reset_index(name='num_bookings')

    booking_trends_data['date'] = pd.to_datetime(booking_trends_data['arrival_date_month'].astype(str) + '-' +
                                                 booking_trends_data['arrival_date_year'].astype(str), format='%B-%Y')

    booking_trends_data = booking_trends_data.sort_values(by='date')

    plt.figure(figsize=(10, 6))
    plt.plot(booking_trends_data['date'], booking_trends_data['num_bookings'], marker='o', linestyle='-')
    plt.title('Booking trends over time')
    plt.xlabel('Date')
    plt.ylabel('Number of bookings')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    sql = ("INSERT INTO booking_trends (arrival_date_year, arrival_date_month, num_bookings) \
                    VALUES (%s, %s, %s) \
                    ON DUPLICATE KEY UPDATE \
                    num_bookings = VALUES(num_bookings)")

    values = []
    for data_row in booking_trends_data.itertuples(index=False):
        values.append((data_row.arrival_date_year, data_row.arrival_date_month, data_row.num_bookings))

    mycursor.executemany(sql, values)
    mydb.commit()


def seasonality():
    data['arrival_date_month'] = data['arrival_date_month'].astype('category')
    data['arrival_date_month'] = data['arrival_date_month'].cat.set_categories(month_order)

    data['season'] = data['arrival_date_month'].apply(get_season)

    seasonal_data = data.groupby(['hotel', 'season', 'is_canceled']).size().unstack().fillna(0)

    for hotel in data['hotel'].unique():
        hotel_seasonal_data = seasonal_data.loc[hotel]
        hotel_seasonal_data.plot(kind='bar', figsize=(10, 6))
        plt.title(f'Seasonality of bookings and cancellations at {hotel}')
        plt.xlabel('Season')
        plt.ylabel('Number of bookings')
        plt.xticks(rotation=0)
        plt.legend(title='Bookings', loc='upper right', labels=['Not Cancelled', 'Cancelled'])
        plt.tight_layout()

    plt.show()

    values = []
    for hotel in data['hotel'].unique():
        hotel_seasonal_data = seasonal_data.loc[hotel]
        for season, data_row in hotel_seasonal_data.iterrows():
            cancelled = int(data_row.get(1, 0))
            not_cancelled = int(data_row.get(0, 0))
            values.append((hotel, season, cancelled, not_cancelled))

    sql = ("INSERT INTO seasonality (hotel, season, cancelled, not_cancelled) \
                        VALUES (%s, %s, %s, %s) \
                        ON DUPLICATE KEY UPDATE \
                        cancelled = VALUES(cancelled), \
                        not_cancelled = VALUES(not_cancelled)")

    mycursor.executemany(sql, values)
    mydb.commit()


def display_statistics():
    statistics_result = basic_statistics(data)

    sql = ("INSERT INTO basic_statistics (hotel, mean_total_nights, mean_weekend_nights, mean_week_nights, "
           "cancellation_rate) \
           VALUES (%s, %s, %s, %s, %s) \
           ON DUPLICATE KEY UPDATE \
           mean_total_nights = VALUES(mean_total_nights), \
           mean_weekend_nights = VALUES(mean_weekend_nights), \
           mean_week_nights = VALUES(mean_week_nights), \
           cancellation_rate = VALUES(cancellation_rate)")

    values = []
    for data_row in statistics_result.itertuples():
        values.append((data_row.Index, data_row[1], data_row[2], data_row[3], data_row[4]))

    mycursor.executemany(sql, values)
    mydb.commit()

    # Create a new window
    statistics_text = statistics_result.to_string()
    statistics_window = tk.Toplevel(root)
    statistics_window.title("Basic Statistics")
    statistics_window.geometry("800x450")

    statistics_textbox = ScrolledText(statistics_window, width=400, height=20)
    statistics_textbox.insert(tk.END, statistics_text)
    statistics_textbox.pack()
    center_window(statistics_window, 800, 450)


# Function to destroy the root window and exit the program
def exit_program():
    root.destroy()
    sys.exit()


# Function to handle window closing
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        exit_program()


# Functions to change button colour on hover
def on_default(event):
    event.widget.configure(bg='orange')


def on_hover(event):
    event.widget.configure(bg='gold')


def on_default_quit(event):
    event.widget.configure(bg='red')


def on_hover_quit(event):
    event.widget.configure(bg='maroon')


# Main window creation
root = tk.Tk()
root.title("Hotel Booking Analysis")
root.configure(bg="gray")

window_width = 1000
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 6
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Menu for exporting data to CSVs
menu = tk.Menu(root)
root.config(menu=menu)

export_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Export into CSV", menu=export_menu)


def export_to_csv(selected_table):

    # Define the name of the file based on the selected table
    filename = f"{selected_table}.csv"
    try:
        # Execute SQL query based on the selected table and fetch the results
        if selected_table == "basic_statistics":
            sql = "SELECT * FROM basic_statistics"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            # Open the CSV file in write mode and write the data
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write the header row based on the selected table
                writer.writerow(["hotel", "mean_total_nights", "mean_weekend_nights", "mean_week_nights",
                                 "cancellation_rate"])
                # Write the data rows
                writer.writerows(result)
        # Repeat the process for each selected table
        elif selected_table == "monthly_distribution":
            sql = "SELECT * FROM monthly_distribution"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["cur_year", "cur_month", "total_bookings"])
                writer.writerows(result)
        elif selected_table == "seasonal_distribution":
            sql = "SELECT * FROM seasonal_distribution"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["cur_year", "season", "total_bookings"])
                writer.writerows(result)
        elif selected_table == "room_type_distribution":
            sql = "SELECT * FROM room_type_distribution"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["room_type", "counter"])
                writer.writerows(result)
        elif selected_table == "customer_types":
            sql = "SELECT * FROM customer_types"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["cust_type", "counter"])
                writer.writerows(result)
        elif selected_table == "booking_trends":
            sql = "SELECT * FROM booking_trends"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["arrival_date_year", "arrival_date_month", "num_bookings"])
                writer.writerows(result)
        elif selected_table == "seasonality":
            sql = "SELECT * FROM seasonality"
            mycursor.execute(sql)
            result = mycursor.fetchall()
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["hotel", "season", "cancelled", "not_cancelled"])
                writer.writerows(result)
        # Show success message if export is successful
        messagebox.showinfo("Export Successful", f"Data exported to {filename} successfully!")
    # Show error message if an exception occurs during export
    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred: {str(e)}")


# Adding commands to export menu
export_menu.add_command(label="Basic Statistics", command=lambda: export_to_csv("basic_statistics"))
export_menu.add_command(label="Monthly Distribution", command=lambda: export_to_csv("monthly_distribution"))
export_menu.add_command(label="Seasonal Distribution", command=lambda: export_to_csv("seasonal_distribution"))
export_menu.add_command(label="Room Type Distribution", command=lambda: export_to_csv("room_type_distribution"))
export_menu.add_command(label="Customer Types", command=lambda: export_to_csv("customer_types"))
export_menu.add_command(label="Booking Trends", command=lambda: export_to_csv("booking_trends"))
export_menu.add_command(label="Seasonality", command=lambda: export_to_csv("seasonality"))

# Create and place the title label at the top of the main window
title_label = tk.Label(root, text="HOTEL BOOKING ANALYSIS", font=("Times New Roman", 23), bg="gray", fg="black")
title_label.pack(pady=40)

# Text label for development info at the bottom right of the main window
text_label = tk.Label(root, text="Developed by Vasilis Zafeiris\nCEID, University of Patras",
                      font=("Comic Sans MS", 12), bg="grey", fg="black")
text_label.pack(side='bottom', anchor='se', padx=10, pady=10)

# Create a frame for the buttons and place it in the center of the main window
button_frame = tk.Frame(root)
button_frame.place(relx=0.5, rely=0.5, anchor="center")
button_frame.configure(bg="gray")

# List of button texts and functions
buttons = [
    ("Display basic statistics", display_statistics),
    ("Display monthly and seasonal distribution", monthly_seasonal_distribution),
    ("Display room type distribution", room_type_distribution),
    ("Display customer types", customer_types),
    ("Display booking trends", booking_trends),
    ("Display booking and cancellation seasonality", seasonality)
]

# List to store the button objects
button_objects = []

# Place the first three buttons on the left side of the frame
row = 0
for text, command in buttons[:3]:
    button = tk.Button(button_frame, text=text, command=command, width=35, height=2, cursor='hand2',
                       font=("Comic Sans MS", 15), bg='orange', activebackground='gold', bd=2)
    button.grid(row=row, column=0, padx=20, pady=20)
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_default)
    button_objects.append(button)
    row += 1

# Place the other three buttons on the right side of the frame
row = 0
for text, command in buttons[3:]:
    button = tk.Button(button_frame, text=text, command=command, width=35, height=2, cursor='hand2',
                       font=("Comic Sans MS", 15), bg='orange', activebackground='gold', bd=2)
    button.grid(row=row, column=1, padx=20, pady=20)
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_default)
    button_objects.append(button)
    row += 1

# Create and place the exit button at the bottom of the frame
button_quit = tk.Button(root, text="EXIT", command=exit_program, width=10, height=1, cursor='hand2',
                        font=("Times New Roman", 13), bg='red', fg='white', activebackground='maroon',
                        activeforeground='white', bd=2)
button_quit.pack(side=tk.BOTTOM, pady=20)
button_quit.bind("<Enter>", on_hover_quit)
button_quit.bind("<Leave>", on_default_quit)

# Start the Tkinter event loop
root.mainloop()

import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import geocoder
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_KEY = "7e7ef8f3cbd8ee433b6af62222fdb82a"  # Replace with your actual OpenWeather API key

# Global variables for theme and search history
search_history = []
current_theme = "light"

# Function to fetch weather data
def get_weather():
    city = city_entry.get()
    if not city:
        messagebox.showerror("Error", "Please enter a city name!")
        return

    unit = unit_var.get()
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"

    show_loading(True)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract weather data
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        weather_desc = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        icon_code = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
        feels_like = data['main']['feels_like']

        # Compute wind chill (approximation for cold regions)
        if temp < 50:
            wind_chill = 35.74 + 0.6215 * temp - 35.75 * (wind_speed ** 0.16) + 0.4275 * temp * (wind_speed ** 0.16)
        else:
            wind_chill = temp

        # Set weather icon
        weather_icon = Image.open(requests.get(icon_url, stream=True).raw)
        weather_icon = weather_icon.resize((50, 50), Image.ANTIALIAS)
        weather_icon_tk = ImageTk.PhotoImage(weather_icon)
        weather_icon_label.config(image=weather_icon_tk)
        weather_icon_label.image = weather_icon_tk

        # Set background image based on weather description
        bg_image_path = get_background_image(weather_desc)
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((400, 400), Image.ANTIALIAS)
        bg_image_tk = ImageTk.PhotoImage(bg_image)
        background_label.config(image=bg_image_tk)
        background_label.image = bg_image_tk

        # Display weather info
        weather_info.config(
            text=f"Weather in {city.capitalize()}:\n"
                 f"Temperature: {temp}°\n"
                 f"Feels Like: {feels_like}°\n"
                 f"Humidity: {humidity}%\n"
                 f"Description: {weather_desc}\n"
                 f"Wind Speed: {wind_speed} m/s\n"
                 f"Wind Chill: {wind_chill:.2f}°"
        )

        # Display sunrise and sunset times
        sunrise = datetime.utcfromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S')
        sunset = datetime.utcfromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S')
        sun_times.config(text=f"Sunrise: {sunrise}\nSunset: {sunset}")

        # Get 5-day forecast data
        get_5_day_forecast(city, unit)

        # Store search history
        if city not in search_history:
            search_history.append(city)
            update_search_history()

        show_loading(False)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        show_loading(False)

# Function to update search history UI
def update_search_history():
    history_listbox.delete(0, tk.END)
    for city in search_history:
        history_listbox.insert(tk.END, city)

# Function to show loading indicator
def show_loading(is_loading):
    if is_loading:
        loading_label.pack(pady=20)
    else:
        loading_label.pack_forget()

# Function to fetch 5-day forecast
def get_5_day_forecast(city, unit):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Clear previous forecast
        for widget in forecast_frame.winfo_children():
            widget.destroy()

        for i in range(0, len(data['list']), 8):  # Forecast every 24 hours
            day = datetime.utcfromtimestamp(data['list'][i]['dt'])
            temp = data['list'][i]['main']['temp']
            weather_desc = data['list'][i]['weather'][0]['description']
            icon_code = data['list'][i]['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"

            # Fetch weather icon for the forecast day
            weather_icon = Image.open(requests.get(icon_url, stream=True).raw)
            weather_icon = weather_icon.resize((40, 40), Image.ANTIALIAS)
            forecast_image_tk = ImageTk.PhotoImage(weather_icon)

            day_frame = tk.Frame(forecast_frame, bg="#ffffff", padx=10, pady=5)
            day_frame.pack(fill=tk.X, pady=5)

            # Add icon to the forecast frame
            image_label = tk.Label(day_frame, image=forecast_image_tk, bg="#ffffff")
            image_label.image = forecast_image_tk  # Keep a reference to avoid garbage collection

            # Add the weather description and temperature
            details_label = tk.Label(day_frame, text=f"{day.strftime('%A')}: {temp}°C, {weather_desc}",
                                     font=("Helvetica", 12), bg="#ffffff")
            image_label.pack(side=tk.LEFT)
            details_label.pack(side=tk.LEFT, padx=10)

        # Plot temperature graph
        plot_temperature(data)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to plot temperature graph for the 5-day forecast
def plot_temperature(data):
    temps = [entry['main']['temp'] for entry in data['list']]
    times = [datetime.utcfromtimestamp(entry['dt']).strftime('%H:%M') for entry in data['list']]

    fig, ax = plt.subplots()
    ax.plot(times, temps)
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Temperature Trend")
    plt.xticks(rotation=45)

    canvas = FigureCanvasTkAgg(fig, master=info_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Function to get appropriate background image
def get_background_image(weather_desc):
    if "clear" in weather_desc.lower():
        return "C:\\Users\\neeraja\\Downloads\\3222800.png"
    elif "rain" in weather_desc.lower():
        return "C:\\Users\\neeraja\\Downloads\\OIP.jpg"
    else:
        return "C:\\Users\\neeraja\\Downloads\\OIP.jpg"

# Function to clear results
def clear_results():
    city_entry.delete(0, tk.END)
    weather_info.config(text="")
    for widget in forecast_frame.winfo_children():
        widget.destroy()
    sun_times.config(text="")
    weather_icon_label.config(image="")

# Function to fetch weather for the current location
def get_current_location_weather():
    g = geocoder.ip('me')
    lat, lng = g.latlng
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    city = data['name']
    city_entry.delete(0, tk.END)
    city_entry.insert(0, city)
    get_weather()

# Function to toggle between light and dark themes
def toggle_theme():
    global current_theme
    if current_theme == "light":
        current_theme = "dark"
        root.config(bg="#333333")
        info_frame.config(bg="#444444")
        weather_info.config(bg="#333333", fg="#ffffff")
        city_label.config(bg="#444444", fg="#ffffff")
        clear_button.config(bg="#ff4d4d")
        search_button.config(bg="#4caf50")
        toggle_button.config(bg="#444444", fg="#ffffff")
    else:
        current_theme = "light"
        root.config(bg="#ffffff")
        info_frame.config(bg="#ffffff")
        weather_info.config(bg="#ffffff", fg="#000000")
        city_label.config(bg="#ffffff", fg="#000000")
        clear_button.config(bg="#f44336")
        search_button.config(bg="#4caf50")
        toggle_button.config(bg="#ffffff", fg="#000000")

# Create the main window
root = tk.Tk()
root.title("Weather App")
root.geometry("800x600")

# Background label
background_label = tk.Label(root, bg="#87cefa")
background_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Frame for weather info and controls
info_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# City input and unit options
city_label = tk.Label(info_frame, text="Enter City Name:", font=("Helvetica", 14, "bold"), bg="#ffffff")
city_label.pack(pady=10)

city_entry = tk.Entry(info_frame, width=30, font=("Helvetica", 12))
city_entry.pack(pady=5)

unit_var = tk.StringVar(value="metric")
unit_frame = tk.Frame(info_frame, bg="#ffffff")
unit_frame.pack(pady=10)
celsius_button = tk.Radiobutton(unit_frame, text="Celsius", variable=unit_var, value="metric", bg="#ffffff")
fahrenheit_button = tk.Radiobutton(unit_frame, text="Fahrenheit", variable=unit_var, value="imperial", bg="#ffffff")
celsius_button.pack(side=tk.LEFT, padx=5)
fahrenheit_button.pack(side=tk.LEFT, padx=5)

# Buttons for actions
search_button = tk.Button(info_frame, text="Get Weather", command=get_weather, font=("Helvetica", 12), bg="#4caf50")
search_button.pack(pady=10)

clear_button = tk.Button(info_frame, text="Clear", command=clear_results, font=("Helvetica", 12), bg="#f44336")
clear_button.pack(pady=5)

# Weather info
weather_info = tk.Label(info_frame, text="", font=("Helvetica", 14), bg="#000000", fg="#ffffff", justify="left")
weather_info.pack(pady=20)

# Forecast
forecast_frame = tk.Frame(info_frame, bg="#ffffff")
forecast_frame.pack(pady=10)

# Sunrise/Sunset Times
sun_times = tk.Label(info_frame, text="", font=("Helvetica", 12), bg="#ffffff")
sun_times.pack(pady=5)

# Weather icon label
weather_icon_label = tk.Label(info_frame, bg="#ffffff")
weather_icon_label.pack(pady=10)

# Loading label
loading_label = tk.Label(info_frame, text="Loading...", font=("Helvetica", 14), fg="#ff0000", bg="#ffffff")
loading_label.pack_forget()

# Button to get current location weather
location_button = tk.Button(info_frame, text="Get Current Location Weather", command=get_current_location_weather, font=("Helvetica", 12), bg="#2196f3")
location_button.pack(pady=10)

# Search History Frame
history_frame = tk.Frame(root)
history_frame.pack(pady=10)

history_label = tk.Label(history_frame, text="Search History", font=("Helvetica", 14))
history_label.pack()

history_listbox = tk.Listbox(history_frame, width=50, height=5)
history_listbox.pack()

# Button to toggle theme
toggle_button = tk.Button(info_frame, text="Toggle Dark/Light Theme", command=toggle_theme, font=("Helvetica", 12))
toggle_button.pack(pady=10)

root.mainloop()

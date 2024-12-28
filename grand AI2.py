import tkinter as tk
from tkinter import messagebox, simpledialog
import speech_recognition as sr
import pyttsx3
import webbrowser
import time
import threading
import psutil
import os
import requests
import json
from PIL import Image, ImageTk
import openai

# Initialize the speech recognition engine
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# File paths for saving API keys
GOOGLE_API_KEY_PATH = 'google_api_key.json'
OPENAI_API_KEY_PATH = 'openai_api_key.json'

# Function to save Google API key
def save_google_api_key(api_key):
    with open(GOOGLE_API_KEY_PATH, 'w') as f:
        json.dump({"google_api_key": api_key}, f)

# Function to load the Google API key
def load_google_api_key():
    if os.path.exists(GOOGLE_API_KEY_PATH):
        with open(GOOGLE_API_KEY_PATH, 'r') as f:
            data = json.load(f)
            return data.get('google_api_key')
    return None

# Function to save OpenAI API key
def save_openai_api_key(api_key):
    with open(OPENAI_API_KEY_PATH, 'w') as f:
        json.dump({"openai_api_key": api_key}, f)

# Function to load OpenAI API key
def load_openai_api_key():
    if os.path.exists(OPENAI_API_KEY_PATH):
        with open(OPENAI_API_KEY_PATH, 'r') as f:
            data = json.load(f)
            return data.get('openai_api_key')
    return None

# Function to fetch news headlines using Google News API
def fetch_news():
    google_api_key = load_google_api_key()
    if not google_api_key:
        speak("Google News API key is missing. Please input the key first.")
        return
    
    try:
        url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={google_api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json()['articles'][:5]
            speak("Here are the top news headlines:")
            for i, article in enumerate(articles):
                speak(f"Headline {i + 1}: {article['title']}")
        else:
            speak("Unable to fetch news. Try again later.")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")

# Function to input the Google API Key
def input_google_api_key():
    def save_key():
        api_key = api_key_entry.get()
        if api_key:
            save_google_api_key(api_key)
            api_key_window.destroy()
            speak("Google News API key has been saved successfully!")
        else:
            speak("Please enter a valid API key.")

    api_key_window = tk.Toplevel(root)
    api_key_window.title("Enter Google News API Key")
    api_key_window.geometry("400x200")

    tk.Label(api_key_window, text="Please enter your Google News API key:").pack(pady=10)
    api_key_entry = tk.Entry(api_key_window, width=40)
    api_key_entry.pack(pady=10)

    save_button = tk.Button(api_key_window, text="Save API Key", command=save_key)
    save_button.pack(pady=10)

# Function to input the OpenAI API Key
def input_openai_api_key():
    def save_key():
        api_key = api_key_entry.get()
        if api_key:
            save_openai_api_key(api_key)
            api_key_window.destroy()
            speak("OpenAI API key has been saved successfully!")
        else:
            speak("Please enter a valid API key.")

    api_key_window = tk.Toplevel(root)
    api_key_window.title("Enter OpenAI API Key")
    api_key_window.geometry("400x200")

    tk.Label(api_key_window, text="Please enter your OpenAI API key:").pack(pady=10)
    api_key_entry = tk.Entry(api_key_window, width=40)
    api_key_entry.pack(pady=10)

    save_button = tk.Button(api_key_window, text="Save API Key", command=save_key)
    save_button.pack(pady=10)

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to handle user input
def handle_user_input():
    user_input = text_entry.get()
    process_input(user_input)

# Function to process input from text entry
def process_input(text):
    commands = {
        "hello": lambda: speak("Hello!"),
        "what time is it": lambda: speak(f"The time is {time.strftime('%I:%M %p')}"),
        "open Google": lambda: webbrowser.open("https://www.google.com"),
        "play music": open_youtube_music,
        "set alarm": set_alarm,
        "make appointment": open_calendar,
        "get directions": get_directions,
        "gather information from the internet": fetch_news,
        "monitor system status": monitor_system,
        "perform system operations": open_task_manager,
        "open email": open_email,
        "chat with GPT": chat_with_gpt,
    }
    if text in commands:
        commands[text]()
    else:
        speak("Sorry, I didn't understand that.")

# Define features
def open_youtube_music():
    speak("Opening YouTube Music.")
    webbrowser.open("https://music.youtube.com")

def set_alarm():
    speak("Opening Windows Alarm & Clock.")
    os.system("start ms-alarm://")

def open_calendar():
    speak("Opening Windows Calendar.")
    os.system("start outlookcal://")

def get_directions():
    speak("Please provide the destination address.")
    destination = text_entry.get()
    url = f"https://www.google.com/maps?q={destination}"
    webbrowser.open(url)

def monitor_system():
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    speak(f"CPU Usage: {cpu_usage}%")
    speak(f"Memory Usage: {memory.percent}%")

def open_task_manager():
    speak("Opening Task Manager.")
    os.system("taskmgr")

def open_email():
    speak("Opening Microsoft Outlook.")
    webbrowser.open("https://outlook.live.com/")

def chat_with_gpt():
    openai_api_key = load_openai_api_key()
    if not openai_api_key:
        speak("OpenAI API key is missing. Please input the key first.")
        return

    user_input = text_entry.get()
    if user_input:
        try:
            openai.api_key = openai_api_key
            response = openai.Completion.create(
                engine="gpt-4",
                prompt=user_input,
                max_tokens=150
            )
            answer = response.choices[0].text.strip()
            speak(f"GPT-4 says: {answer}")
            chat_box.insert(tk.END, f"You: {user_input}\nGPT-4: {answer}\n")
        except Exception as e:
            speak(f"An error occurred while fetching the response: {str(e)}")
    else:
        speak("Please enter a message for GPT-4.")

# Function to start voice input (speech-to-text)
def start_voice_input():
    with sr.Microphone() as source:
        speak("Listening for your command.")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            process_input(text)
        except sr.UnknownValueError:
            speak("I didn't understand that.")
        except sr.RequestError:
            speak("An error occurred. Try again later.")

# Function to list features in the UI
def list_features():
    features = [
        "Greet you", "Tell you the time", "Open websites", "Play music", "Set alarms", 
        "Make appointments", "Get directions", "Gather information from the internet", 
        "Monitor system status", "Perform system operations", "Open email", "Chat with GPT"
    ]
    # Clear previous buttons
    for widget in button_frame.winfo_children():
        widget.destroy()

    # Create new buttons dynamically using grid
    row = 0
    col = 0
    for feature in features:
        tk.Button(button_frame, text=feature, command=lambda f=feature: perform_function(f),
                  width=30, height=2, bg="lightblue", font=("Helvetica", 12, "bold")).grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        col += 1
        if col > 1:  # Move to next row after two columns
            col = 0
            row += 1

# Function to perform the selected feature
def perform_function(feature):
    functions = {
        "Greet you": lambda: speak("Hello!"),
        "Tell you the time": lambda: speak(f"The time is {time.strftime('%I:%M %p')}"),
        "Open websites": lambda: webbrowser.open(f"https://{text_entry.get()}"),
        "Play music": open_youtube_music,
        "Set alarms": set_alarm,
        "Make appointments": open_calendar,
        "Get directions": get_directions,
        "Gather information from the internet": fetch_news,
        "Monitor system status": monitor_system,
        "Perform system operations": open_task_manager,
        "Open email": open_email,
        "Chat with GPT": chat_with_gpt,
    }
    if feature in functions:
        functions[feature]()

# Set up GUI
root = tk.Tk()
root.title("Cool AI Desktop Helper")
root.geometry("800x600")

# Load and set background image
bg_image = Image.open("E:/py/Grand AI/Cool AI desktop helper.jpeg")  # Correct path for .jpeg file
bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)
bg_image = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

# Entry box for text input
text_entry = tk.Entry(root, width=60, font=("Helvetica", 14))
text_entry.pack(pady=10)

# Submit button to handle user input
submit_button = tk.Button(root, text="Submit", command=handle_user_input, font=("Helvetica", 12))
submit_button.pack(pady=5)

# Frame for dynamic buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

list_features()

root.mainloop()


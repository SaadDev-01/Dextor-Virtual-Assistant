import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import pyjokes
import webbrowser
import os
import time
import schedule
import requests
from bs4 import BeautifulSoup

# Initialize speech recognition and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()

# Set the voice properties for Dextor
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
engine.setProperty('rate', 140)  # Speed of speech
engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)


def talk(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()


def take_command(trigger_word_active=True):
    """Listen for voice commands."""
    command = ""
    start_time = time.time()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            listener.adjust_for_ambient_noise(source, duration=1)
            while True:
                if time.time() - start_time > 180:  # Stop listening after 3 minutes
                    print("Stopped listening due to timeout.")
                    break
                try:
                    voice = listener.listen(source, timeout=10, phrase_time_limit=10)
                    command = listener.recognize_google(voice)
                    command = command.lower()
                    if trigger_word_active and 'dextor' in command:
                        command = command.replace('dextor', '').strip()
                        print(f"Command received: {command}")
                        break
                    elif not trigger_word_active:
                        print(f"Command received: {command}")
                        break
                except sr.WaitTimeoutError:
                    continue
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    break
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
    except Exception as e:
        print(f"An error occurred: {e}")
    return command


def search_google(query):
    """Search Google and return the top 5 links."""
    webbrowser.open(f"https://www.google.com/search?q={query}")


def get_wikipedia_summary(topic):
    """Get a summary of a Wikipedia topic."""
    try:
        return wikipedia.summary(topic, sentences=2)
    except wikipedia.exceptions.DisambiguationError:
        return "There are multiple entries for this topic. Please be more specific."
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find any information on that topic."
    except Exception:
        return "Sorry, I couldn't retrieve the information."


def take_notes(note):
    """Take a note and append it to a text file."""
    with open("notes.txt", "a") as f:
        f.write(note + "\n")
    return "Note taken successfully."


def get_notes():
    """Retrieve notes from the notes file."""
    if not os.path.exists("notes.txt"):
        return "No notes found."

    with open("notes.txt", "r") as f:
        notes = f.readlines()
    return " ".join(note.strip() for note in notes)


def set_reminder(task, time_str):
    """Set a reminder for a specific task."""
    schedule.every().day.at(time_str).do(lambda: talk(f"Reminder: {task}"))
    return f"Reminder set for {time_str}."


def scrape_web_answer(query):
    """Scrape the web to find the answer to a general question."""
    try:
        search_url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract answer snippets from Google's search results
        answer = soup.find('div', class_='BNeawe iBp4i AP7Wnd')  # Class for answer snippet
        if answer:
            return answer.text
        else:
            return "I couldn't find an answer to that question."
    except Exception as e:
        print(f"An error occurred while scraping: {e}")
        return "I couldn't retrieve the answer."


def get_weather(city):
    """Get the weather for a specified city."""
    try:
        # Use OpenWeatherMap's free tier for demonstration purposes (API key not included)
        search_url = f"https://wttr.in/{city}?format=3"
        response = requests.get(search_url)
        return response.text
    except Exception as e:
        print(f"Error retrieving weather: {e}")
        return "I couldn't get the weather information."


def calculate_expression(expression):
    """Evaluate a simple mathematical expression."""
    try:
        # Evaluate the expression and return the result
        result = eval(expression)
        return f"The result is {result}."
    except Exception as e:
        print(f"Calculation error: {e}")
        return "I couldn't calculate that. Please check your expression."


def manage_todo_list(command):
    """Manage the to-do list (add or retrieve items)."""
    todo_file = "todo.txt"
    if 'add' in command:
        item = command.split('add', 1)[1].strip()
        with open(todo_file, "a") as f:
            f.write(item + "\n")
        return f"Added to your to-do list: {item}"
    elif 'show' in command:
        if not os.path.exists(todo_file):
            return "Your to-do list is empty."
        with open(todo_file, "r") as f:
            todos = f.readlines()
        return "Your to-do list: " + ", ".join(todo.strip() for todo in todos)
    return "I couldn't understand your to-do list command."


def run_dextor(trigger_word_active=True):
    """Run Dextor and handle commands."""
    command = take_command(trigger_word_active)
    print(f"Command received: {command}")
    command_handled = False

    # Check for exit command
    if 'exit' in command or 'bye' in command:
        print("Program interrupted. Exiting...")
        talk("I am signing off! Goodbye! Have a nice day!")
        return False

    # Greet user
    elif 'hello' in command:
        talk('Hello! How can I assist you today?')
        command_handled = True

    # Check for jokes
    elif 'joke' in command:
        joke = pyjokes.get_joke()
        talk(joke)
        command_handled = True

    # Check for Wikipedia search
    elif 'wikipedia' in command:
        search_term = command.split('wikipedia', 1)[1].strip()
        summary = get_wikipedia_summary(search_term)
        talk(summary)
        command_handled = True

    # Check for general questions
    elif 'what is' in command or 'who is' in command or 'how' in command:
        question = command.strip()
        answer = scrape_web_answer(question)
        talk(answer)
        command_handled = True

    # Check for taking notes
    elif 'take a note' in command:
        note = command.split('take a note', 1)[1].strip()
        response = take_notes(note)
        talk(response)
        command_handled = True

    # Check for retrieving notes
    elif 'get notes' in command:
        notes = get_notes()
        talk(f"Here are your notes: {notes}")
        command_handled = True

    # Check for setting reminders
    elif 'set a reminder' in command:
        try:
            task = command.split('set a reminder', 1)[1].strip().split('at', 1)
            task_description = task[0].strip()
            reminder_time = task[1].strip()
            response = set_reminder(task_description, reminder_time)
            talk(response)
            command_handled = True
        except Exception as e:
            talk("I couldn't set the reminder. Please check the command format.")
            print(f"Reminder error: {e}")
            command_handled = True

    # Check for searching Google
    elif 'search for' in command:
        search_term = command.split('search for', 1)[1].strip()
        search_google(search_term)
        talk(f"Searching for {search_term} on Google.")
        command_handled = True

    # Check for weather
    elif 'weather in' in command:
        city = command.split('weather in', 1)[1].strip()
        weather = get_weather(city)
        talk(weather)
        command_handled = True

    # Check for calculator
    elif 'calculate' in command:
        expression = command.split('calculate', 1)[1].strip()
        result = calculate_expression(expression)
        talk(result)
        command_handled = True

    # Check for to-do list management
    elif 'to-do' in command:
        response = manage_todo_list(command)
        talk(response)
        command_handled = True

    if not command_handled:
        talk("I'm sorry, I didn't understand that. Could you please repeat it?")

    return True


# Initial startup message
print("Hello, I am Dextor, your virtual assistant. I am now activated and ready to assist you.")
talk("Hello, I am Dextor, your virtual assistant. I am now activated and ready to assist you.")

# Main loop
while True:
    try:
        if not run_dextor(trigger_word_active=True):
            break
    except KeyboardInterrupt:
        print("The program has been interrupted. Exiting now...")
        talk("I am signing off. Goodbye, and have a great day!")
        break
    time.sleep(1)

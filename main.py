import tkinter as tk
from tkinter import scrolledtext, messagebox
import speech_recognition as sr
from google import genai
import threading
import os
import asyncio
import edge_tts
from playsound import playsound

# Global variables
client = None  # Gemini API client will be initialized after API key input
history_file = "chat_history.txt"  # File to save/load chat history


# Asynchronous function to convert text to speech using edge-tts
async def edge_speak(text, voice="en-US-JennyNeural"):
    filename = "output.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)
    playsound(filename)
    os.remove(filename)


# Run text-to-speech in a separate thread to avoid blocking the GUI
def speak_text(text):
    lang = voice_language.get()
    # Select voice based on language
    if lang == 'nl-NL':
        voice = "nl-NL-FennaNeural"
    else:
        voice = "en-US-JennyNeural"
    threading.Thread(target=lambda: asyncio.run(edge_speak(text, voice))).start()


# Handle changes in voice language (placeholder for future functionality)
def set_voice_language(lang_code):
    print(f"Voice language set to {lang_code} (handled by edge-tts)")


def on_voice_language_change(*args):
    lang = voice_language.get()
    set_voice_language(lang)


# Save chat messages to a text file for persistence
def save_to_history(speaker, message):
    with open(history_file, "a", encoding="utf-8") as file:
        file.write(f"{speaker}: {message}\n")


# Load chat history from file at startup
def load_history():
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as file:
            return file.read()
    return ""


# Clear chat history both in file and on screen
def clear_history():
    if os.path.exists(history_file):
        open(history_file, "w").close()
    chat_area.config(state='normal')
    chat_area.delete(1.0, tk.END)
    chat_area.config(state='disabled')


# Call Gemini API to get a response based on user input
def get_gemini_response(user_input):
    if not client:
        return "Error: API key not set."
    try:
        resp = client.models.generate_content(model='gemini-2.0-flash', contents=user_input)
        return resp.text
    except Exception as e:
        return f"Error: {e}"


# Use speech recognition to listen to user voice input and insert text into entry
def listen_and_insert():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            # Show listening status in chat area
            chat_area.config(state='normal')
            chat_area.insert(tk.END, "🎙️ Listening...\n", "bot")
            chat_area.config(state='disabled')
            chat_area.see(tk.END)

            audio = recognizer.listen(source, timeout=5)
            lang = voice_language.get()
            text = recognizer.recognize_google(audio, language=lang)

            # Insert recognized text into entry widget
            entry.insert(tk.END, text)
            send_message()
        except Exception as e:
            messagebox.showerror("Voice Input Error", str(e))


# Handle sending of message: display, save, get response, and optionally speak
def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return

    # Display user message
    chat_area.config(state='normal')
    chat_area.insert(tk.END, f"You: {user_input}\n", "user")
    chat_area.see(tk.END)
    entry.delete(0, tk.END)

    save_to_history("You", user_input)

    # Get AI response
    bot_resp = get_gemini_response(user_input)

    # Display AI response
    chat_area.insert(tk.END, f"AIVA: {bot_resp}\n\n", "bot")
    save_to_history("AIVA", bot_resp)

    # Optionally speak the AI response
    if voice_output_enabled.get():
        speak_text(bot_resp)

    chat_area.config(state='disabled')
    chat_area.see(tk.END)


# Toggle between dark mode and light mode UI colors
def toggle_dark_mode():
    if dark_mode_enabled.get():
        root.configure(bg="#2E2E2E")
        menu_frame.configure(bg="#2E2E2E")
        chat_area.configure(bg="#1E1E1E", fg="white", insertbackground="white")
        entry.configure(bg="#2B2B2B", fg="white", insertbackground="white")
        menu_button.configure(bg="#2E2E2E", fg="white", activebackground="#2E2E2E", activeforeground="white")
        title.configure(bg="#2E2E2E", fg='white')
        chat_area.tag_config("user", foreground="white")
        chat_area.tag_config("bot", foreground="white")
        entry_frame.configure(bg="#2B2B2B")
    else:
        root.configure(bg="SystemButtonFace")
        menu_frame.configure(bg="SystemButtonFace")
        chat_area.configure(bg="white", fg="black", insertbackground="black")
        entry.configure(bg="white", fg="black", insertbackground="black")
        menu_button.configure(bg="SystemButtonFace", fg="black", activebackground="SystemButtonFace", activeforeground="black")
        title.configure(bg="SystemButtonFace", fg='black')
        chat_area.tag_config("user", foreground="black")
        chat_area.tag_config("bot", foreground="black")
        entry_frame.configure(bg="SystemButtonFace")


# Popup window to ask user for Gemini API key
def ask_for_api():
    def on_close():
        # If no API key entered, close the whole app
        if not api_entry.get().strip():
            root.destroy()

    def save_api():
        api = api_entry.get().strip()
        if not api:
            messagebox.showerror("Error", "Please enter an API key!")
            return
        global client
        try:
            client = genai.Client(api_key=api)
            # Test API key with a simple request
            test_resp = client.models.generate_content(model='gemini-2.0-flash', contents="Hello")
            if not test_resp or not hasattr(test_resp, 'text'):
                raise Exception("Invalid API response")
            api_window.destroy()
        except Exception as e:
            messagebox.showerror("API Error", f"Invalid API Key or connection problem:\n{str(e)}")

    api_window = tk.Toplevel(root)
    api_window.geometry('500x100')
    api_window.configure(bg="#2E2E2E")
    api_window.title("Enter API Key")
    api_window.transient(root)
    api_window.grab_set()
    api_window.focus()

    api_window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(api_window, text='API Key:', bg="#2E2E2E", fg="white").pack(side='left', padx=10, pady=20)
    api_entry = tk.Entry(api_window, bg="#2B2B2B", fg="white", insertbackground="white")
    api_entry.pack(side='left', fill=tk.X, expand=True, padx=10)
    tk.Button(api_window, text="Submit", command=save_api).pack(side='left', padx=10)
    api_entry.focus()


# === GUI Setup ===

root = tk.Tk()
root.title("AIVA")
root.geometry("800x600")
root.minsize(height=600, width=800)

# Try to set an icon if available
try:
    root.iconbitmap(default='../AIVA.ico')
except Exception:
    pass

# Variables for UI state
voice_output_enabled = tk.BooleanVar(value=False)
dark_mode_enabled = tk.BooleanVar(value=True)
voice_language = tk.StringVar(value='en-US')

voice_language.trace_add('write', on_voice_language_change)

# Top menu frame with a menu button
menu_frame = tk.Frame(root, height=30)
menu_frame.pack(fill=tk.X)

menu_button = tk.Button(root, text="☰", font=("Arial", 14), relief="flat", bd=0)
menu_button.place(x=4, y=2)

# Popup menu for settings
popup_menu = tk.Menu(root, tearoff=0)
popup_menu.add_checkbutton(label="Dark Mode", onvalue=True, offvalue=False, variable=dark_mode_enabled, command=toggle_dark_mode)
popup_menu.add_checkbutton(label="Voice Output", onvalue=True, offvalue=False, variable=voice_output_enabled)
popup_menu.add_command(label="Clear History", command=clear_history)
popup_menu.add_separator()

# Submenu for voice input language selection
voice_lang_menu = tk.Menu(popup_menu, tearoff=0)
popup_menu.add_cascade(label="Voice Input Language", menu=voice_lang_menu)
voice_lang_menu.add_radiobutton(label="English", variable=voice_language, value='en-US')
voice_lang_menu.add_radiobutton(label="Dutch", variable=voice_language, value='nl-NL')

popup_menu.add_command(label="Exit", command=root.quit)

# Bind menu button to show popup menu
menu_button.bind("<Button-1>", lambda event: popup_menu.tk_popup(event.x_root, event.y_root))

# Title label in the menu frame
title = tk.Label(menu_frame, text="AIVA", font=("Arial", 20))
title.place(relx=0.5, rely=0.6, anchor="center")

# Chat display area (scrollable)
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Arial", 12), bg="#333")
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.tag_config("user", foreground="white")
chat_area.tag_config("bot", foreground="white")

# Entry frame containing the input box and buttons
entry_frame = tk.Frame(root, bg="#2E2E2E")
entry_frame.pack(padx=10, pady=5, fill=tk.X)

entry = tk.Entry(entry_frame, font=("Arial", 15))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(entry_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT)

mic_button = tk.Button(entry_frame, text="🎤", command=lambda: threading.Thread(target=listen_and_insert).start())
mic_button.pack(side=tk.RIGHT, padx=5)

# Load previous chat history if available
chat_area.config(state='normal')
chat_area.insert(tk.END, load_history())
chat_area.config(state='disabled')

# Apply initial dark mode settings and set voice language
toggle_dark_mode()
set_voice_language(voice_language.get())

# Prompt user for API key before starting chat
ask_for_api()

# Start the main GUI loop
root.mainloop()
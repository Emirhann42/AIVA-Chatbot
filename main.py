import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import pyttsx3
import speech_recognition as sr
from google import genai
import threading
import os

# Global variables and setup
client = None
history_file = "chat_history.txt"

engine = pyttsx3.init()
engine.setProperty('rate', 160)

# Main GUI Setup
root = tk.Tk()
root.title("AIVA")
root.geometry("800x600")
root.minsize(height=600, width=800)

voice_output_enabled = tk.BooleanVar(value=False)

try:
    root.iconbitmap(default='../AIVA.ico')
except:
    pass

dark_mode_enabled = tk.BooleanVar(value=True)

menu_frame = tk.Frame(root, height=30)
menu_frame.pack(fill=tk.X)

menu_button = tk.Button(root, text="☰", font=("Arial", 14), relief="flat", bd=0)
menu_button.place(x=4, y=2)

popup_menu = tk.Menu(root, tearoff=0)
popup_menu.add_checkbutton(label="Dark Mode", onvalue=True, offvalue=False, variable=dark_mode_enabled, command=lambda: toggle_dark_mode())
popup_menu.add_checkbutton(label="Voice Output", onvalue=True, offvalue=False, variable=voice_output_enabled)
popup_menu.add_command(label="Clear History", command=lambda: clear_history())
popup_menu.add_command(label="Exit", command=root.quit)

menu_button.bind("<Button-1>", lambda event: popup_menu.tk_popup(event.x_root, event.y_root))

title = tk.Label(menu_frame, text="AIVA", font=("Arial", 20))
title.place(relx=0.5, rely=0.6, anchor="center")

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Arial", 12), bg="#333")
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.tag_config("user", foreground="white")
chat_area.tag_config("bot", foreground="white")

entry_frame = tk.Frame(root)
entry_frame.pack(padx=10, pady=5, fill=tk.X)

entry = tk.Entry(entry_frame, font=("Arial", 15))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(entry_frame, text="Send", command=lambda: send_message(), relief="flat", border=0, highlightthickness=0)
send_button.pack(side=tk.RIGHT)

mic_button = tk.Button(entry_frame, text="🎤", command=lambda: threading.Thread(target=listen_and_insert).start())
mic_button.pack(side=tk.RIGHT, padx=5)

# API Key prompt
def ask_for_api():
    def on_close():
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
            api_window.destroy()
        except Exception as e:
            messagebox.showerror("API Error", str(e))

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

# Chat functions
def get_gemini_response(user_input):
    if not client:
        return "Error: API key not set."
    try:
        resp = client.models.generate_content(model='gemini-2.0-flash', contents=user_input)
        return resp.text
    except Exception as e:
        return f"Error: {e}"

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def listen_and_insert():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            chat_area.config(state='normal')
            chat_area.insert(tk.END, "🎙️ Listening...\n", "bot")
            chat_area.config(state='disabled')
            chat_area.see(tk.END)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            entry.insert(tk.END, text)
            send_message()
        except Exception as e:
            messagebox.showerror("Voice Input Error", str(e))

# Chat history management
def save_to_history(speaker, message):
    with open(history_file, "a", encoding="utf-8") as file:
        file.write(f"{speaker}: {message}\n")

def load_history():
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as file:
            return file.read()
    return ""

def clear_history():
    if os.path.exists(history_file):
        open(history_file, "w").close()
    chat_area.config(state='normal')
    chat_area.delete(1.0, tk.END)
    chat_area.config(state='disabled')

def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return

    chat_area.config(state='normal')
    chat_area.insert(tk.END, f"You: {user_input}\n", "user")
    chat_area.see(tk.END)
    entry.delete(0, tk.END)

    save_to_history("You", user_input)

    bot_resp = get_gemini_response(user_input)

    chat_area.insert(tk.END, f"AIVA: {bot_resp}\n\n", "bot")
    save_to_history("AIVA", bot_resp)

    if voice_output_enabled.get():
        speak_text(bot_resp)

    chat_area.config(state='disabled')
    chat_area.see(tk.END)

# UI Appearance toggle
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
    else:
        root.configure(bg="SystemButtonFace")
        menu_frame.configure(bg="SystemButtonFace")
        chat_area.configure(bg="white", fg="black", insertbackground="black")
        entry.configure(bg="white", fg="black", insertbackground="black")
        menu_button.configure(bg="SystemButtonFace", fg="black", activebackground="SystemButtonFace", activeforeground="black")
        title.configure(bg="SystemButtonFace", fg='black')
        chat_area.tag_config("user", foreground="black")
        chat_area.tag_config("bot", foreground="black")

chat_area.config(state='normal')
chat_area.insert(tk.END, load_history())
chat_area.config(state='disabled')

toggle_dark_mode()
ask_for_api()

root.mainloop()
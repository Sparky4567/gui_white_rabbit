import tkinter as tk
from tkinter import ttk

def send_message(entry,chat_box,window):
    def receive_message():
        response = "Bot: Hello! This is just an example response."
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, response + "\n")
        chat_box.config(state=tk.DISABLED)

    message = entry.get()
    if message:
        chat_box.config(state=tk.NORMAL)
        chat_box.delete("1.0", tk.END)
        chat_box.insert(tk.END, "You: " + message + "\n")
        entry.delete(0, tk.END)
        chat_box.config(state=tk.DISABLED)
        window.after(500, receive_message)


def main_window():
    window = tk.Tk()
    window.title("Rabbit v.1.0")
    # Define a custom style for themed widgets
    style = ttk.Style()
    # Configure the style to have a Bootstrap-like appearance
    style.configure("TButton", padding=6, relief="flat", background="#007BFF", foreground="white", font=("Helvetica", 10))
    style.configure("TEntry", padding=6, relief="flat", font=("Helvetica", 10))
    style.configure("TText", padding=6, relief="flat", font=("Helvetica", 10))
    # Create a Text widget for the chat box
    chat_box = tk.Text(window, height=15, width=40, state=tk.DISABLED, wrap=tk.WORD)
    chat_box.pack(pady=10)
    # Create an Entry widget for user input
    entry = ttk.Entry(window, width=40)
    entry.pack(pady=10)
    # Create a button to send messages
    # send_button = ttk.Button(window, text="Send", command=send_message)
    # send_button.pack(pady=10)
    window.bind('<Return>', lambda event=None: send_message(entry,chat_box,window))
    # Start the Tkinter event loop
    window.mainloop()



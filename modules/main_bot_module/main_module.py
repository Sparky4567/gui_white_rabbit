import tkinter as tk
from tkinter import simpledialog
import sqlite3
from fuzzywuzzy import fuzz, process
import random
import speech_recognition as sr
from config import USE_TRANSLATION_SERVICE
from config import ENABLE_OFFLINE_RECOGNITION
from config import SIMILARITY_SCORE
from config import USE_PREDEFINED_COMMANDS
from config import SPEAK_BACK
from modules.is_online.is_online import Is_Online
from modules.speak_back.speak_module import Speak_Back
from modules.speech_recognizers.speech_recognizers import Speech_recognizers
from modules.random_emoji_module.random_emoji import Random_Emoji
from modules.predefined_commands.predefined_commands_module import Predefined_Commands
from googletrans import Translator
import sys

class ChatbotGUI:
    def __init__(self, master):
        self.master = master
        self.master.attributes('-topmost', True)
        self.title = "Rabbit v.1.0"
        self.master.title(self.title)
        self.setup_database()
        self.setup_gui()
        self.is_online = Is_Online()
        self.speak_module = Speak_Back()
        self.speech_recognizers = Speech_recognizers()
        self.emoji_picker = Random_Emoji()
        self.offline_message = "Your offline. Translation services won't be used."
        self.predefined_commands = Predefined_Commands()
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()

        # Set the window size
        self.window_width = 250
        self.window_height = 400

        # Calculate the position of the window
        self.x_position = self.screen_width - self.window_width
        self.y_position = self.screen_height - self.window_height
        self.master.geometry(f"{self.window_width}x{self.window_height}+{self.x_position}+{self.y_position}")

    def setup_database(self):
        self.conn = sqlite3.connect('database/chatbot_database.db')
        self.cursor = self.conn.cursor()
        # Create tables if not exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                answer TEXT,
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        ''')
        self.conn.commit()

    def setup_gui(self):
        self.chat_box = tk.Text(self.master, height=15, width=40, state=tk.DISABLED, wrap=tk.WORD)
        self.chat_box.pack(pady=10)

        self.entry = tk.Entry(self.master, width=40)
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', self.send_message)

        self.speech_button = tk.Button(self.master, text="Press to Speak", command=self.recognize_speech)
        self.speech_button.pack(pady=5)
        
        self.add_message("\n\n{}: {}\n\n".format(self.title,str("Waiting for your input...").upper()))
        self.add_message("\n\n{}: {}\n\n".format(self.title,str("Type in something and press Enter!").upper()))

    def send_message(self, event=None):
        message = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if message:
            if(str(message).lower()=="exit" or str(message).lower()=="end"):
                self.quit()
            self.add_message(f"You: {message}")
            # Process user input and generate response
            response = self.get_answer(message)
            if(response):
                self.add_message(f"{self.title}: {response}")
            self.chat_box.yview_moveto(1.0) 

    def recognize_speech(self):
        if(ENABLE_OFFLINE_RECOGNITION is False):
            self.add_message(f"{self.title()}: Using Google speech regognition.\n\n")
            text = self.speech_recognizers.recognize_speech()
            if(text is False):
                self.add_message(f"{self.title()}: Could not understand audio input, try again.\n\n")
                return
        else:
            self.add_message(f"{self.title()}: Using PocketSphinx speech regognition.\n\n")
            text = self.speech_recognizers.recognize_speech_pocketsphinx()
            if(text is False):
                self.add_message(f"{self.title()}: Could not understand audio input, try again.\n\n")
                return
        if text:
                # Use the 'text' variable for further processing
            if(USE_PREDEFINED_COMMANDS is True and self.predefined_commands.check_command_list(str(text)) is True):
                self.add_message("\n\n{}\n\n".format("Recognized a predefined command and executing it"))
                if(SPEAK_BACK is True):
                    self.add_message("\n\n{}\n\n".format("Reinitiating speech recognition"))
                self.recognize_speech()
            else:
                self.add_message(str("\n\nRecognized text:{}\n\n").format(text))
                user_input=simpledialog.askstring("Input","\n\nWant to approve question ? (y)\n\n")
                if(str(user_input).lower()=="y"):
                    recognized_phrase = text
                    return recognized_phrase
                else:
                    self.recognize_speech()

    def add_message(self, message):
        # print(message)
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, message + "\n")
        self.chat_box.config(state=tk.DISABLED)

    def return_translated_text(self,passed_phrase):
        if(USE_TRANSLATION_SERVICE is True):
            translator = Translator()
            # Detect the language of the input text
            detected_language = translator.detect(passed_phrase).lang
            # Translate the text to English (you can choose a different target language if needed)
            translated_text = translator.translate(passed_phrase, src=detected_language, dest='en').text
            user_approval=str(simpledialog.askstring("Input",str("\n\nDo you want to approve translation: {}? (y)\n\n").format(translated_text)))
            if(user_approval == "y"):
                return translated_text
            else:
                user_input=str(simpledialog.askstring("Input","\n\nWrite your answer:\n\n"))
                return user_input
        else:
            return passed_phrase

    def find_best_match(self,question):
        # Check if the question exists in the database
        self.cursor.execute('SELECT question FROM questions')
        stored_questions = self.cursor.fetchall()

        # Extract questions from the tuple list
        stored_questions = [q[0] for q in stored_questions]
        question = str(question)
        stored_questions = [str(q) for q in stored_questions]
        # Using process.extractOne to find the best match
        result = process.extractOne(question, stored_questions, scorer=fuzz.ratio)
        similarity_threshold = SIMILARITY_SCORE  # Adjust as needed
        if result and result[1] >= similarity_threshold:
            best_match, similarity_score = result
            return best_match, similarity_score
        else:
            return None, 0  # Return a default value when no match is found or the similarity is below the threshold

    def quit(self):
        sys.exit()
    
    def save_question_and_answers_to_database(self,question, answers):
        # Save the question to the questions table
        self.cursor.execute('INSERT INTO questions (question) VALUES (?)', (question,))
        self.conn.commit()

        # Retrieve the question_id for the newly inserted question
        self.cursor.execute('SELECT id FROM questions WHERE question = ?', (question,))
        question_id = self.cursor.fetchone()[0]

        # Save each answer to the answers table, linked to the question
        if(self.is_online.is_online() is False):
            if(len(answers)>1):
                for answer in answers:  
                    self.cursor.execute('INSERT INTO answers (question_id, answer) VALUES (?, ?)', (question_id, str(answer).lower()))
                    self.conn.commit()
            else:
                self.cursor.execute('INSERT INTO answers (question_id, answer) VALUES (?, ?)', (question_id, str(answers[0]).lower()))
                self.conn.commit()
        else:
            if(self.is_online.is_online() is False):
                    self.add_message("\n\n{}\n\n".format(self.offline_message))
            if(len(answers)>1):
                for answer in answers:  
                    answer = self.return_translated_text(answer)
                    self.cursor.execute('INSERT INTO answers (question_id, answer) VALUES (?, ?)', (question_id, str(answer).lower()))
                    self.conn.commit()
            else:
                answer = self.return_translated_text(answers[0])
                self.cursor.execute('INSERT INTO answers (question_id, answer) VALUES (?, ?)', (question_id, str(answer).lower()))
                self.conn.commit()



    def get_answers_from_database(self,question):
        # Check if the question exists in the database
        self.cursor.execute('SELECT id FROM questions WHERE question = ?', (question,))
        question_id = self.cursor.fetchone()

        if question_id:
            # Retrieve all answers associated with the question
            self.cursor.execute('SELECT answer FROM answers WHERE question_id = ?', question_id)
            results = self.cursor.fetchall()
            return [result[0] for result in results]
        else:
            return None

    def get_answer(self,user_input):
        if(USE_PREDEFINED_COMMANDS is True and self.predefined_commands.check_command_list(user_input) is True):
            self.add_message("\n\n{}\n\n".format("Recognized a predefined command and executing it"))
            self.add_message("\n\n{}\n\n".format("Reinitiating speech recognition"))
            return

            # Find the best matching question
        best_match, similarity_score = self.find_best_match(user_input)

        # Check if similarity score is above a certain threshold
        similarity_threshold = SIMILARITY_SCORE  # Adjust as needed
        
        if best_match is not None and similarity_score >= similarity_threshold:
            stored_answers = self.get_answers_from_database(best_match)
            if(len(stored_answers)>1):
                stored_answers = random.choice(stored_answers)
                if stored_answers:
                    answer = stored_answers
                    if(SPEAK_BACK is True):
                        self.speak_module.speak_back(answer)
                    random_emoji = self.emoji_picker.pick_random()
                    self.add_message(f"{self.title}: {str(answer.upper())} {random_emoji}")
                else:
                    new_answers = simpledialog.askstring("Input",f"{self.title}: I don't know the answer. What should I say? (Separate multiple answers with |): ")
                    if(str(new_answers).__contains__("|")):
                        new_answers_list = [ans.strip() for ans in new_answers.split('|')]
                        self.save_question_and_answers_to_database(best_match, new_answers_list)
                    else:
                        self.save_question_and_answers_to_database(best_match, [new_answers])
            else:
                stored_answers = random.choice(stored_answers)
                if stored_answers:
                    answer = stored_answers
                    if(SPEAK_BACK is True):
                        self.speak_module.speak_back(answer)
                    random_emoji = self.emoji_picker.pick_random()
                    self.add_message(f"{self.title}: {str(answer.upper())} {random_emoji}")
                else:
                    new_answers = simpledialog.askstring("Input",f"{self.title}: I don't know the answer. What should I say? (Separate multiple answers with |): ")
                    if(str(new_answers).__contains__("|")):
                        new_answers_list = [ans.strip() for ans in new_answers.split('|')]
                        self.save_question_and_answers_to_database(best_match, new_answers_list)
                    else:
                        self.save_question_and_answers_to_database(best_match, [new_answers])
                
        else:
            new_answers = simpledialog.askstring("Input",f"{self.title}: I don't know the answer. What should I say? (Separate multiple answers with |): ")
            if(str(new_answers).__contains__("|")):
                new_answers_list = [ans.strip() for ans in new_answers.split('|')]
                self.save_question_and_answers_to_database(user_input, new_answers_list)
            else:
                self.save_question_and_answers_to_database(user_input, [new_answers])


    def main(self):
        self.master.mainloop()


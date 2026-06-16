import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import os
import pyttsx3
from tkinter import messagebox 

# Project Modules
import show_attendance
import takeImage
import automaticAttedance
from trainImage import TrainImage 

# ------------------------ Text-to-Speech ------------------------
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# ------------------------ File Paths ------------------------
haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimage_path = "TrainingImage"
trainimagelabel_path = "./TrainingImageLabel/Trainner.yml" 

# Create necessary folders if they don't exist
if not os.path.exists(trainimage_path):
    os.makedirs(trainimage_path)
os.makedirs(os.path.dirname(trainimagelabel_path), exist_ok=True)


# ------------------------ Main Window ------------------------
window = Tk()
window.title("AI-Based Face Recognition Attendance System")
window.geometry("1280x720")
window.configure(bg="#0b0c10")
window.resizable(False, False)

# ------------------------ Title Section ------------------------
logo = Image.open("UI_Image/0001.png").resize((60, 55), Image.LANCZOS)
logo1 = ImageTk.PhotoImage(logo)

title_frame = Frame(window, bg="#0b0c10")
title_frame.pack(pady=20)

logo_label = tk.Label(title_frame, image=logo1, bg="#0b0c10")
logo_label.grid(row=0, column=0, padx=10)

title_label = tk.Label(
    title_frame,
    text="AI-BASED FACE RECOGNITION",
    font=("Verdana", 28, "bold"),
    fg="#66FCF1",
    bg="#0b0c10",
)
title_label.grid(row=0, column=1)

subtitle_label = tk.Label(
    window,
    text="ATTENDANCE MANAGEMENT SYSTEM",
    font=("Verdana", 20, "italic"),
    fg="#C5C6C7",
    bg="#0b0c10",
)
subtitle_label.pack(pady=(0, 30))

# ------------------------ MAIN COMMAND FUNCTIONS ------------------------

def train_button_command():
    """
    Command to run the training model when the button is pressed.
    Defined globally to be accessible by buttons in the main window and pop-ups.
    """
    # Create a temporary Label to show status during training
    status_label = tk.Label(window, text="TRAINING IN PROGRESS...", font=("Verdana", 16), bg="#0b0c10", fg="#66FCF1")
    status_label.pack(pady=10)
    window.update() # Force update to show the status message
    
    try:
        # Call the imported training function
        TrainImage(
            haarcasecade_path, 
            trainimage_path, 
            trainimagelabel_path, 
            status_label,  # Use the status_label for messages
            text_to_speech 
        )
        # TrainImage function will update the status_label with success/error message
    except Exception as e:
        status_label.configure(text=f"ERROR DURING TRAINING: {e}", fg="red")
        messagebox.showerror("Training Error", f"Failed to run training. Check console for details: {e}")

    # Remove the temporary status label after a delay
    status_label.after(3000, status_label.destroy)


def take_attendance():
    automaticAttedance.subjectChoose(text_to_speech)

def view_attendance():
    show_attendance.subjectchoose(text_to_speech)


# ------------------------ Register Window (Corrected with Train Button) ------------------------
def open_register():
    register_window = Toplevel()
    register_window.title("Register Student")
    register_window.geometry("500x450") 
    register_window.configure(background="#1c1c1c")
    register_window.resizable(0, 0)

    Label(register_window, text="Register New Student", font=("Verdana", 20, "bold"), fg="yellow", bg="#1c1c1c").pack(pady=20)

    Label(register_window, text="University Roll No:", font=("Verdana", 14), bg="#1c1c1c", fg="yellow").pack(pady=5)
    roll_entry = Entry(register_window, font=("Verdana", 14), width=25, bg="#333333", fg="yellow")
    roll_entry.pack(pady=5)

    Label(register_window, text="Name:", font=("Verdana", 14), bg="#1c1c1c", fg="yellow").pack(pady=5)
    name_entry = Entry(register_window, font=("Verdana", 14), width=25, bg="#333333", fg="yellow")
    name_entry.pack(pady=5)

    message_label = Label(register_window, text="", bg="#1c1c1c", fg="yellow", font=("Verdana", 12))
    message_label.pack(pady=10)

    def capture_images():
        roll_no = roll_entry.get().strip()
        name = name_entry.get().strip()

        if roll_no == "" or name == "":
            message_label.config(text="Please enter both Roll No and Name!", fg="red")
            return

        # Call takeImage function 
        takeImage.TakeImage(roll_no, name, haarcasecade_path,
                             trainimage_path_arg=trainimage_path,
                             message_widget=message_label,
                             text_to_speech=text_to_speech)

        roll_entry.delete(0, END)
        name_entry.delete(0, END)
        
    
    # 1. Capture Images Button
    Button(
        register_window,
        text="Capture Images",
        command=capture_images,
        font=("Verdana", 14, "bold"),
        bg="#333333",
        fg="yellow",
        width=20,
        height=1
    ).pack(pady=10)

    # 2. TRAIN MODEL BUTTON (Calls the global train_button_command)
    Button(
        register_window,
        text="Train Model",
        command=train_button_command, # FIXED: Calls the global function
        font=("Verdana", 14, "bold"),
        bg="#4CAF50", 
        fg="white",
        width=20,
        height=1
    ).pack(pady=5)


# ------------------------ Icons and Buttons Section ------------------------
frame = tk.Frame(window, bg="#0b0c10")
frame.pack(pady=40)

# Load icons
register_icon = Image.open("UI_Image/register.png").resize((150, 150))
attendance_icon = Image.open("UI_Image/attendance.png").resize((150, 150))
view_icon = Image.open("UI_Image/verifyy.png").resize((150, 150))
# Assuming 'register.png' is being used as a placeholder for the train icon
train_icon = Image.open("UI_Image/register.png").resize((150, 150)) 

register_photo = ImageTk.PhotoImage(register_icon)
attendance_photo = ImageTk.PhotoImage(attendance_icon)
view_photo = ImageTk.PhotoImage(view_icon)
train_photo = ImageTk.PhotoImage(train_icon)


column_gap = 60 


# --- BUTTONS ---
# Register (Column 0)
register_button = tk.Button(frame, image=register_photo, command=open_register, borderwidth=0, bg="#0b0c10", activebackground="#0b0c10")
register_button.grid(row=0, column=0, padx=column_gap)
register_text = tk.Button(frame, text="Register Student", command=open_register, font=("Poppins", 14, "bold"), bg="#45A29E", fg="white", relief="flat", padx=15, pady=5)
register_text.grid(row=1, column=0, pady=10)


# Train Model (Column 1)
train_button = tk.Button(frame, image=train_photo, command=train_button_command, borderwidth=0, bg="#0b0c10", activebackground="#0b0c10")
train_button.grid(row=0, column=1, padx=column_gap)
train_text = tk.Button(frame, text="Train Model", command=train_button_command, font=("Poppins", 14, "bold"), bg="#45A29E", fg="white", relief="flat", padx=15, pady=5)
train_text.grid(row=1, column=1, pady=10)


# Take Attendance (Column 2)
attendance_button = tk.Button(frame, image=attendance_photo, command=take_attendance, borderwidth=0, bg="#0b0c10", activebackground="#0b0c10")
attendance_button.grid(row=0, column=2, padx=column_gap)
attendance_text = tk.Button(frame, text="Take Attendance", command=take_attendance, font=("Poppins", 14, "bold"), bg="#45A29E", fg="white", relief="flat", padx=15, pady=5)
attendance_text.grid(row=1, column=2, pady=10)


# View Attendance (Column 3)
view_button = tk.Button(frame, image=view_photo, command=view_attendance, borderwidth=0, bg="#0b0c10", activebackground="#0b0c10")
view_button.grid(row=0, column=3, padx=column_gap)
view_text = tk.Button(frame, text="View Attendance", command=view_attendance, font=("Poppins", 14, "bold"), bg="#45A29E", fg="white", relief="flat", padx=15, pady=5)
view_text.grid(row=1, column=3, pady=10)


# ------------------------ Exit Button (Centered) ------------------------
exit_button = tk.Button(
    window,
    text="EXIT",
    command=window.quit,
    font=("Poppins", 16, "bold"),
    bg="#66FCF1",
    fg="#0b0c10",
    relief="flat",
    width=20,
    height=2
)
exit_button.pack(pady=25)

window.mainloop()
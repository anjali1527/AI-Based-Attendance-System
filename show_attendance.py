import pandas as pd
from glob import glob
import os
import tkinter
import csv
import tkinter as tk
from tkinter import *
from tkinter import messagebox 

def subjectchoose(text_to_speech):

    def calculate_attendance():
        Subject = tx.get().strip()
        if Subject == "":
            t = 'Please enter the subject name.'
            messagebox.showwarning("Input Error", t)
            text_to_speech(t)
            return

        try:
            # Folder path
            folder_path = os.path.join("Attendance", Subject)

            if not os.path.isdir(folder_path):
                messagebox.showerror("Folder Error", f"Attendance folder for '{Subject}' does not exist.")
                return

            # Get CSV files
            filenames = glob(os.path.join(folder_path, f"{Subject}*.csv"))

            if not filenames:
                messagebox.showinfo("Attendance Error",
                                    f"No attendance records found for {Subject}. Please take attendance first.")
                return

            # Load all CSV files
            df_list = []
            for f in filenames:
                df = pd.read_csv(f, dtype=str)   # read everything as string to avoid type errors
                df_list.append(df)

            # Merge all files
            if len(df_list) > 1:
                merge_keys = df_list[0].columns[:2].tolist()  # Enrollment, Name

                try:
                    all_data = pd.concat(df_list, ignore_index=True)
                    newdf = all_data.groupby(merge_keys).max().reset_index()
                except Exception as e:
                    messagebox.showerror("Merge Error",
                                         f"Failed to merge attendance files.\nDetails: {e}")
                    return
            else:
                newdf = df_list[0]

            # Replace NaN values
            newdf = newdf.fillna(0)

            # Save merged CSV
            final_csv_path = os.path.join(folder_path, "merged_attendance_view.csv")
            newdf.to_csv(final_csv_path, index=False)

            # Display in a new window
            display_window = tk.Toplevel()
            display_window.title("Attendance of " + Subject)
            display_window.configure(background="black")

            with open(final_csv_path) as file:
                reader = csv.reader(file)
                r = 0
                for col in reader:
                    c = 0
                    for row in col:
                        label = tk.Label(
                            display_window,
                            width=12,
                            height=1,
                            fg="yellow",
                            font=("times", 15, "bold"),
                            bg="black",
                            text=row,
                            relief=tk.RIDGE,
                        )
                        label.grid(row=r, column=c, padx=1, pady=1)
                        c += 1
                    r += 1

        except Exception as e:
            messagebox.showerror(
                "CRITICAL ERROR",
                f"Cannot display attendance.\n"
                f"Please make sure CSV files are formatted correctly.\n\nError: {e}"
            )
            return

    # -----------------------------------------------------
    # MAIN SUBJECT WINDOW
    # -----------------------------------------------------
    subject = Tk()
    subject.title("Subject...")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)

    title_label = tk.Label(
        subject,
        text="Which Subject of Attendance?",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    title_label.place(x=100, y=12)

    def Attf():
        sub = tx.get().strip()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            try:
                os.startfile(os.path.join("Attendance", sub))
            except FileNotFoundError:
                messagebox.showerror("File Error", f"Attendance folder for {sub} not found.")

    attf = tk.Button(
        subject,
        text="Check Sheets",
        command=Attf,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=10,
        relief=RIDGE,
    )
    attf.place(x=360, y=170)

    sub_label = tk.Label(
        subject,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 15),
    )
    sub_label.place(x=50, y=100)

    global tx
    tx = tk.Entry(
        subject,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)

    fill_a = tk.Button(
        subject,
        text="View Attendance",
        command=calculate_attendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    fill_a.place(x=195, y=170)

    subject.mainloop()

import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as tkk
import tkinter.font as font
from tkinter import messagebox

haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "TrainingImageLabel\\Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "StudentDetails\\studentdetails.csv"
attendance_path = "Attendance"

CONFIDENCE_THRESHOLD = 80

def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get().strip()
        now = time.time()
        future = now + 20
        
        if sub == "":
            t = "Please enter the subject name!!!"
            messagebox.showwarning("Input Error", t)
            text_to_speech(t)
            return
        
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            if not os.path.exists(trainimagelabel_path):
                e = "Model not found, please train the model first."
                Notifica.configure(text=e, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                text_to_speech(e)
                return
            
            try:
                recognizer.read(trainimagelabel_path)
            except Exception as ex:
                e = "Failed to load trained model: " + str(ex)
                Notifica.configure(text=e, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                text_to_speech(e)
                return

            facecasCade = cv2.CascadeClassifier(haarcasecade_path)
            if facecasCade.empty():
                e = "Haarcascade file not found or invalid."
                Notifica.configure(text=e, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                text_to_speech(e)
                return

            if not os.path.exists(studentdetail_path):
                e = "Student details file not found."
                Notifica.configure(text=e, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                text_to_speech(e)
                return
            
            # Load student details (master list)
            df_master = pd.read_csv(studentdetail_path, dtype=str)
            df_master.fillna("", inplace=True)
            
            enrollment_col = df_master.columns[0]
            name_col = df_master.columns[1]
            
            student_map = {}
            for _, row in df_master.iterrows():
                key = str(row[enrollment_col]).strip()
                student_map[key] = str(row[name_col]).strip()

            marked_enrollments = set()

            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                e = "Cannot open camera."
                Notifica.configure(text=e, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                text_to_speech(e)
                return

            font_cv = cv2.FONT_HERSHEY_SIMPLEX
            
            while True:
                ret, im = cam.read()
                if not ret:
                    break
                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                faces = facecasCade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

                for (x, y, w, h) in faces:
                    roi_gray = gray[y : y + h, x : x + w]
                    Id_str = "Unknown"
                    conf = 999
                    
                    try:
                        Id_raw, conf = recognizer.predict(roi_gray)
                        Id_str = str(Id_raw).strip()
                    except:
                        pass
                        
                    if isinstance(conf, (int, float)) and conf < CONFIDENCE_THRESHOLD:
                        name = student_map.get(Id_str, "ID:"+Id_str)
                        display_name = name if name != "" else "ID:" + Id_str
                        
                        if Id_str not in marked_enrollments:
                            marked_enrollments.add(Id_str)
                        
                        tt = f"{Id_str} - {display_name}"
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 4)
                        cv2.putText(im, tt, (x, y - 10), font_cv, 0.9, (255, 255, 0), 2)
                    else:
                        tt = "Unknown"
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 4)
                        cv2.putText(im, tt, (x, y - 10), font_cv, 0.9, (0, 25, 255), 2)

                cv2.imshow("Filling Attendance...", im)

                if cv2.waitKey(30) & 0xFF == 27:
                    break
                if time.time() > future:
                    break

            cam.release()
            cv2.destroyAllWindows()

            if not marked_enrollments:
                f = "No registered faces recognized."
                text_to_speech(f)
                Notifica.configure(text=f, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                return

            # --- DATA RESTRUCTURING (NO TIME COLUMN) ---
            ts_final = time.time()
            date_col_name = datetime.datetime.fromtimestamp(ts_final).strftime("%Y-%m-%d")
            
            df_attendance = df_master[[enrollment_col, name_col]].copy()
            
            # The saved file now contains: [Enrollment, Name, YYYY-MM-DD (1s/0s)]
            df_attendance[date_col_name] = 0
            
            for enrollment in marked_enrollments:
                df_attendance.loc[df_attendance[enrollment_col] == enrollment, date_col_name] = 1
            
            # 4. Save CSV
            path = os.path.join(attendance_path, sub)
            os.makedirs(path, exist_ok=True)
            
            # *** CRITICAL: FILENAME WITHOUT HOUR/MINUTE/SECOND FOR CLEANER MERGE ***
            date_file_name = datetime.datetime.fromtimestamp(ts_final).strftime("%Y-%m-%d")
            # We add a unique timestamp to prevent overwriting if attendance is taken twice on the same day
            unique_timestamp = datetime.datetime.fromtimestamp(ts_final).strftime("%H%M%S")
            
            fileName = f"{sub}_{date_file_name}_{unique_timestamp}.csv" 
            filePath = os.path.join(path, fileName)

            try:
                df_attendance.to_csv(filePath, index=False)
            except Exception as ex:
                f = "Failed to save attendance file: " + str(ex)
                text_to_speech(f)
                Notifica.configure(text=f, bg="black", fg="yellow", width=33, font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                return

            m = "Attendance Filled Successfully for " + sub
            Notifica.configure(text=m, bg="black", fg="yellow", width=33, relief=RIDGE, bd=5, font=("times", 15, "bold"))
            Notifica.place(x=20, y=250)
            text_to_speech(m)

            # Show the attendance CSV in a new small tkinter window (for verification)
            try:
                import csv as _csv
                import tkinter as _tk

                root = _tk.Tk()
                root.title("Attendance of " + sub)
                root.configure(background="black")
                with open(filePath, newline="") as file:
                    reader = _csv.reader(file)
                    r = 0
                    for col in reader:
                        c = 0
                        for row in col:
                            label = _tk.Label(
                                root,
                                width=20,
                                height=1,
                                fg="yellow",
                                font=("times", 12, " bold "),
                                bg="black",
                                text=row,
                                relief=_tk.RIDGE,
                            )
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                root.mainloop()
            except Exception as ex:
                print("Attendance saved at:", filePath)

        except Exception as e:
            f = "An error occurred during attendance process."
            text_to_speech(f)
            print("Error during attendance:", e)
            try:
                cv2.destroyAllWindows()
            except:
                pass

    # GUI Code (remains the same)
    subject = Tk()
    subject.title("Subject...")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")
    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)
    titl = tk.Label(subject, text="Enter the Subject Name", bg="black", fg="green", font=("arial", 25))
    titl.place(x=160, y=12)
    Notifica = tk.Label(subject, text="Attendance filled Successfully", bg="yellow", fg="black", width=33, height=2, font=("times", 15, "bold"))

    def Attf():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            try:
                os.startfile(f"Attendance\\{sub}")
            except FileNotFoundError:
                messagebox.showerror("File Error", f"Attendance folder for {sub} not found.")

    attf = tk.Button(subject, text="Check Sheets", command=Attf, bd=7, font=("times new roman", 15), bg="black", fg="yellow", height=2, width=10, relief=RIDGE)
    attf.place(x=360, y=170)

    sub = tk.Label(subject, text="Enter Subject", width=10, height=2, bg="black", fg="yellow", bd=5, relief=RIDGE, font=("times new roman", 15))
    sub.place(x=50, y=100)

    tx = tk.Entry(subject, width=15, bd=5, bg="black", fg="yellow", relief=RIDGE, font=("times", 30, "bold"))
    tx.place(x=190, y=100)

    fill_a = tk.Button(subject, text="Fill Attendance", command=FillAttendance, bd=7, font=("times new roman", 15), bg="black", fg="yellow", height=2, width=12, relief=RIDGE)
    fill_a.place(x=195, y=170)
    subject.mainloop()
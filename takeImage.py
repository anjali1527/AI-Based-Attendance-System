import os
import csv
import cv2
import numpy as np
from tkinter import messagebox
from PIL import Image

# Paths (Assuming these are defined in your main file, but defined here for completeness)
studentdetail_path = "./StudentDetails/studentdetails.csv"
trainimage_path = "./TrainingImage"
trainimagelabel_path = "./TrainingImageLabel/Trainner.yml"

# Ensure directories exist
os.makedirs(os.path.dirname(studentdetail_path), exist_ok=True)
os.makedirs(trainimage_path, exist_ok=True)
os.makedirs(os.path.dirname(trainimagelabel_path), exist_ok=True)


def TakeImage(roll_no, name, haarcascade_path, trainimage_path_arg=None, message_widget=None, err_screen=None, text_to_speech=None):
    """
    Capture face images for new student registration, saving them to a unique folder.
    """

    roll_no = str(roll_no).strip()
    name = str(name).strip()

    if roll_no == "" or name == "":
        if err_screen:
            err_screen()
        else:
            messagebox.showerror("Input Error", "Please enter both Roll Number and Name!")
        if text_to_speech:
            text_to_speech("Please enter Roll Number and Name.")
        return

    # --- FIX 1: CREATE UNIQUE FOLDER FOR IMAGES ---
    base_train_path = trainimage_path_arg or trainimage_path 
    
    # Define the unique folder path (e.g., ./TrainingImage/1 or ./TrainingImage/103)
    student_folder = os.path.join(base_train_path, roll_no) 

    # Ensure the unique folder exists
    os.makedirs(student_folder, exist_ok=True)
    # --- END FIX 1 ---
    
    # Initialize face detector
    face_detector = cv2.CascadeClassifier(haarcascade_path)

    # Load existing trained recognizer (for duplicate check)
    recognizer = None
    if os.path.exists(trainimagelabel_path):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            recognizer.read(trainimagelabel_path)
        except cv2.error:
             # Handle case where file exists but is empty or corrupt
             recognizer = None

    # Load student details (for name lookup)
    student_map = {}
    if os.path.exists(studentdetail_path):
        with open(studentdetail_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    student_map[row[0]] = row[1]

    cam = cv2.VideoCapture(0)
    sample_num = 0
    duplicate_detected = False

    if message_widget:
        message_widget.configure(text="Checking for duplicate face...")

    while True:
        ret, img = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]

            # ✅ Duplicate check via recognizer (This is the code causing the "Anjali" error)
            if recognizer is not None:
                try:
                    Id, conf = recognizer.predict(roi_gray)
                    if conf < 50:  # Confidence threshold (adjust this value if needed, e.g., to 70)
                        duplicate_detected = True
                        cam.release()
                        cv2.destroyAllWindows()

                        existing_name = student_map.get(str(Id), "Unknown")
                        msg = f"This face already belongs to {existing_name} (Roll No: {Id}). Registration blocked."

                        messagebox.showwarning("Duplicate Face Found", msg)
                        if message_widget:
                            message_widget.configure(text=msg)
                        if text_to_speech:
                            text_to_speech(f"This face already belongs to {existing_name}. Registration blocked.")
                        return
                except Exception:
                    pass  # If model is loaded but encounters an error (e.g., first run)

            # Capture new samples
            sample_num += 1
            
            # --- FIX 2: MODIFIED SAVE PATH: Saves image into the student_folder ---
            save_path = os.path.join(student_folder, f"{name}.{roll_no}.{sample_num}.jpg")
            
            cv2.imwrite(save_path, roi_gray)

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, f"Samples {sample_num}/30", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Capturing Faces (Press 'q' to quit)", img)
        if cv2.waitKey(1) & 0xFF == ord('q') or sample_num >= 30:
            break

    cam.release()
    cv2.destroyAllWindows()

    if duplicate_detected:
        return

    # Save student details to CSV
    with open(studentdetail_path, "a+", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([roll_no, name])

    success_msg = f"✅ Saved {sample_num} images for {name} (Roll No: {roll_no})"
    messagebox.showinfo("Registration Successful", success_msg)
    if message_widget:
        message_widget.configure(text=success_msg)
    if text_to_speech:
        text_to_speech(f"Saved images for {name}. Registration complete.")
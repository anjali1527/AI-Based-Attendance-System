import os
import cv2
import numpy as np
import pandas as pd
import datetime
import time
from PIL import ImageTk, Image
from tkinter import messagebox

# --- Utility Function: Get Images and Labels ---
def getImagesAndLables(path):
    """Reads all images from subdirectories and extracts the Roll Number (ID)
    from the filename (Format: Name.RollNo.SampleNum.jpg).
    """
    
    faces = []
    Ids = []
    
    # os.walk efficiently traverses the directory and all subdirectories (Roll Number folders)
    for root, dirs, files in os.walk(path):
        for file in files:
            # Check for standard image file extensions
            if file.endswith(('.jpg', '.jpeg', '.png')): 
                imagePath = os.path.join(root, file)
                
                # --- FIX: Extract ID (Roll No) using the DOT delimiter ---
                filename_parts = file.split('.')
                try:
                    # Assume filename format: Name.RollNo.SampleNum.jpg
                    # The Roll No is the second element (index 1)
                    Id = int(filename_parts[1])
                except (IndexError, ValueError):
                    print(f"Skipping file {file}: Could not parse Roll Number. Check filename format.")
                    continue

                # Load the image and convert it to grayscale (Luminosity)
                try:
                    pilImage = Image.open(imagePath).convert("L")
                    imageNp = np.array(pilImage, "uint8")
                except Exception as e:
                    print(f"Skipping image {file}: Could not open/process. Error: {e}")
                    continue

                if imageNp is not None and imageNp.size > 0:
                    faces.append(imageNp)
                    Ids.append(Id)
                
    return faces, Ids


# --- Main Training Function ---
def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message, text_to_speech):
    """
    Trains the LBPH model using all images in the specified training path and saves the Trainner.yml.
    """
    
    # Initialize the LBPH Face Recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(haarcasecade_path) 
    
    # Get all faces and corresponding numeric IDs
    faces, Id = getImagesAndLables(trainimage_path)
    
    if len(faces) == 0:
        res = "Error: No training images found. Please register at least one student."
        message.configure(text=res)
        if text_to_speech:
            text_to_speech(res)
        messagebox.showerror("Training Error", "No images found for training.")
        return
        
    if len(np.unique(Id)) < 2:
        res = "Warning: Only one unique person found. Recognition may be inaccurate."
        message.configure(text=res)
        
    try:
        # Train the model
        recognizer.train(faces, np.array(Id))
        
        # Save the trained model data to create/update Trainner.yml
        recognizer.save(trainimagelabel_path)
        
        res = "Image Trained successfully"
        message.configure(text=res)
        if text_to_speech:
            text_to_speech(res)
        messagebox.showinfo("Training Success", res)

    except cv2.error as e:
        res = f"CV2 Training Error: {e}. Check if you have at least two unique IDs."
        message.configure(text=res)
        if text_to_speech:
            text_to_speech(res)
        messagebox.showerror("Training Error", "Training failed. Ensure you have images for all registered IDs.")
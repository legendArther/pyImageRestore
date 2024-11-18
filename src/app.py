import os
import replicate
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Initialize global variables
input_image_path = None
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Function to process the image
def process_image():
    try:
        if not input_image_url.get():
            messagebox.showerror("Error", "Please upload an image first.")
            return

        # Display a loading message
        status_label.config(text="Processing image... Please wait.")
        app.update()

        # Run the replicate model
        input = {"img": input_image_url.get()}
        output = client.run(
            "tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c",
            input=input,
        )

        # Save the output image
        with open("output.png", "wb") as file:
            file.write(output.read())
            
        processed_img = Image.open("output.png")
        processed_img.thumbnail((300, 300))  # Resize the image for display
        processed_img = ImageTk.PhotoImage(processed_img)
        processed_image_label.config(image=processed_img)
        processed_image_label.image = processed_img  # Keep reference to the image object

        status_label.config(text="Image processed successfully! Saved as output.png.")
    except Exception as e:
        status_label.config(text="Error processing image.")
        messagebox.showerror("Error", str(e))


# Function to upload the image
def upload_image():
    global input_image_path

    # Open file dialog to select an image
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        initialdir=os.path.expanduser("~")  # Or another directory
    )

    if not file_path:
        status_label.config(text="No image selected.")
        return

    input_image_path = file_path

    # Display the uploaded image
    try:
        img = Image.open(file_path)
        img.thumbnail((300, 300))
        img = ImageTk.PhotoImage(img)
        uploaded_image_label.config(image=img)
        uploaded_image_label.image = img
    except Exception as e:
        messagebox.showerror("Image Error", "Failed to display the image.")
        return

    # Simulate uploading to an image host and get a URL
    try:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": "95530f96645280932d5840b93d2cc6b5"},  # Replace with your API key
            files={"image": open(file_path, "rb")},
        )
        response_data = response.json()
        if response.status_code == 200:
            input_image_url.set(response_data["data"]["url"])
            status_label.config(text="Image uploaded successfully!")
        else:
            raise Exception(response_data.get("error", {}).get("message", "Upload failed"))
    except Exception as e:
        messagebox.showerror("Upload Error", str(e))
        status_label.config(text="Failed to upload the image.")


# Initialize GUI
app = tk.Tk()
app.title("Image Processing App")
app.geometry("400x500")

# Initialize StringVar after the root window is created
input_image_url = tk.StringVar()

# Title
title_label = tk.Label(app, text="Image Upscale", font=("Arial", 16))
title_label.pack(pady=10)

# Upload button
upload_btn = tk.Button(app, text="Upload Image", command=upload_image)
upload_btn.pack(pady=10)

# Uploaded image display
uploaded_image_label = tk.Label(app)
uploaded_image_label.pack()

# Process button
process_btn = tk.Button(app, text="Process Image", command=process_image)
process_btn.pack(pady=20)

# Processed image display
processed_image_label = tk.Label(app)
processed_image_label.pack(pady=10)

# Status label
status_label = tk.Label(app, text="", font=("Arial", 12))
status_label.pack(pady=10)

# Run the app
app.mainloop()

import tkinter as tk
import mysql.connector
from mysql.connector import Error
from PIL import Image, ImageTk
import courseSelection


def truncate_tables():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="sqluser",
            password="password",
            database="Exam"
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            tables = ['course','date_range','slot' ]  

            for table in tables:
                cursor.execute(f"TRUNCATE TABLE {table}")

            conn.commit()
            print("All tables truncated successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed.")

def open_next_window():
    root = tk.Tk()
    app = courseSelection.CourseSelectionApp(root)
    root.mainloop()

def display_image_then_open_subject():
    root = tk.Tk()
    root.title("Welcome")

    
    window_width = 800
    window_height = 800  
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

   
    image = Image.open("/home/yash/Downloads/wall.jpeg")
    image = image.resize((600, 600), Image.Resampling.LANCZOS)  
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=photo)
    label.image = photo  
    label.pack()

   
    title_label = tk.Label(root, text="Exam Timetable Generator", font=("Helvetica", 24, "bold"))
    title_label.pack(pady=10)

    
    next_button = tk.Button(root, text="Next", font=("Helvetica", 12), command=lambda: (root.destroy(), open_next_window()))
    next_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    truncate_tables()  #call the truncate_tables function 
    display_image_then_open_subject()













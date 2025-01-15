import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import daterange
class CourseSelectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Selection")
        window_width = 800
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))
        
        # Connect to MySQL database
        try:
            self.connection = mysql.connector.connect(
                host='localhost', 
                database='Exam',  
                user='sqluser', 
                password='password'  
            )
            if self.connection.is_connected():
                print('Connected to MySQL database')

        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True)

        
        self.label = tk.Label(self.main_frame, text="Select Programme", font=("Arial", 14, "bold"))
        self.label.pack(pady=10)

        
        self.selected_option = tk.StringVar()

        
        self.dropdown = ttk.Combobox(self.main_frame, textvariable=self.selected_option)
        self.dropdown['values'] = ("MSc Computer Science", "MCA")
        self.dropdown.pack(pady=10)

        
        self.radio_frame = tk.Frame(self.main_frame)
        self.radio_frame.pack(pady=10)

        
        self.dropdown.bind("<<ComboboxSelected>>", self.show_radio_buttons)

        
        self.subjects = []

        
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        
        tk.Button(button_frame, text="Submit", command=self.open_new_window, bg='blue', fg='white').pack(side=tk.LEFT, padx=5)

        
        tk.Button(button_frame, text="Next", command=self.next_button_action, bg='blue', fg='white').pack(side=tk.LEFT, padx=5)

        
        self.new_window = None

    
    def show_radio_buttons(self, event):
        
        for widget in self.radio_frame.winfo_children():
            widget.destroy()
        
        
        semesters = ["Semester1", "Semester2", "Semester3", "Semester4"]
        self.sem_var = tk.StringVar()
        
        for sem in semesters:
            radio_button = tk.Radiobutton(self.radio_frame, text=sem, variable=self.sem_var, value=sem, command=self.display_data, font=("Arial", 12, "bold"))
            radio_button.pack(side=tk.LEFT, padx=5)

        
        self.display_data()

    
    def open_new_window(self):
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Course Details")
        
        
        window_width = 800
        window_height = 800  
        screen_width = self.new_window.winfo_screenwidth()
        screen_height = self.new_window.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        self.new_window.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

        
        tk.Label(self.new_window, text="Course ID:", font=("Arial", 12, "bold")).pack(pady=5)
        self.course_id_entry = tk.Entry(self.new_window)
        self.course_id_entry.pack(pady=5)

        tk.Label(self.new_window, text="Course Name:", font=("Arial", 12, "bold")).pack(pady=5)
        self.course_name_entry = tk.Entry(self.new_window)
        self.course_name_entry.pack(pady=5)

        tk.Label(self.new_window, text="Instructor Name:", font=("Arial", 12, "bold")).pack(pady=5)
        self.instructor_name_entry = tk.Entry(self.new_window)
        self.instructor_name_entry.pack(pady=5)

        
        backlog_frame = tk.Frame(self.new_window)
        backlog_frame.pack(pady=10)

        
        tk.Label(backlog_frame, text="Backlog:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.backlog_var = tk.StringVar(value="No")
        tk.Radiobutton(backlog_frame, text="Yes", variable=self.backlog_var, value="Yes", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(backlog_frame, text="No", variable=self.backlog_var, value="No", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)

        
        tk.Button(self.new_window, text="Add", command=self.add_course, bg='green', fg='white', font=("Arial", 12)).pack(pady=5)
        tk.Button(self.new_window, text="Update", command=self.update_course, bg='orange', fg='white', font=("Arial", 12)).pack(pady=5)
        tk.Button(self.new_window, text="Delete", command=self.delete_course, bg='red', fg='white', font=("Arial", 12)).pack(pady=5)

        
        self.table_frame = tk.Frame(self.new_window)
        self.table_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.create_table()

        
        self.display_data()

        
        tk.Button(self.new_window, text="Next", command=lambda: self.focus_main_window(self.new_window), bg='blue', fg='white', font=("Arial", 12)).pack(pady=5)

    def create_table(self):
        columns = ("Course ID", "Course Name", "Instructor Name", "Backlog")
        self.subject_table = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        for col in columns:
            self.subject_table.heading(col, text=col)
            self.subject_table.column(col, anchor=tk.CENTER, width=100)
        self.subject_table.pack(fill=tk.BOTH, expand=True)

    def display_data(self):
        
        for row in self.subject_table.get_children():
            self.subject_table.delete(row)

        #
        try:
            cursor = self.connection.cursor()
            branch = self.selected_option.get()
            semester = self.sem_var.get()
            cursor.execute("SELECT course_id, course_name, instructor_name, backlog FROM course WHERE branch = %s AND semester = %s", (branch, semester))
            rows = cursor.fetchall()

            for row in rows:
                self.subject_table.insert('', tk.END, values=row)

        except Error as e:
            print(f"Error fetching data: {e}")

        finally:
            if cursor:
                cursor.close()

    
    def add_course(self):
        course_id = self.course_id_entry.get().strip()
        course_name = self.course_name_entry.get().strip()
        instructor_name = self.instructor_name_entry.get().strip()
        backlog = self.backlog_var.get()

        
        if not course_id or not course_name or not instructor_name:
            messagebox.showerror("Error", "Please fill all fields", parent=self.new_window)
            return

        #Check if course_id already exists
        if self.course_id_exists(course_id):
            messagebox.showerror("Error", f"Course ID '{course_id}' already exists. Please use a different Course ID.", parent=self.new_window)
            return

        subject = (course_id, course_name, instructor_name, backlog)
        self.subjects.append(subject)
        self.subject_table.insert('', tk.END, values=subject)

        #insert into database
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO course (branch, semester, course_id, course_name, instructor_name, backlog) VALUES (%s, %s, %s, %s, %s, %s)"
            branch = self.selected_option.get()
            semester = self.sem_var.get()
            cursor.execute(sql, (branch, semester, course_id, course_name, instructor_name, backlog))
            self.connection.commit()
            messagebox.showinfo("Success", "Course added successfully", parent=self.new_window)

        except Error as e:
            print(f"Error inserting data: {e}")

        finally:
            if cursor:
                cursor.close()

    #function to handle Update action
    def update_course(self):
        selected_item = self.subject_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to update", parent=self.new_window)
            return

        course_id = self.course_id_entry.get().strip()
        course_name = self.course_name_entry.get().strip()
        instructor_name = self.instructor_name_entry.get().strip()
        backlog = self.backlog_var.get()

        
        if not course_id or not course_name or not instructor_name:
            messagebox.showerror("Error", "Please fill all fields", parent=self.new_window)
            return

        # Check if course_id already exists (excluding the current record being updated)
        original_course_id = self.subject_table.item(selected_item, 'values')[0]
        if course_id != original_course_id and self.course_id_exists(course_id):
            messagebox.showerror("Error", f"Course ID '{course_id}' already exists. Please use a different Course ID.", parent=self.new_window)
            return

        updated_subject = (course_id, course_name, instructor_name, backlog)
        self.subject_table.item(selected_item, values=updated_subject)

        #Update in database
        try:
            cursor = self.connection.cursor()
            branch = self.selected_option.get()
            semester = self.sem_var.get()
            sql = "UPDATE course SET course_id = %s, course_name = %s, instructor_name = %s, backlog = %s WHERE branch = %s AND semester = %s AND course_id = %s"
            cursor.execute(sql, (course_id, course_name, instructor_name, backlog, branch, semester, original_course_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Course updated successfully", parent=self.new_window)

        except Error as e:
            print(f"Error updating data: {e}")

        finally:
            if cursor:
                cursor.close()

    #function to handle Delete action
    def delete_course(self):
        selected_item = self.subject_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to delete", parent=self.new_window)
            return

        subject_values = self.subject_table.item(selected_item, 'values')
        self.subject_table.delete(selected_item)

        #++delete from database
        try:
            cursor = self.connection.cursor()
            branch = self.selected_option.get()
            semester = self.sem_var.get()
            course_id = subject_values[0]  #Assuming course_id is the first column
            sql = "DELETE FROM course WHERE branch = %s AND semester = %s AND course_id = %s"
            cursor.execute(sql, (branch, semester, course_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Course deleted successfully", parent=self.new_window)

        except Error as e:
            print(f"Error deleting data: {e}")

        finally:
            if cursor:
                cursor.close()

    #function to check if course_id already exists in the database
    def course_id_exists(self, course_id):
        try:
            cursor = self.connection.cursor()
            branch = self.selected_option.get()
            semester = self.sem_var.get()
            cursor.execute("SELECT course_id FROM course WHERE branch = %s AND semester = %s AND course_id = %s", (branch, semester, course_id))
            row = cursor.fetchone()
            return row is not None

        except Error as e:
            print(f"Error checking course ID existence: {e}")
            return False

        finally:
            if cursor:
                cursor.close()

    #back to main window
    def focus_main_window(self, window):
        window.destroy()

    
    def next_button_action(self):
        self.root.destroy()
        new_root = tk.Tk()
        iapp = daterange.DateRangeApp(new_root)  
        new_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = CourseSelectionApp(root)
    root.mainloop()
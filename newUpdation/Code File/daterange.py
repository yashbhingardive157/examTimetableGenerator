import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import tkinter.messagebox as messagebox
import mysql.connector
import holidays
import courseSelection
import slot

class HolidayCalendar(Calendar):
    def __init__(self, master=None, **kwargs):
        self.holidays = kwargs.pop('holidays', [])
        Calendar.__init__(self, master, **kwargs)
        self.tag_config('holiday', background='red', foreground='white')
        self._highlight_holidays()

    def _highlight_holidays(self):
        for holiday in self.holidays:
            self.calevent_create(holiday, 'Holiday', 'holiday')

class DateRangeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Date Range Selector")
        window_width = 800
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))
        
        # MySQL connection
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="sqluser",
            password="password",
            database="Exam"
        )
        self.mycursor = self.mydb.cursor()

        self.public_holidays = self.fetch_public_holidays()
        self.setup_ui()

    def fetch_public_holidays(self):
        india_holidays = holidays.India(years=range(2020, 2030))  
        return [date for date in india_holidays]

    def setup_ui(self):
        date_frame = tk.Frame(self.root, padx=10, pady=10)
        date_frame.grid(row=0, column=0, sticky="w")

        start_label = tk.Label(date_frame, text="Start Date")
        start_label.grid(row=0, column=0, padx=5, pady=5)
        self.start_date = HolidayCalendar(date_frame, selectmode='day', date_pattern='yyyy-mm-dd', holidays=self.public_holidays)
        self.start_date.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        end_label = tk.Label(date_frame, text="End Date")
        end_label.grid(row=0, column=2, padx=5, pady=5)
        self.end_date = HolidayCalendar(date_frame, selectmode='day', date_pattern='yyyy-mm-dd', holidays=self.public_holidays)
        self.end_date.grid(row=1, column=2, padx=5, pady=5, columnspan=2)

        button_frame = tk.Frame(self.root, padx=10, pady=10)
        button_frame.grid(row=2, column=0, sticky="w")

        self.add_button = tk.Button(button_frame, text="Add", command=self.add_record, bg="green", fg="white")
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.update_button = tk.Button(button_frame, text="Update", command=self.update_record, bg="orange", fg="white")
        self.update_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_record, bg="red", fg="white")
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)

        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.grid(row=3, column=0, sticky="nsew")

        columns = ('#1', '#2')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        self.tree.heading('#1', text='Start Date')
        self.tree.heading('#2', text='End Date')

        self.tree.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        navigation_frame = tk.Frame(self.root, padx=10, pady=10)
        navigation_frame.grid(row=4, column=0, sticky="ew")
       
        prev_button = tk.Button(navigation_frame, text="Previous", command=self.open_prevWindow)
        prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        next_button = tk.Button(navigation_frame, text="Next", command=self.open_nextWindow)
        next_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.update_table()

    def fetch_records_from_database(self):
        self.mycursor.execute("SELECT * FROM date_range")
        records = self.mycursor.fetchall()
        return records

    def add_record(self):
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()
        if start_date in self.public_holidays or end_date in self.public_holidays:
            messagebox.showwarning("Input Error", "Selected dates include a public holiday.")
            return
        self.tree.insert('', 'end', values=(start_date, end_date))
        sql = "INSERT INTO date_range (start_date, end_date) VALUES (%s, %s)"
        val = (start_date, end_date)
        self.mycursor.execute(sql, val)
        self.mydb.commit()

    def update_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            if start_date in self.public_holidays or end_date in self.public_holidays:
                messagebox.showwarning("Input Error", "Selected dates include a public holiday.")
                return
            # Get the current values from the Treeview
            current_start_date = self.tree.item(selected_item, 'values')[0]
            current_end_date = self.tree.item(selected_item, 'values')[1]
            
            # Update the Treeview
            self.tree.item(selected_item, values=(start_date, end_date))
            
            # Update the database
            sql = "UPDATE date_range SET start_date = %s, end_date = %s WHERE start_date = %s AND end_date = %s"
            val = (start_date, end_date, current_start_date, current_end_date)
            self.mycursor.execute(sql, val)
            self.mydb.commit()
        else:
            messagebox.showwarning("Update Error", "Please select a record to update")

    def delete_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            start_date = self.tree.item(selected_item, 'values')[0]
            end_date = self.tree.item(selected_item, 'values')[1]
            
            # Delete from the Treeview
            self.tree.delete(selected_item)
            
            # Delete from the database
            sql = "DELETE FROM date_range WHERE start_date = %s AND end_date = %s"
            val = (start_date, end_date)
            self.mycursor.execute(sql, val)
            self.mydb.commit()
        else:
            messagebox.showwarning("Delete Error", "Please select a record to delete")

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        records = self.fetch_records_from_database()
        for record in records:
            self.tree.insert('', 'end', values=record)


    
    def open_prevWindow(self):
        # top = tk.Toplevel(self.root)
        # app = courseSelection.CourseSelectionApp(top)
        self.root.destroy()
        root = tk.Tk()
        app = courseSelection.CourseSelectionApp(root)
        root.mainloop()

    def open_nextWindow(self):
        # top = tk.Toplevel(self.root)
        # app = slot.TimetableApp(top)
        self.root.destroy()
        root = tk.Tk()
        app = slot.TimetableApp(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = DateRangeApp(root)
    root.mainloop()

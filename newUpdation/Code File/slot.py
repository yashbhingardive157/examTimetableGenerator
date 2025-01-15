import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import mysql.connector
import generate1
import daterange

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Slot")
        
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

        self.setup_ui()
        self.update_table()  

    def setup_ui(self):
        slot_frame = tk.Frame(self.root, padx=10, pady=10)
        slot_frame.grid(row=0, column=0, sticky="w")

        slot_label = tk.Label(slot_frame, text="Slot")
        slot_label.grid(row=0, column=0, padx=5, pady=5)
        self.slot_var = tk.StringVar()
        self.slot_dropdown = ttk.Combobox(slot_frame, textvariable=self.slot_var, state="readonly")
        self.slot_dropdown['values'] = ('1', '2', '3', '4', '5')
        self.slot_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.slot_dropdown.bind("<<ComboboxSelected>>", self.update_slot_times)

        self.slot_time_frame = tk.Frame(self.root, padx=10, pady=10)
        self.slot_time_frame.grid(row=1, column=0, sticky="w")
        
        self.slot_time_entries = []

        button_frame = tk.Frame(self.root, padx=10, pady=10)
        button_frame.grid(row=3, column=0, sticky="w")

        self.add_button = tk.Button(button_frame, text="Add", command=self.add_record, bg="green", fg="white")
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.update_button = tk.Button(button_frame, text="Update", command=self.update_record, bg="orange", fg="white")
        self.update_button.grid(row=0, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_record, bg="red", fg="white")
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)
        
        navigation_frame = tk.Frame(self.root, padx=10, pady=10)
        navigation_frame.grid(row=5, column=0, sticky="ew")
       
        generate_button = tk.Button(navigation_frame, text="Generate Timetable", command=self.open_generate_window)
        generate_button.pack(side=tk.RIGHT, padx=5, pady=5)
       
        prev_button = tk.Button(navigation_frame, text="Previous", command=self.open_duration_window)
        prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Table
        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.grid(row=4, column=0, sticky="nsew")

        columns = ('#1', '#2')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        self.tree.heading('#1', text='Slot')
        self.tree.heading('#2', text='Slot Time')

        self.tree.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

    def update_slot_times(self, event):
        for widget in self.slot_time_frame.winfo_children():
            widget.destroy()
        self.slot_time_entries.clear()

        num_slots = int(self.slot_var.get())

        for i in range(num_slots):
            slot_time_label = tk.Label(self.slot_time_frame, text=f"Slot Time {i+1}")
            slot_time_label.grid(row=i, column=0, padx=5, pady=5)

            start_hour_var = tk.StringVar(value="09")
            start_minute_var = tk.StringVar(value="00")
            start_hour_spinbox = tk.Spinbox(self.slot_time_frame, from_=0, to=23, wrap=True, textvariable=start_hour_var, width=3, format="%02.0f")
            start_minute_spinbox = tk.Spinbox(self.slot_time_frame, from_=0, to=59, wrap=True, textvariable=start_minute_var, width=3, format="%02.0f")

            end_hour_var = tk.StringVar(value="12")
            end_minute_var = tk.StringVar(value="00")
            end_hour_spinbox = tk.Spinbox(self.slot_time_frame, from_=0, to=23, wrap=True, textvariable=end_hour_var, width=3, format="%02.0f")
            end_minute_spinbox = tk.Spinbox(self.slot_time_frame, from_=0, to=59, wrap=True, textvariable=end_minute_var, width=3, format="%02.0f")

            start_hour_spinbox.grid(row=i, column=1, padx=5, pady=5)
            tk.Label(self.slot_time_frame, text=":").grid(row=i, column=2, padx=1, pady=5)
            start_minute_spinbox.grid(row=i, column=3, padx=5, pady=5)
            tk.Label(self.slot_time_frame, text="-").grid(row=i, column=4, padx=5, pady=5)
            end_hour_spinbox.grid(row=i, column=5, padx=5, pady=5)
            tk.Label(self.slot_time_frame, text=":").grid(row=i, column=6, padx=1, pady=5)
            end_minute_spinbox.grid(row=i, column=7, padx=5, pady=5)

            self.slot_time_entries.append((start_hour_spinbox, start_minute_spinbox, end_hour_spinbox, end_minute_spinbox))

    def add_record(self):
        if len(self.tree.get_children()) >= 1:
            messagebox.showwarning("Add Error", "Only one entry is allowed.")
            return
        slot = self.slot_var.get()
        slot_times = [f"{entry[0].get()}:{entry[1].get()}-{entry[2].get()}:{entry[3].get()}" for entry in self.slot_time_entries]
        if slot and all(slot_times):
            for i, slot_time in enumerate(slot_times, 1):
                self.tree.insert('', 'end', values=(f"Slot {i}", slot_time))
                # Insert record into database
                sql = "INSERT INTO slot (slot, slot_time) VALUES (%s, %s)"
                val = (f"Slot {i}", slot_time)
                self.mycursor.execute(sql, val)
                self.mydb.commit()
        else:
            messagebox.showwarning("Input Error", "Please select slot and enter all slot times.")

    def update_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Update Error", "Please select a record to update")
            return
        slot_times = [f"{entry[0].get()}:{entry[1].get()}-{entry[2].get()}:{entry[3].get()}" for entry in self.slot_time_entries]
        if slot_times and all(slot_times):
            for item, slot_time in zip(selected_items, slot_times):
                self.tree.item(item, values=(self.tree.item(item, 'values')[0], slot_time))
                # Update record in database
                sql = "UPDATE slot SET slot_time = %s WHERE slot = %s"
                val = (slot_time, self.tree.item(item, 'values')[0])
                self.mycursor.execute(sql, val)
                self.mydb.commit()
        else:
            messagebox.showwarning("Input Error", "Please enter all slot times.")

    def delete_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Delete Error", "Please select a record to delete")
            return
        for selected_item in selected_items:
            # Extract the slot number from the selected item's values
            slot_value = self.tree.item(selected_item, 'values')[0]
            slot_number = slot_value.split()[1]  # Extracts the numeric part from "Slot X"

            self.tree.delete(selected_item)
            # Delete record from database
            sql = "DELETE FROM slot WHERE slot = %s"
            val = (f"Slot {slot_number}",)  # Construct the slot value for deletion
            self.mycursor.execute(sql, val)
            self.mydb.commit()

            messagebox.showinfo("Delete Successful", f"Record '{slot_value}' deleted successfully")

    def update_table(self):
        for child in self.tree.get_children():
            self.tree.delete(child)

        self.mycursor.execute("SELECT * FROM slot")
        records = self.mycursor.fetchall()

        for record in records:
            self.tree.insert('', 'end', values=record)

    def open_generate_window(self):
        # Replace this with your actual code to open the generate window
        self.root.destroy()
        root = tk.Tk()
        app = generate1.GenerateTimetable(root)
        root.mainloop()
        

    def open_duration_window(self):
        self.root.destroy()
        root = tk.Tk()
        app = daterange.DateRangeApp(root)
        root.mainloop()
        

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()

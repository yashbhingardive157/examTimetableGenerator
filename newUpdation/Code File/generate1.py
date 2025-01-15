import random
import mysql.connector
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import holidays
import calendar
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os

class GenerateTimetable:
    def __init__(self, root):
        self.root = root
        self.root.title("Generated Timetable")
        window_width = 800
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

        self.connect_db()
        self.timetable_data = {}
        self.population_size = 10
        self.generations = 20
        self.crossover_rate = 0.8
        self.mutation_rate = 0.1
        self.gap_days = 0

        self.gap_label = tk.Label(self.root, text="Enter gap days between courses:")
        self.gap_label.pack()
        self.gap_entry = tk.Entry(self.root)
        self.gap_entry.pack()

        self.generate_button = tk.Button(self.root, text="Generate Timetable", command=self.generate_timetable)
        self.generate_button.pack(pady=10)

        self.regenerate_button = tk.Button(self.root, text="Regenerate", command=self.regenerate_timetable)
        self.regenerate_button.pack(pady=10)

        self.pdf_button = tk.Button(self.root, text="Generate PDF", command=self.prompt_for_exam_name)
        self.pdf_button.pack(pady=10)

    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="sqluser",
                password="password",
                database="Exam"
            )
            self.cursor = self.conn.cursor()

            self.cursor.execute("SELECT * FROM course")
            self.courses = self.cursor.fetchall()

            self.cursor.execute("SELECT start_date FROM date_range")
            start_date_result = self.cursor.fetchone()
            if start_date_result:
                self.start_date = start_date_result[0].strftime('%Y-%m-%d')

            self.cursor.execute("SELECT slot, slot_time FROM slot")
            self.slots = self.cursor.fetchall()
            self.slot_times = {slot: slot_time for slot, slot_time in self.slots}

            self.india_holidays = holidays.India()

        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            raise

    def generate_timetable(self):
        try:
            self.gap_days = int(self.gap_entry.get())
        except ValueError:
            self.gap_days = 0

        population = self.initialize_population()

        for generation in range(self.generations):
            population = self.evolve_population(population)

        best_timetable = max(population, key=lambda x: x['fitness'])
        self.timetable_data = best_timetable['timetable']

        self.display_timetable()

    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            timetable = self.create_random_timetable()
            population.append({'timetable': timetable, 'fitness': self.fitness(timetable)})
        return population

    def create_random_timetable(self):
        backlog_courses = [course for course in self.courses if course[5] == 'yes']
        regular_courses = [course for course in self.courses if course[5] != 'yes']

        courses = backlog_courses + regular_courses

        course_groups = {}
        for course in courses:
            branch, semester, course_id, course_name, instructor_name, backlog = course
            if course_id not in course_groups:
                course_groups[course_id] = []
            course_groups[course_id].append((branch, semester, course_id, course_name, instructor_name, backlog))

        timetable = {}
        current_date = datetime.strptime(self.start_date, '%Y-%m-%d')

        for course_id, grouped_courses in course_groups.items():
            while True:
                current_date = self.get_next_available_date(current_date)
                slot_time = random.choice(list(self.slot_times.values()))

                if current_date not in timetable:
                    timetable[current_date] = {slot_time: []}
                elif slot_time not in timetable[current_date]:
                    timetable[current_date][slot_time] = []

                if not timetable[current_date][slot_time]:
                    courses_str = " & ".join([f"{course_id} - {course_name} ({instructor_name})" for _, _, course_id, course_name, instructor_name, _ in grouped_courses])
                    timetable[current_date][slot_time].append(courses_str)
                    current_date += timedelta(days=self.gap_days + 1)
                    break
                current_date += timedelta(days=1)

        return timetable



    def get_next_available_date(self, date):
        while date.weekday() == 6 or date.strftime('%Y-%m-%d') in self.india_holidays:
            date += timedelta(days=1)
        return date

    def fitness(self, timetable):
        fitness_score = 0
        scheduled_courses = set()

        for date, slots in timetable.items():
            for slot_time, courses in slots.items():
                for course_info in courses:
                    course_id = course_info.split(' - ')[0]
                    if course_id in scheduled_courses:
                        fitness_score -= 1
                    else:
                        scheduled_courses.add(course_id)
                        fitness_score += 1
        return fitness_score

    def evolve_population(self, population):
        new_population = []

        for _ in range(self.population_size // 2):
            parent1 = self.selection(population)
            parent2 = self.selection(population)

            if random.random() < self.crossover_rate:
                child1, child2 = self.crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2

            if random.random() < self.mutation_rate:
                child1 = self.mutate(child1)
            if random.random() < self.mutation_rate:
                child2 = self.mutate(child2)

            new_population.append({'timetable': child1, 'fitness': self.fitness(child1)})
            new_population.append({'timetable': child2, 'fitness': self.fitness(child2)})

        return new_population

    def selection(self, population):
        total_fitness = sum(individual['fitness'] for individual in population)
        pick = random.uniform(0, total_fitness)
        current = 0

        for individual in population:
            current += individual['fitness']
            if current > pick:
                return individual['timetable']

    def crossover(self, parent1, parent2):
        child1 = {}
        child2 = {}

        for date in parent1.keys():
            if random.random() > 0.5:
                child1[date] = parent1[date]
                child2[date] = parent2[date]
            else:
                child1[date] = parent2[date]
                child2[date] = parent1[date]

        return child1, child2

    def mutate(self, timetable):
        dates = list(timetable.keys())
        date1 = random.choice(dates)
        date2 = random.choice(dates)

        slot1 = random.choice(list(timetable[date1].keys()))
        slot2 = random.choice(list(timetable[date2].keys()))

        timetable[date1][slot1], timetable[date2][slot2] = timetable[date2][slot2], timetable[date1][slot1]

        return timetable

    def display_timetable(self):
        for widget in self.root.winfo_children():
            if widget not in {self.gap_label, self.gap_entry, self.generate_button, self.regenerate_button, self.pdf_button}:
                widget.destroy()

        tree = ttk.Treeview(self.root, columns=['Date'] + list(self.slot_times.values()), show='headings')
        tree.heading('Date', text='Date')
        for slot_time in self.slot_times.values():
            tree.heading(slot_time, text=f'Slot {slot_time}')

        tree.pack(fill=tk.BOTH, expand=True)

        for date in sorted(self.timetable_data.keys()):
            day_name = calendar.day_name[date.weekday()]
            date_day_combined = f"{date.strftime('%Y-%m-%d')} {day_name}"
            row_values = [date_day_combined]
            for slot_time in self.slot_times.values():
                courses = '\n'.join(self.prefix_course_ids(self.timetable_data[date].get(slot_time, [])))
                row_values.append(courses)
            tree.insert('', tk.END, values=row_values)
    
    def regenerate_timetable(self):
        self.generate_timetable()
    def prompt_for_exam_name(self):
        self.exam_name_window = tk.Toplevel(self.root)
        self.exam_name_window.title("Enter Examination Name")
        window_width = 400
        window_height = 200
        screen_width = self.exam_name_window.winfo_screenwidth()
        screen_height = self.exam_name_window.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (window_width / 2)
        y_coordinate = (screen_height / 2) - (window_height / 2)
        self.exam_name_window.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

        self.exam_name_label = tk.Label(self.exam_name_window, text="Enter Examination Name:")
        self.exam_name_label.pack(pady=10)
        self.exam_name_entry = tk.Entry(self.exam_name_window)
        self.exam_name_entry.pack(pady=10)
        self.exam_name_button = tk.Button(self.exam_name_window, text="Generate PDF", command=self.generate_pdf)
        self.exam_name_button.pack(pady=10)

    def set_exam_name(self):
        self.examination_name = self.exam_name_entry.get()
        self.exam_name_window.destroy()
        self.generate_pdf()
   
    def prefix_course_ids(self, courses):
        prefixed_courses = []
        for course in courses:
            course_details = course.split(' - ')
            course_id = course_details[0]
            if "MCA" in course_id:
                course_id = f"CA - {course_id}"
            elif "MSc Computer Science" in course_id:
                course_id = f"CS - {course_id}"
            prefixed_courses.append(f"{course_id} - {' - '.join(course_details[1:])}")
        return prefixed_courses

    def generate_pdf(self):
        home = os.path.expanduser("~")
        downloads_folder = os.path.join(home, "Downloads")
        pdf_filename = os.path.join(downloads_folder, "exam_timetable.pdf")

        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4

        heading1 = "Savitribai Phule Pune University"
        heading2 = "Department of Computer Science"
        exam_name = self.exam_name_entry.get()  # Retrieve the exam name from the entry widget

        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(width / 2.0, height - 40, heading1)

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 60, heading2)

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2.0, height - 80, exam_name)  # Use the retrieved exam name

        c.setFont("Helvetica", 12)
        headers = ["Date, Day"] + list(self.slot_times.values())
        col_widths = [150] + [200] * len(self.slot_times)
        row_height = 20
        x_offset = (width - sum(col_widths)) / 2
        y_offset = height - 120

        def draw_grid(x_offset, y_offset, row_height, col_widths, rows):
            c.setStrokeColor(colors.black)
            c.setLineWidth(0.5)

            for col_num, col_width in enumerate(col_widths):
                x = x_offset + sum(col_widths[:col_num])
                c.line(x, y_offset, x, y_offset - row_height * (len(rows) + 1))

            y = y_offset
            c.line(x_offset, y, x_offset + sum(col_widths), y)

            c.setFont("Helvetica-Bold", 12)
            for col_num, header in enumerate(headers):
                x = x_offset + sum(col_widths[:col_num])
                c.drawCentredString(x + col_widths[col_num] / 2, y - row_height / 2, header)

            y -= row_height
            c.line(x_offset, y, x_offset + sum(col_widths), y)

            c.setFont("Helvetica", 10)
            for row in rows:
                for col_num, cell in enumerate(row):
                    x = x_offset + sum(col_widths[:col_num])
                    c.drawCentredString(x + col_widths[col_num] / 2, y - row_height / 2, cell)
                y -= row_height
                c.line(x_offset, y, x_offset + sum(col_widths), y)

            c.line(x_offset + sum(col_widths), y_offset, x_offset + sum(col_widths), y_offset - row_height * (len(rows) + 1))

        rows = []
        for date in sorted(self.timetable_data.keys()):
            day_name = calendar.day_name[date.weekday()]
            date_day_combined = f"{date.strftime('%Y-%m-%d')} {day_name}"
            row_values = [date_day_combined]
            for slot_time in self.slot_times.values():
                courses = '\n'.join(self.prefix_course_ids(self.timetable_data[date].get(slot_time, [])))
                row_values.append(courses)
            rows.append(row_values)

        draw_grid(x_offset, y_offset, row_height, col_widths, rows)

        c.save()

        messagebox.showinfo("PDF Generated", f"Exam timetable has been generated and saved to {pdf_filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GenerateTimetable(root)
    root.mainloop()

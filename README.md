# Examination Timetable Generator

A Python application built during my On Job Training (OJT) in Semester III at Savitribai Phule Pune University, Computer Science Department (PUCSD).

## About

This project was developed to solve the real-world challenge of generating conflict-free examination timetables for our department. The application helps automate the exam scheduling process while avoiding conflicts and considering constraints like holidays and gaps between exams.

## Features

- Course management by program (MSc Computer Science, MCA) and semester
- Examination date range selection with holiday detection
- Customizable time slots for exams
- Smart timetable generation using genetic algorithm
- PDF export functionality

## What I Learned

Developing this project provided practical experience with:
- Building GUI applications using Tkinter
- Database integration with MySQL
- Working with dates and calendars
- Implementing genetic algorithms for scheduling problems
- PDF generation for reports

## Setup

### Database Configuration

Create the required MySQL database and tables:

```sql
CREATE DATABASE IF NOT EXISTS Exam;
USE Exam;

CREATE TABLE IF NOT EXISTS course (
    branch VARCHAR(20) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    course_id VARCHAR(20) NOT NULL,
    course_name VARCHAR(20) NOT NULL,
    instructor_name VARCHAR(20) NOT NULL,
    backlog VARCHAR(20),
    PRIMARY KEY (branch, course_id)
);

CREATE TABLE IF NOT EXISTS date_range (
    start_date DATE,
    end_date DATE
);

CREATE TABLE IF NOT EXISTS slot (
    slot VARCHAR(10),
    slot_time VARCHAR(20)
);
```

### Running the Application

1. Ensure you have the required Python packages:
   - mysql-connector-python
   - tkcalendar
   - holidays
   - pillow
   - reportlab

2. Start the application:
```
python welcome.py
```

3. Follow the step-by-step wizard:
   - Add courses
   - Set exam dates
   - Configure time slots
   - Generate and export timetable

## Acknowledgments

Special thanks to the Department of Computer Science, SPPU for the opportunity to work on this practical project as part of my academic curriculum.

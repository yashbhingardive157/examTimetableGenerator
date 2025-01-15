In "Examination Timetable Generarator" for storing and retrieving data we used in our project is "mySQL" DATABASE.


//DATABASE "Exam" need to create using following query.

--CREATE DATABASE IF NOT EXISTS Exam;



//inside the DATABASE "Exam" below table must needs to create using following below mySQL queries.

--USE Exam;

--CREATE TABLE IF NOT EXISTS course(branch varchar(20) not null,semester varchar(20) not null,course_id varchar(20) not null,course_name varchar(20) not null,instructor_name varchar(20) not null,backlog varchar(20),PRIMARY KEY (branch, course_id));
--CREATE TABLE IF NOT EXISTS date_range(start_date date,end_date date);
--CREATE TABLE IF NOT EXISTS slot(slot varchar(10),slot_time varchar(20));


package com.vignan.service;

import com.vignan.model.Student;
import org.springframework.stereotype.Service;
import java.util.ArrayList;
import java.util.List;

@Service
public class StudentService {
    private final List<Student> students = new ArrayList<>(List.of(
        new Student(1, "Aarav", "CSE", 3),
        new Student(2, "Diya", "ECE", 2),
        new Student(3, "Rohan", "IT", 3)
    ));
    public List<Student> findAll() { return students; }
    public void add(Student student) {
        int nextId = students.stream().mapToInt(Student::getId).max().orElse(0) + 1;
        student.setId(nextId);
        students.add(student);
    }
}

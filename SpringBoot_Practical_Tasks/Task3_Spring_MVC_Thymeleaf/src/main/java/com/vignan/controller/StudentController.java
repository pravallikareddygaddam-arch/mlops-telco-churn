package com.vignan.controller;

import com.vignan.model.Student;
import com.vignan.service.StudentService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class StudentController {
    private final StudentService service;
    public StudentController(StudentService service) { this.service = service; }

    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("students", service.findAll());
        model.addAttribute("student", new Student());
        return "students";
    }
    @PostMapping("/students")
    public String addStudent(@ModelAttribute Student student) {
        service.add(student);
        return "redirect:/";
    }
}

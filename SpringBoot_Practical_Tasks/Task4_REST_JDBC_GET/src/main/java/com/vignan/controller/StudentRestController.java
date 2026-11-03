package com.vignan.controller;

import com.vignan.model.Student;
import com.vignan.repository.StudentRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/students")
public class StudentRestController {
    private final StudentRepository repository;
    public StudentRestController(StudentRepository repository) { this.repository = repository; }

    @GetMapping
    public List<Student> getAll() { return repository.findAll(); }

    @GetMapping("/{id}")
    public ResponseEntity<Student> getById(@PathVariable int id) {
        return repository.findById(id).map(ResponseEntity::ok)
            .orElseGet(() -> ResponseEntity.notFound().build());
    }
}

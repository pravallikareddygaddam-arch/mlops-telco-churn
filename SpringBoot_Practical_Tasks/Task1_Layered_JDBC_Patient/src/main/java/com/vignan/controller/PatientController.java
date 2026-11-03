package com.vignan.controller;

import com.vignan.model.Patient;
import com.vignan.service.PatientService;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/patients")
public class PatientController {
    private final PatientService service;
    public PatientController(PatientService service) { this.service = service; }

    @PostMapping
    public String add(@RequestBody Patient patient) {
        service.add(patient);
        return "Patient added successfully";
    }
    @GetMapping
    public List<Patient> show() { return service.show(); }
}

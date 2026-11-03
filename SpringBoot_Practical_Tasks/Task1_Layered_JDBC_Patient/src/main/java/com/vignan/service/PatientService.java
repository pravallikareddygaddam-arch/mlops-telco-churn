package com.vignan.service;

import com.vignan.model.Patient;
import com.vignan.repository.PatientRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class PatientService {
    private final PatientRepository repository;
    public PatientService(PatientRepository repository) { this.repository = repository; }
    public int add(Patient patient) { return repository.add(patient); }
    public List<Patient> show() { return repository.show(); }
}

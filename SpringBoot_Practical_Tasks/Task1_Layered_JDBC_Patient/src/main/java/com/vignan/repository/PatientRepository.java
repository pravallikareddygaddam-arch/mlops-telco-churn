package com.vignan.repository;

import com.vignan.model.Patient;
import java.util.List;

public interface PatientRepository {
    int add(Patient patient);
    List<Patient> show();
}

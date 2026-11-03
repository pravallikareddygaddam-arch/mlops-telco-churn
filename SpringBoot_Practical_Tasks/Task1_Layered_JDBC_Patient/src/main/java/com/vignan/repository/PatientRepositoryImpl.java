package com.vignan.repository;

import com.vignan.model.Patient;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public class PatientRepositoryImpl implements PatientRepository {
    private final JdbcTemplate jdbcTemplate;
    public PatientRepositoryImpl(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }
    private final RowMapper<Patient> mapper = (rs, rowNum) ->
        new Patient(rs.getInt("id"), rs.getString("name"),
                    rs.getInt("age"), rs.getString("disease"));

    @Override
    public int add(Patient patient) {
        String sql = "INSERT INTO patients(name, age, disease) VALUES (?, ?, ?)";
        return jdbcTemplate.update(sql, patient.getName(), patient.getAge(), patient.getDisease());
    }
    @Override
    public List<Patient> show() {
        return jdbcTemplate.query("SELECT id, name, age, disease FROM patients ORDER BY id", mapper);
    }
}

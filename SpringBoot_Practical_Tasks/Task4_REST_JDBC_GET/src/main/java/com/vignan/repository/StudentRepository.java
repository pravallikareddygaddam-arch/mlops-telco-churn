package com.vignan.repository;

import com.vignan.model.Student;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public class StudentRepository {
    private final JdbcTemplate jdbc;
    public StudentRepository(JdbcTemplate jdbc) { this.jdbc = jdbc; }
    private final RowMapper<Student> mapper = (rs, n) ->
        new Student(rs.getInt("id"), rs.getString("name"),
                    rs.getString("department"), rs.getInt("year"));
    public List<Student> findAll() {
        return jdbc.query("SELECT id,name,department,year FROM students ORDER BY id", mapper);
    }
    public Optional<Student> findById(int id) {
        List<Student> rows = jdbc.query("SELECT id,name,department,year FROM students WHERE id=?", mapper, id);
        return rows.stream().findFirst();
    }
}

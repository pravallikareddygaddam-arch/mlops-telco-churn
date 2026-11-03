package com.vignan.config;

import com.vignan.model.Student;
import com.vignan.repository.StudentRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataLoader {
    @Bean
    CommandLineRunner loadStudents(StudentRepository repository) {
        return args -> {
            if (repository.count() == 0) {
                repository.save(new Student("Aarav", "CSE", 3));
                repository.save(new Student("Diya", "ECE", 2));
                repository.save(new Student("Rohan", "IT", 3));
                repository.save(new Student("Meera", "CSE", 4));
                repository.save(new Student("Kiran", "EEE", 2));
            }
        };
    }
}

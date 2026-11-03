package com.vignan;

import com.vignan.model.Patient;
import com.vignan.service.PatientService;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class Task1Application {
    public static void main(String[] args) {
        SpringApplication.run(Task1Application.class, args);
    }

    @Bean
    CommandLineRunner demo(PatientService service) {
        return args -> {
            service.add(new Patient("Aarav", 22, "Fever"));
            service.add(new Patient("Diya", 21, "Headache"));
            System.out.println("\n========== PATIENT RECORDS ==========");
            service.show().forEach(System.out::println);
        };
    }
}

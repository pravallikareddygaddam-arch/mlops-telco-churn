package com.vignan;

import com.vignan.model.Customer;
import com.vignan.model.CustomerOrder;
import com.vignan.repository.CustomerRepository;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@SpringBootApplication
public class Task2Application {
    public static void main(String[] args) { SpringApplication.run(Task2Application.class, args); }

    @Bean
    CommandLineRunner demo(CustomerRepository customers, HqlDemo hqlDemo) {
        return args -> {
            if (customers.count() == 0) {
                Customer c1 = new Customer("Aarav", "aarav@example.com");
                c1.addOrder(new CustomerOrder("Laptop", 65000.0));
                c1.addOrder(new CustomerOrder("Mouse", 900.0));
                Customer c2 = new Customer("Diya", "diya@example.com");
                c2.addOrder(new CustomerOrder("Keyboard", 1800.0));
                customers.saveAll(List.of(c1, c2));
            }
            hqlDemo.printCustomersAndOrders();
        };
    }
}

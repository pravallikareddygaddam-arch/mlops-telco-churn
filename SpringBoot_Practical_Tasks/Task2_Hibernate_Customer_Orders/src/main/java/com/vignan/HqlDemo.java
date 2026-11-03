package com.vignan;

import com.vignan.model.Customer;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Component
public class HqlDemo {
    @PersistenceContext private EntityManager entityManager;

    @Transactional(readOnly = true)
    public void printCustomersAndOrders() {
        List<Customer> result = entityManager.createQuery(
            "SELECT DISTINCT c FROM Customer c LEFT JOIN FETCH c.orders", Customer.class
        ).getResultList();

        System.out.println("\n========== CUSTOMERS AND THEIR ORDERS (HQL) ==========");
        for (Customer customer : result) {
            System.out.println(customer);
            customer.getOrders().forEach(System.out::println);
        }
    }
}

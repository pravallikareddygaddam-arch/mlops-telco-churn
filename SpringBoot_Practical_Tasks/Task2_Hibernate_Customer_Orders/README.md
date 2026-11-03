# Task 2 – Hibernate One-to-Many / Many-to-One

`Customer` has many `CustomerOrder` records (`@OneToMany`). Each order belongs to one customer (`@ManyToOne`). Hibernate creates/updates the tables automatically.

## Run
Set the MySQL password in `application.properties`, then run `mvn spring-boot:run`. The application inserts two customers and three orders once (when the customer table is empty), then prints customers and their orders using HQL.

## HQL examples
```java
// All customers
from Customer

// Customer and order data in one query
SELECT DISTINCT c FROM Customer c LEFT JOIN FETCH c.orders

// Orders for customer id 1
SELECT o FROM CustomerOrder o WHERE o.customer.id = :customerId
```
Generated SQL is printed because `spring.jpa.show-sql=true` and `hibernate.format_sql=true`.

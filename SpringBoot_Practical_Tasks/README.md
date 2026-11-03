# Spring Boot Practical Assignments – Complete Source

This bundle contains five separate Maven projects:
1. Layered architecture + JdbcTemplate patient management
2. Hibernate Customer–Orders one-to-many / many-to-one mapping + HQL
3. Spring MVC + Thymeleaf + Bootstrap
4. REST GET API using JdbcTemplate + five MySQL records
5. REST CRUD API using Spring Data JPA / Hibernate + five MySQL records

## Requirements
- JDK 17 or later
- Maven 3.9 or later
- MySQL Server 8 or later
- Postman (for API testing)

## MySQL configuration
All database-backed projects use the database name `spring_practical` and MySQL user `root`.
In each applicable project's `src/main/resources/application.properties`, change:
`spring.datasource.password=YOUR_MYSQL_PASSWORD`
to your actual local MySQL password. If your MySQL username differs, change that too.

The JDBC URL includes `createDatabaseIfNotExist=true`. The MySQL user must have permission to create the database. Otherwise create it manually:
```sql
CREATE DATABASE spring_practical;
```

## Run a project
Open a terminal in the required project folder and run:
```bash
mvn spring-boot:run
```
Run only one project at a time if you prefer; each uses a separate port:
- Task 1: 8081
- Task 2: 8082
- Task 3: 8083
- Task 4: 8084
- Task 5: 8085

Each subfolder has its own README with task-specific instructions and endpoints.

## Notes
- Task 3 intentionally uses an in-memory list to demonstrate MVC, Model, Thymeleaf and Bootstrap without introducing a database requirement not specified in that task.
- Task 1's CommandLineRunner adds two demonstration patients every time the application starts. Remove or change those sample `service.add(...)` lines if you do not want repeated demo rows.
- Task 2 seeds its sample customers and orders only when the customer table is empty.
- Task 4 uses `INSERT IGNORE` to maintain five stable sample rows on repeated starts.
- Task 5 seeds five students only when the JPA table is empty.

# Task 1 – Layered Architecture with JdbcTemplate (Patient Management)

## Flow
`Controller -> Service -> Repository -> JdbcTemplate -> MySQL`

Packages: `model`, `component` (configuration bean), `repository`, `controller`, `service`, `config`.

## Run
1. Install JDK 17+, Maven 3.9+, and MySQL 8+.
2. Start MySQL. Edit `src/main/resources/application.properties` and replace `YOUR_MYSQL_PASSWORD`.
3. Open a terminal in this folder and run: `mvn spring-boot:run`.
4. The CommandLineRunner inserts two sample patients and prints all rows. Re-running adds the sample rows again.
5. API: `GET http://localhost:8081/api/patients`; add with `POST http://localhost:8081/api/patients` and JSON `{"name":"Ravi","age":23,"disease":"Cold"}`.

The database `spring_practical` is created automatically by the JDBC URL if the MySQL user has permission.

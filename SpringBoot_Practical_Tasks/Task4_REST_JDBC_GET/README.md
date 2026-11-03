# Task 4 – REST GET API using JdbcTemplate

## Run
1. Set MySQL password in `application.properties`.
2. Run `mvn spring-boot:run`.
3. `schema.sql` creates the table and `data.sql` inserts five sample records using `INSERT IGNORE`.

## Test
- Browser/Postman: `GET http://localhost:8084/api/students`
- Single record: `GET http://localhost:8084/api/students/1`
- Unknown ID returns HTTP 404.

Postman: choose GET, enter the URL, and click Send. Spring serializes the Java objects to JSON.

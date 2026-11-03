# Task 5 – REST CRUD using Spring Data JPA / Hibernate

## Run
Set the MySQL password in `application.properties`, then run `mvn spring-boot:run`. Hibernate creates `jpa_students`; a startup loader inserts five sample records only when the table is empty.

## CRUD endpoints
Base URL: `http://localhost:8085/api/students`

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/students` | Read all |
| GET | `/api/students/1` | Read one |
| POST | `/api/students` | Create |
| PUT | `/api/students/1` | Update |
| DELETE | `/api/students/1` | Delete |

POST/PUT JSON:
```json
{
  "name": "Ananya",
  "department": "CSE",
  "year": 3
}
```
Use Postman with `Content-Type: application/json`. DELETE returns HTTP 204; missing IDs return HTTP 404.

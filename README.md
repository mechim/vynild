# Vynild - Music Reviewing and Discussion App

## 1. Start Up Instructions
run
 ```
docker-compose up --build 
```
in Postman create a user and then have fun.

## 2. Diagram
![latest-diagram](https://github.com/user-attachments/assets/313f4991-c982-42aa-93ff-ee4120ad7124)

## 3. API Documentation
This API provides services for managing users, music reviews, and related data. Below are the endpoints, organized by service.

---

## User Service

### Endpoints

#### 1. List Users
- **URL:** `{{user_service_url}}users/list?id={id}`
- **Method:** GET
- **Parameters:**
  - `id` (optional): ID of the user to fetch.
- **Description:** Retrieves a list of users or a specific user if an ID is provided.

#### 2. Create User
- **URL:** `{{user_service_url}}users/create`
- **Method:** POST
- **Body:**
  ```json
  {
      "username": "JohnDoe",
      "password": "12345"
  }
  ```
- **Description:** Creates a new user with the provided username and password.

#### 3. Status Check
- **URL:** `{{user_service_url}}utilities/status`
- **Method:** GET
- **Description:** Checks the status of the User Service.

#### 4. Sleep
- **URL:** `{{user_service_url}}utilities/sleep`
- **Method:** GET
- **Description:** An endpoint for testing server delay. There are duplicates of this endpoint for testing.

---

## Review Service

### Endpoints

#### 1. Create Review
- **URL:** `{{review_service_url}}reviews/create`
- **Method:** POST
- **Body:**
  ```json
  {
      "user_id": "1",
      "release": "1",
      "review_text": "me likey",
      "review_mark": "10"
  }
  ```
- **Description:** Creates a new review for a specific release by a user.

#### 2. List Reviews
- **URL:** `{{review_service_url}}reviews/list`
- **Method:** GET
- **Description:** Retrieves a list of all reviews.

#### 3. List Releases
- **URL:** `{{review_service_url}}releases/list?id={id}`
- **Method:** GET
- **Parameters:**
  - `id` (optional): ID of the release to fetch.
- **Description:** Retrieves a list of releases or a specific release if an ID is provided.

#### 4. Create Release
- **URL:** `{{review_service_url}}releases/create`
- **Method:** POST
- **Body:**
  ```json
  {
      "release_name": "To Pimp A Butterfly",
      "artist_name": "Kendrick Lamar"
  }
  ```
- **Description:** Creates a new music release.

#### 5. Discussion Identifier
- **URL:** `{{review_service_url}}releases/1`
- **Method:** GET
- **Description:** Retrieves discussion identifier details for the specified release ID.

#### 6. Status Check
- **URL:** `{{review_service_url}}utilities/status`
- **Method:** GET
- **Description:** Checks the status of the Review Service.

---

## Gateway Service

### Endpoints

#### 1. Ping
- **URL:** `http://localhost:8080/ping`
- **Method:** GET
- **Description:** Pings the gateway to check connectivity.

---

### Variables

- `user_service_url`: Base URL for the User Service.
- `review_service_url`: Base URL for the Review Service.
- `gateway_url`: Base URL for the Gateway Service.

---

This API uses standard HTTP status codes for indicating success or error. Ensure to replace variable placeholders (`{{user_service_url}}`, etc.) with actual URLs when making requests.

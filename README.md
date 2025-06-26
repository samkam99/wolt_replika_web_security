# Wolt Replica – Web Application Security Project

This project was developed as part of my studies at KEA (Copenhagen School of Design and Technology). It simulates a Wolt-style delivery platform with a strong focus on **web application security**.

The app is built with **Flask**, containerized using **Docker**, and includes security best practices aligned with the OWASP Top 10.

---

## 💼 My role in the project

I worked on:

- Implementing **rate limiting** using Flask-Limiter
- Securing user input with **regular expressions** for names, emails, and passwords
- Handling **secure sessions** via Redis (`flask_session`)
- Managing **database setup** and **test data seeding** with `seed.py`
- Version control with Git & GitHub
- Testing endpoints using Postman

---

## 🔐 Key security measures

- ✅ Rate limiting on selected endpoints to prevent abuse
- ✅ Input validation using strict regex patterns
- ✅ CSRF protection through Flask session handling
- ✅ Secure session storage using Redis
- ✅ Full Docker isolation via `docker-compose`

---

## 🧱 Technologies used

- Python (Flask)
- HTML / CSS / JavaScript
- Docker & Docker Compose
- MySQL & phpMyAdmin
- Redis (for sessions)
- ArangoDB (experimental / bonus)
- Postman (for API testing)

---

## ▶️ Getting started

```bash
# 1. Start all services
docker-compose up -d

# 2. Seed test data
docker exec -it wolt_flask python3 seed.py

# 3. Open the app
http://localhost


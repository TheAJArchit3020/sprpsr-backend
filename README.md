# sprpsr Backend

This is the backend service for the **sprpsr** application, built with Flask, MongoDB, and Firebase for authentication. It provides RESTful APIs for user management, event creation and participation, chat, and more.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- User authentication (Firebase, JWT)
- Event creation, joining, and management
- Event requests (for private events)
- Real-time chat for events
- User profile management
- Ratings and feedback
- Swagger/OpenAPI documentation

---

## Tech Stack

- **Python 3**
- **Flask** (REST API framework)
- **MongoDB** (Database)
- **Firebase Admin SDK** (Authentication)
- **PyJWT** (JWT tokens)
- **Flasgger/APISpec** (API docs)
- **Docker** (optional, for deployment)

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd sprpsr
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the root directory with the following:
     ```
     MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/sprpsr_db
     ```
   - (Refer to your MongoDB provider for the correct URI.)

5. **Add Firebase credentials:**
   - Place your `firebase-credentials.json` file in the project root.
   - This file should be a Firebase service account key (never commit this file to version control).

---

## Running the Application

```bash
python app.py
```

- The server will start on `http://localhost:8890/` by default.

---

## API Documentation

- Interactive API docs are available at:  
  `http://localhost:8890/docs`

---

## Project Structure

```
sprpsr/
│
├── app.py                  # Main entry point
├── requirements.txt        # Python dependencies
├── firebase-credentials.json  # Firebase Admin SDK credentials (not committed)
├── src/
│   ├── config/             # Configuration (DB, Swagger, etc.)
│   ├── controllers/        # Business logic for each resource
│   ├── middleware/         # Auth and other middleware
│   ├── models/             # Database models
│   ├── routes/             # API route blueprints
│   ├── services/           # Service layer (business logic)
│   └── utils/              # Utility functions (e.g., Firebase)
└── ...
```

---

## Deployment

- See `deployment.md` (to be created) for deployment instructions, including Dockerization and environment setup.

---

## Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

---

## License

This project is proprietary and confidential. All rights reserved. 
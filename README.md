# flood-prediction-system
Flash Flood Early Warning and Risk Prediction System
# Flash Flood Risk Prediction and Early Warning System

## 1. Project Overview

Flash floods are sudden and highly destructive natural disasters that can occur within a short period of time. Because of their rapid onset, traditional flood monitoring and warning methods may not always provide sufficient time for people to respond.

This project proposes a **Flash Flood Risk Prediction and Early Warning System** that uses rainfall and water-level information to estimate the current flood risk for selected districts of West Bengal.

The prototype provides a software-based platform where environmental data can be processed, analyzed, and converted into an understandable flood-risk level such as:

* LOW
* MEDIUM
* HIGH

The system is designed as a web-based application with a separate frontend and Node.js/Express backend.

## 2. Problem Statement

Flash floods are particularly challenging because:

* They can develop very quickly.
* The available response time can be short.
* Rainfall intensity can change rapidly.
* Water levels can rise suddenly.
* People may not have an easily understandable indication of the current risk.
* Raw environmental data is difficult for ordinary users to interpret.

Therefore, the objective of this project is to provide a system that converts relevant environmental parameters into a simple and understandable flood-risk assessment.

## 3. Proposed Solution

The proposed system follows this workflow:

Environmental Data
       ↓
Frontend
       ↓
Node.js / Express Backend
       ↓
Input Validation
       ↓
Prediction Module
       ↓
Flood Risk Assessment
       ↓
Risk + Confidence Response
       ↓
Frontend Dashboard

The backend receives environmental parameters, validates them, processes them through the prediction module, and returns the predicted flood-risk level to the frontend.

The prediction module is designed so that the current prototype can later be replaced by a trained Machine Learning model without requiring a complete restructuring of the backend.

## 4. Target Locations

The current prototype supports the following five locations:

1. **Jalpaiguri**
2. **Cooch Behar**
3. **Alipurduar**
4. **Kalimpong**
5. **Malda**

These locations are configured in the backend location configuration.

## 5. Key Features

### 5.1 Flood Risk Prediction

The system accepts environmental parameters such as:

* Rainfall
* Soil moisture

and produces a corresponding flood-risk assessment.

### 5.2 Risk Classification

The current prototype classifies the input into risk levels including:

* LOW
* MEDIUM
* HIGH

### 5.3 Input Validation

The backend validates incoming prediction requests to ensure that:

* Required values are present.
* Rainfall is numeric.
* Water level is numeric.
* Values are non-negative.

Invalid requests return an appropriate error response instead of being processed.

### 5.4 Location Support

The application currently supports five predefined locations:

* Jalpaiguri
* Cooch Behar
* Alipurduar
* Kalimpong
* Malda

### 5.5 Live Weather Data

The backend can retrieve live weather-related data using an external weather service through Axios.

The project uses **Open-Meteo** for weather data retrieval.

### 5.6 API-Based Architecture

The frontend and backend communicate through REST APIs.

This makes the system modular and allows the frontend and prediction logic to be developed independently.

# 6. Technology Stack

## Frontend

The frontend is responsible for:

* User interaction
* Displaying environmental information
* Sending prediction requests
* Displaying the predicted risk level

## Backend

The backend uses:

* **Node.js**
* **Express.js**
* **Axios**

The backend runs on:
Port: 5000

## Data / Prediction

The prediction pipeline currently uses the backend prediction module.

The architecture is designed to allow the prediction module to be replaced by a trained Machine Learning model in the future.

## External Data Source

Weather information is obtained using:

**Open-Meteo API**

# 7. System Architecture

The project follows a client-server architecture.

```text
                   ┌──────────────────────┐
                   │      User            │
                   │   Web Interface      │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │      Frontend        │
                   └──────────┬───────────┘
                              │
                        HTTP Requests
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Node.js + Express    │
                   │      Backend         │
                   └──────────┬───────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌─────────────────┐       ┌─────────────────┐
        │ Input Validation│       │ Live Weather    │
        │                 │       │ Data / API      │
        └────────┬────────┘       └────────┬────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                   ┌──────────────────────┐
                   │ Prediction Module    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Risk Assessment      │
                   │ LOW / MEDIUM / HIGH  │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ JSON API Response    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Frontend Dashboard   │
                   └──────────────────────┘
```

# 8. Project Structure

The repository is organized into separate frontend and backend components.

A typical structure is:

```text
project-root/
│
├── backend/
│   ├── server.js
│   ├── prediction.js
│   ├── locations.js
│   ├── package.json
│   ├── package-lock.json
│   └── ...
│
├── frontend/
│   └── ...
│
├── README.md
└── ...
```

### Important backend files

### `server.js`

This is the main Express server.

It is responsible for:

* Starting the backend server.
* Defining API routes.
* Receiving requests.
* Validating input.
* Calling the prediction module.
* Returning responses.

### `prediction.js`

This file contains the flood-risk prediction logic.

The module is intentionally separated from the server so that it can later be replaced with an ML-based prediction model.

### `locations.js`

This file contains the supported locations and their corresponding configuration information.

The current supported locations are:

```text
Jalpaiguri
Cooch Behar
Alipurduar
Kalimpong
Malda
```

---

# 9. Prerequisites

Before deploying the project, install the following software.

## 9.1 Node.js

Install Node.js on the machine.

Verify the installation:

```bash
node --version
```

Then verify npm:

```bash
npm --version
```

If both commands return version numbers, Node.js and npm are installed correctly.

---

# 10. Clone the Repository

Open a terminal and clone the GitHub repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project directory:

```bash
cd <PROJECT_FOLDER_NAME>
```

If the repository is private, the person cloning it must have appropriate access to the repository.

---

# 11. Backend Installation

Move into the backend directory:

```bash
cd backend
```

Install the required Node.js dependencies:

```bash
npm install
```

This installs the packages specified in `package.json`.

After installation, the backend is ready to run.

---

# 12. Starting the Backend

From the `backend` directory, start the server using:

```bash
node server.js
```

If the project contains an appropriate npm start script, the server can also be started using:

```bash
npm start
```

A successful startup should display a message indicating that the server is running on:

```text
http://localhost:5000
```

---

# 13. Backend API

The backend exposes several API endpoints.

## 13.1 Health Check

### Endpoint

```text
GET /api/health
```

### Purpose

This endpoint verifies that the backend server is running correctly.

### Example

```text
http://localhost:5000/api/health
```

A successful response indicates that the backend is operational.

---

# 14. Prediction API

## Endpoint

```text
POST /api/predict
```

This endpoint receives environmental parameters and returns the predicted flood-risk level.

### Example Request

```json
{
  "rainfall": 120,
  "waterLevel": 4.5
}
```

### Example Response

```json
{
  "risk": "HIGH",
  "confidence": null
}
```

The exact prediction depends on the implemented prediction logic and input values.

---

# 15. Input Validation

The prediction endpoint validates the received data before performing prediction.

For example, rainfall and water level must be numeric and non-negative.

An invalid request such as:

```json
{
  "rainfall": -10,
  "waterLevel": 4
}
```

will be rejected instead of being processed as a valid prediction.

Similarly, missing required parameters will result in an error response.

This prevents invalid data from entering the prediction pipeline.

---

# 16. Location API

The backend also provides access to the supported locations.

### Endpoint

```text
GET /api/locations
```

This endpoint returns the locations configured in the backend.

The current supported locations are:

```text
Jalpaiguri
Cooch Behar
Alipurduar
Kalimpong
Malda
```

---

# 17. Live Weather Data

The backend can obtain weather-related information from the **Open-Meteo API**.

The backend uses Axios to communicate with the external service.

The general data flow is:

```text
Frontend
   ↓
Backend
   ↓
Open-Meteo API
   ↓
Weather Data
   ↓
Backend Processing
   ↓
Frontend
```

This approach prevents the frontend from having to directly manage the external API communication.

---

# 18. Running the Complete Application

To run the complete application locally:

### Step 1 — Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

### Step 2 — Enter the project

```bash
cd <PROJECT_FOLDER_NAME>
```

### Step 3 — Enter the backend

```bash
cd backend
```

### Step 4 — Install backend dependencies

```bash
npm install
```

### Step 5 — Start the backend

```bash
node server.js
```

The backend should now be available at:

```text
http://localhost:5000
```

### Step 6 — Start the frontend

Open a **second terminal** and navigate to the frontend directory.

For example:

```bash
cd <PROJECT_FOLDER_NAME>/frontend
```

Then start the frontend using the command specified by its frontend framework.

The frontend should then provide the user interface through which the backend APIs can be accessed.

---

# 19. Deployment

The application can be deployed by hosting the frontend and backend as separate services.

## Backend Deployment

The Node.js/Express backend can be deployed on a cloud service that supports Node.js applications.

The deployment process is generally:

```text
GitHub Repository
       ↓
Cloud Hosting Service
       ↓
Install Dependencies
       ↓
Start Node.js Server
       ↓
Public Backend URL
```

The production server should listen on the port supplied by the hosting platform.

For example, the backend should use the environment-provided port:

```javascript
const PORT = process.env.PORT || 5000;
```

This allows the application to run locally on port `5000` while also supporting cloud deployment.

After deployment, the backend will have a public URL such as:

```text
https://your-backend-domain.example
```

The frontend must then use this deployed backend URL instead of:

```text
http://localhost:5000
```

---

# 20. Frontend Deployment

The frontend can be deployed separately using a suitable web-hosting platform.

The deployment process is:

```text
Frontend Source Code
        ↓
Build Application
        ↓
Deploy to Hosting Platform
        ↓
Public Website URL
```

Before deployment, make sure the frontend API configuration points to the deployed backend URL.

For example:

```text
Development:
http://localhost:5000

Production:
https://your-deployed-backend-url
```

---

# 21. Environment Variables

If API URLs, API keys, or other configuration values are added later, they should be stored using environment variables rather than hard-coding them into the source code.

For example:

```text
PORT=5000
API_URL=https://your-backend-url
```

Do **not** commit private API keys, passwords, tokens, or other secrets to GitHub.

If an environment file is used, add it to `.gitignore`.

Example:

```text
.env
node_modules/
```

---

# 22. Production Deployment Workflow

The recommended deployment workflow is:

```text
1. Push project to GitHub
          ↓
2. Connect repository to hosting platform
          ↓
3. Configure environment variables
          ↓
4. Install dependencies
          ↓
5. Build frontend if required
          ↓
6. Start backend
          ↓
7. Obtain deployed backend URL
          ↓
8. Configure frontend with backend URL
          ↓
9. Deploy frontend
          ↓
10. Test complete application
```

---

# 23. Testing the Backend

Before deploying the complete application, verify the backend independently.

### Test health endpoint

Open:

```text
http://localhost:5000/api/health
```

### Test prediction endpoint

Send a POST request to:

```text
http://localhost:5000/api/predict
```

with:

```json
{
  "rainfall": 120,
  "waterLevel": 4.5
}
```

Verify that the server returns a valid JSON response containing the risk classification.

---

# 24. Error Handling

The backend handles invalid requests instead of allowing them to reach the prediction module unchecked.

Examples of invalid inputs include:

* Missing rainfall.
* Missing water level.
* Non-numeric rainfall.
* Non-numeric water level.
* Negative rainfall.
* Negative water level.

This makes the API more reliable and provides a clear separation between input handling and prediction.

---

# 25. Machine Learning Integration

The current architecture is designed to support future Machine Learning integration.

The backend follows the structure:

```text
Request
   ↓
server.js
   ↓
Input Validation
   ↓
prediction.js
   ↓
Risk Result
```

A future trained ML model can replace or be integrated into `prediction.js`.

The server itself does not need to be completely rewritten.

A future ML pipeline could use features such as:

* Rainfall intensity
* Accumulated rainfall
* Water level
* Rate of water-level increase
* Temperature
* Humidity
* Historical flood information
* Geographic information
* Other meteorological parameters

The ML model could then return:

```json
{
  "risk": "HIGH",
  "confidence": 0.91
}
```

This is why the current API response structure already contains a `confidence` field.

---

# 26. Limitations of the Current Prototype

The current system is a prototype and should not be treated as an official disaster-warning system.

Current limitations include:

* The prediction module is not yet a fully trained production ML model.
* The supported geographic locations are currently limited to five districts.
* The quality of prediction depends on the quality and availability of environmental data.
* External weather services may have availability and API limitations.
* Real-world disaster prediction requires significantly more historical and real-time data.
* The prototype requires further validation against historical flood events before operational deployment.

---

# 27. Future Enhancements

Possible future improvements include:

1. Training and integrating a dedicated Machine Learning model.
2. Using historical flood datasets for model training.
3. Adding more geographic locations.
4. Incorporating additional environmental parameters.
5. Adding real-time monitoring.
6. Adding historical trend visualization.
7. Implementing automated alerts.
8. Adding map-based visualization.
9. Improving prediction confidence estimation.
10. Integrating more reliable government or institutional data sources.
11. Performing continuous model evaluation.
12. Deploying the system on scalable cloud infrastructure.

---

# 28. Security Considerations

For production deployment:

* Never expose API keys in frontend source code.
* Store secrets in environment variables.
* Validate all user input.
* Configure CORS appropriately.
* Use HTTPS.
* Implement rate limiting where required.
* Keep Node.js dependencies updated.
* Do not commit `.env` files.
* Use appropriate authentication if administrative functionality is introduced.

---

# 29. How to Contribute

To contribute to the project:

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

### 2. Create a new branch

```bash
git checkout -b feature-name
```

### 3. Make your changes

### 4. Test the application

### 5. Commit the changes

```bash
git add .
git commit -m "Describe your changes"
```

### 6. Push the branch

```bash
git push origin feature-name
```

### 7. Create a Pull Request

Review the changes before merging them into the main branch.

---

# 30. Team Members

| Member   | Responsibility                                   |
| -------- | ------------------------------------------------ |
| Person 1 | Backend / Input-to-Prediction Pipeline           |
| Person 2 | Development / Project Contribution               |
| Team     | Frontend, integration, testing and documentation |

Update this section with the actual names and responsibilities of all team members before final submission.

---

# 31. Project Status

**Current Status:** Working Prototype

The current implementation provides the backend prediction pipeline, API endpoints, location configuration and live weather-data integration required for the prototype.

The architecture is designed to allow further Machine Learning integration and production deployment.

---

# 32. Conclusion

The Flash Flood Risk Prediction and Early Warning System aims to transform environmental information into an easily understandable flood-risk assessment.

By combining a web interface, Node.js/Express backend, live weather-data integration and a modular prediction pipeline, the project provides a foundation for a scalable software-based flash-flood monitoring and prediction system.

The current prototype demonstrates the complete flow from data input to risk assessment, while its modular architecture allows more advanced Machine Learning models and additional real-time data sources to be integrated in future versions.

---

## License

Add the appropriate project license here if required by the project submission guidelines.

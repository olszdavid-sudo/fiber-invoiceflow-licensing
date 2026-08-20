# Fiber License Backend

Backend API developed in **Python and FastAPI** for managing trial periods, license activation and license validation for a desktop automation application.

The project was created as part of a larger Python-based solution designed to automate invoice processing, business data handling and repetitive administrative workflows.

## 🎯 Project purpose

The backend provides a centralized licensing mechanism for a desktop application.

It allows the client application to:

* start a trial period,
* validate the current license status,
* activate a license,
* deactivate a license,
* verify API availability,
* communicate with a centralized licensing database.

## 🛠️ Technologies

* **Python**
* **FastAPI**
* **REST API**
* **Supabase / SQL**
* **Render**
* **Uvicorn**
* **JSON**
* Environment-based configuration

## ⚙️ Main API endpoints

| Method | Endpoint       | Purpose                       |
| ------ | -------------- | ----------------------------- |
| `POST` | `/trial/start` | Starts a trial period         |
| `POST` | `/validate`    | Validates the current license |
| `POST` | `/activate`    | Activates a license           |
| `POST` | `/deactivate`  | Deactivates a license         |
| `GET`  | `/health`      | Checks API availability       |

Request and response models are defined in:

`app/schemas.py`

## 🗄️ Database

The project uses a SQL database for storing licensing-related information.

The database schema is available in:

`sql/schema.sql`

The backend communicates with the database using configuration provided through environment variables.

## 🚀 Deployment

The API can be deployed using **Render**.

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI application:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```text
DATABASE_URL
LICENSE_SIGNING_SECRET
LICENSE_TRIAL_DAYS
```

Example trial configuration:

```text
LICENSE_TRIAL_DAYS=30
```

## 🖥️ Desktop application integration

The desktop application communicates with the backend API using the following configuration:

```text
FIBER_LICENSE_API_URL
```

The API provides licensing and validation services used by the desktop client.

The application can also use a signing configuration for secure communication with the licensing backend.

## 📂 Project structure

```text
app/
├── FastAPI application
├── API endpoints
├── request and response models
└── licensing logic

scripts/
└── supporting scripts

sql/
└── database schema
```

Additional project files include:

```text
requirements.txt
render.yaml
runtime.txt
API_SPEC.md
```

## 🔐 Configuration and security

Sensitive configuration values are not stored directly in the source code.

The application uses environment variables for information such as:

* database connection details,
* license signing secrets,
* trial configuration,
* deployment-specific settings.

This approach keeps sensitive credentials separate from the application source code.

## 💡 What I learned

This project helped me gain practical experience in:

* designing REST API endpoints,
* developing backend services with FastAPI,
* working with SQL databases,
* integrating a desktop application with a backend service,
* managing application configuration with environment variables,
* deploying Python applications,
* designing license activation and validation workflows,
* structuring a Python backend project.

## 🚧 Further development

Possible areas for further development include:

* extended license management,
* administrative license management tools,
* additional API validation,
* improved monitoring and logging,
* expanded documentation,
* automated testing.

## 👤 Author

**Dawid Olszewski**

CAD/GIS • FTTH • Python Automation

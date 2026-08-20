<div align="center">

# 🧾 Fiber InvoiceFlow – License Backend

### Python • FastAPI • SQL • REST API • Business Process Automation

Backend licensing and activation service developed for a larger Python-based invoice-processing automation application.

</div>

---

## 🚀 About the project

**Fiber InvoiceFlow** is a Python-based automation solution designed to reduce repetitive manual work related to invoice processing, calculations, Excel updates and business-data handling.

This repository contains the **licensing and activation backend** used by the desktop application.

The backend was developed using **Python and FastAPI** and provides centralized license validation, trial management and application activation.

---

## 💼 Business value

The complete InvoiceFlow solution was created to automate a repetitive invoice-processing workflow and reduce the amount of manual work required for invoice handling.

According to the prepared project business case, the manual workflow required approximately:

- **2 hours per day**
- **10 hours per week**
- approximately **40 hours per month**
- approximately **480 hours per year**

### 📊 Estimated business impact

| Metric | Estimated value |
|---|---:|
| Time saving | **~40 h / month** |
| Annual time saving | **~480 h / year** |
| Estimated monthly productivity value | **~PLN 3,906** |
| Estimated annual productivity value | **~PLN 46,875** |
| Estimated implementation value | **PLN 30,000** |
| Estimated break-even period | **~7.7 months** |

> **Important:**  
> The business-impact figures refer to the complete **InvoiceFlow automation solution**.  
> This repository contains the licensing and activation backend used by that application.

The calculations are based on workload and employer-cost assumptions defined in the project business case.

---

## 🎯 Project purpose

The backend provides a centralized licensing mechanism for the desktop application.

It allows the client application to:

- start a trial period,
- validate the current license status,
- activate a license,
- deactivate a license,
- verify API availability,
- communicate with a centralized licensing database.

The goal was to separate licensing logic from the desktop application and provide an independent backend responsible for license management.

---

## 🛠️ Technology stack

| Area | Technology |
|---|---|
| Programming language | **Python** |
| Backend framework | **FastAPI** |
| API architecture | **REST API** |
| Database | **Supabase / SQL** |
| Application server | **Uvicorn** |
| Deployment | **Render** |
| Data exchange | **JSON** |
| Configuration | **Environment variables** |

---

## ⚙️ Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/trial/start` | Starts a trial period |
| `POST` | `/validate` | Validates the current license |
| `POST` | `/activate` | Activates a license |
| `POST` | `/deactivate` | Deactivates a license |
| `GET` | `/health` | Checks API availability |

Request and response models are defined in:

```text
app/schemas.py
```

---

## 🔄 Application workflow

The simplified licensing workflow looks like this:

```text
Desktop Application
        │
        │ HTTPS / REST API
        ▼
┌─────────────────────────┐
│     FastAPI Backend     │
│                         │
│  Trial management       │
│  License validation     │
│  License activation     │
│  License deactivation   │
└────────────┬────────────┘
             │
             │ SQL
             ▼
┌─────────────────────────┐
│    Supabase Database    │
│                         │
│  License records        │
│  Activation data        │
│  Trial information      │
└─────────────────────────┘
```

---

## 🗄️ Database

The project uses a SQL database for storing licensing-related information.

The database schema is available in:

```text
sql/schema.sql
```

The backend communicates with the database using configuration provided through environment variables.

This allows deployment-specific and sensitive values to remain outside the application source code.

---

## 📂 Project structure

```text
fiber-invoiceflow-licensing/
│
├── app/
│   ├── FastAPI application
│   ├── API endpoints
│   ├── request / response models
│   └── licensing logic
│
├── scripts/
│   └── supporting scripts
│
├── sql/
│   └── database schema
│
├── API_SPEC.md
├── requirements.txt
├── render.yaml
├── runtime.txt
├── LICENSE
└── README.md
```

---

## 🚀 Deployment

The API can be deployed using **Render**.

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the FastAPI application

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🔧 Environment variables

The backend uses environment variables instead of storing sensitive configuration directly in the source code.

Required variables include:

```text
DATABASE_URL
LICENSE_SIGNING_SECRET
LICENSE_TRIAL_DAYS
```

Example trial configuration:

```text
LICENSE_TRIAL_DAYS=30
```

---

## 🖥️ Desktop application integration

The desktop application communicates with the backend using:

```text
FIBER_LICENSE_API_URL
```

The API provides licensing and validation services used by the desktop client.

A simplified client-side flow:

```text
START APPLICATION
       │
       ▼
VALIDATE LICENSE
       │
       ├── VALID ─────────► START APPLICATION
       │
       └── INVALID
              │
              ▼
        CHECK TRIAL
              │
              ├── ACTIVE ─► START APPLICATION
              │
              └── EXPIRED
                     │
                     ▼
              ACTIVATE LICENSE
```

---

## 🔐 Security and configuration

Sensitive configuration values are not stored directly in the repository.

The application uses environment variables for:

- database connection details,
- license-signing secrets,
- trial configuration,
- deployment-specific settings.

This keeps credentials and sensitive configuration separate from the application source code.

---

## 🧠 Technical challenges

The project required solving several practical problems, including:

- separating licensing logic from the desktop application,
- designing REST API endpoints,
- managing trial and activation workflows,
- creating request and response models,
- integrating the backend with a SQL database,
- handling environment-based configuration,
- deploying the API as an independent service,
- integrating the desktop client with a remote backend.

---

## 💡 What I learned

This project helped me gain practical experience in:

- designing REST API endpoints,
- developing backend services with FastAPI,
- working with SQL databases,
- integrating desktop and backend applications,
- managing application configuration using environment variables,
- deploying Python services,
- designing license activation and validation workflows,
- structuring a Python backend project,
- translating a real business-process problem into an automation solution,
- estimating the business value of process automation.

---

## 📈 From business problem to technical solution

The project was developed as a response to a real repetitive business process.

```text
Manual invoice-processing workflow
                │
                ▼
Identification of repetitive work
                │
                ▼
Process and workload analysis
                │
                ▼
Automation concept
                │
                ▼
Python application development
                │
                ▼
Backend and licensing architecture
                │
                ▼
Deployment
                │
                ▼
Business value analysis
```

This approach combines:

**Python Development • Process Automation • Business Analysis • Measurable Business Value**

---

## 📌 Key project highlights

- ✅ Real business-process automation
- ✅ Python desktop application integration
- ✅ FastAPI backend
- ✅ REST API architecture
- ✅ SQL database integration
- ✅ Environment-based configuration
- ✅ Remote deployment
- ✅ License activation workflow
- ✅ Trial-period management
- ✅ Estimated **~40 hours saved per month**
- ✅ Estimated **~480 hours saved per year**
- ✅ Estimated **~PLN 46,875 annual productivity value**
- ✅ Estimated **~7.7-month break-even period**

---

## 🚧 Further development

Possible areas for future development include:

- extended license management,
- administrative license-management tools,
- additional API validation,
- improved monitoring and logging,
- automated testing,
- expanded API documentation,
- additional application-usage metrics,
- reporting of automation performance,
- administrative dashboards.

---

## 👤 Author

**Dawid Olszewski**

CAD/GIS • FTTH • Spatial Data • Python Automation

GitHub: [olszdavid-sudo](https://github.com/olszdavid-sudo)

---

<div align="center">

### GIS • FTTH • Python • Automation

*Combining technical experience with practical process automation.*

</div>

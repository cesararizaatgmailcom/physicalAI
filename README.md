# 🤖 PhysicalAI -- Robotic WMS API (Azure + PostgreSQL)

## 📌 Project Overview

PhysicalAI is a cloud-native Warehouse Management System (WMS) API
designed to integrate:

-   ERP / Salesforce orders
-   Autonomous robots
-   PostgreSQL database
-   Azure App Service deployment

The system automatically converts incoming sales orders into robotic
missions for warehouse execution.

------------------------------------------------------------------------

# 🏗 High-Level Cloud Architecture

``` mermaid
flowchart LR
    A[Salesforce / ERP] -->|REST API| B[Azure App Service - FastAPI]
    B --> C[Azure PostgreSQL]
    B --> D[Robot Mission Engine]
    D --> E[Autonomous Robots]
```

------------------------------------------------------------------------

# 🗄 Database Schema

## Orders

``` sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100),
    status VARCHAR(30) DEFAULT 'created',
    recipient_name VARCHAR(150),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Order Items

``` sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_code VARCHAR(50),
    quantity INT
);
```

## Robot Missions

``` sql
CREATE TABLE robot_missions (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    pickup_location VARCHAR(100),
    dropoff_location VARCHAR(100),
    status VARCHAR(30) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
```

------------------------------------------------------------------------

# 🔁 System Flow

## Order Creation

1.  Salesforce sends POST /orders
2.  API stores order in PostgreSQL
3.  Order items inserted
4.  Robot mission automatically generated

## Robot Execution

1.  Robot calls GET /missions/next
2.  API returns pending mission
3.  Robot executes delivery
4.  Robot reports completion

------------------------------------------------------------------------

# 🚀 Deployment (Azure)

``` bash
az webapp create   --resource-group InterlogisticsGroup   --plan MyAppServicePlan   --name physicalai-api   --runtime "PYTHON|3.11"
```

``` bash
az webapp up --name physicalai-api
```

------------------------------------------------------------------------

# 📊 Future Improvements

-   Inventory validation
-   Multi-robot scheduling
-   AI voice command integration
-   Monitoring dashboard
-   Digital Twin integration

------------------------------------------------------------------------

# 👤 Author


Cloud Robotics / Warehouse Automation Engineer

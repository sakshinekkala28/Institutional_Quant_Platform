# Documentation Assets

This directory contains all non-text assets used throughout the **Institutional Quant Platform** documentation.

The assets are organized into dedicated folders to keep the documentation modular, maintainable, and easy to navigate.

---

# Purpose

The assets directory provides a centralized location for:

- Architecture diagrams
- Deployment diagrams
- API diagrams
- Pipeline diagrams
- Dashboard screenshots
- Technical illustrations
- Images used in documentation
- Other visual documentation resources

These assets support the MkDocs documentation site and improve the readability of technical documentation.

---

# Directory Structure

```text
assets/

├── diagrams/
│   ├── architecture/
│   ├── api/
│   ├── dashboard/
│   ├── data/
│   ├── deployment/
│   ├── events/
│   ├── execution/
│   ├── pipelines/
│   ├── plugins/
│   └── repository/
│
├── images/
│
├── screenshots/
│
└── README.md
```

---

# Directory Descriptions

## diagrams/

Contains technical diagrams illustrating platform design and workflows.

### architecture/

High-level platform architecture.

Examples:

- System Architecture
- Component Diagram
- Module Relationships
- Layered Architecture
- Domain Model

---

### api/

REST API documentation diagrams.

Examples:

- Request Lifecycle
- Authentication Flow
- API Gateway
- Service Interaction
- OpenAPI Examples

---

### dashboard/

Dashboard layouts and UI documentation.

Examples:

- Dashboard Navigation
- Widget Layouts
- Reporting Screens
- Analytics Pages
- User Interface Flows

---

### data/

Data architecture diagrams.

Examples:

- Data Flow
- ETL Pipeline
- Database Relationships
- Repository Structure
- Data Validation Pipeline

---

### deployment/

Infrastructure and deployment diagrams.

Examples:

- Docker Deployment
- Kubernetes Architecture
- Cloud Infrastructure
- CI/CD Pipeline
- Network Topology

---

### events/

Event-driven architecture documentation.

Examples:

- Event Flow
- Message Queue
- Scheduler Workflow
- Event Processing
- Notification Pipeline

---

### execution/

Execution engine documentation.

Examples:

- Order Lifecycle
- Trade Processing
- Execution Workflow
- Broker Integration
- Reconciliation

---

### pipelines/

Analytics and orchestration workflows.

Examples:

- ETL Pipeline
- Analytics Pipeline
- Signal Generation
- Portfolio Construction
- Reporting Pipeline

---

### plugins/

Plugin architecture documentation.

Examples:

- Plugin Lifecycle
- Registration Process
- Extension Points
- Discovery Flow

---

### repository/

Repository organization diagrams.

Examples:

- Folder Structure
- Package Dependencies
- Module Relationships
- Layered Design

---

## images/

General-purpose images referenced throughout the documentation.

Examples:

- Logos
- Icons
- Illustrations
- Branding Assets

Prefer SVG or PNG formats for scalability and clarity.

---

## screenshots/

Application screenshots used in user guides and tutorials.

Examples:

- Dashboard Views
- API Documentation
- Configuration Pages
- Reports
- Charts
- Error Messages

Screenshots should be updated whenever major UI changes occur.

---

# Recommended File Formats

| Asset Type | Recommended Format |
|------------|-------------------|
| Diagrams | SVG |
| Architecture | SVG |
| Flowcharts | SVG |
| Screenshots | PNG |
| Icons | SVG |
| Logos | SVG |
| Photos | JPEG |
| Animations | GIF or MP4 |

---

# Naming Conventions

Use descriptive, lowercase filenames with hyphens.

Examples:

```text
system-architecture.svg
portfolio-workflow.svg
signal-engine.png
api-request-flow.svg
dashboard-overview.png
deployment-topology.svg
```

Avoid:

```text
image1.png
diagram.png
final-final.svg
newimage.jpg
```

---

# Asset Guidelines

Assets should:

- Be version controlled.
- Use consistent styling.
- Match project branding.
- Be optimized for web viewing.
- Avoid unnecessary file size.
- Include alt text when referenced in Markdown.

---

# Updating Assets

When replacing an asset:

1. Preserve the filename where possible.
2. Update any affected documentation.
3. Verify rendering in MkDocs.
4. Remove obsolete assets if no longer referenced.

---

# Best Practices

- Prefer vector graphics (SVG) for diagrams.
- Keep screenshots current.
- Group related assets together.
- Avoid duplicate files.
- Use meaningful filenames.
- Optimize images before committing.
- Document large or complex diagrams alongside their source files if available.

---

# Related Documentation

- Getting Started Guide
- Architecture Documentation
- Deployment Guide
- API Documentation
- Dashboard Documentation
- Pipeline Documentation
- Repository Structure
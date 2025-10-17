# Azure Data Engineer Internship Task

## Project Overview
This repository contains the solution for migrating the NBLK Stability Evaluation application from Supabase (PostgreSQL) to Azure SQL Database.

## Solution Architecture

### Database Schema
- **Normalized relational design** with proper foreign key relationships
- **Lookup tables** for age ranges and regions to ensure data consistency
- **Separate scores table** for flexible indicator management
- **Report requests tracking** for email functionality

### Key Features
- Azure SQL Database compatibility
- Data integrity through constraints and relationships
- Performance optimization with indexes
- Security best practices implementation

## Azure Deployment Plan

### 1. Azure SQL Database Configuration

#### Recommended Tier: Standard S3
- **Why**: Balanced performance and cost for moderate workload
- **Compute**: 100 DTUs provides adequate performance for initial load
- **Storage**: 250GB to accommodate growth
- **Scaling**: Auto-scale enabled for peak periods

#### Security Configuration:
- **Network**: Private Endpoint + VNet integration
- **Authentication**: Azure AD integration
- **Encryption**: Transparent Data Encryption enabled
- **Auditing**: Azure SQL Auditing enabled

### 2. Connection Security

#### Recommended Approach: Managed Identity
```csharp
// Application connection using Managed Identity
var connectionString = "Server=tcp:stability-sql.database.windows.net;Database=StabilityApp;Authentication=Active Directory Managed Identity";
```
### Alternative: Azure Key Vault
- Store connection strings in Key Vault
- Application retrieves secrets at runtime
- Automatic secret rotation support

### 3. Deployment Steps

## Phase 1: Infrastructure Provisioning
1. Create Resource Group
2. Deploy Azure SQL Database with recommended configuration
3. Configure network security (NSG rules, Private Endpoint)
4. Set up monitoring and alerts

## Phase 2: Schema Deployment
1. Execute schema.sql to create database objects
2. Populate lookup tables with reference data
3. Create required indexes and constraints
4. Set up database users and permissions

## Phase 3: Data Migration
1. Execute migration plan using Azure Database Migration Service
2. Validate data integrity post-migration
3. Update application connection strings
4. Conduct smoke tests

## Phase 4: Monitoring & Optimization
1. Configure Azure Monitor alerts
2. Set up query performance insights
3. Implement backup and retention policies
4. Establish disaster recovery procedures

### 4. Future Extensibility

## Power BI Integration
- Direct query connection to Azure SQL
- Pre-built dashboards for:
  - Regional analysis
  - Demographic trends
  - Score distributions over time

## Azure Synapse Analytics
- Future migration path for large-scale analytics
- Integration with other data sources
- Advanced machine learning capabilities

## Data Archival Strategy
- Implement temporal tables for change tracking
- Archive old data to Azure Blob Storage
- Cold storage strategy for compliance

### Local Development Setup

## Prerequisites
- Python 3.8+
- SQL Server (local or Docker)
- ODBC Driver 17 or 18 for SQL Server (for this project I used 18)

## Quick Start
1. Clone repository
2. Create local SQL Server database
3. Execute database/schema.sql
4. Run python database/load_data.py to load sample data
5. Run query database/data_verification.sql to verify if data has been loaded
6. Test queries with database/analytical_queries.sql

File Structure
text
├── database/          # Database schema and queries
├── migration/         # Migration plan and scripts  
├── scripts/           # Utility scripts and PDF generator
├── data/             # Sample data files
└── README.md         # This file

Contact
For questions about this solution, contact: munatsialwyn26@gmail.com

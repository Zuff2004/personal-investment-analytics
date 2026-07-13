# Personal Investment Analytics & Strategy Platform

## 1. Project Overview

The goal of this project is to build a local personal investment analytics and strategy platform that goes beyond a traditional spreadsheet.

The system will be used to track personal investments, transactions, dividends, stock lending income, trading performance, transaction costs, realized gains, taxes, loss carryforwards, annual returns, investment strategies, trading signals, backtesting results and automated reports.

The project is designed from the beginning as a complete personal investment platform, combining portfolio tracking, tax-aware performance analytics, strategy management, signal generation, backtesting and reporting.

## 2. Core Idea

Spreadsheet / Manual Inputs / Market Data  
→ Python Importers  
→ Local Database  
→ Portfolio Engine  
→ Tax Engine  
→ Strategy Engine  
→ Signal Engine  
→ Backtesting Engine  
→ Performance Analytics  
→ Local Dashboard  
→ Automated Reports

Real financial data stays local for security reasons, while a public demo version with fictitious data can be published on GitHub and LinkedIn.

## 3. Core Features

The platform should include:

- portfolio tracking;
- transaction-level investment history;
- average cost calculation;
- realized and unrealized PnL;
- dividends and income tracking;
- stock lending income tracking;
- transaction cost tracking;
- tax-aware realized gains;
- loss carryforward;
- monthly and annual returns;
- benchmark comparison;
- investment strategy management;
- manual and automated signals;
- signal-to-trade connection;
- backtesting engine;
- strategy-level performance evaluation;
- automated reporting;
- local dashboard.

## 4. Security Principles

The project must follow these principles:

- real financial data stays local;
- no real data is committed to GitHub;
- no API keys are stored in the source code;
- `.env` files are ignored;
- database files are ignored;
- broker exports are ignored;
- public demos use only fictitious data;
- backups should be encrypted.

## 5. Initial Tech Stack

- Python
- SQLite
- pandas
- SQLAlchemy
- Streamlit
- Plotly
- pytest
- Pydantic
- python-dotenv

## 6. Phase 1 Scope

Phase 1 focuses on project setup.

Deliverables:

- local repository;
- folder structure;
- Python virtual environment;
- dependency file;
- `.gitignore`;
- README;
- project plan;
- initial database schema;
- database initialization script.

## 7. Phase 1 Success Criteria

Phase 1 is complete when:

- the project can be opened locally;
- the Python environment works;
- dependencies are installed;
- the folder structure exists;
- Git ignores real data;
- the initial database can be created;
- the project has clear documentation.

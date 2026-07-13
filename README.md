# Personal Investment Analytics & Strategy Platform

A local Python-based personal investment analytics and strategy platform for portfolio tracking, tax-aware performance analytics, signal generation, backtesting and automated reporting.

## Project Goal

The goal of this project is to build a local system that goes beyond traditional spreadsheet-based investment tracking.

The platform is designed to track:

- portfolio positions;
- transactions;
- average cost;
- realized and unrealized PnL;
- dividends and income;
- stock lending income;
- transaction costs;
- taxes on realized gains;
- loss carryforwards;
- investment strategies;
- manual and automated signals;
- backtesting results;
- automated reports.

## Core Architecture

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

## Security

Real financial data stays local.

This repository should only contain:

- source code;
- documentation;
- database schema;
- demo data;
- screenshots based on fictitious data.

This repository must not contain:

- real portfolio data;
- real transactions;
- broker exports;
- credentials;
- API keys;
- local database files.

## Initial Tech Stack

- Python
- SQLite
- pandas
- SQLAlchemy
- Streamlit
- Plotly
- pytest
- Pydantic

## Roadmap

### Phase 1 — Project Setup

- Create repository structure
- Configure Python environment
- Create database schema
- Create database initialization script
- Add initial documentation

### Phase 2 — Spreadsheet Import

- Map spreadsheet tabs
- Import transactions
- Validate data
- Store data in SQLite

### Phase 3 — Portfolio and Tax-Aware Analytics

- Calculate positions
- Calculate average cost
- Calculate realized and unrealized PnL
- Track income and costs
- Estimate taxes and loss carryforwards

### Phase 4 — Strategy and Signal Engine

- Register strategies
- Create manual signals
- Connect signals to trades
- Evaluate signal performance

### Phase 5 — Backtesting Engine

- Run simple backtests
- Compare strategies
- Track assumptions and results

### Phase 6 — Dashboard

- Build local dashboard
- Add overview, portfolio, income, trades, taxes, performance, strategies, signals and backtesting pages

### Phase 7 — Automated Reporting

- Generate monthly and annual reports
- Export reports as CSV, HTML or PDF

### Phase 8 — Public Demo

- Create fictitious demo data
- Add screenshots
- Prepare GitHub and LinkedIn presentation

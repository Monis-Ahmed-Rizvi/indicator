# Technical Indicator Backtesting Platform

## Overview
A web application that analyzes the historical performance of technical indicators for stocks.

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd technical-indicator-platform/backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations stocks
   python manage.py migrate
   ```

5. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Usage

1. Backend API: http://localhost:8000/api/
2. Frontend: http://localhost:3000/
3. Admin: http://localhost:8000/admin/ (if superuser created)

## Features

- Stock search with Yahoo Finance integration
- Technical indicators: SMA, RSI, MACD, Bollinger Bands
- Backtesting with performance metrics
- Interactive charts and comparison tables
- Responsive design

## Important Note

This is for educational purposes only. Past performance does not guarantee future results.
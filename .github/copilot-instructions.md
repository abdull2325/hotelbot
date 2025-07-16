<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# HotelBot Project - Copilot Instructions

This is a Python project for a hotel booking system that uses PostgreSQL as the database.

## Project Structure
- `database.py`: Contains the DatabaseConnection class for PostgreSQL connectivity
- `main.py`: Example usage and demonstration of database operations
- `.env`: Environment variables for database configuration
- `requirements.txt`: Python dependencies

## Key Libraries Used
- `psycopg2-binary`: PostgreSQL adapter for Python
- `python-dotenv`: For loading environment variables from .env file

## Database Schema
The project includes tables for:
- `hotels`: Store hotel information
- `rooms`: Store room details linked to hotels
- `bookings`: Store booking information

## Development Notes
- Always use the DatabaseConnection class for database operations
- Environment variables are loaded from `.env` file
- Database queries use parameterized statements to prevent SQL injection
- The project uses a virtual environment for dependency management

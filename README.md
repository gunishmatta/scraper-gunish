# FastAPI Web Scraper

This project is a **web scraper** built using **FastAPI** that scrapes product information (title, price, and image)
from a target e-commerce website. It provides configurable settings, supports in-memory caching with **Redis**, and
allows data storage in local **JSON** files. The project follows a **clean architecture** pattern and leverages *
*object-oriented programming (OOP)** principles for easy extensibility and maintainability.


**Prerequisites**
Before you begin, ensure that the following software is installed on your system:
* Docker 
* Docker Compose

Steps to Run the Docker Image
Clone the Repository
`git clone <repository_url>
cd <repository_name>`

After closing Run

`docker-compose up -d --build
`
For logs use, docker logs <container_id> to check logs


## Features

- **Product Information Scraping**: Scrapes product title, price, and image from a target website.
- **Configurable Settings**: Easily configurable scraping parameters such as `pages_limit`, `proxy`, etc., with defaults
  and validation.
- **Redis Caching**: Uses Redis for in-memory caching to improve scraping performance by avoiding redundant requests.
- **JSON Storage**: Stores scraped product data in local JSON files for persistence.
- **Health Check Endpoint**: A simple `/health` endpoint to check the service's status.
- **Authorization**: API authentication is supported to ensure secure access to the scraping functionality.
- **Extensible Architecture**: Designed using clean architecture principles to support future enhancements and easy
  integration of new features.
- **Environment Configuration**: Settings like API tokens and URLs are externalized in an `.env` file for easy
  configuration and security.

## Project Structure

- `app/`: The main directory containing all application code.
    - `api/`: Contains the API logic for routing and dependencies.
        - `__init__.py`: Initializes the `api` module.
        - `dependencies.py`: Defines dependencies for FastAPI endpoints (e.g., scraper dependency).
        - `endpoints.py`: Contains API route definitions and logic for scraping products.
    - `core/`: Contains the core functionality of the application.
        - `__init__.py`: Initializes the `core` module.
        - `auth.py`: Handles authentication and token validation logic.
        - `cache.py`: Manages caching mechanisms (e.g., Redis).
        - `config.py`: Holds configuration settings for the application.
        - `database.py`: Handles database connections and models.
        - `interfaces.py`: Defines interfaces or abstract classes for common services.
        - `notifications.py`: Contains logic for sending notifications.
    - `tests/`: Contains test cases for the application.
        - `__init__.py`: Initializes the `tests` module.
        - `test_scraper.py`: Contains test cases for the scraper logic.
    - `__init__.py`: Initializes the main application module.
    - `main.py`: Entry point for the FastAPI application, where the app is instantiated.
    - `models.py`: Contains data models used in the application (e.g., product, scraper).
    - `scraper.py`: Contains the logic for scraping product data from the target website.
    - `utils.py`: Contains utility functions for common tasks (e.g., parsing, data handling).
      `.gitignore`: Specifies files and directories to be ignored by Git.
        - `README.md`: Documentation for testing the application.

## Configuration

### Environment Variables

This project requires some environment variables for configuration. Create a `.env` file in the root of the project with
the following variables:

- `AUTH_TOKEN`: A secret token used for API authentication.
- `BASE_URL`: The base URL for the website you want to scrape.

Example `.env` file:

```env
AUTH_TOKEN=your-secret-token
BASE_URL=https://dentalstall.com/shop/
```

# Redis Caching and API Endpoints

To improve performance, the project uses **Redis** for in-memory caching. You will need to have a Redis server running
locally or use a cloud Redis service. If you're running Redis locally, make sure the default port **6379** is
accessible.

## API Endpoints

### Health Check

- **Endpoint:** `GET /health`
- **Description:** This endpoint returns a simple health status of the service.

# Scrape Products API

This API endpoint initiates the scraping process and returns the scraped product data.

## Endpoint

- **Method:** `POST`
- **URL:** `/scrape/`

## Query Parameters

- **pages_limit**: The number of pages to scrape (default: **5**, range: **1–100**).
- **proxy**: (Optional) The proxy string to use for requests.

## Authentication

All scraping routes require authentication. Include a Bearer token in the Authorization header for secure access:

## Example Request

To initiate the scraping process, you can use the following example request:

POST /scrape/?pages_limit=10&proxy=http://yourproxy.com Authorization: Bearer your-secret-token

## Example Response

A successful response will look like this:

{
"status": "success",
"message": "50 products scraped and saved successfully."
}

## Testing the API

You can test the API using tools like Postman or curl. Below is an example of how to test the scrape endpoint using
curl:

curl -X POST "http://127.0.0.1:8000/scrape/?pages_limit=10" -H "Authorization: Bearer your-secret-token"





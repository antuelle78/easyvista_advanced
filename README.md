# EasyVista Advanced Tool - JSON-RPC Wrapper

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com)
[![Code Quality](https://img.shields.io/badge/quality-A-brightgreen)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced, production-ready JSON-RPC 2.0 wrapper for the EasyVista REST API. This service provides a robust, scalable, and easy-to-use interface for interacting with EasyVista, designed for integration with LLM agents, such as Open-WebUI, and other external systems.

## Features

- **Asynchronous and Performant**: Built with FastAPI and `httpx` for high-performance, non-blocking I/O.
- **Robust Error Handling**: Includes automatic retries with exponential backoff and translates API errors into standard JSON-RPC error responses.
- **Secure**: Protects the service with API key authentication.
- **Rich Toolset**: Provides a comprehensive set of tools for managing tickets and generating reports.
- **Containerized**: Fully containerized with Docker and Docker Compose for easy deployment and scalability.
- **Mock API Included**: Comes with a built-in mock API for testing and development, allowing you to run the service without a live EasyVista instance.

## Architecture

The project follows a clean, layered architecture that separates concerns:

- **API Layer (`app/api`)**: The entry point for all incoming requests, built with FastAPI.
- **Service Layer (`app/services`)**: Contains the business logic for interacting with the EasyVista API.
- **Data Model Layer (`app/models`)**: Defines the data structures used throughout the application with Pydantic.
- **Core Configuration (`app/core`)**: Manages application-level settings and environment variables.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd easyvista_advanced
    ```

2.  **Configure the environment:**

    Create a `.env` file in the project root and add the following variables. For local testing, the default values will work with the included mock API.

    ```env
    # The URL of the EasyVista API (or the mock API)
    EASYVISTA_URL=http://mock_api:8085

    # The API key for the EasyVista API
    EASYVISTA_API_KEY=your_api_key

    # The account ID for the EasyVista API
    EASYVISTA_ACCOUNT_ID=your_account_id

    # The API key to secure this service
    EASYVISTA_TOOL_API_KEY=a-very-secret-api-key
    ```

3.  **Build and run the services:**

    ```bash
    docker compose up --build -d
    ```

    This will start the `easyvista_tool` service (available at `http://localhost:8004`) and the `mock_api` service (available at `http://localhost:8085`).

## Usage

All tools are accessed via a single JSON-RPC endpoint: `http://localhost:8004/api/v1/mcp`.

You must include your API key in the `X-API-KEY` header for all requests.

**Example Request (`list_tickets`):**

```bash
curl -X POST http://localhost:8004/api/v1/mcp \
     -H "Content-Type: application/json" \
     -H "X-API-KEY: a-very-secret-api-key" \
     -d 
           "jsonrpc": "2.0",
           "method": "list_tickets",
           "params": {"status": "Open"},
           "id": 1
         }
```

## API Reference

The following tools are available:

| Method | Description | Parameters |
| :--- | :--- | :--- |
| `create_ticket` | Creates a new ticket. | `title`, `description`, `category`, `priority` |
| `get_ticket` | Retrieves a single ticket by its RFC number. | `rfc_number` |
| `list_tickets` | Lists tickets, with optional filtering. | `status`, `priority`, `group_id`, `limit`, `offset` |
| `get_tickets_by_group` | Retrieves tickets for a specific group. | `group_id` |
| `get_tickets_by_status` | Retrieves tickets with a specific status. | `status` |
| `get_tickets_by_priority` | Retrieves tickets with a specific priority. | `priority` |
| `generate_report` | Generates a report of tickets. | `report_type` (`summary`, `csv`, `html`), `filters` (`status`, `priority`, `group_id`) |

## Running Tests

The project includes a full suite of unit tests. To run the tests, execute the following command:

```bash
docker compose exec easyvista_tool pytest
```

This will run the tests inside the service container, ensuring a consistent testing environment.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# MCP Bloomeo Server

An MCP (Model Context Protocol) server for accessing Bloomeo experiment data. This server provides a unified interface to query experiment data, notebooks, treatments, variable groups, and trial notations from the Bloomeo API.

## Features

- **Experiment Discovery**: Count and paginate through experiments with filtering
- **Complete Experiment Data**: Get comprehensive experiment data including all related components
- **Individual Data Access**: Access specific data types (notebooks, treatments, variables, notations)
- **Search Functionality**: Search experiments by name with partial or exact matching
- **Bearer Token Authentication**: Secure API access with Bearer token support
- **Response Size Management**: Automatic pagination and data size limits to prevent timeouts

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install the Package

1. Clone this repository:
```bash
git clone https://github.com/mcrimi/bloomeomcp.git
cd bloomeomcp
```

2. Install the package:
```bash
pip install -e .
```

## Claude Desktop Setup

To use this MCP server with Claude Desktop:

1. **Get your Bloomeo Bearer Token**:
   - Log into the Bloomeo web application
   - Open your browser's developer tools (F12)
   - Go to the Network tab and make a request to the API
   - Copy the Bearer token from the Authorization header

2. **Configure Claude Desktop**:
   
   Open your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. **Add the server configuration**:
```json
{
  "mcpServers": {
    "bloomeo": {
      "command": "python",
      "args": ["-m", "mcp_bloomeo"],
      "env": {
        "BLOOMEO_BEARER_TOKEN": "your_bearer_token_here"
      }
    }
  }
}
```

4. **Restart Claude Desktop** for the changes to take effect.

## Available Tools

### Core Experiment Tools

#### `get_experiments_count`
Get the total count of available experiments.
- **Returns**: Total count (221 experiments) and pagination information

#### `get_all_experiments`
Get a single page of experiments with full pagination control.
- **Parameters**: 
  - `page`: Page number (0-based)
  - `page_size`: Results per page (max 100)
  - `filters`: Optional filter criteria
- **Returns**: One page of experiment data

#### `get_all_experiments_paginated`
Automatically fetch multiple pages of experiments.
- **Parameters**:
  - `max_pages`: Maximum pages to fetch (default: 5)
  - `include_full_data`: Return full data vs summary (default: false)
- **Returns**: Combined results from multiple pages

#### `get_experiment_data`
Get complete experiment data including all related information.
- **Parameters**: `experiment_id` - The experiment ID to fetch
- **Returns**: Comprehensive experiment data with notebooks, treatments, variables, etc.

### Individual Data Access Tools

#### `get_experiment_notebook`
Get notebook entries for a specific trial.
- **Parameters**: `trial_id` - The trial ID
- **Returns**: Array of notebook entries with observer data

#### `get_experiment_treatment`
Get treatment data for a trial.
- **Parameters**: `trial_id` - The trial ID
- **Returns**: Treatment information for the trial

#### `get_trial_notation`
Get notation data for a trial.
- **Parameters**: `trial_id` - The trial ID
- **Returns**: Trial notation data

#### `get_variable_groups`
Get observation round variable groups for a trial.
- **Parameters**: `trial_id` - The trial ID
- **Returns**: Variable groups and their configurations

### Search Tools

#### `search_experiments_by_name`
Search experiments by name with partial or exact matching.
- **Parameters**: 
  - `search_term`: Name to search for
  - `exact_match`: True for exact match, false for partial (default: false)
- **Returns**: Matching experiments

## Usage Examples

Once configured in Claude Desktop, you can use natural language commands:

### Basic Operations
```
"How many experiments are available in Bloomeo?"
"Show me the first 10 experiments"
"Get all experiments with full data for the first 2 pages"
```

### Specific Experiment Data
```
"Get complete data for experiment 66e461d780d19c639145198b"
"Show me the notebook entries for trial 66e461d780d19c639145198b"
"Get the treatment data for this experiment"
```

### Search Operations
```
"Search for experiments containing 'wheat' in the name"
"Find experiments with the exact name 'Trial 2024-01'"
```

## API Endpoints Covered

This server interfaces with the following Bloomeo API endpoints:

- `GET /experiment/v2/trial` - Experiment listing and search
- `GET /experiment/op-task/experiment/{id}` - Experiment task data
- `GET /experiment/notebook?filter={"trialId":"..."}` - Notebook entries
- `GET /experiment/treatment/trial/{id}` - Treatment data
- `GET /experiment/notation/trial/{id}` - Trial notations
- `GET /experiment/op-task/observation-round/variable-group/trial/{id}` - Variable groups
- `POST /germplasm/genotype/get/many` - Genotype data

## Authentication

The server supports Bearer token authentication through:

1. **Environment Variable** (recommended): Set `BLOOMEO_BEARER_TOKEN`
2. **Tool Parameter**: Include `bearer_token` in each tool call

## Response Size Management

The server includes automatic safeguards to prevent response size issues:

- Paginated requests are limited to prevent timeouts
- Summary mode returns only essential fields by default
- Full data mode is limited to smaller result sets
- Automatic pagination with configurable limits

## Development

### Project Structure
```
mcp_bloomeo/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── fastmcp_server.py    # FastMCP server with tool definitions
├── client.py           # Bloomeo API client
└── models.py           # Pydantic data models
```

### Key Components
- **FastMCP Framework**: Provides the MCP protocol implementation
- **HTTPx Client**: Handles async HTTP requests to Bloomeo API
- **Pydantic Models**: Type-safe data models for API responses
- **Error Handling**: Comprehensive error handling and logging

## Troubleshooting

### Common Issues

1. **"No bearer token provided"**
   - Ensure `BLOOMEO_BEARER_TOKEN` is set in Claude Desktop config
   - Verify the token is valid and not expired

2. **"Failed to fetch experiments"**
   - Check your internet connection
   - Verify the Bloomeo API is accessible
   - Confirm your bearer token has proper permissions

3. **"Response exceeds maximum length"**
   - Use `include_full_data=false` for large result sets
   - Reduce `max_pages` parameter
   - Use pagination with smaller page sizes

4. **Tool not available in Claude**
   - Restart Claude Desktop after configuration changes
   - Check the configuration file syntax is valid JSON
   - Verify the Python environment has the package installed

### Debug Mode

For debugging, you can run the server directly:
```bash
python -m mcp_bloomeo
```

This will show any startup errors or configuration issues.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for accessing Bloomeo experiment data via the MCP protocol. 
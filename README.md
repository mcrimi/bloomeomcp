# MCP Bloomeo Server

An MCP (Model Context Protocol) server for accessing Bloomeo experiment data. This server provides a unified interface to query experiment data, genotypes, trial notations, and variable groups from the Bloomeo API.

## Features

- **Unified Experiment Data**: Get complete experiment data with a single call that aggregates all related information
- **Individual API Access**: Access specific endpoints for experiment tasks, genotypes, trial notations, and variable groups
- **Automatic ID Matching**: Automatically extracts and matches related IDs from experiment responses
- **Bearer Token Management**: Secure authentication with Bearer token support

## Installation

1. Ensure you have Python 3.8+ and pip installed
2. Clone this repository or create the project structure
3. Install in development mode:

```bash
pip install -e .
```

## Tools Available

### 1. `get_experiment_data`
Get complete experiment data including task info, genotypes, trial notations, and variable groups.

**Parameters:**
- `experiment_id` (required): The experiment ID to fetch data for
- `bearer_token` (optional): Bearer token for authentication

**Example:**
```json
{
  "experiment_id": "66e461d780d19c639145198b",
  "bearer_token": "your_bearer_token_here"
}
```

### 2. `get_experiment_task`
Get experiment task data only.

**Parameters:**
- `experiment_id` (required): The experiment ID
- `task_type` (optional): Type of task (default: "observation+round")
- `bearer_token` (optional): Bearer token for authentication

### 3. `get_genotypes`
Get genotype data for specific IDs.

**Parameters:**
- `genotype_ids` (required): Array of genotype IDs
- `bearer_token` (optional): Bearer token for authentication

**Example:**
```json
{
  "genotype_ids": ["66e2e702f684d776e8503fe6", "66e2e706f684d776e850400a"],
  "bearer_token": "your_bearer_token_here"
}
```

### 4. `get_trial_notation`
Get trial notation data.

**Parameters:**
- `trial_id` (required): The trial ID
- `bearer_token` (optional): Bearer token for authentication

### 5. `get_variable_groups`
Get observation round variable groups for a trial.

**Parameters:**
- `trial_id` (required): The trial ID
- `bearer_token` (optional): Bearer token for authentication

### 6. `set_bearer_token`
Set the Bearer token for authentication.

**Parameters:**
- `bearer_token` (required): Bearer token for authentication

## Authentication

You can provide authentication in two ways:

1. **Environment Variable**: Set `BLOOMEO_BEARER_TOKEN` environment variable
2. **Tool Parameter**: Include `bearer_token` in each tool call
3. **Set Token Tool**: Use the `set_bearer_token` tool to set it once

## Configuration

To use this MCP server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bloomeo": {
      "command": "python",
      "args": ["-m", "mcp_bloomeo.server"],
      "env": {
        "BLOOMEO_BEARER_TOKEN": "your_bearer_token_here"
      }
    }
  }
}
```

## API Endpoints Covered

This server covers the following Bloomeo API endpoints:

1. `GET /experiment/op-task/experiment/{experiment_id}?type=observation+round`
2. `POST /germplasm/genotype/get/many`
3. `GET /experiment/notation/trial/{trial_id}`
4. `GET /experiment/op-task/observation-round/variable-group/trial/{trial_id}`

## Usage Example

Once configured, you can use the server in Claude:

1. **Set your bearer token** (if not using environment variable):
```
Use the set_bearer_token tool with your authentication token.
```

2. **Get complete experiment data**:
```
Use get_experiment_data tool with experiment_id "66e461d780d19c639145198b"
```

3. **Get specific data types**:
```
Use get_genotypes tool with the IDs: ["66e2e702f684d776e8503fe6", "66e2e706f684d776e850400a"]
```

## Development

The server is structured as follows:

- `mcp_bloomeo/models.py`: Pydantic models for API responses
- `mcp_bloomeo/client.py`: HTTP client for Bloomeo API
- `mcp_bloomeo/server.py`: MCP server implementation

## Notes

- The server automatically attempts to extract related IDs (genotype IDs, trial IDs) from experiment responses
- If automatic ID extraction doesn't work perfectly for your data structure, you may need to customize the extraction methods in `client.py`
- All API calls include the same headers as your original curl requests for maximum compatibility
- The server handles authentication and error cases gracefully

## Troubleshooting

1. **Authentication errors**: Ensure your bearer token is valid and not expired
2. **No data returned**: Check that the experiment ID exists and you have proper permissions
3. **ID extraction issues**: The automatic ID extraction may need customization based on your specific data structure 
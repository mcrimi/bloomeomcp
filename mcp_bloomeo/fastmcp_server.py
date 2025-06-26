"""FastMCP server for Bloomeo experiment data."""

import os
import sys
import json
from typing import List, Dict, Any, Optional

from fastmcp import FastMCP
from .client import BloomeoClient

# Create FastMCP app
mcp = FastMCP("bloomeo-experiment-server")

# Global client instance
_client: Optional[BloomeoClient] = None


async def _count_by_pagination(client: BloomeoClient, filters: Optional[Dict[str, Any]] = None) -> int:
    """Count experiments by paginating through all pages."""
    total_count = 0
    page = 0
    page_size = 100
    
    while True:
        experiments_data = await client.get_all_experiments(filters, {"name": "asc"}, page, page_size)
        
        if experiments_data is None:
            break
            
        data = experiments_data.get("data", [])
        if not data:
            break
            
        total_count += len(data)
        
        # If we got less than page_size, we've reached the end
        if len(data) < page_size:
            break
            
        page += 1
        
        # Safety limit to prevent infinite loops
        if page > 50:  # Max 5000 experiments
            total_count = f"{total_count}+"
            break
    
    return total_count


def get_client(bearer_token: Optional[str] = None) -> BloomeoClient:
    """Get or create the Bloomeo client."""
    global _client
    
    # If a new token is provided, create a new client
    if bearer_token:
        _client = BloomeoClient(bearer_token)
        return _client
    
    # If no client exists, try to create one with environment token
    if not _client:
        env_token = os.getenv("BLOOMEO_BEARER_TOKEN")
        if not env_token:
            raise ValueError("No bearer token provided. Environment variable BLOOMEO_BEARER_TOKEN not found.")
        _client = BloomeoClient(env_token)
    
    return _client


@mcp.tool
async def get_experiment_data(experiment_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get complete experiment data including task info, genotypes, trial notations, and variable groups.
    
    Args:
        experiment_id: The experiment ID to fetch data for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Complete experiment data with all related information
    """
    client = get_client(bearer_token)
    experiment_data = await client.get_complete_experiment_data(experiment_id)
    return experiment_data.model_dump()


@mcp.tool
async def get_experiment_task(experiment_id: str, task_type: str = "observation round", bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get experiment task data only.
    
    Args:
        experiment_id: The experiment ID to fetch task data for
        task_type: Type of task (default: observation round)
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Experiment task data
    """
    client = get_client(bearer_token)
    task_data = await client.get_experiment_task(experiment_id, task_type)
    
    if task_data is None:
        return {"error": f"No experiment task data found for experiment {experiment_id}"}
    
    return task_data


@mcp.tool
async def get_genotypes(genotype_ids: List[str], bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get genotype data for specific IDs.
    
    Args:
        genotype_ids: List of genotype IDs to fetch
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Genotype data for the specified IDs
    """
    client = get_client(bearer_token)
    genotypes_data = await client.get_genotypes(genotype_ids)
    
    if genotypes_data is None:
        return {"error": f"No genotype data found for IDs: {genotype_ids}"}
    
    return {"genotypes": genotypes_data}


@mcp.tool
async def get_trial_notation(trial_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get trial notation data.
    
    Args:
        trial_id: The trial ID to fetch notation data for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Trial notation data
    """
    client = get_client(bearer_token)
    notation_data = await client.get_trial_notation(trial_id)
    
    if notation_data is None:
        return {"error": f"No trial notation data found for trial {trial_id}"}
    
    return notation_data


@mcp.tool
async def get_variable_groups(trial_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get observation round variable groups for a trial.
    
    Args:
        trial_id: The trial ID to fetch variable groups for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Variable groups data for the trial
    """
    client = get_client(bearer_token)
    variable_groups_data = await client.get_variable_groups(trial_id)
    
    if variable_groups_data is None:
        return {"error": f"No variable groups data found for trial {trial_id}"}
    
    return variable_groups_data


@mcp.tool
async def get_experiment_notebook(trial_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get experiment notebook data for a trial.
    
    Args:
        trial_id: The trial ID to fetch notebook data for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Experiment notebook data for the trial
    """
    client = get_client(bearer_token)
    notebook_data = await client.get_experiment_notebook(trial_id)
    
    if notebook_data is None:
        return {"error": f"No notebook data found for trial {trial_id}"}
    
    return notebook_data


@mcp.tool
async def get_experiment_treatment(trial_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get experiment treatment data for a trial.
    
    Args:
        trial_id: The trial ID to fetch treatment data for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Experiment treatment data for the trial
    """
    client = get_client(bearer_token)
    treatment_data = await client.get_experiment_treatment(trial_id)
    
    if treatment_data is None:
        return {"error": f"No treatment data found for trial {trial_id}"}
    
    return treatment_data


@mcp.tool
async def get_all_experiments(filters: Optional[Dict[str, Any]] = None, sort: Optional[Dict[str, str]] = None, page: int = 0, page_size: int = 50, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get experiments with pagination. IMPORTANT: This returns only ONE page of results.
    
    To get ALL experiments, you need to:
    1. First call get_experiments_count to see total number of experiments
    2. Then call this function multiple times with different page numbers (0, 1, 2, etc.)
    3. Or use get_all_experiments_paginated to get all experiments automatically
    
    Args:
        filters: Filter object for experiments (optional). Default is empty filters.
        sort: Sort configuration (optional). Default is name ascending.
        page: Page number (default: 0). Use 0 for first page, 1 for second page, etc.
        page_size: Number of results per page (default: 50, max: 100)
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        ONE page of experiments data. Check _pagination.has_more to see if there are more pages.
        The '_id' field in each experiment is the experiment ID.
        
    Example usage for getting all experiments:
    1. get_experiments_count() - to see total
    2. get_all_experiments(page=0) - first page
    3. get_all_experiments(page=1) - second page
    4. Continue until _pagination.has_more is false
    """
    client = get_client(bearer_token)
    experiments_data = await client.get_all_experiments(filters, sort, page, page_size)
    
    if experiments_data is None:
        return {"error": "Failed to fetch experiments data"}
    
    return experiments_data


@mcp.tool
async def get_variable_details(variable_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a specific variable.
    
    Args:
        variable_id: The variable ID to fetch details for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Variable details including metadata, units, and relationships
    """
    client = get_client(bearer_token)
    variable_data = await client.get_variable_details(variable_id)
    
    if variable_data is None:
        return {"error": f"No variable details found for variable {variable_id}"}
    
    return variable_data


@mcp.tool
async def get_variables_by_experiment(experiment_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get all variables associated with a specific experiment.
    
    Args:
        experiment_id: The experiment ID to fetch variables for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        All variables associated with the experiment, including their relationships and metadata
    """
    client = get_client(bearer_token)
    variables_data = await client.get_variables_by_experiment(experiment_id)
    
    if variables_data is None:
        return {"error": f"No variables found for experiment {experiment_id}"}
    
    return variables_data


@mcp.tool
async def get_variable_group_details(variable_group_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a variable group.
    
    Args:
        variable_group_id: The variable group ID to fetch details for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Variable group details including contained variables and metadata
    """
    client = get_client(bearer_token)
    variable_group_data = await client.get_variable_group_details(variable_group_id)
    
    if variable_group_data is None:
        return {"error": f"No variable group details found for group {variable_group_id}"}
    
    return variable_group_data


@mcp.tool
async def get_genotype_details(genotype_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a specific genotype.
    
    Args:
        genotype_id: The genotype ID to fetch details for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Genotype details including metadata and relationships
    """
    client = get_client(bearer_token)
    genotype_data = await client.get_genotype_details(genotype_id)
    
    if genotype_data is None:
        return {"error": f"No genotype details found for genotype {genotype_id}"}
    
    return genotype_data


@mcp.tool
async def get_experiment_structure(experiment_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get the complete structure and hierarchy of an experiment.
    
    Args:
        experiment_id: The experiment ID to fetch structure for
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Complete experiment structure including hierarchy, variables, and relationships
    """
    client = get_client(bearer_token)
    structure_data = await client.get_experiment_structure(experiment_id)
    
    if structure_data is None:
        return {"error": f"No experiment structure found for experiment {experiment_id}"}
    
    return structure_data


@mcp.tool
async def search_experiments_by_name(search_term: str, exact_match: bool = False, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Search experiments by name. Supports both partial and exact matching.
    
    Args:
        search_term: The name or partial name to search for
        exact_match: Whether to search for exact match (default: False for partial match)
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        All matching experiments data. The '_id' field in each experiment is the experiment ID.
    """
    client = get_client(bearer_token)
    experiments_data = await client.search_experiments_by_name(search_term, exact_match)
    
    if experiments_data is None:
        return {"error": f"Failed to search experiments with term '{search_term}'"}
    
    return experiments_data


@mcp.tool
async def search_experiments_advanced(search_criteria: Dict[str, Any], bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Advanced search experiments by multiple criteria.
    
    Args:
        search_criteria: Dictionary with search criteria. Supported fields:
            - name: Search in experiment name (partial match)
            - description: Search in experiment description (partial match)
            - status: Filter by experiment status
            - created_after: Filter experiments created after this date
            - created_before: Filter experiments created before this date
            - tags: Filter by tags (string or array of strings)
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        All matching experiments data. The '_id' field in each experiment is the experiment ID.
    """
    client = get_client(bearer_token)
    experiments_data = await client.search_experiments_advanced(search_criteria)
    
    if experiments_data is None:
        return {"error": f"Failed to search experiments with criteria: {search_criteria}"}
    
    return experiments_data


@mcp.tool
async def get_experiments_page(page: int = 0, page_size: int = 50, filters: Optional[Dict[str, Any]] = None, sort: Optional[Dict[str, str]] = None, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get a specific page of experiments with pagination.
    
    Args:
        page: Page number (default: 0)
        page_size: Number of results per page (default: 50, max: 100)
        filters: Filter object for experiments (optional)
        sort: Sort configuration (optional)
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Paginated experiments data with pagination metadata.
    """
    client = get_client(bearer_token)
    experiments_data = await client.get_all_experiments(filters, sort, page, page_size)
    
    if experiments_data is None:
        return {"error": "Failed to fetch experiments data"}
    
    return experiments_data


@mcp.tool
async def get_experiments_count(filters: Optional[Dict[str, Any]] = None, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get the total count of experiments matching the filters.
    
    Args:
        filters: Filter object for experiments (optional)
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Total count of experiments and pagination information.
    """
    client = get_client(bearer_token)
    
    # First try with a small page to see the API response structure  
    experiments_data = await client.get_all_experiments(filters, {"name": "asc"}, 0, 1)
    
    if experiments_data is None:
        return {"error": "Failed to fetch experiments count"}
    
    # Debug the response structure and try to find total count
    total_count = None
    
    # Try multiple possible locations for total count
    possible_paths = [
        ("total",),
        ("totalCount",),
        ("count",),
        ("pagination", "total"),
        ("pagination", "totalCount"),
        ("pagination", "count"),
        ("_pagination", "total"),
        ("_pagination", "totalCount"),
        ("_pagination", "count"),
        ("meta", "total"),
        ("meta", "totalCount"),
        ("meta", "count"),
        ("totalElements",),
        ("totalItems",),
    ]
    
    for path in possible_paths:
        try:
            current = experiments_data
            for key in path:
                current = current[key]
            if isinstance(current, (int, float)) and current > 0:
                total_count = int(current)
                break
        except (KeyError, TypeError):
            continue
    
    # If we still haven't found the total, try a different approach
    if total_count is None:
        # Try with a larger page size to see if the total appears
        larger_response = await client.get_all_experiments(filters, {"name": "asc"}, 0, 100)
        if larger_response:
            # Try the same paths on the larger response
            for path in possible_paths:
                try:
                    current = larger_response
                    for key in path:
                        current = current[key]
                    if isinstance(current, (int, float)) and current > 0:
                        total_count = int(current)
                        break
                except (KeyError, TypeError):
                    continue
        
        # If still no total found, count by pagination
        if total_count is None:
            total_count = await _count_by_pagination(client, filters)
    
    # Calculate total pages, handling string values
    if isinstance(total_count, str):
        total_pages = "Many"
        pagination_info = f"Use get_all_experiments with page parameter (0, 1, 2, etc.) to get all experiments. There are {total_count} experiments."
    else:
        total_pages = (total_count + 49) // 50  # Assuming 50 per page
        pagination_info = f"Use get_all_experiments with page parameter (0 to {total_pages-1}) to get all experiments"
    
    return {
        "total_experiments": total_count,
        "total_pages": total_pages,
        "experiments_per_page": 50,
        "pagination_info": pagination_info
    }


@mcp.tool
async def get_all_experiments_paginated(filters: Optional[Dict[str, Any]] = None, sort: Optional[Dict[str, str]] = None, max_pages: int = 5, include_full_data: bool = False, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Get experiments by automatically paginating through pages.
    
    This tool fetches experiments from multiple pages. By default, it returns only essential
    information (id, name, description) to avoid response size limits. Use include_full_data=True
    to get complete experiment data, but be aware this may hit response limits with many experiments.
    
    Args:
        filters: Filter object for experiments (optional)
        sort: Sort configuration (optional)
        max_pages: Maximum number of pages to fetch (default: 5, set to -1 for ALL pages)
        include_full_data: Whether to include all experiment data (default: False for summary only)
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Experiments data from multiple pages. When include_full_data=False, returns summary info only.
        
    Example:
        - get_all_experiments_paginated(max_pages=3) - Get first 150 experiments (summary)
        - get_all_experiments_paginated(max_pages=2, include_full_data=True) - Get first 100 experiments (full data)
    """
    client = get_client(bearer_token)
    
    all_experiments = []
    page = 0
    page_size = 50
    total_fetched = 0
    
    while True:
        # Check if we've reached max pages
        if max_pages > 0 and page >= max_pages:
            break
            
        experiments_data = await client.get_all_experiments(filters, sort, page, page_size)
        
        if experiments_data is None:
            return {"error": f"Failed to fetch experiments data for page {page}"}
        
        # Extract experiments from response
        experiments = experiments_data.get("data", [])
        if not experiments:
            break  # No more data
        
        # Process experiments based on include_full_data flag
        if include_full_data:
            all_experiments.extend(experiments)
        else:
            # Extract only essential information to reduce response size
            for exp in experiments:
                summary = {
                    "_id": exp.get("_id"),
                    "name": exp.get("name"),
                    "description": exp.get("description", ""),
                    "status": exp.get("status"),
                    "createdAt": exp.get("createdAt"),
                    "updatedAt": exp.get("updatedAt")
                }
                all_experiments.append(summary)
        
        total_fetched += len(experiments)
        
        # Check if this was the last page
        if len(experiments) < page_size:
            break
            
        page += 1
        
        # Safety check to prevent extremely large responses
        if total_fetched >= 500 and not include_full_data:
            break
        elif total_fetched >= 100 and include_full_data:
            break
    
    response = {
        "experiments": all_experiments,
        "total_fetched": total_fetched,
        "pages_fetched": page + 1,
        "pagination_summary": f"Fetched {total_fetched} experiments from {page + 1} pages",
        "data_type": "full" if include_full_data else "summary"
    }
    
    if not include_full_data:
        response["note"] = "This returns summary data only. Use include_full_data=True to get complete experiment data, or use get_all_experiments() for individual pages."
    
    return response



@mcp.tool
async def test_experiment_endpoints(experiment_id: str, bearer_token: Optional[str] = None) -> Dict[str, Any]:
    """Test individual experiment endpoints to debug issues.
    
    Args:
        experiment_id: The experiment ID to test
        bearer_token: Bearer token for authentication (optional if set via environment)
        
    Returns:
        Results from testing each endpoint individually
    """
    client = get_client(bearer_token)
    
    results = {}
    
    # Test experiment task
    results["experiment_task"] = await client.get_experiment_task(experiment_id)
    
    # Test trial notation
    results["trial_notation"] = await client.get_trial_notation(experiment_id)
    
    # Test variable groups
    results["variable_groups"] = await client.get_variable_groups(experiment_id)
    
    # Test notebook
    results["notebook"] = await client.get_experiment_notebook(experiment_id)
    
    return results


def main():
    """Main entry point."""
    print("Starting FastMCP Bloomeo server...", file=sys.stderr)
    try:
        # Run the FastMCP server
        mcp.run()
    except Exception as e:
        print(f"Error in main: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 
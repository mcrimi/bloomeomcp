"""Bloomeo API client for making HTTP requests."""

import httpx
import sys
from typing import List, Dict, Any, Optional
import json
from .models import ExperimentData, ExperimentTask, Genotype, TrialNotation, VariableGroup


class BloomeoClient:
    """Client for interacting with the Bloomeo API."""
    
    def __init__(self, bearer_token: str, base_url: str = "https://api.app.bloomeo-app.com"):
        """Initialize the Bloomeo client.
        
        Args:
            bearer_token: The Bearer token for authentication
            base_url: The base URL for the Bloomeo API
        """
        self.base_url = base_url
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,bho;q=0.6',
            'authorization': f'Bearer {bearer_token}',
            'origin': 'https://app.bloomeo-app.com',
            'referer': 'https://app.bloomeo-app.com/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }
    
    async def get_experiment_task(self, experiment_id: str, task_type: str = "observation round") -> Optional[Dict[str, Any]]:
        """Get experiment task data.
        
        Args:
            experiment_id: The experiment ID
            task_type: The type of task (default: "observation round")
            
        Returns:
            The experiment task data or None if not found
        """
        url = f"{self.base_url}/experiment/op-task/experiment/{experiment_id}"
        params = {"type": task_type}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching experiment task: {e}", file=sys.stderr)
                return None
    
    async def get_genotypes(self, genotype_ids: List[str]) -> Optional[List[Dict[str, Any]]]:
        """Get genotype data for multiple IDs.
        
        Args:
            genotype_ids: List of genotype IDs
            
        Returns:
            List of genotype data or None if error
        """
        url = f"{self.base_url}/germplasm/genotype/get/many"
        headers = {**self.headers, 'content-type': 'application/json'}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=genotype_ids)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching genotypes: {e}", file=sys.stderr)
                return None
    
    async def get_trial_notation(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """Get trial notation data.
        
        Args:
            trial_id: The trial ID
            
        Returns:
            The trial notation data or None if not found
        """
        url = f"{self.base_url}/experiment/notation/trial/{trial_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching trial notation: {e}", file=sys.stderr)
                return None
    
    async def get_variable_groups(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """Get observation round variable groups.
        
        Args:
            trial_id: The trial ID
            
        Returns:
            The variable groups data or None if not found
        """
        url = f"{self.base_url}/experiment/op-task/observation-round/variable-group/trial/{trial_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching variable groups: {e}", file=sys.stderr)
                return None
    
    async def get_experiment_notebook(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """Get experiment notebook data.
        
        Args:
            trial_id: The trial ID
            
        Returns:
            The experiment notebook data or None if not found
        """
        url = f"{self.base_url}/experiment/notebook"
        params = {"filter": json.dumps({"trialId": trial_id})}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching experiment notebook: {e}", file=sys.stderr)
                return None
    
    async def get_experiment_treatment(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """Get experiment treatment data.
        
        Args:
            trial_id: The trial ID
            
        Returns:
            The experiment treatment data or None if not found
        """
        url = f"{self.base_url}/experiment/treatment/trial/{trial_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching experiment treatment: {e}", file=sys.stderr)
                return None
    
    async def get_all_experiments(self, filters: Optional[Dict[str, Any]] = None, sort: Optional[Dict[str, str]] = None, page: int = 0, page_size: int = 50) -> Optional[Dict[str, Any]]:
        """Get experiments with pagination. Note that '_id' in the response is the experiment id.
        
        Args:
            filters: Filter object for experiments (optional)
            sort: Sort configuration (optional)
            page: Page number (default: 0)
            page_size: Number of results per page (default: 50, max: 100)
            
        Returns:
            Paginated experiments data. The '_id' field in each experiment is the experiment ID.
        """
        url = f"{self.base_url}/experiment/v2/trial"
        
        # Default filter if none provided
        if filters is None:
            filters = {
                "mode": "and",
                "filters": [
                    {"mode": "and", "filters": []},
                    {"mode": "or", "filters": []}
                ]
            }
        
        # Default sort if none provided
        if sort is None:
            sort = {"name": "asc"}
        
        # Limit page size to prevent timeouts
        page_size = min(page_size, 100)
        
        params = {
            "page": page,
            "pageSize": page_size,
            "filter": json.dumps(filters),
            "sort": json.dumps(sort)
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching experiments: {e}", file=sys.stderr)
                return None
    
    async def get_variable_details(self, variable_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific variable.
        
        Args:
            variable_id: The variable ID to fetch details for
            
        Returns:
            Variable details or None if error
        """
        url = f"{self.base_url}/core/variable/{variable_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching variable details: {e}", file=sys.stderr)
                return None
    
    async def get_variables_by_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get all variables associated with a specific experiment.
        
        This method:
        1. Gets variable group associations for the trial/experiment
        2. Gets all variable definitions from the paginated endpoint
        3. Cross-references to return only variables used in this experiment
        
        Args:
            experiment_id: The experiment ID to fetch variables for
            
        Returns:
            Dict with variables used in the experiment, including their definitions and usage context
        """
        try:
            # Step 1: Get variable group associations for this trial/experiment
            variable_groups_url = f"{self.base_url}/experiment/op-task/observation-round/variable-group/trial/{experiment_id}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(variable_groups_url, headers=self.headers)
                response.raise_for_status()
                variable_groups = response.json()
            
            if not variable_groups or not isinstance(variable_groups, list):
                return {"error": f"No variable groups found for experiment {experiment_id}"}
            
            # Step 2: Extract all variable IDs used in this experiment
            variable_ids_used = set()
            experiment_context = []
            
            for group in variable_groups:
                group_info = {
                    "observation_round_id": group.get("_id"),
                    "variables_by_level": {}
                }
                
                variable_by_level = group.get("variableByLevel", {})
                for level, variables in variable_by_level.items():
                    if variables:  # Only include levels that have variables
                        group_info["variables_by_level"][level] = []
                        for var in variables:
                            var_id = var.get("variableId")
                            if var_id:
                                variable_ids_used.add(var_id)
                                group_info["variables_by_level"][level].append({
                                    "variableId": var_id,
                                    "scope": var.get("scope", 2)
                                })
                
                if group_info["variables_by_level"]:  # Only add if it has variables
                    experiment_context.append(group_info)
            
            if not variable_ids_used:
                return {"error": f"No variables found in experiment {experiment_id}"}
            
            # Step 3: Get all variable definitions from the paginated endpoint
            variables_url = f"{self.base_url}/core/variables/custom/paginated"
            params = {"page": 0, "pageSize": 3000}  # Large page size to get all variables
            
            async with httpx.AsyncClient() as client:
                response = await client.get(variables_url, headers=self.headers, params=params)
                response.raise_for_status()
                all_variables_response = response.json()
            
            all_variables = all_variables_response.get("data", [])
            if not all_variables:
                return {"error": "No variables found in system"}
            
            # Step 4: Cross-reference to get only variables used in this experiment
            experiment_variables = []
            variables_dict = {var["_id"]: var for var in all_variables}
            
            for var_id in variable_ids_used:
                if var_id in variables_dict:
                    var_definition = variables_dict[var_id]
                    
                    # Add usage context for this variable in the experiment
                    usage_context = []
                    for context in experiment_context:
                        for level, level_vars in context["variables_by_level"].items():
                            for level_var in level_vars:
                                if level_var["variableId"] == var_id:
                                    usage_context.append({
                                        "observation_round_id": context["observation_round_id"],
                                        "level": level,
                                        "scope": level_var["scope"]
                                    })
                    
                    # Enhance variable definition with experiment context
                    enhanced_variable = {
                        **var_definition,
                        "experiment_usage": usage_context
                    }
                    experiment_variables.append(enhanced_variable)
            
            return {
                "experiment_id": experiment_id,
                "total_variables": len(experiment_variables),
                "variables": experiment_variables,
                "experiment_context": experiment_context,
                "metadata": {
                    "total_observation_rounds": len(experiment_context),
                    "unique_variable_ids": list(variable_ids_used)
                }
            }
            
        except httpx.HTTPError as e:
            print(f"Error fetching experiment variables: {e}", file=sys.stderr)
            return {"error": f"Failed to fetch variables for experiment {experiment_id}: {str(e)}"}
        except Exception as e:
            print(f"Unexpected error in get_variables_by_experiment: {e}", file=sys.stderr)
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def get_variable_group_details(self, variable_group_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a variable group.
        
        Args:
            variable_group_id: The variable group ID to fetch details for
            
        Returns:
            Variable group details or None if error
        """
        url = f"{self.base_url}/core/variable-group/{variable_group_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching variable group details: {e}", file=sys.stderr)
                return None
    
    async def get_genotype_details(self, genotype_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific genotype.
        
        Args:
            genotype_id: The genotype ID to fetch details for
            
        Returns:
            Genotype details or None if error
        """
        url = f"{self.base_url}/germplasm/genotype/{genotype_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching genotype details: {e}", file=sys.stderr)
                return None
    
    async def get_experiment_structure(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get the complete structure and hierarchy of an experiment.
        
        Args:
            experiment_id: The experiment ID to fetch structure for
            
        Returns:
            Experiment structure or None if error
        """
        url = f"{self.base_url}/experiment/structure/{experiment_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching experiment structure: {e}", file=sys.stderr)
                return None
    
    async def search_experiments_by_name(self, search_term: str, exact_match: bool = False) -> Optional[Dict[str, Any]]:
        """Search experiments by name.
        
        Args:
            search_term: The name or partial name to search for
            exact_match: Whether to search for exact match (default: False for partial match)
            
        Returns:
            All matching experiments data
        """
        url = f"{self.base_url}/experiment/v2/trial"
        
        # Create filter using the correct Bloomeo structure
        if exact_match:
            # Exact match filter
            filters = {
                "mode": "and",
                "filters": [
                    {"mode": "and", "filters": []},
                    {
                        "mode": "or",
                        "filters": [
                            {
                                "key": "name",
                                "op": {
                                    "$text": {
                                        "mode": "eq",
                                        "value": search_term
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        else:
            # Partial match filter (contains) - matches the UI structure
            filters = {
                "mode": "and",
                "filters": [
                    {"mode": "and", "filters": []},
                    {
                        "mode": "or",
                        "filters": [
                            {
                                "key": "name",
                                "op": {
                                    "$text": {
                                        "mode": "contains",
                                        "value": search_term
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        
        # Sort by name for better results
        sort = {"name": "asc"}
        
        # Use a large page size to get all results
        params = {
            "page": 0,
            "pageSize": 1000,  # Large page size to get all results
            "filter": json.dumps(filters),
            "sort": json.dumps(sort)
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error searching experiments by name: {e}", file=sys.stderr)
                return None
    
    async def search_experiments_advanced(self, search_criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Advanced search experiments by multiple criteria.
        
        Args:
            search_criteria: Dictionary with search criteria. Supported fields:
                - name: Search in experiment name (partial match)
                - description: Search in experiment description (partial match)
                - status: Filter by experiment status
                - created_after: Filter experiments created after this date
                - created_before: Filter experiments created before this date
                - tags: Filter by tags
                
        Returns:
            All matching experiments data
        """
        url = f"{self.base_url}/experiment/v2/trial"
        
        # Build filters using the correct Bloomeo structure
        filters = {
            "mode": "and",
            "filters": [
                {"mode": "and", "filters": []},
                {"mode": "or", "filters": []}
            ]
        }
        
        # Add name filter if provided (in the OR section like the UI)
        if "name" in search_criteria:
            filters["filters"][1]["filters"].append({
                "key": "name",
                "op": {
                    "$text": {
                        "mode": "contains",
                        "value": search_criteria["name"]
                    }
                }
            })
        
        # Add description filter if provided (in the OR section)
        if "description" in search_criteria:
            filters["filters"][1]["filters"].append({
                "key": "description",
                "op": {
                    "$text": {
                        "mode": "contains",
                        "value": search_criteria["description"]
                    }
                }
            })
        
        # Add status filter if provided (in the AND section)
        if "status" in search_criteria:
            filters["filters"][0]["filters"].append({
                "key": "status",
                "op": {
                    "$eq": search_criteria["status"]
                }
            })
        
        # Add date range filters if provided (in the AND section)
        if "created_after" in search_criteria:
            filters["filters"][0]["filters"].append({
                "key": "createdAt",
                "op": {
                    "$gte": search_criteria["created_after"]
                }
            })
        
        if "created_before" in search_criteria:
            filters["filters"][0]["filters"].append({
                "key": "createdAt",
                "op": {
                    "$lte": search_criteria["created_before"]
                }
            })
        
        # Add tags filter if provided (in the AND section)
        if "tags" in search_criteria:
            if isinstance(search_criteria["tags"], list):
                for tag in search_criteria["tags"]:
                    filters["filters"][0]["filters"].append({
                        "key": "tags",
                        "op": {
                            "$text": {
                                "mode": "contains",
                                "value": tag
                            }
                        }
                    })
            else:
                filters["filters"][0]["filters"].append({
                    "key": "tags",
                    "op": {
                        "$text": {
                            "mode": "contains",
                            "value": search_criteria["tags"]
                        }
                    }
                })
        
        # Sort by name for better results
        sort = {"name": "asc"}
        
        # Use a large page size to get all results
        params = {
            "page": 0,
            "pageSize": 1000,  # Large page size to get all results
            "filter": json.dumps(filters),
            "sort": json.dumps(sort)
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error in advanced experiment search: {e}", file=sys.stderr)
                return None
    
    def extract_genotype_ids_from_response(self, experiment_data: Dict[str, Any]) -> List[str]:
        """Extract genotype IDs from experiment response data.
        
        This method looks for genotype IDs in the experiment response.
        You may need to adjust this based on the actual structure of your data.
        
        Args:
            experiment_data: The experiment response data
            
        Returns:
            List of genotype IDs found in the data
        """
        genotype_ids = []
        
        # This is a generic extraction - you may need to customize based on actual data structure
        if isinstance(experiment_data, dict):
            # Look for common fields that might contain genotype IDs
            for key, value in experiment_data.items():
                if 'genotype' in key.lower() and isinstance(value, (list, str)):
                    if isinstance(value, list):
                        genotype_ids.extend([str(v) for v in value if v])
                    else:
                        genotype_ids.append(str(value))
                elif isinstance(value, dict):
                    genotype_ids.extend(self.extract_genotype_ids_from_response(value))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            genotype_ids.extend(self.extract_genotype_ids_from_response(item))
        
        return list(set(genotype_ids))  # Remove duplicates
    
    def extract_trial_id_from_response(self, experiment_data: Dict[str, Any]) -> Optional[str]:
        """Extract trial ID from experiment response data.
        
        Args:
            experiment_data: The experiment response data
            
        Returns:
            Trial ID if found, None otherwise
        """
        if isinstance(experiment_data, dict):
            # Look for trial ID in common fields
            for key, value in experiment_data.items():
                if 'trial' in key.lower() and 'id' in key.lower():
                    return str(value)
                elif key.lower() == 'trialid':
                    return str(value)
                elif isinstance(value, dict):
                    trial_id = self.extract_trial_id_from_response(value)
                    if trial_id:
                        return trial_id
        
        return None
    
    async def get_complete_experiment_data(self, experiment_id: str) -> ExperimentData:
        """Get complete experiment data by aggregating all related information.
        
        Args:
            experiment_id: The experiment ID
            
        Returns:
            ExperimentData object with all related information
        """
        # Get experiment task data first - this returns an array of tasks
        experiment_task_data = await self.get_experiment_task(experiment_id)
        
        experiment_data = ExperimentData(experiment_id=experiment_id)
        
        if experiment_task_data and isinstance(experiment_task_data, list) and len(experiment_task_data) > 0:
            # Store all experiment tasks
            experiment_data.experiment_task = ExperimentTask(
                id=experiment_id,
                type="observation round",
                experiment_id=experiment_id,
                data=experiment_task_data  # Store the entire array
            )
            
            # Extract related IDs from all experiment tasks
            all_genotype_ids = []
            trial_id = None
            
            # Process each experiment task to gather IDs
            for task in experiment_task_data:
                if isinstance(task, dict):
                    # Try to extract trial_id from any task
                    if not trial_id:
                        task_trial_id = self.extract_trial_id_from_response(task)
                        if task_trial_id:
                            trial_id = task_trial_id
                    
                    # Extract genotype IDs from each task
                    task_genotype_ids = self.extract_genotype_ids_from_response(task)
                    all_genotype_ids.extend(task_genotype_ids)
            
            # Remove duplicate genotype IDs
            all_genotype_ids = list(set(all_genotype_ids))
            
            # If we couldn't extract trial_id from experiment data, use experiment_id as fallback
            if not trial_id:
                trial_id = experiment_id
            
            # Fetch related data sequentially to avoid issues
            genotypes_data = None
            trial_notation_data = None
            variable_groups_data = None
            notebook_data = None
            treatment_data = None
            
            # Get genotypes if we found genotype IDs
            if all_genotype_ids:
                genotypes_data = await self.get_genotypes(all_genotype_ids)
                if genotypes_data:
                    experiment_data.genotypes = [
                        Genotype(id=str(i), data=genotype) 
                        for i, genotype in enumerate(genotypes_data)
                    ]
            
            # Get trial notation
            if trial_id:
                trial_notation_data = await self.get_trial_notation(trial_id)
                if trial_notation_data:
                    experiment_data.trial_notation = TrialNotation(
                        trial_id=trial_id,
                        notations=trial_notation_data if isinstance(trial_notation_data, list) else [trial_notation_data]
                    )
                
                # Get variable groups
                variable_groups_data = await self.get_variable_groups(trial_id)
                if variable_groups_data:
                    experiment_data.variable_groups = VariableGroup(
                        trial_id=trial_id,
                        variable_groups=variable_groups_data if isinstance(variable_groups_data, list) else [variable_groups_data]
                    )
                
                # Get experiment notebook
                notebook_data = await self.get_experiment_notebook(trial_id)
                
                # Get experiment treatment
                treatment_data = await self.get_experiment_treatment(trial_id)
            
            # Store raw aggregated data
            experiment_data.raw_data = {
                "experiment_task": experiment_task_data,
                "genotypes": genotypes_data,
                "trial_notation": trial_notation_data,
                "variable_groups": variable_groups_data,
                "notebook": notebook_data,
                "treatment": treatment_data
            }
        else:
            # Even if experiment task fails, try to fetch other data using experiment_id as trial_id
            trial_id = experiment_id
            
            # Fetch other data that might still be available
            trial_notation_data = await self.get_trial_notation(trial_id)
            if trial_notation_data:
                experiment_data.trial_notation = TrialNotation(
                    trial_id=trial_id,
                    notations=trial_notation_data if isinstance(trial_notation_data, list) else [trial_notation_data]
                )
            
            variable_groups_data = await self.get_variable_groups(trial_id)
            if variable_groups_data:
                experiment_data.variable_groups = VariableGroup(
                    trial_id=trial_id,
                    variable_groups=variable_groups_data if isinstance(variable_groups_data, list) else [variable_groups_data]
                )
            
            notebook_data = await self.get_experiment_notebook(trial_id)
            treatment_data = await self.get_experiment_treatment(trial_id)
            
            # Store what we could fetch
            experiment_data.raw_data = {
                "experiment_task": None,
                "genotypes": None,
                "trial_notation": trial_notation_data,
                "variable_groups": variable_groups_data,
                "notebook": notebook_data,
                "treatment": treatment_data
            }
            
        return experiment_data 
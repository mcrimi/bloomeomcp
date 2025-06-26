"""Pydantic models for Bloomeo API responses."""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel


class ExperimentTask(BaseModel):
    """Model for experiment task data."""
    id: str
    type: Optional[str] = None
    experiment_id: Optional[str] = None
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None


class Genotype(BaseModel):
    """Model for genotype data."""
    id: str
    name: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class TrialNotation(BaseModel):
    """Model for trial notation data."""
    trial_id: str
    notations: Optional[List[Dict[str, Any]]] = None


class VariableGroup(BaseModel):
    """Model for observation round variable groups."""
    trial_id: str
    variable_groups: Optional[List[Dict[str, Any]]] = None


class ExperimentData(BaseModel):
    """Unified model for experiment data combining all related information."""
    experiment_id: str
    experiment_task: Optional[ExperimentTask] = None
    genotypes: Optional[List[Genotype]] = None
    trial_notation: Optional[TrialNotation] = None
    variable_groups: Optional[VariableGroup] = None
    raw_data: Optional[Dict[str, Any]] = None 
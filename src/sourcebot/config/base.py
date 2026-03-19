# src/sourcebot/config/base.py
from pydantic import BaseModel, ConfigDict
from typing import Any, Dict


class Base(BaseModel):
    """Basic configuration class"""
    model_config = ConfigDict(
        extra = "forbid",  
        validate_assignment = True, 
        arbitrary_types_allowed = False,  
        populate_by_name = True,  
    )
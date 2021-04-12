"""
    Dependencies.py
"""
from typing import Optional

class CommonQueryParams:
    def __init__(self,
        code_postal: Optional[str] = None,
        code_departement: Optional[str] = None,
        code_region: Optional[str] = None
    ):
        self.code_postal = code_postal
        self.code_departement = code_departement
        self.code_region = code_region
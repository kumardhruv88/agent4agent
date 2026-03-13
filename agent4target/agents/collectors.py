import httpx
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from agent4target.schema.evidence import TargetRequest, RawEvidence, EvidenceSource

class EvidenceCollector(ABC):
    """Base interface for an evidence collector agent"""
    
    @abstractmethod
    def fetch_evidence(self, target: TargetRequest) -> RawEvidence:
        """Fetches evidence for a given target"""
        pass

class PharosAgent(EvidenceCollector):
    """Collector for target development level from PHAROS API"""
    
    def __init__(self):
        self.api_url = "https://pharos-api.ncats.io/graphql"

    def fetch_evidence(self, target: TargetRequest) -> RawEvidence:
        print(f"[{target.symbol}] Fetching from real PHAROS API...")
        
        # GraphQL Query for Target Development Level
        query = """
        query targetDetails($sym: String!) {
          target(q: {sym: $sym}) {
            name
            sym
            tdl
            fam
          }
        }
        """
        variables = {"sym": target.symbol}
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self.api_url, 
                    json={"query": query, "variables": variables}
                )
                response.raise_for_status()
                data = response.json()
                
                target_data = data.get("data", {}).get("target")
                
                if target_data is None:
                    # Handle case where target is not found
                    return RawEvidence(
                        source=EvidenceSource.PHAROS, 
                        raw_data={"development_level": "Unknown", "error": "Target not found"}
                    )
                
                raw_data = {
                    "target": target_data.get("sym"),
                    "name": target_data.get("name"),
                    "development_level": target_data.get("tdl"), # e.g., Tclin, Tchem
                    "family": target_data.get("fam")
                }
                
        except Exception as e:
            print(f"Error fetching from PHAROS: {e}")
            raw_data = {"development_level": "Unknown", "error": str(e)}

        return RawEvidence(source=EvidenceSource.PHAROS, raw_data=raw_data)

class DepMapAgent(EvidenceCollector):
    """Collector for genetic and drug dependency from DepMap"""
    def fetch_evidence(self, target: TargetRequest) -> RawEvidence:
        # Mocking an API call to DepMap (requires specific dataset downloads usually, keeping mock for now)
        print(f"[{target.symbol}] Fetching from DepMap (Mock)...")
        raw_data = {
            "target": target.symbol,
            "crispr_dependency_score": -0.8, # Mock score (e.g., strong essentiality)
            "dependent_cell_lines": 150
        }
        return RawEvidence(source=EvidenceSource.DEPMAP, raw_data=raw_data)

class OpenTargetsAgent(EvidenceCollector):
    """Collector for disease associations from Open Targets API"""
    
    def __init__(self):
        self.api_url = "https://api.platform.opentargets.org/api/v4/graphql"
        
    def fetch_evidence(self, target: TargetRequest) -> RawEvidence:
        print(f"[{target.symbol}] Fetching from Open Targets API...")
        
        # Ensembl ID is generally preferred, but we'll use a search query for the symbol
        query = """
        query searchTarget($queryString: String!) {
          search(queryString: $queryString, entityNames: ["target"], page: {index: 0, size: 1}) {
            hits {
              id
              entity
              object {
                ... on Target {
                  id
                  approvedSymbol
                  approvedName
                  targetClass {
                    label
                  }
                }
              }
            }
          }
        }
        """
        variables = {"queryString": target.symbol}
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self.api_url, 
                    json={"query": query, "variables": variables}
                )
                response.raise_for_status()
                data = response.json()
                
                hits = data.get("data", {}).get("search", {}).get("hits", [])
                
                if not hits:
                    return RawEvidence(
                        source=EvidenceSource.OPEN_TARGETS, 
                        raw_data={"overall_association_score": 0.0, "error": "Target not found"}
                    )
                
                # Mocking the actual association score for now as it requires complex target-disease specific queries
                # In a real scenario, we'd take the Ensembl ID from the search and query associations
                target_info = hits[0].get("object", {})
                
                raw_data = {
                    "target": target_info.get("approvedSymbol"),
                    "ensembl_id": target_info.get("id"),
                    "overall_association_score": 0.85, # Still mocking the actual score metric
                    "association_types": {
                        "genetic_associations": 0.7,
                        "somatic_mutations": 0.5,
                        "drugs": 0.9,
                    }
                }
                
        except Exception as e:
            print(f"Error fetching from Open Targets: {e}")
            raw_data = {"overall_association_score": 0.0, "error": str(e)}

        return RawEvidence(source=EvidenceSource.OPEN_TARGETS, raw_data=raw_data)

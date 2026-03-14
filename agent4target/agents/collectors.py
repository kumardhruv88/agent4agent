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
                    return RawEvidence(
                        source=EvidenceSource.PHAROS, 
                        raw_data={"development_level": "Unknown", "error": "Target not found"}
                    )
                
                raw_data = {
                    "target": target_data.get("sym"),
                    "name": target_data.get("name"),
                    "development_level": target_data.get("tdl"),
                    "family": target_data.get("fam")
                }
                
        except Exception as e:
            print(f"Error fetching from PHAROS: {e}")
            raw_data = {"development_level": "Unknown", "error": str(e)}

        return RawEvidence(source=EvidenceSource.PHAROS, raw_data=raw_data)


class DepMapAgent(EvidenceCollector):
    """Collector for genetic dependency from DepMap CSV dataset (25Q3)"""
    
    def __init__(self, csv_path: str = "data/depmap/CRISPRGeneEffect.csv"):
        import pandas as pd
        print("Loading DepMap CSV... (one-time startup cost)")
        self.df = pd.read_csv(csv_path, index_col=0)
        self.gene_columns = {
            col.split(" (")[0]: col 
            for col in self.df.columns
        }
        print(f"DepMap loaded: {self.df.shape[0]} cell lines, {self.df.shape[1]} genes")

    def fetch_evidence(self, target: TargetRequest) -> RawEvidence:
        print(f"[{target.symbol}] Fetching from DepMap (Real CSV)...")
        
        col = self.gene_columns.get(target.symbol)
        
        if col is None:
            return RawEvidence(
                source=EvidenceSource.DEPMAP,
                raw_data={
                    "target": target.symbol,
                    "crispr_dependency_score": None,
                    "dependent_cell_lines": 0,
                    "error": "Gene not found in DepMap dataset"
                }
            )
        
        scores = self.df[col].dropna()
        mean_score = round(float(scores.mean()), 4)
        dependent_lines = int((scores < -0.5).sum())
        
        raw_data = {
            "target": target.symbol,
            "crispr_dependency_score": mean_score,
            "dependent_cell_lines": dependent_lines,
            "total_cell_lines": len(scores)
        }
        
        return RawEvidence(source=EvidenceSource.DEPMAP, raw_data=raw_data)


class OpenTargetsAgent(EvidenceCollector):
    """Collector for disease associations from Open Targets API"""
    
    def __init__(self):
        self.api_url = "https://api.platform.opentargets.org/api/v4/graphql"
        
    def fetch_evidence(self, target: TargetRequest) -> RawEvidence:
        print(f"[{target.symbol}] Fetching from Open Targets API...")
        
        # Step 1: Get Ensembl ID from gene symbol
        search_query = """
        query searchTarget($queryString: String!) {
          search(queryString: $queryString, entityNames: ["target"], page: {index: 0, size: 1}) {
            hits {
              object {
                ... on Target {
                  id
                  approvedSymbol
                }
              }
            }
          }
        }
        """
        
        try:
            with httpx.Client(timeout=15.0) as client:
                # Step 1: resolve symbol → Ensembl ID
                response = client.post(
                    self.api_url,
                    json={"query": search_query, "variables": {"queryString": target.symbol}}
                )
                response.raise_for_status()
                data = response.json()
                
                hits = data.get("data", {}).get("search", {}).get("hits", [])
                if not hits:
                    return RawEvidence(
                        source=EvidenceSource.OPEN_TARGETS,
                        raw_data={"overall_association_score": 0.0, "error": "Target not found"}
                    )
                
                ensembl_id = hits[0]["object"]["id"]
                approved_symbol = hits[0]["object"]["approvedSymbol"]
                
                # Step 2: fetch real overall association scores across all diseases
                assoc_query = """
                query targetAssociations($ensemblId: String!) {
                  target(ensemblId: $ensemblId) {
                    associatedDiseases(page: {index: 0, size: 10}) {
                      count
                      rows {
                        score
                        datatypeScores {
                          id
                          score
                        }
                      }
                    }
                  }
                }
                """
                
                response2 = client.post(
                    self.api_url,
                    json={"query": assoc_query, "variables": {"ensemblId": ensembl_id}}
                )
                response2.raise_for_status()
                data2 = response2.json()
                
                assoc_data = data2.get("data", {}).get("target", {}).get("associatedDiseases", {})
                rows = assoc_data.get("rows", [])
                total_associations = assoc_data.get("count", 0)
                
                if not rows:
                    overall_score = 0.0
                    datatype_scores = {}
                else:
                    # Mean of top 10 association scores — reflects breadth of evidence
                    scores = [r["score"] for r in rows if r.get("score") is not None]
                    overall_score = round(sum(scores) / len(scores), 4) if scores else 0.0
                    
                    # Aggregate datatype scores across top associations
                    datatype_totals = {}
                    datatype_counts = {}
                    for row in rows:
                        for dt in row.get("datatypeScores", []):
                            dt_id = dt["id"]
                            datatype_totals[dt_id] = datatype_totals.get(dt_id, 0) + dt["score"]
                            datatype_counts[dt_id] = datatype_counts.get(dt_id, 0) + 1
                    datatype_scores = {
                        k: round(datatype_totals[k] / datatype_counts[k], 4)
                        for k in datatype_totals
                    }
                
                raw_data = {
                    "target": approved_symbol,
                    "ensembl_id": ensembl_id,
                    "overall_association_score": overall_score,
                    "total_associated_diseases": total_associations,
                    "datatype_scores": datatype_scores
                }
                
        except Exception as e:
            print(f"Error fetching from Open Targets: {e}")
            raw_data = {"overall_association_score": 0.0, "error": str(e)}

        return RawEvidence(source=EvidenceSource.OPEN_TARGETS, raw_data=raw_data)
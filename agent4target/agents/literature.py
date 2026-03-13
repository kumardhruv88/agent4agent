import httpx
from agent4target.schema.evidence import TargetRequest, RawEvidence, EvidenceSource


class LiteratureAgent:
    """
    Collector for literature evidence from Europe PMC.
    
    This agent queries the Europe PMC REST API to count the number of
    peer-reviewed publications associated with a given gene target.
    A higher publication count signals greater research maturity.
    This addresses the GSoC requirement for 'automatically summarized
    literature evidence'.
    """

    def __init__(self):
        self.api_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def fetch_evidence(self, target: TargetRequest) -> RawEvidence:
        print(f"[{target.symbol}] Fetching from Europe PMC (Literature)...")

        params = {
            "query": f"{target.symbol} AND (SRC:MED) AND (LANG:eng)",
            "format": "json",
            "pageSize": 1,  # We only need the hitCount, not all articles
            "resultType": "lite",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.api_url, params=params)
                response.raise_for_status()
                data = response.json()

                hit_count = data.get("hitCount", 0)

                raw_data = {
                    "target": target.symbol,
                    "publication_count": hit_count,
                    "source_db": "Europe PMC",
                    "query": params["query"],
                }

        except Exception as e:
            print(f"Error fetching from Europe PMC: {e}")
            raw_data = {
                "publication_count": 0,
                "error": str(e),
            }

        return RawEvidence(source=EvidenceSource.LITERATURE, raw_data=raw_data)

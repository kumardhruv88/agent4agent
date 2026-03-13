import typer
import json
from rich.console import Console

from agent4target.orchestrator.workflow import run_pipeline

app = typer.Typer(help="Agent4Target: Agent-based Evidence Aggregation Toolkit")
console = Console()

@app.command()
def run(
    target: str = typer.Option(..., "--target", "-t", help="Gene symbol or target ID to evaluate"),
    output: str = typer.Option(None, "--output", "-o", help="Optional path to save JSON output")
):
    """
    Run the Agent4Target evidence aggregation pipeline for a specific target.
    """
    console.print(f"[bold green]Starting Agent4Target pipeline for {target}...[/bold green]\n")
    
    result = run_pipeline(target)
    
    if result.get("errors"):
        console.print("[bold red]Errors occurred during execution:[/bold red]")
        for err in result["errors"]:
            console.print(f"- {err}")
            
    scored_target = result.get("scored_target")
    if scored_target:
        console.print(f"\n[bold blue]Final Aggregate Score:[/bold blue] {scored_target.aggregate_score:.2f}")
        console.print("\n[bold blue]Explanation:[/bold blue]")
        console.print(scored_target.explanation)
        
        # Determine representation
        output_json = scored_target.model_dump_json(indent=2)
        
        if output:
            with open(output, "w") as f:
                f.write(output_json)
            console.print(f"\n[green]Results saved to {output}[/green]")
        else:
            console.print("\n[bold]Full JSON Output:[/bold]")
            console.print(output_json)
    else:
        console.print("[bold red]Pipeline failed to produce a final ScoredTarget.[/bold red]")

if __name__ == "__main__":
    app()

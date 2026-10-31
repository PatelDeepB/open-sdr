import argparse
import asyncio
import csv
import json
import sys
from typing import List

from opensdr import __version__
from opensdr.copywriting.writer import CopywriterAgent
from opensdr.enrichment.waterfall import WaterfallEnricher
from opensdr.models import Lead
from opensdr.research.agent import ResearchAgent


async def execute_lead_pipeline(lead: Lead, template_name: str = "quick_question") -> Lead:
    """Run full enrichment, research, and copywriting pipeline on a lead."""
    enricher = WaterfallEnricher()
    researcher = ResearchAgent()
    copywriter = CopywriterAgent()

    lead = await enricher.run(lead)
    lead = await researcher.analyze(lead)
    lead = copywriter.process_lead(lead, template_name=template_name)
    return lead


def handle_pipeline_command(args: argparse.Namespace) -> None:
    """Execute pipeline for a single prospect from CLI arguments."""
    lead = Lead(
        first_name=args.first_name,
        last_name=args.last_name,
        company_name=args.company,
        domain=args.domain
    )

    processed = asyncio.run(execute_lead_pipeline(lead, args.template))
    print(json.dumps(processed.model_dump(), indent=2))


def handle_batch_csv_command(args: argparse.Namespace) -> None:
    """Process a batch of prospects from a CSV file."""
    leads: List[Lead] = []
    with open(args.file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(
                Lead(
                    first_name=row.get("first_name", ""),
                    last_name=row.get("last_name", ""),
                    company_name=row.get("company_name", ""),
                    domain=row.get("domain", "")
                )
            )

    print(f"Loaded {len(leads)} leads from {args.file}. Processing...")
    results = []
    for lead in leads:
        processed = asyncio.run(execute_lead_pipeline(lead))
        results.append(processed.model_dump())

    if args.output:
        with open(args.output, mode="w", encoding="utf-8") as out:
            json.dump(results, out, indent=2)
        print(f"Exported results to {args.output}")
    else:
        print(json.dumps(results, indent=2))


def main() -> None:
    """CLI Entrypoint for OpenSDR commands."""
    parser = argparse.ArgumentParser(
        prog="open-sdr",
        description="OpenSDR: Open-Source Alternative to Clay and Autonomous AI SDRs"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Version command
    subparsers.add_parser("version", help="Print OpenSDR version")

    # Single pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run SDR pipeline for a single lead")
    pipeline_parser.add_argument("--first-name", required=True, help="First name")
    pipeline_parser.add_argument("--last-name", required=True, help="Last name")
    pipeline_parser.add_argument("--company", required=True, help="Company name")
    pipeline_parser.add_argument("--domain", required=True, help="Company domain")
    pipeline_parser.add_argument("--template", default="quick_question", help="Email template")

    # CSV batch command
    batch_parser = subparsers.add_parser("batch", help="Run batch processing from CSV file")
    batch_parser.add_argument("--file", required=True, help="Path to input CSV file")
    batch_parser.add_argument("--output", help="Optional output JSON file path")

    args = parser.parse_args()

    if args.command == "version":
        print(f"OpenSDR version {__version__}")
    elif args.command == "pipeline":
        handle_pipeline_command(args)
    elif args.command == "batch":
        handle_batch_csv_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

import json

import typer
from pathlib import Path
from paddleocr_app.invoice_extraction import create_invoice_extractor

app = typer.Typer()


@app.command()
def extract_invoice(
        image_path: Path = typer.Argument(..., help="Path to invoice image"),
        output: Path = typer.Option(None, help="Output JSON file"),
):
    """Extract and parse invoice from image."""
    extractor = create_invoice_extractor()

    try:
        invoice = extractor.extract_from_image(image_path)

        if output:
            import json
            with open(output, 'w') as f:
                json.dump(invoice.dict(), f, indent=2)
            typer.echo(f"✓ Saved to {output}")
        else:
            typer.echo(invoice.json())

    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def batch_invoices(
        image_dir: Path = typer.Argument(..., help="Directory with invoices"),
        output_dir: Path = typer.Option(None, help="Output directory for JSON files"),
):
    """Process multiple invoices."""
    extractor = create_invoice_extractor()
    results = extractor.extract_from_batch(image_dir)

    for image_path, invoice in results.items():
        if invoice and output_dir:
            output_file = output_dir / (Path(image_path).stem + ".json")
            with open(output_file, 'w') as f:
                json.dump(invoice.dict(), f, indent=2)
            typer.echo(f"✓ {Path(image_path).name}")
        elif not invoice:
            typer.echo(f"✗ {Path(image_path).name}")

def main():
    """Entry point for CLI."""
    app()

if __name__ == "__main__":
    main()
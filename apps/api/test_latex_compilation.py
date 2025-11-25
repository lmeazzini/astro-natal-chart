#!/usr/bin/env python3
"""
Test script to verify LaTeX template compilation.
This mimics the PDF generation process but runs locally.
"""

import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))


def test_latex_compilation():
    """Test LaTeX template compilation with sample data."""

    print("🔍 Testing LaTeX template compilation...\n")

    # Sample chart data
    sample_data = {
        "person_name": "Test Person",
        "birth_date": "15/05/1990",
        "birth_time": "14:30",
        "birth_datetime": "15/05/1990 às 14:30 (UTC-03:00)",
        "location": "São Paulo, Brazil",
        "coordinates": "23.55°S, 46.63°W",
        "house_system": "Placidus",
        "zodiac_type": "Tropical",
        "ascendant": "15° Leo",
        "midheaven": "25° Taurus",
        "generation_date": datetime.now().strftime("%d/%m/%Y às %H:%M"),
        "planets": [
            {
                "name": "Sun",
                "symbol": "Sol",
                "sign": "Taurus",
                "degree": "24.12",
                "house": 10,
                "dignity": "peregrinus",
                "retrograde": "Não",
                "interpretation": "The Sun in Taurus in the 10th house indicates a strong focus on career and public image. This placement brings stability and determination to professional pursuits.",
            },
            {
                "name": "Moon",
                "symbol": "Lua",
                "sign": "Virgo",
                "degree": "15.45",
                "house": 3,
                "dignity": "peregrine",
                "retrograde": "Não",
                "interpretation": "The Moon in Virgo in the 3rd house emphasizes analytical thinking and attention to detail in communication.",
            },
        ],
        "houses": [
            {
                "number": 1,
                "sign": "Leo",
                "degree": "3.45",
                "interpretation": "The 1st house in Leo suggests a confident and charismatic personality.",
            },
            {
                "number": 2,
                "sign": "Virgo",
                "degree": "3.78",
                "interpretation": "The 2nd house in Virgo indicates practical approach to finances.",
            },
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "aspect": "trine",
                "planet2": "Moon",
                "orb": "2.3",
                "interpretation": "Sun trine Moon creates harmony between conscious will and emotional needs.",
            }
        ],
    }

    # Setup Jinja2 environment
    # When running in container, report_templates is at /app/report_templates
    template_dir = Path(__file__).parent / "report_templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))

    print(f"📁 Template directory: {template_dir}")
    print(f"   Files: {list(template_dir.glob('*.tex'))}\n")

    # Render template
    try:
        template = env.get_template("natal_chart_report.tex")
        latex_source = template.render(**sample_data)
        print("✅ Template rendered successfully\n")
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback

        print("\n--- Full traceback ---")
        traceback.print_exc()
        return False

    # Test LaTeX compilation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Write main tex file
        main_tex = temp_path / "natal_chart_report.tex"
        main_tex.write_text(latex_source, encoding="utf-8")
        print(f"📝 Wrote main LaTeX file to: {main_tex}\n")

        # Copy other template files to temp directory
        for template_file in ["macros.tex", "frontpage.tex"]:
            src = template_dir / template_file
            dst = temp_path / template_file
            if src.exists():
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"📋 Copied {template_file}")
            else:
                print(f"⚠️  Warning: {template_file} not found")

        print("\n🔧 Running pdflatex (first pass)...\n")

        # First pass
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-output-directory",
                str(temp_path),
                str(main_tex),
            ],
            cwd=temp_path,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            print(f"❌ First pass failed (exit code {result.returncode})")
            print("\n--- STDOUT ---")
            print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            print("\n--- STDERR ---")
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            return False

        print("✅ First pass completed successfully\n")

        print("🔧 Running pdflatex (second pass)...\n")

        # Second pass
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-output-directory",
                str(temp_path),
                str(main_tex),
            ],
            cwd=temp_path,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            print(f"❌ Second pass failed (exit code {result.returncode})")
            print("\n--- STDOUT ---")
            print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            print("\n--- STDERR ---")
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            return False

        print("✅ Second pass completed successfully\n")

        # Check if PDF was generated
        pdf_file = temp_path / "natal_chart_report.pdf"
        if pdf_file.exists():
            pdf_size = pdf_file.stat().st_size
            print("✅ PDF generated successfully!")
            print(f"   Size: {pdf_size:,} bytes")
            print(f"   Location: {pdf_file}\n")

            # Copy to current directory for inspection
            output_pdf = Path("test_natal_chart.pdf")
            output_pdf.write_bytes(pdf_file.read_bytes())
            print(f"📄 PDF copied to: {output_pdf.absolute()}\n")

            return True
        else:
            print("❌ PDF file was not generated\n")
            return False


if __name__ == "__main__":
    success = test_latex_compilation()
    sys.exit(0 if success else 1)

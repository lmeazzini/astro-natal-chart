#!/usr/bin/env python3
"""
Script para testar compilação do template LaTeX refatorado
"""
import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import all models to configure relationships
from app.models import chart, interpretation, user  # noqa: F401
from app.models.chart import BirthChart
from app.services.interpretation_service import InterpretationService
from app.services.pdf_service import PDFService


async def test_pdf_compilation():
    """Test PDF compilation with existing chart"""
    # Create database session
    engine = create_async_engine(
        "postgresql+asyncpg://astro:dev_password@localhost:5432/astro_dev",
        echo=False,
    )
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        # Fetch chart
        chart_id = UUID("ac041455-3797-444e-a9b6-a9f4548df4bc")
        stmt = select(BirthChart).where(BirthChart.id == chart_id)
        result = await db.execute(stmt)
        birth_chart = result.scalar_one_or_none()

        if not birth_chart:
            print(f"❌ Chart {chart_id} not found")
            return

        print(f"✅ Found chart: {birth_chart.person_name}")
        print(f"   Birth: {birth_chart.birth_datetime}")
        print(f"   Location: {birth_chart.latitude}, {birth_chart.longitude}")
        print(f"   House System: {birth_chart.house_system}")

        # Initialize services
        pdf_service = PDFService()
        interpretation_service = InterpretationService(db)

        # Get interpretations
        print("\n🔄 Fetching interpretations...")
        interpretations = await interpretation_service.get_interpretations_by_chart(chart_id)

        has_planet_interps = bool(interpretations.get('planets'))
        has_house_interps = bool(interpretations.get('houses'))
        has_aspect_interps = bool(interpretations.get('aspects'))

        print(f"   Planets: {len(interpretations.get('planets', []))} interpretations")
        print(f"   Houses: {len(interpretations.get('houses', []))} interpretations")
        print(f"   Aspects: {len(interpretations.get('aspects', []))} interpretations")

        if not (has_planet_interps and has_house_interps and has_aspect_interps):
            print("\n⚠️  Missing interpretations. Generating...")
            await interpretation_service.generate_all_interpretations(
                chart_id=chart_id,
                chart_data=birth_chart.chart_data,
            )
            interpretations = await interpretation_service.get_interpretations_by_chart(chart_id)
            print("✅ Interpretations generated successfully")

        # Prepare template data
        print("\n🔄 Preparing template data...")
        template_data = pdf_service.prepare_template_data(
            chart_data={
                **birth_chart.chart_data,
                'person_name': birth_chart.person_name,
                'birth_datetime': birth_chart.birth_datetime,
                'city': birth_chart.city,
                'country': birth_chart.country,
                'latitude': float(birth_chart.latitude),
                'longitude': float(birth_chart.longitude),
                'house_system': birth_chart.house_system,
                'zodiac_type': birth_chart.zodiac_type,
            },
            interpretations=interpretations,
            chart_image_path=None,
        )
        print("✅ Template data prepared")

        # Render LaTeX template
        print("\n🔄 Rendering LaTeX template...")
        latex_source = pdf_service.render_template(template_data)
        print(f"✅ LaTeX template rendered ({len(latex_source)} characters)")

        # Compile PDF
        print("\n🔄 Compiling PDF with pdflatex...")
        pdf_path = pdf_service.generate_pdf_path(chart_id)

        # Use temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / "document.tex"
            tex_file.write_text(latex_source, encoding='utf-8')

            print(f"   LaTeX source: {tex_file}")

            # Copy macros.tex to temp directory
            templates_dir = Path(__file__).parent / "report_templates"
            macros_file = templates_dir / "macros.tex"
            if macros_file.exists():
                (temp_path / "macros.tex").write_text(
                    macros_file.read_text(encoding='utf-8'),
                    encoding='utf-8'
                )
                print("   Copied macros.tex")

            # Run pdflatex twice
            for pass_num in [1, 2]:
                print(f"\n   🔄 Running pdflatex pass {pass_num}/2...")
                process = subprocess.run(
                    [
                        'pdflatex',
                        '-interaction=nonstopmode',
                        '-output-directory', str(temp_path),
                        str(tex_file),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if process.returncode != 0:
                    # Check if PDF was actually generated despite warnings
                    temp_pdf = temp_path / "document.pdf"
                    if temp_pdf.exists() and pass_num == 1:
                        print(f"   ⚠️  Pass {pass_num} completed with warnings (PDF generated)")
                    else:
                        print(f"   ❌ pdflatex failed on pass {pass_num}")
                        print(f"\n   STDOUT:\n{process.stdout}")
                        print(f"\n   STDERR:\n{process.stderr}")

                        if pass_num == 1:
                            print("\n❌ PDF compilation failed")
                            return
                else:
                    print(f"   ✅ Pass {pass_num} completed successfully")

            # Copy generated PDF to final location
            temp_pdf = temp_path / "document.pdf"
            if not temp_pdf.exists():
                print("❌ PDF file was not generated by pdflatex")
                print("\nFiles in temp directory:")
                for f in temp_path.iterdir():
                    print(f"   - {f.name}")
                return

            # Create output directory if needed
            pdf_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy PDF
            shutil.copy2(temp_pdf, pdf_path)

            print("\n✅ PDF generated successfully!")
            print(f"   Location: {pdf_path.absolute()}")
            print(f"   Size: {pdf_path.stat().st_size / 1024:.2f} KB")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_pdf_compilation())

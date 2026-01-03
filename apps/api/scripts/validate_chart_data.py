#!/usr/bin/env python3
"""
Validate chart_data after migration to language-first format.
"""

import asyncio
import sys

from loguru import logger
from sqlalchemy import select

sys.path.insert(0, "/app")

from app.core.database import AsyncSessionLocal
from app.models.chart import BirthChart
from app.models.public_chart import PublicChart
from app.utils.chart_data_accessor import is_language_first_format, validate_language_data


async def validate_all_charts():
    """Run comprehensive validation on all charts."""
    logger.info("=" * 70)
    logger.info("Chart Data Validation Report")
    logger.info("=" * 70)

    async with AsyncSessionLocal() as db:
        # =================================================================
        # 1. BirthChart Format Distribution
        # =================================================================
        logger.info("\n[1] BirthChart Format Distribution")
        logger.info("-" * 70)

        stmt = select(BirthChart).where(
            BirthChart.chart_data.isnot(None),
            BirthChart.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        birth_charts = result.scalars().all()

        lang_first_count = 0
        flat_count = 0

        for chart in birth_charts:
            if is_language_first_format(chart.chart_data):
                lang_first_count += 1
            else:
                flat_count += 1

        total_birth = len(birth_charts)
        logger.info(f"  Total BirthCharts: {total_birth}")
        logger.info(
            f"  Language-first format: {lang_first_count} ({lang_first_count / total_birth * 100:.1f}%)"
        )
        logger.info(
            f"  Legacy flat format: {flat_count} ({flat_count / total_birth * 100:.1f}% if total_birth else 0)"
        )

        # =================================================================
        # 2. PublicChart Format Distribution
        # =================================================================
        logger.info("\n[2] PublicChart Format Distribution")
        logger.info("-" * 70)

        stmt = select(PublicChart).where(PublicChart.chart_data.isnot(None))
        result = await db.execute(stmt)
        public_charts = result.scalars().all()

        lang_first_public = 0
        flat_public = 0

        for chart in public_charts:
            if is_language_first_format(chart.chart_data):
                lang_first_public += 1
            else:
                flat_public += 1

        total_public = len(public_charts)
        logger.info(f"  Total PublicCharts: {total_public}")
        logger.info(
            f"  Language-first format: {lang_first_public} ({lang_first_public / total_public * 100:.1f}%)"
        )
        logger.info(
            f"  Legacy flat format: {flat_public} ({flat_public / total_public * 100:.1f}% if total_public else 0)"
        )

        # =================================================================
        # 3. Language Availability
        # =================================================================
        logger.info("\n[3] Language Availability Check")
        logger.info("-" * 70)

        has_en = 0
        has_pt = 0
        has_both = 0

        for chart in birth_charts:
            if chart.chart_data:
                en_avail = "en-US" in chart.chart_data
                pt_avail = "pt-BR" in chart.chart_data

                if en_avail:
                    has_en += 1
                if pt_avail:
                    has_pt += 1
                if en_avail and pt_avail:
                    has_both += 1

        logger.info(
            f"  BirthCharts with en-US: {has_en}/{total_birth} ({has_en / total_birth * 100:.1f}%)"
        )
        logger.info(
            f"  BirthCharts with pt-BR: {has_pt}/{total_birth} ({has_pt / total_birth * 100:.1f}%)"
        )
        logger.info(
            f"  BirthCharts with BOTH: {has_both}/{total_birth} ({has_both / total_birth * 100:.1f}%)"
        )

        # =================================================================
        # 4. Data Integrity Validation
        # =================================================================
        logger.info("\n[4] Data Integrity Validation")
        logger.info("-" * 70)

        validation_errors = []

        for chart in birth_charts[:5]:  # Sample first 5
            if is_language_first_format(chart.chart_data):
                for lang in ["en-US", "pt-BR"]:
                    valid, error = validate_language_data(chart.chart_data, lang)
                    if not valid:
                        validation_errors.append(
                            f"  ✗ Chart {chart.id} ({chart.person_name}): {lang} - {error}"
                        )
                    else:
                        # Check planet/house counts
                        lang_data = chart.chart_data.get(lang, {})
                        planet_count = len(lang_data.get("planets", []))
                        house_count = len(lang_data.get("houses", []))
                        logger.info(
                            f"  ✓ Chart {chart.id} ({chart.person_name}): {lang} OK - {planet_count} planets, {house_count} houses"
                        )

        if validation_errors:
            logger.error(f"\n  Found {len(validation_errors)} validation errors:")
            for error in validation_errors:
                logger.error(error)
        else:
            logger.info("\n  ✓ All sampled charts passed validation")

        # =================================================================
        # 5. Sample Data Structure
        # =================================================================
        logger.info("\n[5] Sample Data Structure")
        logger.info("-" * 70)

        if birth_charts:
            sample = birth_charts[0]
            if sample.chart_data:
                logger.info(f"  Sample from BirthChart: {sample.person_name}")
                logger.info(f"  Top-level keys: {list(sample.chart_data.keys())}")

                if "en-US" in sample.chart_data:
                    en_keys = list(sample.chart_data["en-US"].keys())
                    logger.info(f"  en-US keys: {en_keys[:10]}...")  # First 10 keys

        # =================================================================
        # Summary
        # =================================================================
        logger.info("\n" + "=" * 70)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 70)

        all_lang_first = (lang_first_count == total_birth) and (lang_first_public == total_public)
        all_have_both = has_both == total_birth

        if all_lang_first and all_have_both and not validation_errors:
            logger.info("✅ ALL CHECKS PASSED!")
            logger.info(f"  • {total_birth + total_public} charts in database")
            logger.info("  • 100% using language-first format")
            logger.info("  • 100% have both languages (en-US, pt-BR)")
            logger.info("  • All sampled data passed integrity validation")
        else:
            logger.warning("⚠️  SOME ISSUES FOUND:")
            if not all_lang_first:
                logger.warning("  • Not all charts using language-first format")
            if not all_have_both:
                logger.warning(f"  • {total_birth - has_both} charts missing one or both languages")
            if validation_errors:
                logger.warning(f"  • {len(validation_errors)} validation errors")

        logger.info("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(validate_all_charts())

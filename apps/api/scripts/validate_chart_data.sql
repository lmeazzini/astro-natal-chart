-- Validation SQL Queries for Chart Data Migration
-- Checks format distribution and data integrity

-- ============================================================================
-- 1. Format Distribution: BirthChart
-- ============================================================================
SELECT
  'BirthChart Format Distribution' as check_name,
  CASE
    WHEN chart_data ? 'en-US' OR chart_data ? 'pt-BR' THEN 'language-first'
    ELSE 'flat/other'
  END as format_type,
  COUNT(*) as count
FROM birth_chart
WHERE chart_data IS NOT NULL
  AND deleted_at IS NULL
GROUP BY format_type;

-- ============================================================================
-- 2. Format Distribution: PublicChart
-- ============================================================================
SELECT
  'PublicChart Format Distribution' as check_name,
  CASE
    WHEN chart_data ? 'en-US' OR chart_data ? 'pt-BR' THEN 'language-first'
    ELSE 'flat/other'
  END as format_type,
  COUNT(*) as count
FROM public_charts
WHERE chart_data IS NOT NULL
GROUP BY format_type;

-- ============================================================================
-- 3. Language Availability Check: BirthChart
-- ============================================================================
SELECT
  'BirthChart Language Availability' as check_name,
  SUM(CASE WHEN chart_data ? 'en-US' THEN 1 ELSE 0 END) as has_en_us,
  SUM(CASE WHEN chart_data ? 'pt-BR' THEN 1 ELSE 0 END) as has_pt_br,
  SUM(CASE WHEN (chart_data ? 'en-US') AND (chart_data ? 'pt-BR') THEN 1 ELSE 0 END) as has_both,
  COUNT(*) as total
FROM birth_chart
WHERE chart_data IS NOT NULL
  AND deleted_at IS NULL;

-- ============================================================================
-- 4. Language Availability Check: PublicChart
-- ============================================================================
SELECT
  'PublicChart Language Availability' as check_name,
  SUM(CASE WHEN chart_data ? 'en-US' THEN 1 ELSE 0 END) as has_en_us,
  SUM(CASE WHEN chart_data ? 'pt-BR' THEN 1 ELSE 0 END) as has_pt_br,
  SUM(CASE WHEN (chart_data ? 'en-US') AND (chart_data ? 'pt-BR') THEN 1 ELSE 0 END) as has_both,
  COUNT(*) as total
FROM public_charts
WHERE chart_data IS NOT NULL;

-- ============================================================================
-- 5. Data Structure Integrity: BirthChart
-- Check that both languages have required keys (planets, houses)
-- ============================================================================
SELECT
  'BirthChart Data Integrity' as check_name,
  id,
  person_name,
  (chart_data->'en-US' ? 'planets')::text as en_has_planets,
  (chart_data->'en-US' ? 'houses')::text as en_has_houses,
  (chart_data->'pt-BR' ? 'planets')::text as pt_has_planets,
  (chart_data->'pt-BR' ? 'houses')::text as pt_has_houses,
  jsonb_array_length(chart_data->'en-US'->'planets') as en_planet_count,
  jsonb_array_length(chart_data->'pt-BR'->'planets') as pt_planet_count
FROM birth_chart
WHERE chart_data IS NOT NULL
  AND deleted_at IS NULL
  AND (chart_data ? 'en-US' OR chart_data ? 'pt-BR')
LIMIT 5;

-- ============================================================================
-- 6. Data Structure Integrity: PublicChart
-- ============================================================================
SELECT
  'PublicChart Data Integrity' as check_name,
  slug,
  full_name,
  (chart_data->'en-US' ? 'planets')::text as en_has_planets,
  (chart_data->'en-US' ? 'houses')::text as en_has_houses,
  (chart_data->'pt-BR' ? 'planets')::text as pt_has_planets,
  (chart_data->'pt-BR' ? 'houses')::text as pt_has_houses,
  jsonb_array_length(chart_data->'en-US'->'planets') as en_planet_count,
  jsonb_array_length(chart_data->'pt-BR'->'planets') as pt_planet_count
FROM public_charts
WHERE chart_data IS NOT NULL
  AND (chart_data ? 'en-US' OR chart_data ? 'pt-BR')
LIMIT 5;

-- ============================================================================
-- 7. Sample Data Verification
-- Show actual structure from one BirthChart
-- ============================================================================
SELECT
  'Sample BirthChart Structure' as check_name,
  id,
  person_name,
  jsonb_object_keys(chart_data) as top_level_keys
FROM birth_chart
WHERE chart_data IS NOT NULL
  AND deleted_at IS NULL
LIMIT 1;

-- ============================================================================
-- 8. Summary Statistics
-- ============================================================================
SELECT
  '=== SUMMARY ===' as summary,
  (SELECT COUNT(*) FROM birth_chart WHERE chart_data IS NOT NULL AND deleted_at IS NULL) as total_birth_charts,
  (SELECT COUNT(*) FROM birth_chart WHERE chart_data IS NOT NULL AND deleted_at IS NULL AND (chart_data ? 'en-US' AND chart_data ? 'pt-BR')) as birth_charts_migrated,
  (SELECT COUNT(*) FROM public_charts WHERE chart_data IS NOT NULL) as total_public_charts,
  (SELECT COUNT(*) FROM public_charts WHERE chart_data IS NOT NULL AND (chart_data ? 'en-US' AND chart_data ? 'pt-BR')) as public_charts_migrated;

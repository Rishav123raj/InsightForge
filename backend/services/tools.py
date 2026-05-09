import logging
import re

from .ingest import connect


# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    handlers=[
        logging.FileHandler("insightforge.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("insightforge.tools")


# -----------------------------------------------------------------------------
# Allowed Tables
# -----------------------------------------------------------------------------

ALLOWED_TABLES = {
    "movies",
    "watch_activity",
    "reviews",
    "marketing_spend",
    "regional_performance"
}


# -----------------------------------------------------------------------------
# Generic Query Executor
# -----------------------------------------------------------------------------

def _rows(sql: str, params: tuple = ()) -> list[dict]:

    logger.info("Executing SQL query")

    logger.info(f"SQL params: {params}")

    try:

        with connect() as conn:

            result = [
                dict(row)
                for row in conn.execute(sql, params).fetchall()
            ]

            logger.info(
                f"Query executed successfully "
                f"(rows returned={len(result)})"
            )

            return result

    except Exception as e:

        logger.exception(
            f"Database query failed: {str(e)}"
        )

        raise


# -----------------------------------------------------------------------------
# Best Titles Analytics
# -----------------------------------------------------------------------------

def best_titles(year: int = 2025) -> list[dict]:

    logger.info(
        f"Fetching best titles analytics for year={year}"
    )

    return _rows(
        """
        WITH watch_stats AS (
            SELECT
                movie_id,
                ROUND(SUM(minutes_watched), 1) AS minutes,
                SUM(completed) AS completions
            FROM watch_activity
            WHERE strftime('%Y', watch_date)=?
            GROUP BY movie_id
        ),

        review_stats AS (
            SELECT
                movie_id,
                ROUND(AVG(rating), 2) AS avg_rating
            FROM reviews
            WHERE strftime('%Y', review_date)=?
            GROUP BY movie_id
        ),

        revenue_stats AS (
            SELECT
                movie_id,
                ROUND(SUM(revenue), 2) AS revenue
            FROM regional_performance
            WHERE substr(month,1,4)=?
            GROUP BY movie_id
        )

        SELECT
            m.title,
            m.genre,
            COALESCE(w.minutes, 0) AS minutes,
            COALESCE(w.completions, 0) AS completions,
            COALESCE(r.avg_rating, 0) AS avg_rating,
            COALESCE(rv.revenue, 0) AS revenue

        FROM movies m

        LEFT JOIN watch_stats w
            ON w.movie_id = m.movie_id

        LEFT JOIN review_stats r
            ON r.movie_id = m.movie_id

        LEFT JOIN revenue_stats rv
            ON rv.movie_id = m.movie_id

        ORDER BY revenue DESC, minutes DESC
        LIMIT 8
        """,
        (str(year), str(year), str(year)),
    )


# -----------------------------------------------------------------------------
# Compare Titles
# -----------------------------------------------------------------------------

def compare_titles(left: str, right: str) -> list[dict]:

    logger.info(
        f"Comparing titles: '{left}' vs '{right}'"
    )

    return _rows(
        """
        WITH watch_stats AS (
            SELECT
                movie_id,
                ROUND(SUM(minutes_watched), 1) AS minutes,
                SUM(completed) AS completions
            FROM watch_activity
            GROUP BY movie_id
        ),

        review_stats AS (
            SELECT
                movie_id,
                ROUND(AVG(rating), 2) AS avg_rating
            FROM reviews
            GROUP BY movie_id
        ),

        revenue_stats AS (
            SELECT
                movie_id,
                ROUND(SUM(revenue), 2) AS revenue
            FROM regional_performance
            GROUP BY movie_id
        ),

        marketing_stats AS (
            SELECT
                movie_id,
                ROUND(SUM(amount), 2) AS marketing_spend
            FROM marketing_spend
            GROUP BY movie_id
        )

        SELECT
            m.title,
            m.genre,
            COALESCE(w.minutes, 0) AS minutes,
            COALESCE(w.completions, 0) AS completions,
            COALESCE(r.avg_rating, 0) AS avg_rating,
            COALESCE(rv.revenue, 0) AS revenue,
            COALESCE(ms.marketing_spend, 0) AS marketing_spend

        FROM movies m

        LEFT JOIN watch_stats w
            ON w.movie_id = m.movie_id

        LEFT JOIN review_stats r
            ON r.movie_id = m.movie_id

        LEFT JOIN revenue_stats rv
            ON rv.movie_id = m.movie_id

        LEFT JOIN marketing_stats ms
            ON ms.movie_id = m.movie_id

        WHERE lower(m.title) IN (lower(?), lower(?))
        """,
        (left, right),
    )


# -----------------------------------------------------------------------------
# City Engagement
# -----------------------------------------------------------------------------

def city_engagement(month: str = "2025-12") -> list[dict]:

    logger.info(
        f"Fetching city engagement for month={month}"
    )

    return _rows(
        """
        SELECT city,SUM(views) AS views,ROUND(AVG(completion_rate),3) AS completion_rate,
               ROUND(SUM(revenue),2) AS revenue
        FROM regional_performance
        WHERE month=?
        GROUP BY city
        ORDER BY views DESC, completion_rate DESC
        LIMIT 10
        """,
        (month,),
    )


# -----------------------------------------------------------------------------
# Genre Growth
# -----------------------------------------------------------------------------

def genre_growth() -> list[dict]:

    logger.info("Fetching genre growth analytics")

    return _rows(
        """
        SELECT m.genre,
               SUM(CASE WHEN rp.month BETWEEN '2025-01' AND '2025-03' THEN rp.views ELSE 0 END) AS q1_views,
               SUM(CASE WHEN rp.month BETWEEN '2025-10' AND '2025-12' THEN rp.views ELSE 0 END) AS q4_views,
               ROUND((SUM(CASE WHEN rp.month BETWEEN '2025-10' AND '2025-12' THEN rp.views ELSE 0 END) -
                      SUM(CASE WHEN rp.month BETWEEN '2025-01' AND '2025-03' THEN rp.views ELSE 0 END))*100.0 /
                      NULLIF(SUM(CASE WHEN rp.month BETWEEN '2025-01' AND '2025-03' THEN rp.views ELSE 0 END),0),2) AS pct_growth
        FROM movies m JOIN regional_performance rp ON rp.movie_id=m.movie_id
        GROUP BY m.genre
        ORDER BY pct_growth DESC
        """
    )


# -----------------------------------------------------------------------------
# Weak Comedy Analysis
# -----------------------------------------------------------------------------

def weak_comedy() -> list[dict]:

    logger.info("Fetching weak comedy analytics")

    return _rows(
        """
        WITH review_stats AS (
            SELECT
                movie_id,
                ROUND(AVG(rating), 2) AS avg_rating
            FROM reviews
            GROUP BY movie_id
        ),

        completion_stats AS (
            SELECT
                movie_id,
                ROUND(AVG(completion_rate), 3) AS completion_rate,
                ROUND(SUM(revenue), 2) AS revenue
            FROM regional_performance
            GROUP BY movie_id
        ),

        marketing_stats AS (
            SELECT
                movie_id,
                ROUND(SUM(amount), 2) AS marketing_spend
            FROM marketing_spend
            GROUP BY movie_id
        )

        SELECT
            m.title,
            COALESCE(r.avg_rating, 0) AS avg_rating,
            COALESCE(c.completion_rate, 0) AS completion_rate,
            COALESCE(ms.marketing_spend, 0) AS marketing_spend,
            COALESCE(c.revenue, 0) AS revenue

        FROM movies m

        LEFT JOIN review_stats r
            ON r.movie_id = m.movie_id

        LEFT JOIN completion_stats c
            ON c.movie_id = m.movie_id

        LEFT JOIN marketing_stats ms
            ON ms.movie_id = m.movie_id

        WHERE lower(m.genre)='comedy'

        ORDER BY revenue ASC
        """
    )


# -----------------------------------------------------------------------------
# Safe SQL Executor
# -----------------------------------------------------------------------------

def safe_sql(sql: str) -> list[dict]:

    logger.info("Validating safe SQL query")

    normalized = sql.strip().lower()

    if not normalized.startswith("select") or ";" in normalized:

        logger.warning(
            "Blocked unsafe SQL query "
            "(non-read-only statement)"
        )

        raise ValueError(
            "Only a single read-only SELECT statement is allowed"
        )

    tables = set(
        re.findall(
            r"(?:from|join)\s+([a-z_]+)",
            normalized
        )
    )

    logger.info(f"Detected tables in query: {tables}")

    if not tables.issubset(ALLOWED_TABLES):

        logger.warning(
            f"Blocked query using unapproved tables: {tables}"
        )

        raise ValueError(
            "Query references an unapproved table"
        )

    logger.info("Safe SQL validation passed")

    return _rows(sql)


# -----------------------------------------------------------------------------
# Standalone Testing
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    logger.info("Running standalone analytics tools test")

    print("Testing analytics tools...\n")

    print("=" * 80)
    print("BEST TITLES\n")

    print(best_titles())

    print("\n" + "=" * 80)
    print("COMPARE TITLES\n")

    print(compare_titles("Dark Orbit", "Last Kingdom"))

    print("\n" + "=" * 80)
    print("CITY ENGAGEMENT\n")

    print(city_engagement())

    print("\n" + "=" * 80)
    print("GENRE GROWTH\n")

    print(genre_growth())

    print("\n" + "=" * 80)
    print("WEAK COMEDY\n")

    print(weak_comedy())

    print("\n" + "=" * 80)
    print("SAFE SQL\n")

    print(safe_sql("""
        SELECT title, genre
        FROM movies
        LIMIT 5
    """))
"""Ingest job category nodes and edges into Neo4j for career path graph.

Reads promotion_path + transition_to from job_categories MySQL table,
creates/merges Category nodes and PROMOTES_TO / TRANSITIONS_TO relationships.
"""
import json
from sqlalchemy import select
from app.db.mysql import AsyncSessionLocal
from app.db.neo4j import neo4j_manager
from app.models.job_category import JobCategory


async def ingest_neo4j_graph():
    """Build Neo4j career graph from job_categories data."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(JobCategory))
        categories = result.scalars().all()

    if not categories:
        print("[Neo4j] No job categories found — skipping graph ingest.")
        return

    session = await neo4j_manager.get_session()

    try:
        # Create all category nodes
        for c in categories:
            await session.run(
                """
                MERGE (cat:Category {id: $id})
                SET cat.name = $name,
                    cat.description = $description,
                    cat.core_skills = $core_skills,
                    cat.promotion_path = $promotion_path
                """,
                id=c.id,
                name=c.name or "",
                description=c.description or "",
                core_skills=json.dumps(c.core_skills or [], ensure_ascii=False),
                promotion_path=json.dumps(c.promotion_path or [], ensure_ascii=False),
            )

        # Create edges: PROMOTES_TO (internal promotion path stages)
        for c in categories:
            path = c.promotion_path or []
            if isinstance(path, str):
                try:
                    path = json.loads(path)
                except (json.JSONDecodeError, TypeError):
                    path = []
            for stage in path:
                if isinstance(stage, dict) and stage.get("stage"):
                    await session.run(
                        """
                        MATCH (cat:Category {id: $id})
                        MERGE (cat)-[:PROMOTES_TO {stage: $stage, salary: $salary,
                               timeline: $timeline, goal: $goal}]->(cat)
                        """,
                        id=c.id,
                        stage=stage.get("stage", ""),
                        salary=stage.get("salary", ""),
                        timeline=stage.get("timeline", ""),
                        goal=stage.get("goal", ""),
                    )

        # Create edges: TRANSITIONS_TO (cross-category transitions)
        for c in categories:
            targets = c.transition_to or []
            if isinstance(targets, str):
                try:
                    targets = json.loads(targets)
                except (json.JSONDecodeError, TypeError):
                    targets = []
            for target_id in targets:
                await session.run(
                    """
                    MATCH (a:Category {id: $from_id})
                    MATCH (b:Category {id: $to_id})
                    MERGE (a)-[:TRANSITIONS_TO]->(b)
                    """,
                    from_id=c.id,
                    to_id=target_id,
                )
    finally:
        await session.close()

    print(f"[Neo4j] Ingested {len(categories)} Category nodes with edges.")

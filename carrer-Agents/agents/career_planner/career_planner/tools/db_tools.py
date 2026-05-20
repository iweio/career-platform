import os
from typing import Optional, Dict, Any, List
import pymysql
import json
from pathlib import Path

_dotenv_path = Path(__file__).parent.parent / ".env"
if _dotenv_path.exists():
    with open(_dotenv_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)


def get_mysql_connection():
    host = os.getenv("MYSQL_HOST", "backend-mysql-1")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "password")
    database = os.getenv("MYSQL_DATABASE", "job_db")
    charset = "utf8mb4"

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset=charset,
        connect_timeout=10
    )


def get_top_matched_job(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_mysql_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT j.title as job_name, j.industry, j.city, 80.0 as match_score
                FROM favorites f
                JOIN jobs j ON f.job_id = j.id
                WHERE f.user_id = %s
                LIMIT 1
            """, (user_id,))
            result = cursor.fetchone()
            return result
    finally:
        conn.close()


def get_promotion_transition(job_name: str) -> List[Dict[str, Any]]:
    conn = get_mysql_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT job_id, current_role, next_role, required_skills,
                       transition_type, years_exp
                FROM promotion_transition
                WHERE current_role LIKE %s OR next_role LIKE %s
                LIMIT 20
            """, (f"%{job_name}%", f"%{job_name}%"))
            results = cursor.fetchall()
            for r in results:
                if isinstance(r.get("required_skills"), str):
                    try:
                        r["required_skills"] = json.loads(r["required_skills"])
                    except:
                        r["required_skills"] = [r["required_skills"]]
            return results
    finally:
        conn.close()


def save_career_plan(
    user_id: int,
    top_job: str,
    match_score: float,
    trends_data: Dict[str, Any],
    career_path_data: Dict[str, Any],
    chart_path: str = None
) -> bool:
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            plan_json = json.dumps({
                "trends": trends_data,
                "career_path": career_path_data
            }, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO career_plans (user_id, plan_data, target_position, status)
                VALUES (%s, %s, %s, 'active')
                ON DUPLICATE KEY UPDATE
                    plan_data = VALUES(plan_data),
                    target_position = VALUES(target_position),
                    updated_at = NOW()
            """, (user_id, plan_json, top_job))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()

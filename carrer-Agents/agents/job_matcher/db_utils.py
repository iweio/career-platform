import json
from typing import Optional, List, Dict, Any
import pymysql
from .config import settings


def get_mysql_connection():
    return pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT profile_data FROM user_profiles WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                profile_data = result['profile_data']
                if isinstance(profile_data, str):
                    return json.loads(profile_data)
                return profile_data
    finally:
        conn.close()
    return None


def get_user_favorite_job_ids(user_id: int) -> List[int]:
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT job_id FROM favorites WHERE user_id = %s", (user_id,))
            results = cursor.fetchall()
            return [row['job_id'] for row in results]
    finally:
        conn.close()


def get_job_detail(job_id: int) -> Optional[Dict[str, Any]]:
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, description, company_description FROM jobs WHERE id = %s",
                (job_id,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id": result['id'],
                    "title": result['title'],
                    "job_detail": result['description'],
                    "company_detail": result['company_description']
                }
    finally:
        conn.close()
    return None


def get_job_details_batch(job_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    if not job_ids:
        return {}
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            placeholders = ','.join(['%s'] * len(job_ids))
            query = f"SELECT id, title, description, company_description FROM jobs WHERE id IN ({placeholders})"
            cursor.execute(query, tuple(job_ids))
            results = cursor.fetchall()
            return {
                row['id']: {
                    "id": row['id'],
                    "title": row['title'],
                    "job_detail": row['description'],
                    "company_detail": row['company_description']
                }
                for row in results
            }
    finally:
        conn.close()


def get_all_jobs(limit: int = 100) -> Dict[int, Dict[str, Any]]:
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT id, title, description, company_description FROM jobs LIMIT {limit}")
            results = cursor.fetchall()
            return {
                row['id']: {
                    "id": row['id'],
                    "title": row['title'],
                    "job_detail": row['description'],
                    "company_detail": row['company_description']
                }
                for row in results
            }
    finally:
        conn.close()


def save_user_profile(user_id: int, profile_data: Dict[str, Any], status: str = "active") -> bool:
    conn = get_mysql_connection()
    try:
        import json
        with conn.cursor() as cursor:
            profile_json = json.dumps(profile_data, ensure_ascii=False)

            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                cursor.execute(
                    """INSERT INTO users (id, name, email, resume, skills, experience, education, career_goals)
                       VALUES (%s, 'User %s', 'user@example.com', '', '', '', '', '')""",
                    (user_id, user_id)
                )

            cursor.execute(
                """INSERT INTO user_profiles (user_id, profile_data, status, created_at, updated_at)
                   VALUES (%s, %s, %s, NOW(), NOW())
                   ON DUPLICATE KEY UPDATE profile_data = VALUES(profile_data), status = VALUES(status), updated_at = NOW()""",
                (user_id, profile_json, status)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Error saving user profile: {e}")
        return False
    finally:
        conn.close()


def save_match_report(report_data: Dict[str, Any]) -> bool:
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            user_id = report_data.get('user_id')
            best_match = report_data.get('best_match', {})
            
            cursor.execute(
                "UPDATE user_profiles SET match_score = %s, updated_at = NOW() WHERE user_id = %s",
                (report_data.get('best_match_score'), user_id)
            )
            
            cursor.execute("""
                INSERT INTO matching_report (user_id, job_name, industry, city, match_score, publish_date, created_at)
                VALUES (%s, %s, %s, %s, %s, CURDATE(), NOW())
                ON DUPLICATE KEY UPDATE
                job_name = VALUES(job_name), industry = VALUES(industry), city = VALUES(city),
                match_score = VALUES(match_score), created_at = NOW()
            """, (
                user_id,
                best_match.get('job_title', ''),
                best_match.get('industry', ''),
                best_match.get('city', ''),
                best_match.get('final_score', 0)
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error saving match report: {e}")
        return False
    finally:
        conn.close()


def save_analysis_result(user_id: int, analysis_data: Dict[str, Any], target_position: str = "", target_company: str = "") -> bool:
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            plan_data_json = json.dumps(analysis_data, ensure_ascii=False)
            cursor.execute(
                """INSERT INTO career_plans (user_id, plan_data, target_position, target_company, timeline_months, status)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE plan_data = VALUES(plan_data), target_position = VALUES(target_position),
                   target_company = VALUES(target_company), updated_at = NOW()""",
                (user_id, plan_data_json, target_position, target_company, 12, "active")
            )
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


from neo4j import GraphDatabase


class Neo4jConnection:
    def __init__(self):
        self.driver = None

    def connect(self):
        if self.driver is None:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        return self.driver

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def get_session(self):
        driver = self.connect()
        return driver.session()


neo4j_conn = Neo4jConnection()


def get_job_profile_from_neo4j(job_title: str) -> Optional[Dict[str, Any]]:
    try:
        with neo4j_conn.get_session() as session:
            result = session.run(
                "MATCH (j:JobProfile {title: $title}) RETURN j.title AS title, "
                "j.专业技能 AS 专业技能, j.证书 AS 证书, j.创新能力 AS 创新能力, "
                "j.学习能力 AS 学习能力, j.抗压能力 AS 抗压能力, j.沟通能力 AS 沟通能力, "
                "j.实习能力 AS 实习能力",
                title=job_title
            ).single()
            if result:
                return dict(result)
    except Exception as e:
        print(f"Neo4j query error: {e}")
    return None


def init_neo4j_job_profiles() -> bool:
    """初始化 Neo4j 中的 JobProfile 节点"""
    try:
        with neo4j_conn.get_session() as session:
            # 定义一些常见岗位的画像数据
            job_profiles = [
                {
                    "title": "Data Analyst",
                    "专业技能": "SQL, Python, Excel, Tableau",
                    "证书": "SQL认证, Tableau认证",
                    "创新能力": "数据分析创新",
                    "学习能力": "快速学习新工具",
                    "抗压能力": "处理大量数据压力",
                    "沟通能力": "数据可视化和汇报",
                    "实习能力": "数据处理实习经验"
                },
                {
                    "title": "Python Backend Dev",
                    "专业技能": "Python, Django, Flask, SQL",
                    "证书": "Python认证",
                    "创新能力": "后端架构创新",
                    "学习能力": "学习新框架",
                    "抗压能力": "处理高并发",
                    "沟通能力": "团队协作",
                    "实习能力": "后端开发实习经验"
                },
                {
                    "title": "Frontend Developer",
                    "专业技能": "HTML, CSS, JavaScript, React",
                    "证书": "前端认证",
                    "创新能力": "UI/UX创新",
                    "学习能力": "学习新前端框架",
                    "抗压能力": "处理浏览器兼容性",
                    "沟通能力": "与设计团队协作",
                    "实习能力": "前端开发实习经验"
                },
                {
                    "title": "Product Manager",
                    "专业技能": "产品规划, 用户研究, 数据分析",
                    "证书": "PMP认证",
                    "创新能力": "产品创新",
                    "学习能力": "了解市场趋势",
                    "抗压能力": "项目压力管理",
                    "沟通能力": "跨团队沟通",
                    "实习能力": "产品管理实习经验"
                }
            ]
            
            for profile in job_profiles:
                session.run(
                    """
                    MERGE (j:JobProfile {title: $title})
                    SET j.专业技能 = $专业技能,
                        j.证书 = $证书,
                        j.创新能力 = $创新能力,
                        j.学习能力 = $学习能力,
                        j.抗压能力 = $抗压能力,
                        j.沟通能力 = $沟通能力,
                        j.实习能力 = $实习能力
                    """,
                    **profile
                )
            return True
    except Exception as e:
        print(f"Neo4j initialization error: {e}")
        return False
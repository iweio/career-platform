import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import pymysql

dotenv_path = Path(__file__).parent.parent / ".env"
if dotenv_path.exists():
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "backend-mysql-1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "password"),
        database=os.getenv("MYSQL_DATABASE", "career_db"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


def get_user_profile(user_id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT profile_data FROM user_profiles WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result and result.get("profile_data"):
                if isinstance(result["profile_data"], str):
                    try:
                        return json.loads(result["profile_data"])
                    except json.JSONDecodeError:
                        return {}
                return result["profile_data"]
            return {}
    finally:
        conn.close()


def get_target_job(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT job_name AS job_title, match_score, industry, city
                FROM matching_report
                WHERE user_id = %s
                ORDER BY match_score DESC
                LIMIT 1
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'job_title': result['job_title'],
                    'match_score': float(result['match_score']),
                    'industry': result['industry'],
                    'city': result['city']
                }
            return None
    finally:
        conn.close()


def save_learning_plan(plan) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO learning_plans (user_id, target_job, plan_type, phases, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                target_job = VALUES(target_job), plan_type = VALUES(plan_type),
                phases = VALUES(phases), updated_at = NOW()
            """, (
                plan.user_id,
                plan.target_job,
                plan.plan_type,
                json.dumps(plan.phases, ensure_ascii=False)
            ))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_learning_plan(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT target_job, plan_type, phases, created_at, updated_at
                FROM learning_plans
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'target_job': result['target_job'],
                    'plan_type': result['plan_type'],
                    'phases': json.loads(result['phases']) if result['phases'] else [],
                    'created_at': result['created_at'],
                    'updated_at': result['updated_at']
                }
            return None
    finally:
        conn.close()


def save_learning_task(task) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO learning_tasks (user_id, task_date, task_type, task_content, 
                                          estimated_time, completed, resources, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                task.user_id,
                task.task_date,
                task.task_type,
                task.task_content,
                task.estimated_time,
                task.completed,
                json.dumps(task.resources, ensure_ascii=False) if task.resources else "[]"
            ))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def save_daily_tasks(tasks) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            for task in tasks:
                cursor.execute("""
                    INSERT INTO learning_tasks (user_id, task_date, task_type, task_content, 
                                              estimated_time, completed, resources, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    task.user_id,
                    datetime.now().strftime('%Y-%m-%d'),  # 使用当前日期作为 task_date
                    'daily',  # 设置默认 task_type
                    task.title,  # 使用 title 作为 task_content
                    task.duration,  # 使用 duration 作为 estimated_time
                    task.status == 'completed',  # 转换 status 为 completed 布尔值
                    json.dumps(task.resources, ensure_ascii=False) if task.resources else "[]"
                ))
            conn.commit()
            return len(tasks) > 0
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1146:  # Table doesn't exist
            print("Error: learning_tasks table doesn't exist. Please create it first.")
            # Create the table if it doesn't exist
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_tasks (
                        task_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        task_date DATE NOT NULL,
                        task_type VARCHAR(50) NOT NULL,
                        task_content TEXT NOT NULL,
                        estimated_time VARCHAR(50),
                        completed BOOLEAN DEFAULT FALSE,
                        resources JSON,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
                # Try inserting again
                for task in tasks:
                    cursor.execute("""
                        INSERT INTO learning_tasks (user_id, task_date, task_type, task_content, 
                                                  estimated_time, completed, resources, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        task.user_id,
                        datetime.now().strftime('%Y-%m-%d'),
                        'daily',
                        task.title,
                        task.duration,
                        task.status == 'completed',
                        json.dumps(task.resources, ensure_ascii=False) if task.resources else "[]"
                    ))
                conn.commit()
                return len(tasks) > 0
            except Exception as create_error:
                print(f"Error creating learning_tasks table: {create_error}")
                return False
        else:
            print(f"Database error: {e}")
            return False
    except Exception as e:
        print(f"Error saving daily tasks: {e}")
        return False
    finally:
        conn.close()


def update_task_status(task_id: int, completed: bool) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE learning_tasks 
                SET completed = %s, updated_at = NOW() 
                WHERE task_id = %s
            """, (completed, task_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_daily_tasks(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT task_id, task_date, task_type, task_content, 
                       estimated_time, completed, resources
                FROM learning_tasks
                WHERE user_id = %s
                ORDER BY task_date DESC, task_id ASC
            """, (user_id,))
            tasks = []
            for row in cursor.fetchall():
                task = {
                    'task_id': row['task_id'],
                    'task_date': row['task_date'].strftime('%Y-%m-%d') if row['task_date'] else None,
                    'task_type': row['task_type'],
                    'task_content': row['task_content'],
                    'estimated_time': row['estimated_time'],
                    'completed': row['completed'],
                    'resources': json.loads(row['resources']) if row['resources'] else []
                }
                tasks.append(task)
            return tasks
    finally:
        conn.close()

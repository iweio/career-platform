import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field
from .config import settings
from .db_utils import (
    get_user_profile, get_user_favorite_job_ids, get_job_detail,
    get_job_profile_from_neo4j, save_match_report, get_job_details_batch
)
#这里是数据库的导入吗？


class WeightResult(BaseModel):
    专业技能: float = Field(description="专业技能权重")
    证书: float = Field(description="证书权重")
    创新能力: float = Field(description="创新能力权重")
    学习能力: float = Field(description="学习能力权重")
    抗压能力: float = Field(description="抗压能力权重")
    沟通能力: float = Field(description="沟通能力权重")
    实习能力: float = Field(description="实习能力权重")


class DimensionScore(BaseModel):
    score: int = Field(description="该维度得分(0-100)")
    gap: str = Field(description="差距描述")
#差距描述是什么？gap 是 差距描述 （Gap Description），用于记录用户在该维度与岗位要求之间的具体差距

class MatchResult(BaseModel):
    专业技能: DimensionScore
    证书: DimensionScore
    创新能力: DimensionScore
    学习能力: DimensionScore
    抗压能力: DimensionScore
    沟通能力: DimensionScore
    实习能力: DimensionScore
    total_score: float = Field(description="加权总分")
    job_type: str = Field(default="", description="岗位类型")


class JobMatchAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL,
            temperature=0.3
        )
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_MATCHES)
        self._setup_chains()

    def _setup_chains(self):
        weight_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个岗位分析专家。根据岗位信息（岗位详情与公司详情）评估该岗位对人员在以下7个维度的重视程度，并给出相应的权重（总和必须等于1）。
            维度说明：
            - 专业技能：技术能力、专业知识
            - 证书：相关资质证书
            - 创新能力：创新思维、问题解决能力
            - 学习能力：学习速度、知识吸收能力
            - 抗压能力：压力管理、危机处理
            - 沟通能力：团队协作、表达沟通
            - 实习能力：实践经验、项目经验

            参考：
            - 技术岗：专业技能权重较高(0.3-0.5)
            - 管理岗：沟通能力、抗压能力权重较高
            - 其他岗位：相对均衡

            请直接返回JSON格式的权重配置。"""),
            ("user", """岗位标题：{job_title}     
                        岗位详情：{job_detail}
                        公司详情：{company_detail}
             请分析该岗位并返回各维度权重。""")
        ])
        #改成岗位id？因为岗位标题可能会重复
        self.weight_chain = weight_prompt | self.llm | JsonOutputParser()

        match_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的人岗匹配分析师。请对比用户画像和岗位要求，
            对每个维度进行评分（0-100分）并给出差距描述。

            评分标准：
            - 90-100分：完全匹配或超出要求
            - 70-89分：基本匹配，有少量差距
            - 50-69分：部分匹配，有明显差距
            - 30-49分：差距较大
            - 0-29分：严重不匹配

            请返回JSON格式结果，包含每个维度的score和gap，以及加权总分total_score。"""),
            ("user", """用户画像：
            {user_profile}

            岗位要求：
            {job_requirement}                                          

            各维度权重：
            {weights}   

            请进行匹配分析并返回结果。""")
        ])
         #{job_requirement}是什么？第一次调用 ：MySQL 中的具体岗位详情，第二次调用 ：Neo4j 中的岗位画像

        self.match_chain = match_prompt | self.llm | JsonOutputParser()

    def _determine_weights(self, job_info: Dict[str, Any]) -> Dict[str, float]:
        try:
            result = self.weight_chain.invoke({
                "job_title": job_info.get("title", ""),
                "job_detail": job_info.get("job_detail", ""),
                "company_detail": job_info.get("company_detail", "")
            })
            #确保权重总和为1.0
            total = sum(result.values())
            if abs(total - 1.0) > 0.01:
                result = {k: v / total for k, v in result.items()}
            return result
        #有问题，返回默认权重？
        except Exception as e:
            print(f"Weight determination error: {e}")
            return {
                "专业技能": 0.25, "证书": 0.10, "创新能力": 0.15,
                "学习能力": 0.15, "抗压能力": 0.10, "沟通能力": 0.15, "实习能力": 0.10
            }

    def _calculate_match_score(
        self,
        user_profile: Dict[str, Any],
        job_requirement: Dict[str, Any],
        weights: Dict[str, float],
        requirement_source: str                       #这个是什么？
    ) -> Dict[str, Any]:
        try:
            print(f"[_calculate_match_score] source={requirement_source}, user_profile keys={list(user_profile.keys())}")
            result = self.match_chain.invoke({
                "user_profile": json.dumps(user_profile, ensure_ascii=False, indent=2),
                "job_requirement": json.dumps(job_requirement, ensure_ascii=False, indent=2),
                "weights": json.dumps(weights, ensure_ascii=False, indent=2)
            })
            print(f"[_calculate_match_score] LLM raw result type={type(result)}, result={str(result)[:200]}")

            parsed_result = {}
            if "analysis" in result:
                analysis = result["analysis"]
                if isinstance(analysis, list):
                    for item in analysis:
                        dim = item.get("dimension", "")
                        if dim in weights:
                            parsed_result[dim] = {
                                "score": item.get("score", 50),
                                "gap": item.get("gap", "")
                            }
                elif isinstance(analysis, dict):
                    for dim, data in analysis.items():
                        if dim in weights:
                            parsed_result[dim] = {
                                "score": data.get("score", 50),
                                "gap": data.get("gap", "")
                            }

            for dim in weights:
                if dim not in parsed_result:
                    parsed_result[dim] = {"score": 50, "gap": "无数据"}

            total_score = 0.0
            for dim, weight in weights.items():
                dim_data = parsed_result.get(dim, {"score": 50, "gap": "无数据"})
                score = dim_data.get("score", 50)
                total_score += score * weight

            parsed_result["total_score"] = round(total_score, 2)
            parsed_result["source"] = requirement_source
            return parsed_result
        #当大模型调用失败时，该岗位会被赋予 默认 50 分 （中等分数）。也许需要调整？
        except Exception as e:
            print(f"Match calculation error: {e}")
            return {
                "total_score": 50.0,
                "source": requirement_source,
                "error": str(e)
            }

    def _extract_job_requirement_from_detail(self, job_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": job_info.get("title", ""),           #如果要改成用岗位id索引，这里需要改成岗位id
            "job_detail": job_info.get("job_detail", ""),
            "company_detail": job_info.get("company_detail", ""),
            "source": "具体岗位信息"
        }
    #生成简要匹配报告，如果需要长报告，还需要调用一次大模型
    def _merge_gap_reports(
        self,
        detail_result: Dict[str, Any],
        profile_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        merged = {}
        dimensions = ["专业技能", "证书", "创新能力", "学习能力", "抗压能力", "沟通能力", "实习能力"]

        for dim in dimensions:
            detail_dim = detail_result.get(dim, {"score": 50, "gap": "无要求"})
            profile_dim = profile_result.get(dim, {"score": 50, "gap": "无要求"})

            detail_score = detail_dim.get("score", 50)
            profile_score = profile_dim.get("score", 50)
            avg_score = round((detail_score + profile_score) / 2, 1)

            detail_gap = detail_dim.get("gap", "")
            profile_gap = profile_dim.get("gap", "")

            merged_gap = f"与目标公司要求差距：{detail_gap}；与行业普遍要求差距：{profile_gap}"

            merged[dim] = {
                "score": avg_score,
                "detail_score": detail_score,
                "profile_score": profile_score,
                "gap": merged_gap,
                "detail_gap": detail_gap,
                "profile_gap": profile_gap
            }

        detail_total = detail_result.get("total_score", 50)
        profile_total = profile_result.get("total_score", 50)
        merged["total_score"] = round(0.5 * detail_total + 0.5 * profile_total, 2)
        merged["detail_total_score"] = detail_total
        merged["profile_total_score"] = profile_total

        return merged
    #单个岗位的完整匹配流程 ，包含同步执行和异步包装两个方法。
    def _match_single_job(
        self,
        user_profile: Dict[str, Any],
        job_info: Dict[str, Any],
        job_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        weights = self._determine_weights(job_info)

        detail_requirement = self._extract_job_requirement_from_detail(job_info)
        detail_result = self._calculate_match_score(
            user_profile, detail_requirement, weights, "具体岗位信息"
        )

        if job_profile:
            profile_result = self._calculate_match_score(
                user_profile, job_profile, weights, "岗位画像"
            )
        else:
            profile_result = {
                "total_score": 50.0,
                "source": "岗位画像",
                "note": "未找到岗位画像，使用默认分数"
            }
            for dim in ["专业技能", "证书", "创新能力", "学习能力", "抗压能力", "沟通能力", "实习能力"]:
                profile_result[dim] = {"score": 50, "gap": "无岗位画像数据"}

        merged_result = self._merge_gap_reports(detail_result, profile_result)

        return {
            "job_id": job_info.get("id"),
            "job_title": job_info.get("title"),
            "weights": weights,
            "detail_match": detail_result,
            "profile_match": profile_result,
            "merged_result": merged_result,
            "final_score": merged_result["total_score"]
        }

    async def _async_match_job(
        self,
        user_profile: Dict[str, Any],
        job_info: Dict[str, Any],
        job_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._match_single_job,
            user_profile,
            job_info,
            job_profile
        )

    def run_match(self, user_id: int) -> Dict[str, Any]:
        user_profile = get_user_profile(user_id)
        if not user_profile:
            return {"error": f"未找到用户 {user_id} 的画像数据", "user_id": user_id}

        favorite_job_ids = get_user_favorite_job_ids(user_id)
        if not favorite_job_ids:
            return {"error": f"用户 {user_id} 没有收藏任何岗位", "user_id": user_id}

        job_details = get_job_details_batch(favorite_job_ids)

        async def match_all_jobs():
            tasks = []
            for job_id in favorite_job_ids:
                job_info = job_details.get(job_id)
                if not job_info:
                    continue

                job_profile = get_job_profile_from_neo4j(job_info.get("title", ""))

                task = self._async_match_job(user_profile, job_info, job_profile)
                tasks.append(task)

            return await asyncio.gather(*tasks)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            match_results = loop.run_until_complete(match_all_jobs())
        finally:
            loop.close()

        if not match_results:
            return {"error": "无法匹配任何岗位", "user_id": user_id}

        sorted_results = sorted(match_results, key=lambda x: x["final_score"], reverse=True)
        best_match = sorted_results[0]

        report_json = {
            "user_id": user_id,
            "job_id": best_match["job_id"],
            "job_title": best_match["job_title"],
            "final_score": best_match["final_score"],
            "merged_result": best_match["merged_result"],
            "weights": best_match["weights"]
        }

        try:
            save_match_report({
                "user_id": user_id,
                "best_match_score": best_match["final_score"],
                "best_match": {
                    "job_title": best_match["job_title"],
                    "final_score": best_match["final_score"],
                    "industry": best_match.get("industry", ""),
                    "city": best_match.get("city", "")
                }
            })
        except Exception as e:
            print(f"保存报告失败：{e}")

        return {
            "user_id": user_id,
            "match_results": [
                {
                    "job_id": r["job_id"],
                    "job_title": r["job_title"],
                    "final_score": r["final_score"],
                    "detail_score": r["detail_match"].get("total_score", 0) if r.get("detail_match") else 0,
                    "profile_score": r["profile_match"].get("total_score", 0) if r.get("profile_match") else 0,
                    "merged_result": r.get("merged_result", {})
                }
                for r in sorted_results
            ],
            "best_match": {
                "job_id": best_match["job_id"],
                "job_title": best_match["job_title"],
                "final_score": best_match["final_score"],
                "gap_report": best_match["merged_result"]
            }
        }


agent_instance: Optional[JobMatchAgent] = None


def get_agent() -> JobMatchAgent:
    global agent_instance
    if agent_instance is None:
        agent_instance = JobMatchAgent()
    return agent_instance


def run_match(user_id: int) -> Dict[str, Any]:
    return get_agent().run_match(user_id)

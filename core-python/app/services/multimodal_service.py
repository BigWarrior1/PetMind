"""
多模态服务
宠物健康图片分析（皮肤、外伤、排泄物等）
"""
import uuid
from typing import Optional, Dict, List
from app.services.llm_service import get_llm_service
from app.rag.retriever import RAGRetriever

# 默认系统提示词
DEFAULT_IMAGE_PROMPT = """你是一个专业的宠物健康顾问，擅长分析宠物图片并提供健康建议。

你的职责：
1. 仔细观察用户上传的图片，描述你看到的具体情况
2. 基于图片内容，结合宠物健康知识进行分析
3. 当情况危急时（如严重外伤、出血、脱水症状等），提醒用户立即就医
4. 始终强调：你的分析仅供参考，不能替代执业兽医的诊断

图片分析要求：
- 详细描述图片中宠物的状态
- 指出可能的健康问题
- 提供初步建议
- 如需进一步检查，说明需要做什么

语言要求：
- 语言通俗易懂，适合普通宠物主人理解
- 回答要专业但不要过度使用专业术语
"""


class MultiModalService:
    """多模态服务类"""

    def __init__(self):
        self.llm_service = get_llm_service()
        self.retriever = RAGRetriever()

    def _build_image_prompt(self, question: str, pet_info: Optional[Dict] = None) -> str:
        """
        构建图片分析提示词

        Args:
            question: 用户问题
            pet_info: 宠物信息

        Returns:
            完整的用户提示词
        """
        pet_context = ""
        if pet_info:
            pet_context = f"\n\n用户宠物信息：\n- 种类：{pet_info.get('species', '未知')}\n- 品种：{pet_info.get('breed', '未知')}\n- 年龄：{pet_info.get('age', '未知')}\n- 体重：{pet_info.get('weight', '未知')}\n"

        prompt = f"""请分析这张宠物图片，并回答用户的问题。

用户问题：{question}
{pet_context}

请详细描述图片内容，并回答用户的问题。如果图片中宠物的状态令人担忧，请明确告知。"""
        return prompt

    def analyze_pet_image(
        self,
        image_path: str,
        question: str = "请分析这张图片中的宠物健康状况",
        pet_info: Optional[Dict] = None,
    ) -> Dict:
        """
        分析单张宠物图片

        Args:
            image_path: 图片路径
            question: 用户的问题
            pet_info: 宠物信息

        Returns:
            {
                "analysis": "图片分析结果",
                "image_description": "图片描述",
                "warning": "就医警示（如有）",
                "sources": "相关知识来源（如有）"
            }
        """
        # 构建提示词
        user_prompt = self._build_image_prompt(question, pet_info)

        # 调用 LLM 分析图片
        analysis = self.llm_service.analyze_image(
            image_path=image_path,
            user_prompt=user_prompt,
            system_prompt=DEFAULT_IMAGE_PROMPT,
        )

        # 检查是否需要就医警示
        warning = self._check_warning(analysis)

        # 尝试检索相关知识
        sources = []
        documents, source_list = self.retriever.retrieve_with_sources(question)
        if documents:
            sources = source_list

        return {
            "analysis": analysis,
            "warning": warning,
            "sources": sources,
        }

    def analyze_pet_images(
        self,
        image_paths: List[str],
        question: str = "请分析这些图片中的宠物健康状况",
        pet_info: Optional[Dict] = None,
    ) -> Dict:
        """
        分析多张宠物图片

        Args:
            image_paths: 图片路径列表
            question: 用户的问题
            pet_info: 宠物信息

        Returns:
            {
                "analysis": "图片分析结果",
                "warning": "就医警示（如有）",
                "sources": "相关知识来源（如有）"
            }
        """
        # 构建提示词
        user_prompt = self._build_image_prompt(question, pet_info)

        # 调用 LLM 分析多张图片
        analysis = self.llm_service.analyze_images(
            image_paths=image_paths,
            user_prompt=user_prompt,
            system_prompt=DEFAULT_IMAGE_PROMPT,
        )

        # 检查是否需要就医警示
        warning = self._check_warning(analysis)

        # 尝试检索相关知识
        sources = []
        documents, source_list = self.retriever.retrieve_with_sources(question)
        if documents:
            sources = source_list

        return {
            "analysis": analysis,
            "warning": warning,
            "sources": sources,
        }

    def _check_warning(self, analysis: str) -> Optional[str]:
        """检查是否需要就医警示"""
        keywords = [
            "严重", "危急", "大量出血", "呼吸困难",
            "昏迷", "中毒", "骨折", "休克", "脱水",
            "高烧", "持续呕吐", "便血", "血尿",
        ]

        analysis_lower = analysis.lower()
        for keyword in keywords:
            if keyword in analysis:
                return "⚠️ 根据图片分析，宠物状况可能需要立即就医，建议尽快联系兽医！"

        return None


# 全局单例
_multimodal_service: Optional[MultiModalService] = None


def get_multimodal_service() -> MultiModalService:
    """获取全局多模态服务实例"""
    global _multimodal_service
    if _multimodal_service is None:
        _multimodal_service = MultiModalService()
    return _multimodal_service

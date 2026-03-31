"""
多模态 API 端点
处理宠物图片上传和分析
"""
import os
import uuid
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.services.multimodal_service import get_multimodal_service

router = APIRouter()

# 上传目录
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class PetInfo(BaseModel):
    """宠物信息"""
    species: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[str] = None
    weight: Optional[str] = None


class ImageAnalysisRequest(BaseModel):
    """单图分析请求"""
    question: str = "请分析这张图片中的宠物健康状况"
    pet_info: Optional[PetInfo] = None


class ImageAnalysisResponse(BaseModel):
    """图片分析响应"""
    analysis: str
    warning: Optional[str] = None
    sources: List[dict] = []


@router.post("/analyze/image", response_model=ImageAnalysisResponse)
async def analyze_single_image(
    file: UploadFile = File(...),
    question: str = Form("请分析这张图片中的宠物健康状况"),
    species: Optional[str] = Form(None),
    breed: Optional[str] = Form(None),
    age: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
):
    """
    分析单张宠物图片

    - **file**: 图片文件 (支持 jpg, png, jpeg)
    - **question**: 关于图片的问题
    - **species**: 宠物种类（狗/猫）
    - **breed**: 宠物品种
    - **age**: 宠物年龄
    - **weight**: 宠物体重
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}，支持的类型: jpg, png, jpeg"
        )

    # 保存上传的文件
    file_ext = file.filename.split(".")[-1] if file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 构建宠物信息
    pet_info = None
    if any([species, breed, age, weight]):
        pet_info = {
            "species": species,
            "breed": breed,
            "age": age,
            "weight": weight,
        }

    # 调用多模态服务
    try:
        multimodal_service = get_multimodal_service()
        result = multimodal_service.analyze_pet_image(
            image_path=file_path,
            question=question,
            pet_info=pet_info,
        )
    except Exception as e:
        # 清理上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")

    # 清理上传的文件
    if os.path.exists(file_path):
        os.remove(file_path)

    return ImageAnalysisResponse(**result)


@router.post("/analyze/images", response_model=ImageAnalysisResponse)
async def analyze_multiple_images(
    files: List[UploadFile] = File(...),
    question: str = Form("请分析这些图片中的宠物健康状况"),
    species: Optional[str] = Form(None),
    breed: Optional[str] = Form(None),
    age: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
):
    """
    分析多张宠物图片

    - **files**: 图片文件列表 (支持 jpg, png, jpeg，最多 5 张)
    - **question**: 关于图片的问题
    - **species**: 宠物种类（狗/猫）
    - **breed**: 宠物品种
    - **age**: 宠物年龄
    - **weight**: 宠物体重
    """
    # 验证文件数量
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="最多支持上传 5 张图片")

    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.content_type}，支持的类型: jpg, png, jpeg"
            )

    # 保存上传的文件
    file_paths = []
    for file in files:
        file_ext = file.filename.split(".")[-1] if file.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            file_paths.append(file_path)
        except Exception as e:
            # 清理已保存的文件
            for path in file_paths:
                if os.path.exists(path):
                    os.remove(path)
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 构建宠物信息
    pet_info = None
    if any([species, breed, age, weight]):
        pet_info = {
            "species": species,
            "breed": breed,
            "age": age,
            "weight": weight,
        }

    # 调用多模态服务
    try:
        multimodal_service = get_multimodal_service()
        result = multimodal_service.analyze_pet_images(
            image_paths=file_paths,
            question=question,
            pet_info=pet_info,
        )
    except Exception as e:
        # 清理上传的文件
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")

    # 清理上传的文件
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)

    return ImageAnalysisResponse(**result)

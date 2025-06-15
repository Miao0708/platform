"""
Git配置相关API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_git import git_credential, repository
from app.schemas.git import (
    GitCredentialCreate, GitCredentialUpdate, GitCredentialResponse,
    GitConnectionTestRequest, GitConnectionTestResponse,
    RepositoryCreate, RepositoryUpdate, RepositoryResponse
)
from app.core.git_utils import test_git_connection
from app.core.security import decrypt_token

router = APIRouter()


@router.post("/credentials", response_model=GitCredentialResponse)
def create_git_credential(
    *,
    db: Session = Depends(get_db),
    credential_in: GitCredentialCreate
):
    """创建Git凭证"""
    try:
        credential = git_credential.create(db=db, obj_in=credential_in)
        return credential
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/credentials", response_model=List[GitCredentialResponse])
def read_git_credentials(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """获取Git凭证列表"""
    credentials = git_credential.get_multi(db, skip=skip, limit=limit)
    return credentials


@router.get("/credentials/{credential_id}", response_model=GitCredentialResponse)
def read_git_credential(
    *,
    db: Session = Depends(get_db),
    credential_id: int
):
    """获取单个Git凭证"""
    credential = git_credential.get(db=db, id=credential_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Git凭证不存在"
        )
    return credential


@router.put("/credentials/{credential_id}", response_model=GitCredentialResponse)
def update_git_credential(
    *,
    db: Session = Depends(get_db),
    credential_id: int,
    credential_in: GitCredentialUpdate
):
    """更新Git凭证"""
    credential = git_credential.get(db=db, id=credential_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Git凭证不存在"
        )
    
    try:
        credential = git_credential.update(
            db=db, db_obj=credential, obj_in=credential_in
        )
        return credential
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/credentials/{credential_id}")
def delete_git_credential(
    *,
    db: Session = Depends(get_db),
    credential_id: int
):
    """删除Git凭证"""
    credential = git_credential.get(db=db, id=credential_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Git凭证不存在"
        )
    
    git_credential.remove(db=db, id=credential_id)
    return {"message": "Git凭证已删除"}


@router.post("/credentials/test", response_model=GitConnectionTestResponse)
def test_git_connection_endpoint(
    *,
    db: Session = Depends(get_db),
    test_request: GitConnectionTestRequest
):
    """测试Git连接"""
    # 获取激活的凭证
    active_credential = git_credential.get_active_credential(db)
    if not active_credential:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有激活的Git凭证"
        )
    
    # 确定测试URL
    test_url = test_request.test_url
    if not test_url:
        # 如果没有提供测试URL，使用第一个激活的仓库
        active_repos = repository.get_active_repositories(db)
        if not active_repos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有可用的仓库进行测试"
            )
        test_url = active_repos[0].url
    
    # 解密token并测试连接
    try:
        token = decrypt_token(active_credential.encrypted_token)
        success, message = test_git_connection(
            test_url, active_credential.username, token
        )
        
        return GitConnectionTestResponse(
            success=success,
            message=message,
            test_url=test_url
        )
    except Exception as e:
        return GitConnectionTestResponse(
            success=False,
            message=f"测试失败: {str(e)}",
            test_url=test_url
        )


# 仓库配置相关端点
@router.post("/repositories", response_model=RepositoryResponse)
def create_repository(
    *,
    db: Session = Depends(get_db),
    repository_in: RepositoryCreate
):
    """创建仓库配置"""
    try:
        repo = repository.create(db=db, obj_in=repository_in)
        return repo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建仓库配置失败: {str(e)}"
        )


@router.get("/repositories", response_model=List[RepositoryResponse])
def read_repositories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """获取仓库配置列表"""
    repositories = repository.get_multi(db, skip=skip, limit=limit)
    return repositories


@router.get("/repositories/{repository_id}", response_model=RepositoryResponse)
def read_repository(
    *,
    db: Session = Depends(get_db),
    repository_id: int
):
    """获取单个仓库配置"""
    repo = repository.get(db=db, id=repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库配置不存在"
        )
    return repo


@router.put("/repositories/{repository_id}", response_model=RepositoryResponse)
def update_repository(
    *,
    db: Session = Depends(get_db),
    repository_id: int,
    repository_in: RepositoryUpdate
):
    """更新仓库配置"""
    repo = repository.get(db=db, id=repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库配置不存在"
        )

    try:
        repo = repository.update(db=db, db_obj=repo, obj_in=repository_in)
        return repo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/repositories/{repository_id}")
def delete_repository(
    *,
    db: Session = Depends(get_db),
    repository_id: int
):
    """删除仓库配置"""
    repo = repository.get(db=db, id=repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库配置不存在"
        )

    repository.remove(db=db, id=repository_id)
    return {"message": "仓库配置已删除"}

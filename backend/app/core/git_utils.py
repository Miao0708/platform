"""
Git操作工具函数
"""
import subprocess
import tempfile
import os
from typing import List, Optional, Tuple
from app.schemas.git import BranchInfo, CommitInfo


def test_git_connection(url: str, username: str, token: str) -> Tuple[bool, str]:
    """
    测试Git连接
    
    Args:
        url: 仓库URL
        username: 用户名
        token: 访问令牌
        
    Returns:
        (是否成功, 消息)
    """
    try:
        # 构建带认证的URL
        if url.startswith("https://"):
            auth_url = url.replace("https://", f"https://{username}:{token}@")
        else:
            return False, "仅支持HTTPS协议的仓库URL"
        
        # 执行git ls-remote命令测试连接
        result = subprocess.run(
            ["git", "ls-remote", auth_url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, "连接成功"
        else:
            return False, f"连接失败: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "连接超时"
    except FileNotFoundError:
        return False, "Git命令未找到，请确保已安装Git"
    except Exception as e:
        return False, f"连接测试失败: {str(e)}"


def get_remote_branches(url: str, username: str, token: str) -> List[str]:
    """
    获取远程分支列表
    
    Args:
        url: 仓库URL
        username: 用户名
        token: 访问令牌
        
    Returns:
        分支名称列表
    """
    try:
        # 构建带认证的URL
        if url.startswith("https://"):
            auth_url = url.replace("https://", f"https://{username}:{token}@")
        else:
            return []
        
        # 执行git ls-remote命令获取分支
        result = subprocess.run(
            ["git", "ls-remote", "--heads", auth_url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # 格式: commit_hash refs/heads/branch_name
                    parts = line.split('\t')
                    if len(parts) == 2 and parts[1].startswith('refs/heads/'):
                        branch_name = parts[1].replace('refs/heads/', '')
                        branches.append(branch_name)
            return branches
        else:
            return []
            
    except Exception:
        return []


def get_recent_commits(
    url: str, username: str, token: str, branch: str = "main", limit: int = 10
) -> List[CommitInfo]:
    """
    获取最近的提交记录
    
    Args:
        url: 仓库URL
        username: 用户名
        token: 访问令牌
        branch: 分支名
        limit: 限制数量
        
    Returns:
        提交信息列表
    """
    try:
        # 构建带认证的URL
        if url.startswith("https://"):
            auth_url = url.replace("https://", f"https://{username}:{token}@")
        else:
            return []
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 克隆仓库（仅获取指定分支的最近提交）
            clone_result = subprocess.run(
                [
                    "git", "clone", "--depth", str(limit), 
                    "--branch", branch, auth_url, temp_dir
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if clone_result.returncode != 0:
                return []
            
            # 获取提交历史
            log_result = subprocess.run(
                [
                    "git", "log", f"--max-count={limit}",
                    "--pretty=format:%H|%an|%s|%ai"
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if log_result.returncode == 0:
                commits = []
                for line in log_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) == 4:
                            commits.append(CommitInfo(
                                hash=parts[0],
                                author=parts[1],
                                message=parts[2],
                                date=parts[3]
                            ))
                return commits
            else:
                return []
                
    except Exception:
        return []


def generate_diff(
    url: str, username: str, token: str, 
    base_ref: str, head_ref: str, output_path: str
) -> Tuple[bool, str]:
    """
    生成代码差异文件
    
    Args:
        url: 仓库URL
        username: 用户名
        token: 访问令牌
        base_ref: 基准引用（分支或提交）
        head_ref: 目标引用（分支或提交）
        output_path: 输出文件路径
        
    Returns:
        (是否成功, 消息)
    """
    try:
        # 构建带认证的URL
        if url.startswith("https://"):
            auth_url = url.replace("https://", f"https://{username}:{token}@")
        else:
            return False, "仅支持HTTPS协议的仓库URL"
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 克隆仓库
            clone_result = subprocess.run(
                ["git", "clone", auth_url, temp_dir],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if clone_result.returncode != 0:
                return False, f"克隆仓库失败: {clone_result.stderr}"
            
            # 生成diff
            diff_result = subprocess.run(
                ["git", "diff", base_ref, head_ref],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if diff_result.returncode == 0:
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 写入diff文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(diff_result.stdout)
                
                return True, f"差异文件已生成: {output_path}"
            else:
                return False, f"生成差异失败: {diff_result.stderr}"
                
    except Exception as e:
        return False, f"生成差异失败: {str(e)}"

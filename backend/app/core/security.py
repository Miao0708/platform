"""
安全相关功能：密码哈希、简单认证等
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密实例
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())


def create_access_token(
    subject: Union[str, int], expires_delta: Optional[timedelta] = None
) -> str:
    """创建简单的访问令牌（使用随机字符串）"""
    # 生成随机token
    token = secrets.token_urlsafe(32)
    return f"{subject}:{token}:{int(datetime.utcnow().timestamp())}"


def verify_token(token: str) -> Optional[str]:
    """验证令牌并返回用户ID"""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None

        user_id, token_part, timestamp = parts

        # 检查token是否过期（30天）
        token_time = datetime.fromtimestamp(int(timestamp))
        if datetime.utcnow() - token_time > timedelta(days=30):
            return None

        return user_id
    except (ValueError, Exception):
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def encrypt_text(plain_text: str) -> str:
    """加密文本"""
    encrypted_bytes = cipher_suite.encrypt(plain_text.encode())
    return encrypted_bytes.decode()


def decrypt_text(encrypted_text: str) -> str:
    """解密文本"""
    decrypted_bytes = cipher_suite.decrypt(encrypted_text.encode())
    return decrypted_bytes.decode()


def encrypt_token(token: str) -> str:
    """加密令牌（用于存储Git Token等敏感信息）"""
    return encrypt_text(token)


def decrypt_token(encrypted_token: str) -> str:
    """解密令牌"""
    return decrypt_text(encrypted_token)

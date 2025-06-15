#!/usr/bin/env python3
"""
创建管理员用户的脚本
"""
import sys
import os

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlmodel import Session
from app.core.database import engine
from app.crud.crud_user import user
from app.schemas.user import UserRegister


def create_admin_user(username: str = "admin", 
                     password: str = "admin123456"):
    """创建管理员用户"""
    
    with Session(engine) as db:
        # 检查是否已存在用户
        existing_user = user.get_by_username(db, username=username)
        if existing_user:
            print(f"❌ 用户名 '{username}' 已存在")
            return False
        
        try:
            # 创建用户
            admin_data = UserRegister(
                username=username,
                password=password
            )
            admin_user = user.create(db=db, obj_in=admin_data)
            
            # 设置为超级用户
            admin_user.is_superuser = True
            admin_user.is_verified = True
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print(f"✅ 管理员用户创建成功:")
            print(f"   ID: {admin_user.id}")
            print(f"   用户名: {admin_user.username}")
            print(f"   密码: {password}")
            print(f"   超级用户: {admin_user.is_superuser}")
            print(f"   创建时间: {admin_user.created_at}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建管理员用户失败: {str(e)}")
            return False


def list_all_users():
    """列出所有用户"""
    with Session(engine) as db:
        users = user.get_multi(db, limit=100)
        if not users:
            print("📝 数据库中暂无用户")
            return
        
        print(f"📝 当前数据库中的用户 (共 {len(users)} 个):")
        print("-" * 60)
        for u in users:
            print(f"ID: {u.id:3d} | 用户名: {u.username:15s} | 超级用户: {u.is_superuser}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python create_admin.py create [username] [password]")
        print("  python create_admin.py list")
        print("")
        print("示例:")
        print("  python create_admin.py create")
        print("  python create_admin.py create admin admin123456")
        print("  python create_admin.py list")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        # 解析参数
        username = sys.argv[2] if len(sys.argv) > 2 else "admin"
        password = sys.argv[3] if len(sys.argv) > 3 else "admin123456"
        
        print(f"🚀 正在创建管理员用户...")
        success = create_admin_user(username, password)
        
        if success:
            print(f"\n⚠️  请及时修改默认密码以确保安全!")
        
    elif command == "list":
        list_all_users()
        
    else:
        print(f"❌ 未知命令: {command}")
        print("支持的命令: create, list")


if __name__ == "__main__":
    main() 
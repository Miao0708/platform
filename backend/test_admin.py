#!/usr/bin/env python3
"""
测试管理员用户创建的调试脚本
"""
import sys
import os

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    print("1. 导入模块...")
    from sqlmodel import Session
    from app.core.database import engine
    from app.crud.crud_user import user
    from app.schemas.user import UserRegister
    print("✅ 模块导入成功")

    print("\n2. 测试数据库连接...")
    with Session(engine) as db:
        print("✅ 数据库连接成功")
        
        print("\n3. 查询现有用户...")
        existing_user = user.get_by_username(db, username="admin")
        print(f"现有admin用户: {existing_user}")
        
        if not existing_user:
            print("\n4. 创建admin用户...")
            admin_data = UserRegister(
                username="admin",
                email="admin@platform.com",
                password="admin123456",
                full_name="系统管理员"
            )
            print(f"用户数据: {admin_data}")
            
            try:
                admin_user = user.create(db=db, obj_in=admin_data)
                print(f"✅ 用户创建成功: {admin_user}")
                
                # 设置为超级用户
                admin_user.is_superuser = True
                admin_user.is_verified = True
                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)
                
                print(f"✅ 管理员用户创建完成:")
                print(f"   ID: {admin_user.id}")
                print(f"   用户名: {admin_user.username}")
                print(f"   邮箱: {admin_user.email}")
                print(f"   超级用户: {admin_user.is_superuser}")
                
            except Exception as e:
                print(f"❌ 创建用户失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"ℹ️  管理员用户已存在: {existing_user.username}")

except Exception as e:
    print(f"❌ 脚本执行失败: {e}")
    import traceback
    traceback.print_exc() 
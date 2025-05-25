# User 用户模型文档

## 概述

`User` 模型是基于 SQLModel 构建的用户管理系统核心模型，用于管理系统中的用户信息、身份认证和权限分配。该模型与部门模型关联，支持基于部门的用户管理，并集成了角色权限系统，是整个系统的用户管理基础。

## 模型结构

### 数据表信息
- **表名**: `users`
- **主键**: `id`
- **外键**: `department_id` (关联到 `departments.id`)

### 字段说明

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| `id` | `Optional[int]` | 主键，自增 | 用户唯一标识符 |
| `username` | `str` | 必填，唯一，索引 | 用户名，用于登录 |
| `password_hash` | `str` | 必填 | 密码哈希值（SM3加密） |
| `id_card_number` | `str` | 必填 | 身份证号码 |
| `phone_number` | `str` | 必填 | 手机号码 |
| `real_name` | `str` | 必填 | 真实姓名 |
| `department_id` | `int` | 外键，必填 | 所属部门ID，关联到departments表 |
| `login_attempts` | `int` | 默认0 | 登录尝试次数，用于安全控制 |
| `role_ids` | `List[int]` | JSON类型，默认空列表 | 用户拥有的角色ID列表 |
| `created_at` | `datetime` | 自动生成 | 创建时间（UTC时区） |
| `updated_at` | `datetime` | 自动生成 | 更新时间（UTC时区） |

## 异常处理

### UserModelException

自定义异常类，用于处理用户模型相关的异常情况。

**属性**:
- `code`: 错误代码
- `message`: 错误信息

**构造函数**:
```python
def __init__(self, code: int, message: str)
```

## 静态方法详解

### hash_password() - 密码哈希处理

```python
@staticmethod
def hash_password(password: str) -> str
```

**功能**: 将明文密码进行SM3哈希处理

**参数**:
- `password` (str): 需要进行哈希处理的明文密码

**返回值**: 
- `str`: 经过SM3哈希处理后的密码字符串（十六进制格式）

**安全特性**:
- 使用SM3国密哈希算法
- 添加固定盐值"舒一君"和"1e9ffcec"增强安全性
- 相同输入总是产生相同哈希值

**使用示例**:
```python
hashed = User.hash_password("mypassword123")
print(hashed)  # 输出十六进制哈希值
```

## 类方法详解

### 1. create() - 创建用户

```python
@classmethod
def create(cls, username: str, password: str, id_card_number: str, 
          phone_number: str, real_name: str, department_id: int) -> Dict[str, str]
```

**功能**: 创建新的用户记录

**参数**:
- `username` (str): 用户名，必填，系统内唯一
- `password` (str): 明文密码，将自动进行哈希处理
- `id_card_number` (str): 身份证号码，必填
- `phone_number` (str): 手机号码，必填
- `real_name` (str): 真实姓名，必填
- `department_id` (int): 所属部门ID，必填

**返回值**: 
- 成功: `{'success': "用户创建成功"}`

**异常**:
- `UserModelException`: 
  - 400: 用户名已存在
  - 404: 指定的部门不存在
  - 500: 用户创建失败

**业务逻辑**:
1. 验证指定的部门是否存在
2. 对密码进行SM3哈希处理
3. 创建用户记录
4. 提交事务

**使用示例**:
```python
try:
    result = User.create(
        username="zhangsan",
        password="password123",
        id_card_number="110101199001011234",
        phone_number="13800138000",
        real_name="张三",
        department_id=1
    )
    print(result)  # {'success': '用户创建成功'}
except UserModelException as e:
    print(f"创建失败: {e.message}")
```

### 2. update() - 更新用户信息

```python
@classmethod
def update(cls, user_id: int, username: Optional[str] = None,
          id_card_number: Optional[str] = None, phone_number: Optional[str] = None,
          real_name: Optional[str] = None, department_id: Optional[int] = None,
          role_ids: Optional[List[int]] = None) -> Dict[str, str]
```

**功能**: 更新指定用户的信息

**参数**:
- `user_id` (int): 要更新的用户ID，必填
- `username` (Optional[str]): 用户名，可选
- `id_card_number` (Optional[str]): 身份证号码，可选
- `phone_number` (Optional[str]): 手机号码，可选
- `real_name` (Optional[str]): 真实姓名，可选
- `department_id` (Optional[int]): 所属部门ID，可选
- `role_ids` (Optional[List[int]]): 角色ID列表，可选

**返回值**: 
- 成功: `{'success': "用户更新成功"}`

**异常**:
- `UserModelException`: 
  - 400: 用户名已存在
  - 404: 指定的用户不存在或指定的部门不存在
  - 500: 用户更新失败

**注意事项**:
- 只更新传入的非空参数
- 自动更新 `updated_at` 时间戳
- 更新部门时会验证部门是否存在

**使用示例**:
```python
try:
    result = User.update(
        user_id=1,
        real_name="张三丰",
        phone_number="13900139000",
        role_ids=[1, 2, 3]
    )
    print(result)  # {'success': '用户更新成功'}
except UserModelException as e:
    print(f"更新失败: {e.message}")
```

### 3. delete() - 删除用户

```python
@classmethod
def delete(cls, user_id: int) -> Dict[str, str]
```

**功能**: 删除指定的用户记录

**参数**:
- `user_id` (int): 要删除的用户ID

**返回值**: 
- 成功: `{'success': "用户删除成功"}`

**异常**:
- `UserModelException`: 
  - 404: 指定的用户不存在
  - 500: 用户删除失败

**注意事项**: 
- 删除操作不可逆，请谨慎使用
- 建议在删除前检查用户是否有关联数据

**使用示例**:
```python
try:
    result = User.delete(user_id=1)
    print(result)  # {'success': '用户删除成功'}
except UserModelException as e:
    print(f"删除失败: {e.message}")
```

### 4. get_user() - 获取单个用户

```python
@classmethod
def get_user(cls, user_id: Optional[int] = None, 
            username: Optional[str] = None) -> Dict[str, str]
```

**功能**: 根据用户ID或用户名获取用户详细信息

**参数**:
- `user_id` (Optional[int]): 用户ID，可选
- `username` (Optional[str]): 用户名，可选

**返回值**: 包含用户完整信息的字典
```python
{
    "id": int,
    "username": str,
    "id_card_number": str,
    "phone_number": str,
    "real_name": str,
    "department_id": int,
    "role_ids": List[int],
    "login_attempts": int,
    "created_at": datetime,
    "updated_at": datetime
}
```

**异常**:
- `UserModelException`: 
  - 400: 用户ID或用户名不能同时为空
  - 404: 指定的用户不存在
  - 500: 获取用户失败

**注意事项**:
- `user_id` 和 `username` 至少需要提供一个
- 优先使用 `user_id` 进行查询

**使用示例**:
```python
try:
    # 通过用户ID获取
    user = User.get_user(user_id=1)
    print(f"用户名: {user['username']}")
    
    # 通过用户名获取
    user = User.get_user(username="zhangsan")
    print(f"真实姓名: {user['real_name']}")
except UserModelException as e:
    print(f"获取失败: {e.message}")
```

### 5. get_user_by_department_id() - 根据部门获取用户列表

```python
@classmethod
def get_user_by_department_id(cls, department_id: int) -> List[Dict[str, str]]
```

**功能**: 根据部门ID获取该部门下的所有用户列表

**参数**:
- `department_id` (int): 部门ID

**返回值**: 用户信息列表，每个元素包含完整的用户信息字典

**异常**:
- `UserModelException`: 获取失败时抛出

**使用示例**:
```python
try:
    users = User.get_user_by_department_id(department_id=1)
    for user in users:
        print(f"用户: {user['real_name']}, 角色数量: {len(user['role_ids'])}")
except UserModelException as e:
    print(f"获取失败: {e.message}")
```

### 6. verify_password() - 验证用户密码

```python
@classmethod
def verify_password(cls, username: str, password: str) -> bool
```

**功能**: 验证用户密码是否正确

**参数**:
- `username` (str): 用户名
- `password` (str): 明文密码

**返回值**: 
- `bool`: 验证成功返回True，验证失败返回False

**异常**:
- `UserModelException`: 验证过程中发生错误时抛出

**业务逻辑**:
1. 根据用户名查找用户
2. 对输入密码进行哈希处理
3. 比较哈希值是否匹配

**使用示例**:
```python
try:
    is_valid = User.verify_password("zhangsan", "password123")
    if is_valid:
        print("密码验证成功")
    else:
        print("密码验证失败")
except UserModelException as e:
    print(f"验证失败: {e.message}")
```

## 安全特性

### 密码安全

1. **SM3哈希算法**: 使用国密SM3算法进行密码哈希
2. **盐值加密**: 添加固定盐值增强安全性
3. **不可逆加密**: 密码哈希后无法逆向解密

### 登录安全

1. **登录尝试计数**: `login_attempts` 字段记录失败次数
2. **用户名唯一性**: 确保用户名在系统中唯一
3. **身份验证**: 支持用户名密码验证

## 权限管理

### 角色分配

用户的权限通过 `role_ids` 字段管理：

```python
def assign_roles_to_user(user_id: int, role_ids: List[int]):
    """为用户分配角色"""
    try:
        result = User.update(user_id, role_ids=role_ids)
        return result
    except UserModelException as e:
        print(f"角色分配失败: {e.message}")
        return None
```

### 权限检查

```python
def check_user_permission(user_id: int, required_permission: str) -> bool:
    """检查用户是否具有指定权限"""
    try:
        user = User.get_user(user_id)
        from models.core.role import Role
        
        for role_id in user['role_ids']:
            role = Role.get_role(role_id)
            if required_permission in role['permissions']:
                return True
        return False
    except Exception:
        return False
```

## 使用场景

### 1. 用户注册

```python
def register_user(username: str, password: str, real_name: str, 
                 id_card: str, phone: str, department_id: int):
    """用户注册"""
    try:
        # 验证输入数据
        if len(password) < 8:
            raise ValueError("密码长度不能少于8位")
        
        # 创建用户
        result = User.create(
            username=username,
            password=password,
            id_card_number=id_card,
            phone_number=phone,
            real_name=real_name,
            department_id=department_id
        )
        return result
    except UserModelException as e:
        return {"error": e.message}
```

### 2. 用户登录

```python
def login_user(username: str, password: str):
    """用户登录"""
    try:
        # 验证密码
        if User.verify_password(username, password):
            user = User.get_user(username=username)
            # 重置登录尝试次数
            User.update(user['id'], login_attempts=0)
            return {"success": "登录成功", "user": user}
        else:
            # 增加登录尝试次数
            user = User.get_user(username=username)
            if user:
                attempts = user['login_attempts'] + 1
                User.update(user['id'], login_attempts=attempts)
            return {"error": "用户名或密码错误"}
    except UserModelException as e:
        return {"error": e.message}
```

### 3. 批量用户操作

```python
def batch_update_department(user_ids: List[int], new_department_id: int):
    """批量更新用户部门"""
    results = []
    for user_id in user_ids:
        try:
            result = User.update(user_id, department_id=new_department_id)
            results.append({"user_id": user_id, "status": "success"})
        except UserModelException as e:
            results.append({"user_id": user_id, "status": "failed", "error": e.message})
    return results
```

### 4. 用户信息导出

```python
def export_users_by_department(department_id: int):
    """导出部门用户信息"""
    try:
        users = User.get_user_by_department_id(department_id)
        export_data = []
        
        for user in users:
            export_data.append({
                "用户名": user['username'],
                "真实姓名": user['real_name'],
                "身份证号": user['id_card_number'],
                "手机号码": user['phone_number'],
                "创建时间": user['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return export_data
    except UserModelException as e:
        return {"error": e.message}
```

## 注意事项

### 1. 数据完整性
- 创建用户时必须指定有效的部门ID
- 用户名必须在系统中唯一
- 身份证号码和手机号码应该进行格式验证

### 2. 密码安全
- 密码应该满足复杂度要求
- 定期提醒用户更改密码
- 记录密码修改历史

### 3. 权限管理
- 角色分配应该遵循最小权限原则
- 定期审查用户权限
- 及时回收离职用户权限

### 4. 性能考虑
- 角色ID列表存储为JSON格式，查询时需要反序列化
- 对于频繁的用户查询，建议使用缓存机制
- 避免在单个用户上分配过多角色

### 5. 安全性
- 登录失败次数应该有上限控制
- 敏感操作应该记录审计日志
- 定期检查异常登录行为

### 6. 事务管理
- 所有数据库操作都在事务中执行
- 发生异常时会自动回滚事务
- 确保数据一致性


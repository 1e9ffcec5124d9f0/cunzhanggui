# Department 部门模型文档

## 概述

`Department` 模型是基于 SQLModel 构建的部门管理系统核心模型，用于管理组织架构中的部门信息。该模型支持多级部门结构，可以构建完整的组织树形架构。

## 模型结构

### 数据表信息
- **表名**: `departments`
- **主键**: `id`
- **外键**: `parent_id` (自关联到 `departments.id`)

### 字段说明

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| `id` | `Optional[int]` | 主键，自增 | 部门唯一标识符 |
| `name` | `str` | 必填，索引 | 部门名称 |
| `level` | `int` | 必填 | 部门级别：0-根部门, 1-县级, 2-镇街级, 3-村社级 |
| `parent_id` | `int` | 外键 | 父部门ID，关联到本表的id字段 |
| `description` | `Optional[str]` | 可选，默认空字符串 | 部门描述信息 |
| `manager_name` | `Optional[str]` | 可选，默认空字符串 | 部门负责人姓名 |
| `manager_phone` | `Optional[str]` | 可选，默认空字符串 | 部门负责人联系电话 |
| `created_at` | `datetime` | 自动生成 | 创建时间（UTC时区） |
| `updated_at` | `datetime` | 自动生成 | 更新时间（UTC时区） |

## 异常处理

### DepartmentModelException

自定义异常类，用于处理部门模型相关的异常情况。

**属性**:
- `code`: 错误代码
- `message`: 错误信息

**构造函数**:
```python
def __init__(self, code: int, message: str)
```

## 类方法详解

### 1. create() - 创建部门

```python
@classmethod
def create(cls, name: str, level: int, parent_id: int, 
          description: Optional[str] = None, 
          manager_name: Optional[str] = None, 
          manager_phone: Optional[str] = None) -> Dict[str, str]
```

**功能**: 创建新的部门记录

**参数**:
- `name` (str): 部门名称，必填
- `level` (int): 部门级别，必填
- `parent_id` (int): 父部门ID，必填
- `description` (Optional[str]): 部门描述，可选
- `manager_name` (Optional[str]): 负责人姓名，可选
- `manager_phone` (Optional[str]): 负责人电话，可选

**返回值**: 
- 成功: `{'success': "部门创建成功"}`

**异常**:
- `DepartmentModelException`: 创建失败时抛出，包含错误代码500和相应错误信息

**使用示例**:
```python
try:
    result = Department.create(
        name="技术部",
        level=2,
        parent_id=1,
        description="负责技术开发工作",
        manager_name="张三",
        manager_phone="13800138000"
    )
    print(result)  # {'success': '部门创建成功'}
except DepartmentModelException as e:
    print(f"创建失败: {e.message}")
```

### 2. update() - 更新部门

```python
@classmethod
def update(cls, department_id: int, name: Optional[str] = None,
          level: Optional[int] = None, parent_id: Optional[int] = None,
          description: Optional[str] = None, 
          manager_name: Optional[str] = None,
          manager_phone: Optional[str] = None) -> Dict[str, str]
```

**功能**: 更新指定部门的信息

**参数**:
- `department_id` (int): 要更新的部门ID，必填
- 其他参数均为可选，只更新传入的非空参数

**返回值**: 
- 成功: `{'success': "部门更新成功"}`

**异常**:
- `DepartmentModelException`: 
  - 404: 部门不存在
  - 500: 更新失败

**使用示例**:
```python
try:
    result = Department.update(
        department_id=1,
        name="新技术部",
        manager_name="李四"
    )
    print(result)  # {'success': '部门更新成功'}
except DepartmentModelException as e:
    print(f"更新失败: {e.message}")
```

### 3. delete() - 删除部门

```python
@classmethod
def delete(cls, department_id: int) -> Dict[str, str]
```

**功能**: 删除指定的部门记录

**参数**:
- `department_id` (int): 要删除的部门ID

**返回值**: 
- 成功: `{'success': "部门删除成功"}`

**异常**:
- `DepartmentModelException`: 
  - 404: 部门不存在
  - 500: 删除失败

**注意事项**: 
- 删除部门前应确保没有子部门依赖
- 删除操作不可逆，请谨慎使用

**使用示例**:
```python
try:
    result = Department.delete(department_id=1)
    print(result)  # {'success': '部门删除成功'}
except DepartmentModelException as e:
    print(f"删除失败: {e.message}")
```

### 4. get_department() - 获取单个部门

```python
@classmethod
def get_department(cls, department_id: int) -> Dict[str, str]
```

**功能**: 根据部门ID获取部门详细信息

**参数**:
- `department_id` (int): 部门ID

**返回值**: 包含部门完整信息的字典
```python
{
    "id": int,
    "name": str,
    "level": int,
    "parent_id": int,
    "description": str,
    "manager_name": str,
    "manager_phone": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

**异常**:
- `DepartmentModelException`: 
  - 404: 部门不存在
  - 500: 查询失败

**使用示例**:
```python
try:
    department = Department.get_department(department_id=1)
    print(f"部门名称: {department['name']}")
    print(f"部门级别: {department['level']}")
except DepartmentModelException as e:
    print(f"获取失败: {e.message}")
```

### 5. get_department_by_parent_id() - 获取子部门列表

```python
@classmethod
def get_department_by_parent_id(cls, parent_id: int) -> List[Dict[str, str]]
```

**功能**: 根据父部门ID获取所有直接子部门列表

**参数**:
- `parent_id` (int): 父部门ID

**返回值**: 子部门信息列表，每个元素包含完整的部门信息字典

**异常**:
- `DepartmentModelException`: 查询失败时抛出

**使用示例**:
```python
try:
    children = Department.get_department_by_parent_id(parent_id=1)
    for child in children:
        print(f"子部门: {child['name']}, 级别: {child['level']}")
except DepartmentModelException as e:
    print(f"获取失败: {e.message}")
```

### 6. get_department_tree_by_parent_id() - 构建部门树

```python
@classmethod
def get_department_tree_by_parent_id(cls, parent_id: int) -> List[Dict[str, str]]
```

**功能**: 根据父部门ID构建完整的部门树形结构，包含所有层级的子部门

**参数**:
- `parent_id` (int): 根部门ID

**返回值**: 树形结构的部门列表，每个部门包含 `children` 字段存储子部门

**特点**:
- 递归查询所有子部门
- 返回完整的树形结构
- 每个节点包含 `children` 数组

**数据结构示例**:
```python
[
    {
        "id": 1,
        "name": "总部",
        "level": 0,
        "parent_id": 0,
        "description": "公司总部",
        "manager_name": "总经理",
        "manager_phone": "13800138000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "children": [
            {
                "id": 2,
                "name": "技术部",
                "level": 1,
                "parent_id": 1,
                "children": [
                    {
                        "id": 3,
                        "name": "前端组",
                        "level": 2,
                        "parent_id": 2,
                        "children": []
                    }
                ]
            }
        ]
    }
]
```

**使用示例**:
```python
try:
    tree = Department.get_department_tree_by_parent_id(parent_id=0)
    
    def print_tree(departments, indent=0):
        for dept in departments:
            print("  " * indent + f"- {dept['name']} (级别: {dept['level']})")
            if dept['children']:
                print_tree(dept['children'], indent + 1)
    
    print_tree(tree)
except DepartmentModelException as e:
    print(f"构建树失败: {e.message}")
```

### 7. is_direct_child() - 检查直接下级关系

```python
@classmethod
def is_direct_child(cls, parent_id: int, child_id: int) -> bool
```

**功能**: 检查指定部门是否为另一个部门的直接下级部门

**参数**:
- `parent_id` (int): 父部门ID
- `child_id` (int): 子部门ID

**返回值**: 
- `True`: 是直接下级关系
- `False`: 不是直接下级关系

**异常**:
- `DepartmentModelException`: 
  - 404: 父部门或子部门不存在
  - 500: 查询失败

**使用场景**:
- 权限验证
- 组织架构验证
- 数据访问控制

**使用示例**:
```python
try:
    is_child = Department.is_direct_child(parent_id=1, child_id=2)
    if is_child:
        print("部门2是部门1的直接下级")
    else:
        print("部门2不是部门1的直接下级")
except DepartmentModelException as e:
    print(f"检查失败: {e.message}")
```

## 使用注意事项

### 1. 部门级别设计
- **0级**: 根部门（通常是公司或组织总部）
- **1级**: 县级部门
- **2级**: 镇街级部门  
- **3级**: 村社级部门

### 2. 数据完整性
- 创建部门时必须指定有效的父部门ID
- 删除部门前应检查是否有子部门依赖
- 更新部门层级时需要考虑子部门的影响

### 3. 性能考虑
- `get_department_tree_by_parent_id()` 方法使用递归查询，对于深层次的组织架构可能影响性能
- 建议在大型组织中限制查询深度或使用分页

### 4. 错误处理
- 所有方法都会抛出 `DepartmentModelException` 异常
- 在生产环境中，详细错误信息会被隐藏（根据 `DEBUG_MODE` 配置）
- 建议在调用时使用 try-catch 块进行异常处理

### 5. 事务管理
- 所有数据库操作都在事务中执行
- 发生异常时会自动回滚事务
- 确保数据一致性

## 最佳实践

1. **创建部门时**：先创建上级部门，再创建下级部门
2. **删除部门时**：先删除下级部门，再删除上级部门
3. **查询优化**：根据实际需求选择合适的查询方法
4. **异常处理**：始终使用 try-catch 块处理可能的异常
5. **数据验证**：在调用模型方法前进行必要的参数验证

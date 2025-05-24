"""
自定义SM2密钥生成器
实现标准的SM2椭圆曲线密钥对生成
"""
import os
import secrets
import hashlib
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class SM2Parameters:
    """SM2推荐参数"""
    # 素数p (256位)
    p = int("FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF", 16)
    
    # 椭圆曲线参数a
    a = int("FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC", 16)
    
    # 椭圆曲线参数b  
    b = int("28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93", 16)
    
    # 基点G的x坐标
    gx = int("32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7", 16)
    
    # 基点G的y坐标
    gy = int("BC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0", 16)
    
    # 基点G的阶n
    n = int("FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123", 16)


class SM2Point:
    """椭圆曲线上的点"""
    
    def __init__(self, x: Optional[int] = None, y: Optional[int] = None):
        self.x = x
        self.y = y
        self.is_infinity = (x is None and y is None)
    
    def __eq__(self, other):
        if not isinstance(other, SM2Point):
            return False
        return self.x == other.x and self.y == other.y and self.is_infinity == other.is_infinity
    
    def __str__(self):
        if self.is_infinity:
            return "Point(∞)"
        return f"Point({hex(self.x)}, {hex(self.y)})"


class SM2KeyGenerator:
    """SM2密钥生成器"""
    
    def __init__(self):
        self.params = SM2Parameters()
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """计算模逆"""
        if a < 0:
            a = (a % m + m) % m
        
        # 扩展欧几里得算法
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a, m)
        if gcd != 1:
            raise ValueError("模逆不存在")
        return (x % m + m) % m
    
    def _point_add(self, p1: SM2Point, p2: SM2Point) -> SM2Point:
        """椭圆曲线点加法"""
        if p1.is_infinity:
            return p2
        if p2.is_infinity:
            return p1
        
        if p1.x == p2.x:
            if p1.y == p2.y:
                # 点倍乘
                return self._point_double(p1)
            else:
                # 相反点，结果为无穷远点
                return SM2Point()
        
        # 一般情况的点加法
        lambda_val = ((p2.y - p1.y) * self._mod_inverse(p2.x - p1.x, self.params.p)) % self.params.p
        x3 = (lambda_val * lambda_val - p1.x - p2.x) % self.params.p
        y3 = (lambda_val * (p1.x - x3) - p1.y) % self.params.p
        
        return SM2Point(x3, y3)
    
    def _point_double(self, p: SM2Point) -> SM2Point:
        """椭圆曲线点倍乘"""
        if p.is_infinity:
            return p
        
        lambda_val = ((3 * p.x * p.x + self.params.a) * self._mod_inverse(2 * p.y, self.params.p)) % self.params.p
        x3 = (lambda_val * lambda_val - 2 * p.x) % self.params.p
        y3 = (lambda_val * (p.x - x3) - p.y) % self.params.p
        
        return SM2Point(x3, y3)
    
    def _point_multiply(self, k: int, point: SM2Point) -> SM2Point:
        """椭圆曲线标量乘法 k*P"""
        if k == 0:
            return SM2Point()  # 无穷远点
        if k == 1:
            return point
        
        result = SM2Point()  # 无穷远点
        addend = point
        
        while k:
            if k & 1:
                result = self._point_add(result, addend)
            addend = self._point_double(addend)
            k >>= 1
        
        return result
    
    def _generate_private_key(self) -> int:
        """生成私钥（1到n-1之间的随机数）"""
        while True:
            # 生成256位随机数
            random_bytes = secrets.token_bytes(32)
            private_key = int.from_bytes(random_bytes, 'big')
            
            # 确保私钥在有效范围内
            if 1 <= private_key < self.params.n:
                return private_key
    
    def _compute_public_key(self, private_key: int) -> SM2Point:
        """根据私钥计算公钥"""
        base_point = SM2Point(self.params.gx, self.params.gy)
        return self._point_multiply(private_key, base_point)
    
    def generate_key_pair(self) -> Tuple[int, SM2Point]:
        """
        生成SM2密钥对
        
        Returns:
            Tuple[int, SM2Point]: (私钥, 公钥点)
        """
        private_key = self._generate_private_key()
        public_key = self._compute_public_key(private_key)
        return private_key, public_key
    
    def private_key_to_bytes(self, private_key: int) -> bytes:
        """将私钥转换为32字节"""
        return private_key.to_bytes(32, 'big')
    
    def public_key_to_bytes(self, public_key: SM2Point, compressed: bool = False) -> bytes:
        """
        将公钥转换为字节格式
        
        Args:
            public_key: 公钥点
            compressed: 是否使用压缩格式
            
        Returns:
            bytes: 公钥字节数据
        """
        if public_key.is_infinity:
            raise ValueError("无效的公钥点")
        
        x_bytes = public_key.x.to_bytes(32, 'big')
        y_bytes = public_key.y.to_bytes(32, 'big')
        
        if compressed:
            # 压缩格式：02/03 + x坐标
            prefix = b'\x02' if public_key.y % 2 == 0 else b'\x03'
            return prefix + x_bytes
        else:
            # 非压缩格式：04 + x坐标 + y坐标
            return b'\x04' + x_bytes + y_bytes
    
    def bytes_to_private_key(self, key_bytes: bytes) -> int:
        """将字节转换为私钥"""
        if len(key_bytes) != 32:
            raise ValueError("私钥必须是32字节")
        return int.from_bytes(key_bytes, 'big')
    
    def bytes_to_public_key(self, key_bytes: bytes) -> SM2Point:
        """将字节转换为公钥点"""
        if len(key_bytes) == 33:
            # 压缩格式
            prefix = key_bytes[0]
            x = int.from_bytes(key_bytes[1:], 'big')
            
            # 计算y坐标
            y_squared = (pow(x, 3, self.params.p) + self.params.a * x + self.params.b) % self.params.p
            y = pow(y_squared, (self.params.p + 1) // 4, self.params.p)
            
            # 根据前缀选择正确的y值
            if (y % 2) != (prefix - 2):
                y = self.params.p - y
            
            return SM2Point(x, y)
        
        elif len(key_bytes) == 65:
            # 非压缩格式
            if key_bytes[0] != 0x04:
                raise ValueError("无效的公钥格式")
            
            x = int.from_bytes(key_bytes[1:33], 'big')
            y = int.from_bytes(key_bytes[33:], 'big')
            
            return SM2Point(x, y)
        
        else:
            raise ValueError("无效的公钥长度")
    
    def verify_key_pair(self, private_key: int, public_key: SM2Point) -> bool:
        """验证密钥对是否匹配"""
        computed_public_key = self._compute_public_key(private_key)
        return computed_public_key == public_key
    
    def generate_key_pair_hex(self) -> Tuple[str, str]:
        """
        生成十六进制格式的密钥对
        
        Returns:
            Tuple[str, str]: (私钥十六进制, 公钥十六进制)
        """
        private_key, public_key = self.generate_key_pair()
        
        private_key_hex = format(private_key, '064x')
        public_key_bytes = self.public_key_to_bytes(public_key, compressed=False)
        public_key_hex = public_key_bytes.hex()
        
        return private_key_hex, public_key_hex


def test_sm2_key_generator():
    """测试SM2密钥生成器"""
    try:
        generator = SM2KeyGenerator()
        
        print("=== SM2密钥生成器测试 ===")
        
        # 生成密钥对
        private_key, public_key = generator.generate_key_pair()
        print(f"私钥: {private_key:064x}")
        print(f"公钥x: {public_key.x:064x}")
        print(f"公钥y: {public_key.y:064x}")
        
        # 验证密钥对
        is_valid = generator.verify_key_pair(private_key, public_key)
        print(f"密钥对验证: {'通过' if is_valid else '失败'}")
        
        # 测试字节转换
        private_key_bytes = generator.private_key_to_bytes(private_key)
        public_key_bytes = generator.public_key_to_bytes(public_key)
        
        print(f"私钥字节长度: {len(private_key_bytes)}")
        print(f"公钥字节长度: {len(public_key_bytes)}")
        
        # 测试十六进制格式
        private_hex, public_hex = generator.generate_key_pair_hex()
        print(f"新私钥(hex): {private_hex}")
        print(f"新公钥(hex): {public_hex}")
        
        print("=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_sm2_key_generator() 
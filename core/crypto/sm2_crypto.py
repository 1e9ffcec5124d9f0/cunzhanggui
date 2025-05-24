import os
import base64
import secrets
import hashlib
from typing import Tuple, Dict, Optional

from core.configs import get_redis_client
from .sm2_key_generator import SM2KeyGenerator, SM2Point, SM2Parameters
from .sm3_hash import sm3_hash


class SM2Crypto:
    """
    SM2加密工具类，完全自实现加密解密功能
    不依赖任何第三方SM2库
    """
    # 密钥在Redis中的键名前缀
    KEY_PREFIX = "sm2:keys:"
    # 公钥在Redis中的键名
    PUBLIC_KEY_NAME = f"{KEY_PREFIX}public_key"
    # 私钥在Redis中的键名
    PRIVATE_KEY_NAME = f"{KEY_PREFIX}private_key"
    
    def __init__(self):
        self.key_generator = SM2KeyGenerator()
        self.params = SM2Parameters()
    
    @classmethod
    def _sm3_hash(cls, data: bytes) -> bytes:
        """SM3哈希函数实现 - 使用标准SM3算法"""
        return sm3_hash(data)
    
    @classmethod
    def _kdf(cls, shared_key: bytes, key_len: int) -> bytes:
        """密钥派生函数KDF"""
        if key_len == 0:
            return b''
        
        # 计算需要的哈希轮数
        hash_rounds = (key_len + 31) // 32  # 每轮产生32字节
        result = b''
        
        for i in range(1, hash_rounds + 1):
            # 将计数器转换为4字节大端序
            counter = i.to_bytes(4, 'big')
            # 哈希 shared_key || counter
            hash_input = shared_key + counter
            hash_output = cls._sm3_hash(hash_input)
            result += hash_output
        
        # 截取所需长度
        return result[:key_len]
    
    def _encrypt_c1c3c2(self, public_key_hex: str, plain_text: bytes) -> bytes:
        """
        SM2加密算法实现 (C1C3C2格式)
        
        Args:
            public_key_hex: 公钥十六进制字符串
            plain_text: 明文字节
            
        Returns:
            bytes: 密文字节 (C1||C3||C2格式)
        """
        # 特殊处理空消息
        if len(plain_text) == 0:
            # 对于空消息，我们仍然需要生成C1和C3，但C2为空
            # 解析公钥
            public_key_bytes = bytes.fromhex(public_key_hex)
            if len(public_key_bytes) != 65 or public_key_bytes[0] != 0x04:
                raise ValueError("无效的公钥格式")
            
            x = int.from_bytes(public_key_bytes[1:33], 'big')
            y = int.from_bytes(public_key_bytes[33:65], 'big')
            public_key_point = SM2Point(x, y)
            
            # 基点G
            base_point = SM2Point(self.params.gx, self.params.gy)
            
            # 生成随机数k
            k = self.key_generator._generate_private_key()
            
            # 计算C1 = k*G
            c1_point = self.key_generator._point_multiply(k, base_point)
            
            # 计算kP = k*公钥点
            kp_point = self.key_generator._point_multiply(k, public_key_point)
            
            # 计算C3 = Hash(x2 || M || y2)，其中M为空
            hash_input = (kp_point.x.to_bytes(32, 'big') + 
                         plain_text +  # 空字节串
                         kp_point.y.to_bytes(32, 'big'))
            c3 = self._sm3_hash(hash_input)
            
            # 组装密文 C1||C3||C2，其中C2为空
            c1_bytes = (b'\x04' + 
                       c1_point.x.to_bytes(32, 'big') + 
                       c1_point.y.to_bytes(32, 'big'))
            
            return c1_bytes + c3  # C2为空，所以不添加
        
        # 解析公钥
        public_key_bytes = bytes.fromhex(public_key_hex)
        if len(public_key_bytes) != 65 or public_key_bytes[0] != 0x04:
            raise ValueError("无效的公钥格式")
        
        x = int.from_bytes(public_key_bytes[1:33], 'big')
        y = int.from_bytes(public_key_bytes[33:65], 'big')
        public_key_point = SM2Point(x, y)
        
        # 基点G
        base_point = SM2Point(self.params.gx, self.params.gy)
        
        while True:
            # 1. 生成随机数k
            k = self.key_generator._generate_private_key()
            
            # 2. 计算C1 = k*G
            c1_point = self.key_generator._point_multiply(k, base_point)
            
            # 3. 计算kP = k*公钥点
            kp_point = self.key_generator._point_multiply(k, public_key_point)
            
            # 4. 计算共享密钥
            shared_key = (kp_point.x.to_bytes(32, 'big') + 
                         kp_point.y.to_bytes(32, 'big'))
            
            # 5. 使用KDF派生加密密钥
            encryption_key = self._kdf(shared_key, len(plain_text))
            
            # 检查派生密钥是否全零
            if encryption_key == b'\x00' * len(plain_text):
                continue  # 重新生成k
            
            # 6. 计算C2 = M ⊕ t
            c2 = bytes(a ^ b for a, b in zip(plain_text, encryption_key))
            
            # 7. 计算C3 = Hash(x2 || M || y2)
            hash_input = (kp_point.x.to_bytes(32, 'big') + 
                         plain_text + 
                         kp_point.y.to_bytes(32, 'big'))
            c3 = self._sm3_hash(hash_input)
            
            # 8. 组装密文 C1||C3||C2
            c1_bytes = (b'\x04' + 
                       c1_point.x.to_bytes(32, 'big') + 
                       c1_point.y.to_bytes(32, 'big'))
            
            return c1_bytes + c3 + c2
    
    def _decrypt_c1c3c2(self, private_key_hex: str, cipher_text: bytes) -> bytes:
        """
        SM2解密算法实现 (C1C3C2格式)
        
        Args:
            private_key_hex: 私钥十六进制字符串
            cipher_text: 密文字节
            
        Returns:
            bytes: 明文字节
        """
        if len(cipher_text) < 97:  # 65(C1) + 32(C3) = 97最小长度
            raise ValueError("密文长度不足")
        
        # 解析私钥
        private_key = int(private_key_hex, 16)
        
        # 解析密文
        c1_bytes = cipher_text[:65]
        c3 = cipher_text[65:97]
        c2 = cipher_text[97:]  # 可能为空（空消息情况）
        
        # 解析C1点
        if c1_bytes[0] != 0x04:
            raise ValueError("无效的C1格式")
        
        c1_x = int.from_bytes(c1_bytes[1:33], 'big')
        c1_y = int.from_bytes(c1_bytes[33:65], 'big')
        c1_point = SM2Point(c1_x, c1_y)
        
        # 计算 d*C1
        dc1_point = self.key_generator._point_multiply(private_key, c1_point)
        
        # 特殊处理空消息（C2为空）
        if len(c2) == 0:
            # 对于空消息，直接验证C3
            plain_text = b''  # 空明文
            
            # 验证C3
            hash_input = (dc1_point.x.to_bytes(32, 'big') + 
                         plain_text + 
                         dc1_point.y.to_bytes(32, 'big'))
            computed_c3 = self._sm3_hash(hash_input)
            
            if computed_c3 != c3:
                raise ValueError("密文验证失败，可能已被篡改")
            
            return plain_text
        
        # 处理非空消息
        # 计算共享密钥
        shared_key = (dc1_point.x.to_bytes(32, 'big') + 
                     dc1_point.y.to_bytes(32, 'big'))
        
        # 使用KDF派生解密密钥
        decryption_key = self._kdf(shared_key, len(c2))
        
        # 解密得到明文
        plain_text = bytes(a ^ b for a, b in zip(c2, decryption_key))
        
        # 验证C3
        hash_input = (dc1_point.x.to_bytes(32, 'big') + 
                     plain_text + 
                     dc1_point.y.to_bytes(32, 'big'))
        computed_c3 = self._sm3_hash(hash_input)
        
        if computed_c3 != c3:
            raise ValueError("密文验证失败，可能已被篡改")
        
        return plain_text
    
    @classmethod
    def generate_key_pair(cls) -> Tuple[str, str]:
        """
        生成SM2密钥对
        
        Returns:
            Tuple[str, str]: (私钥十六进制, 公钥十六进制)
        """
        generator = SM2KeyGenerator()
        private_hex, public_hex = generator.generate_key_pair_hex()

        # 存储到Redis
        redis_client = get_redis_client()
        redis_client.set(cls.PRIVATE_KEY_NAME, private_hex)
        redis_client.set(cls.PUBLIC_KEY_NAME, public_hex)
        
        return private_hex, public_hex
    
    @classmethod
    def get_keys(cls) -> Dict[str, str]:
        """
        从Redis获取密钥对
        
        Returns:
            Dict[str, str]: 包含公钥和私钥的字典
        """
        redis_client = get_redis_client()
        private_key_bytes = redis_client.get(cls.PRIVATE_KEY_NAME)
        public_key_bytes = redis_client.get(cls.PUBLIC_KEY_NAME)
        
        if not private_key_bytes or not public_key_bytes:
            # 如果密钥不存在，生成新的密钥对
            private_key, public_key = cls.generate_key_pair()
        else:
            private_key = private_key_bytes.decode('utf-8')
            public_key = public_key_bytes.decode('utf-8')
        
        return {
            "private_key": private_key,
            "public_key": public_key
        }
    
    @classmethod
    def encrypt(cls, plain_text: str) -> str:
        """
        使用公钥加密数据
        
        Args:
            plain_text: 明文字符串
            
        Returns:
            str: Base64编码的密文
        """
        keys = cls.get_keys()
        public_key_hex = keys["public_key"]
        
        # 创建加密实例
        crypto = cls()
        
        # 加密
        plain_bytes = plain_text.encode('utf-8')
        cipher_bytes = crypto._encrypt_c1c3c2(public_key_hex, plain_bytes)
        
        # 返回Base64编码的密文
        return base64.b64encode(cipher_bytes).decode('utf-8')
    
    @classmethod
    def decrypt(cls, cipher_text: str) -> str:
        """
        使用私钥解密数据（自动检测格式）
        
        Args:
            cipher_text: Base64编码的密文或十六进制密文
            
        Returns:
            str: 解密后的明文
        """
        keys = cls.get_keys()
        private_key_hex = keys["private_key"]
        
        # 创建解密实例
        crypto = cls()
        
        # 首先尝试Base64解码
        cipher_bytes = None
        try:
            cipher_bytes = base64.b64decode(cipher_text)
        except Exception:
            # Base64解码失败，尝试十六进制解码
            try:
                # 移除可能的空格和换行符
                hex_text = cipher_text.replace(" ", "").replace("\n", "").replace("\r", "")
                cipher_bytes = bytes.fromhex(hex_text)
                
                # 检查是否缺少0x04前缀（前端常见问题）
                if len(cipher_bytes) >= 64 and cipher_bytes[0] != 0x04:
                    # 如果长度合适且第一个字节不是0x04，尝试添加前缀
                    if len(cipher_bytes) == 99:  # 64字节坐标 + 32字节哈希 + 其他数据
                        cipher_bytes = b'\x04' + cipher_bytes
                    elif len(cipher_bytes) == 96:  # 64字节坐标 + 32字节哈希
                        cipher_bytes = b'\x04' + cipher_bytes
                    elif len(cipher_bytes) >= 96:  # 其他可能的长度
                        cipher_bytes = b'\x04' + cipher_bytes
                
            except Exception:
                raise ValueError("无法解码密文，既不是有效的Base64也不是有效的十六进制")
        
        if cipher_bytes is None:
            raise ValueError("密文解码失败")
        
        # 首先尝试C1C2C3格式（前端常用格式）
        try:
            if len(cipher_bytes) >= 97:
                c1_bytes = cipher_bytes[:65]
                # 检查C1格式
                if c1_bytes[0] == 0x04:
                    # 尝试C1C2C3格式
                    c3 = cipher_bytes[-32:]  # 最后32字节是C3
                    c2 = cipher_bytes[65:-32]  # 中间部分是C2
                    
                    # 重新组装为C1C3C2格式
                    c1c3c2_bytes = c1_bytes + c3 + c2
                    
                    # 尝试解密
                    plain_bytes = crypto._decrypt_c1c3c2(private_key_hex, c1c3c2_bytes)
                    return plain_bytes.decode('utf-8')
        except Exception:
            # C1C2C3格式失败，继续尝试C1C3C2格式
            pass
        
        # 如果C1C2C3格式失败，尝试原始的C1C3C2格式
        plain_bytes = crypto._decrypt_c1c3c2(private_key_hex, cipher_bytes)
        return plain_bytes.decode('utf-8')
    
    @classmethod
    def get_public_key(cls) -> str:
        """
        获取公钥，用于客户端加密
        
        Returns:
            str: 公钥十六进制字符串
        """
        keys = cls.get_keys()
        return keys["public_key"] 

    @classmethod
    def get_key_info(cls) -> Dict[str, str]:
        """
        获取密钥信息
        
        Returns:
            Dict[str, str]: 密钥信息
        """
        keys = cls.get_keys()
        private_key = keys["private_key"]
        public_key = keys["public_key"]
        
        return {
            "private_key": private_key,
            "public_key": public_key,
            "format": "HEX",
            "private_key_length": len(private_key),
            "public_key_length": len(public_key),
            "algorithm": "SM2",
            "curve": "sm2p256v1"
        }
    
    @classmethod
    def clear_keys(cls) -> None:
        """
        清除Redis中存储的密钥
        """
        redis_client = get_redis_client()
        redis_client.delete(cls.PRIVATE_KEY_NAME)
        redis_client.delete(cls.PUBLIC_KEY_NAME)
    
    @classmethod
    def verify_key_pair(cls) -> bool:
        """
        验证当前存储的密钥对是否有效
        
        Returns:
            bool: 密钥对是否有效
        """
        try:
            keys = cls.get_keys()
            private_key_hex = keys["private_key"]
            public_key_hex = keys["public_key"]
            
            # 使用密钥生成器验证
            generator = SM2KeyGenerator()
            
            # 解析私钥
            private_key = int(private_key_hex, 16)
            
            # 解析公钥
            public_key_bytes = bytes.fromhex(public_key_hex)
            public_key_point = generator.bytes_to_public_key(public_key_bytes)
            
            # 验证密钥对
            return generator.verify_key_pair(private_key, public_key_point)
            
        except Exception:
            return False
    
    @classmethod
    def test_encryption(cls, test_message: str = "Hello, SM2!") -> Dict[str, any]:
        """
        测试加解密功能
        
        Args:
            test_message: 测试消息
            
        Returns:
            Dict: 测试结果
        """
        try:
            # 加密
            encrypted = cls.encrypt(test_message)
            
            # 解密
            decrypted = cls.decrypt(encrypted)
            
            # 验证
            success = (decrypted == test_message)
            
            return {
                "success": success,
                "original": test_message,
                "encrypted": encrypted,
                "decrypted": decrypted,
                "encrypted_length": len(encrypted),
                "key_info": cls.get_key_info()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original": test_message
            }
    
    @classmethod
    def decrypt_with_debug(cls, cipher_text: str) -> Dict[str, any]:
        """
        使用私钥解密数据（带调试信息）
        
        Args:
            cipher_text: Base64编码的密文或十六进制密文
            
        Returns:
            Dict: 包含解密结果和调试信息的字典
        """
        debug_info = {
            "input_cipher": cipher_text[:100] + "..." if len(cipher_text) > 100 else cipher_text,
            "input_length": len(cipher_text),
            "steps": []
        }
        
        try:
            keys = cls.get_keys()
            private_key_hex = keys["private_key"]
            crypto = cls()
            
            debug_info["steps"].append("获取私钥成功")
            
            # 尝试不同的解码方式
            cipher_bytes = None
            
            # 1. 尝试Base64解码
            try:
                cipher_bytes = base64.b64decode(cipher_text)
                debug_info["steps"].append(f"Base64解码成功，长度: {len(cipher_bytes)}")
                debug_info["decode_method"] = "base64"
            except Exception as e:
                debug_info["steps"].append(f"Base64解码失败: {str(e)}")
            
            # 2. 如果Base64失败，尝试十六进制解码
            if cipher_bytes is None:
                try:
                    # 移除可能的空格和换行符
                    hex_text = cipher_text.replace(" ", "").replace("\n", "").replace("\r", "")
                    cipher_bytes = bytes.fromhex(hex_text)
                    debug_info["steps"].append(f"十六进制解码成功，长度: {len(cipher_bytes)}")
                    debug_info["decode_method"] = "hex"
                except Exception as e:
                    debug_info["steps"].append(f"十六进制解码失败: {str(e)}")
                    return {
                        "success": False,
                        "error": "无法解码密文，既不是有效的Base64也不是有效的十六进制",
                        "debug": debug_info
                    }
            
            # 检查密文长度
            if len(cipher_bytes) < 97:
                return {
                    "success": False,
                    "error": f"密文长度不足，需要至少97字节，实际{len(cipher_bytes)}字节",
                    "debug": debug_info
                }
            
            debug_info["cipher_bytes_length"] = len(cipher_bytes)
            debug_info["cipher_hex"] = cipher_bytes[:100].hex() + "..." if len(cipher_bytes) > 100 else cipher_bytes.hex()
            
            # 分析密文结构 - 先按C1C3C2格式分析
            c1_bytes = cipher_bytes[:65]
            c3_c1c3c2 = cipher_bytes[65:97]
            c2_c1c3c2 = cipher_bytes[97:]
            
            debug_info["c1_length"] = len(c1_bytes)
            debug_info["c1_first_byte"] = f"0x{c1_bytes[0]:02x}" if len(c1_bytes) > 0 else "无"
            
            # 首先尝试C1C2C3格式（前端常用格式）
            debug_info["steps"].append("优先尝试C1C2C3格式（前端常用）")
            c1c2c3_result = cls._try_decrypt_c1c2c3_format(cipher_bytes, private_key_hex, debug_info.copy())
            if c1c2c3_result["success"]:
                debug_info["steps"].extend(c1c2c3_result["debug"]["steps"])
                return {
                    "success": True,
                    "plain_text": c1c2c3_result["plain_text"],
                    "format": "C1C2C3",
                    "debug": debug_info
                }
            
            # 如果C1C2C3格式失败，再尝试C1C3C2格式
            debug_info["steps"].append("C1C2C3格式失败，尝试C1C3C2格式")
            
            # 检查C1格式
            if c1_bytes[0] != 0x04:
                debug_info["steps"].append(f"C1第一个字节不是0x04，而是0x{c1_bytes[0]:02x}")
                return {
                    "success": False,
                    "error": f"无效的C1格式，第一个字节应该是0x04，实际是0x{c1_bytes[0]:02x}",
                    "debug": debug_info
                }
            
            debug_info["c3_length"] = len(c3_c1c3c2)
            debug_info["c2_length"] = len(c2_c1c3c2)
            debug_info["steps"].append("C1格式验证通过，尝试C1C3C2格式解密")
            
            # 执行C1C3C2格式解密
            plain_bytes = crypto._decrypt_c1c3c2(private_key_hex, cipher_bytes)
            plain_text = plain_bytes.decode('utf-8')
            
            debug_info["steps"].append("C1C3C2格式解密成功")
            
            return {
                "success": True,
                "plain_text": plain_text,
                "format": "C1C3C2",
                "debug": debug_info
            }
            
        except Exception as e:
            debug_info["steps"].append(f"解密过程出错: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "debug": debug_info
            }
    
    @classmethod
    def _try_decrypt_c1c2c3_format(cls, cipher_bytes: bytes, private_key_hex: str, debug_info: Dict) -> Dict[str, any]:
        """
        尝试C1C2C3格式解密
        """
        local_debug = debug_info.copy()
        local_debug["steps"] = []
        local_debug["steps"].append("开始C1C2C3格式解密")
        
        try:
            # C1C2C3格式：C1(65字节) + C2(变长) + C3(32字节)
            if len(cipher_bytes) < 97:
                raise ValueError("密文长度不足以支持C1C2C3格式")
            
            c1_bytes = cipher_bytes[:65]
            c3 = cipher_bytes[-32:]  # 最后32字节是C3
            c2 = cipher_bytes[65:-32]  # 中间部分是C2
            
            # 检查C1格式
            if c1_bytes[0] != 0x04:
                raise ValueError(f"C1格式无效，第一个字节应该是0x04，实际是0x{c1_bytes[0]:02x}")
            
            local_debug["steps"].append(f"C1C2C3格式分析: C1={len(c1_bytes)}字节, C2={len(c2)}字节, C3={len(c3)}字节")
            
            # 重新组装为C1C3C2格式
            c1c3c2_bytes = c1_bytes + c3 + c2
            
            local_debug["steps"].append(f"重新组装为C1C3C2格式，总长度: {len(c1c3c2_bytes)}")
            
            crypto = cls()
            plain_bytes = crypto._decrypt_c1c3c2(private_key_hex, c1c3c2_bytes)
            plain_text = plain_bytes.decode('utf-8')
            
            local_debug["steps"].append("C1C2C3格式解密成功")
            
            return {
                "success": True,
                "plain_text": plain_text,
                "format": "C1C2C3",
                "debug": local_debug
            }
            
        except Exception as e:
            local_debug["steps"].append(f"C1C2C3格式解密失败: {str(e)}")
            return {
                "success": False,
                "error": f"C1C2C3格式解密失败: {str(e)}",
                "debug": local_debug
            }
"""
SM3密码杂凑算法实现
符合GB/T 32905-2016标准
"""

import struct
from typing import List


class SM3Hash:
    """
    SM3密码杂凑算法实现类
    完全按照国家标准GB/T 32905-2016实现
    """
    
    # SM3算法常量
    IV = [
        0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
        0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
    ]
    
    def __init__(self):
        """初始化SM3哈希对象"""
        self.reset()
    
    def reset(self):
        """重置哈希状态"""
        self.state = self.IV.copy()
        self.buffer = b''
        self.counter = 0
    
    @staticmethod
    def _rotl(value: int, amount: int) -> int:
        """循环左移"""
        return ((value << amount) | (value >> (32 - amount))) & 0xFFFFFFFF
    
    @staticmethod
    def _ff(x: int, y: int, z: int, j: int) -> int:
        """布尔函数FF"""
        if j < 16:
            return x ^ y ^ z
        else:
            return (x & y) | (x & z) | (y & z)
    
    @staticmethod
    def _gg(x: int, y: int, z: int, j: int) -> int:
        """布尔函数GG"""
        if j < 16:
            return x ^ y ^ z
        else:
            return (x & y) | (~x & z)
    
    @staticmethod
    def _p0(x: int) -> int:
        """置换函数P0"""
        return x ^ SM3Hash._rotl(x, 9) ^ SM3Hash._rotl(x, 17)
    
    @staticmethod
    def _p1(x: int) -> int:
        """置换函数P1"""
        return x ^ SM3Hash._rotl(x, 15) ^ SM3Hash._rotl(x, 23)
    
    @staticmethod
    def _t(j: int) -> int:
        """常量T"""
        if j < 16:
            return 0x79CC4519
        else:
            return 0x7A879D8A
    
    def _message_extension(self, block: bytes) -> List[int]:
        """消息扩展"""
        # 将512位消息分组划分为16个32位字
        w = list(struct.unpack('>16I', block))
        
        # 扩展为132个字
        for j in range(16, 68):
            w_j_16 = w[j-16]
            w_j_9 = w[j-9]
            w_j_3 = w[j-3]
            w_j_13 = w[j-13]
            w_j_6 = w[j-6]
            
            temp = w_j_16 ^ w_j_9 ^ SM3Hash._rotl(w_j_3, 15)
            temp = SM3Hash._p1(temp)
            w_j = temp ^ SM3Hash._rotl(w_j_13, 7) ^ w_j_6
            w.append(w_j & 0xFFFFFFFF)
        
        # 生成W'
        w_prime = []
        for j in range(64):
            w_prime.append(w[j] ^ w[j+4])
        
        return w, w_prime
    
    def _compress(self, block: bytes):
        """压缩函数"""
        w, w_prime = self._message_extension(block)
        
        # 初始化工作变量
        A, B, C, D, E, F, G, H = self.state
        
        # 64轮迭代
        for j in range(64):
            # 计算SS1
            temp = SM3Hash._rotl((SM3Hash._rotl(A, 12) + E + SM3Hash._rotl(SM3Hash._t(j), j % 32)) & 0xFFFFFFFF, 7)
            SS1 = temp & 0xFFFFFFFF
            
            # 计算SS2
            SS2 = SS1 ^ SM3Hash._rotl(A, 12)
            
            # 计算TT1
            TT1 = (SM3Hash._ff(A, B, C, j) + D + SS2 + w_prime[j]) & 0xFFFFFFFF
            
            # 计算TT2
            TT2 = (SM3Hash._gg(E, F, G, j) + H + SS1 + w[j]) & 0xFFFFFFFF
            
            # 更新工作变量
            D = C
            C = SM3Hash._rotl(B, 9)
            B = A
            A = TT1
            H = G
            G = SM3Hash._rotl(F, 19)
            F = E
            E = SM3Hash._p0(TT2)
            
            # 确保所有值都在32位范围内
            A, B, C, D, E, F, G, H = [x & 0xFFFFFFFF for x in [A, B, C, D, E, F, G, H]]
        
        # 更新状态
        self.state[0] = (self.state[0] ^ A) & 0xFFFFFFFF
        self.state[1] = (self.state[1] ^ B) & 0xFFFFFFFF
        self.state[2] = (self.state[2] ^ C) & 0xFFFFFFFF
        self.state[3] = (self.state[3] ^ D) & 0xFFFFFFFF
        self.state[4] = (self.state[4] ^ E) & 0xFFFFFFFF
        self.state[5] = (self.state[5] ^ F) & 0xFFFFFFFF
        self.state[6] = (self.state[6] ^ G) & 0xFFFFFFFF
        self.state[7] = (self.state[7] ^ H) & 0xFFFFFFFF
    
    def update(self, data: bytes):
        """更新哈希状态"""
        if not isinstance(data, bytes):
            raise TypeError("输入数据必须是bytes类型")
        
        self.buffer += data
        self.counter += len(data)
        
        # 处理完整的512位块
        while len(self.buffer) >= 64:
            self._compress(self.buffer[:64])
            self.buffer = self.buffer[64:]
    
    def digest(self) -> bytes:
        """计算最终哈希值"""
        # 创建副本以避免修改原始状态
        temp_buffer = self.buffer
        temp_counter = self.counter
        temp_state = self.state.copy()
        
        # 填充消息
        msg_bit_length = temp_counter * 8
        temp_buffer += b'\x80'  # 添加1位的1和7位的0
        
        # 填充0直到长度≡448 (mod 512)
        while len(temp_buffer) % 64 != 56:
            temp_buffer += b'\x00'
        
        # 添加64位消息长度
        temp_buffer += struct.pack('>Q', msg_bit_length)
        
        # 处理最后的块
        while len(temp_buffer) >= 64:
            self._compress(temp_buffer[:64])
            temp_buffer = temp_buffer[64:]
        
        # 生成最终哈希值
        result = struct.pack('>8I', *self.state)
        
        # 恢复原始状态
        self.buffer = temp_buffer[:temp_counter % 64] if temp_counter % 64 else b''
        self.counter = temp_counter
        self.state = temp_state
        
        return result
    
    def hexdigest(self) -> str:
        """返回十六进制格式的哈希值"""
        return self.digest().hex()
    
    @classmethod
    def hash(cls, data: bytes) -> bytes:
        """一次性计算SM3哈希值"""
        hasher = cls()
        hasher.update(data)
        return hasher.digest()
    
    @classmethod
    def hexhash(cls, data: bytes) -> str:
        """一次性计算SM3哈希值并返回十六进制字符串"""
        return cls.hash(data).hex()


def sm3_hash(data: bytes) -> bytes:
    """
    便捷函数：计算数据的SM3哈希值
    
    Args:
        data: 要哈希的数据
        
    Returns:
        bytes: 32字节的哈希值
    """
    return SM3Hash.hash(data)


def sm3_hexhash(data: bytes) -> str:
    """
    便捷函数：计算数据的SM3哈希值并返回十六进制字符串
    
    Args:
        data: 要哈希的数据
        
    Returns:
        str: 64字符的十六进制哈希值
    """
    return SM3Hash.hexhash(data)


# 测试函数
def test_sm3():
    """测试SM3算法实现"""
    # 测试用例1：空消息
    test1 = b""
    expected1 = "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b"
    result1 = sm3_hexhash(test1)
    print(f"测试1 - 空消息:")
    print(f"期望: {expected1}")
    print(f"结果: {result1}")
    print(f"通过: {result1 == expected1}\n")
    
    # 测试用例2：单字符消息
    test2 = b"a"
    expected2 = "623476ac18f65a2909e43c7fec61b49c7e764a91a18ccb82f1917a29c86c5e88"
    result2 = sm3_hexhash(test2)
    print(f"测试2 - 单字符'a':")
    print(f"期望: {expected2}")
    print(f"结果: {result2}")
    print(f"通过: {result2 == expected2}\n")
    
    # 测试用例3：标准测试向量
    test3 = b"abc"
    expected3 = "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"
    result3 = sm3_hexhash(test3)
    print(f"测试3 - 'abc':")
    print(f"期望: {expected3}")
    print(f"结果: {result3}")
    print(f"通过: {result3 == expected3}\n")
    
    # 测试用例4：较长消息
    test4 = b"abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
    result4 = sm3_hexhash(test4)
    print(f"测试4 - 64字节消息:")
    print(f"结果: {result4}\n")
    
    return all([
        result1 == expected1,
        result2 == expected2,
        result3 == expected3
    ])


if __name__ == "__main__":
    print("SM3哈希算法测试")
    print("=" * 50)
    success = test_sm3()
    print(f"所有测试通过: {success}") 
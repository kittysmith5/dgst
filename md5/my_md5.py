#!/usr/bin/python3
# _*_ encoding: utf-8 _*_
"""
@File   :   my_md5.py
@Time   :   5/4/2022 9:07 PM
@Author :   Barry Johnson
@Version:   1.0
@Contact:   *******@***.com
@License:   None
@Desc   :   None
"""
T = (0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
     0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
     0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
     0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
     0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
     0xd62f105d, 0x2441453, 0xd8a1e681, 0xe7d3fbc8,
     0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
     0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
     0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
     0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
     0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x4881d05,
     0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
     0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
     0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
     0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
     0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391)

SFF = (7, 12, 17, 22)
SGG = (5, 9, 14, 20)
SHH = (4, 11, 16, 23)
SII = (6, 10, 15, 21)


def f(x, y, z):
    return x & y | ~x & z


def g(x, y, z):
    return x & z | y & ~z


def h(x, y, z):
    return x ^ y ^ z


def i(x, y, z):
    return y ^ (x | ~z)


def rol(num, count):
    #
    # num需要是32位的
    """
    坑！！！
    :param num:
    :param count:
    :return:
    """
    b = (num & 0xffffffff) << count
    return (b & 0xffffffff) + (b >> 32)
    # return (num << count) | (num >> 32 - count)


def ff(a, b, c, d, mj, s, ti):
    """
    返回值不需要控制长度 超过32位也可以
    :param a:
    :param b:
    :param c:
    :param d:
    :param mj:
    :param s:
    :param ti:
    :return:
    """
    return b + rol((a + f(b, c, d) + mj + ti), s)


def gg(a, b, c, d, mj, s, ti):
    return b + rol((a + g(b, c, d) + mj + ti), s)


def hh(a, b, c, d, mj, s, ti):
    return b + rol((a + h(b, c, d) + mj + ti), s)


def ii(a, b, c, d, mj, s, ti):
    return b + rol((a + i(b, c, d) + mj + ti), s)


def plain2bit(plain: str):
    """
    三个部分，原文需要小端序就是 0xabce f012   ---> 0x12f0 cdab
            中间的补充码和前面原文一起小端序  8bit小端序
            最后的长度需要单独处理，前后32位进行交换即可
    :param plain:
    :return:
    """
    bit_lis = []
    bit_str = ""
    bit_lis_32 = []

    for char in plain:
        bit_str += f"{int(str(bin(ord(char))).replace('0b', '')):08}"

    # 补位 使总长度除以512的余数为448 512->64B  一个ascii码 8位->1个B
    rmd = len(bit_str) % 512
    if rmd == 448:
        bit_str += '1' + '0' * 511
    else:
        bit_str += '1' + '0' * (448 - rmd - 1)

    # 后64位补充长度信息 采用小端序
    # len 是比特的数量，不是字符串的数量
    len2_str = f"{int(str(bin(len(plain) * 8)).replace('0b', '')):064}"
    bit_str += len2_str
    for j in range(int(len(bit_str) / 512)):
        bit_lis.append(bit_str[j * 512:(j + 1) * 512])

    for block in bit_lis:
        bit_lis_32_item = []
        for j in range(int(512 / 32)):
            hex_str = hex(int(block[j * 32:(j + 1) * 32], 2))
            bit_lis_32_item.append(int(reverse_hex(hex_str.replace("0x", '')), 16))

        bit_lis_32.append(bit_lis_32_item)
    # 最后64位是32位小端序
    bit_lis_32[-1][-1] = int(len2_str[0:32], 2)
    bit_lis_32[-1][-2] = int(len2_str[32:64], 2)

    print(bit_lis_32)
    return bit_lis_32


def reverse_hex(hex_str: str):
    hex_str = hex_str.replace('0x', '')
    hex_str_list = []
    for j in range(len(hex_str)):
        hex_str = "0" * (8 - len(hex_str)) + hex_str

    for j in range(0, 8, 2):
        hex_str_list.append(hex_str[j: j + 2])
    hex_str_list.reverse()
    hex_str = "".join(hex_str_list)
    return hex_str


def main_loop(plain):
    lis = plain2bit(plain)

    A = 0x67452301
    B = 0xefcdab89
    C = 0x98badcfe
    D = 0x10325476

    for item in lis:
        a = A
        b = B
        c = C
        d = D
        # Round 1   --->  1
        a = ff(a, b, c, d, mj=item[0], s=SFF[0], ti=T[0])
        d = ff(d, a, b, c, mj=item[1], s=SFF[1], ti=T[1])
        c = ff(c, d, a, b, mj=item[2], s=SFF[2], ti=T[2])
        b = ff(b, c, d, a, mj=item[3], s=SFF[3], ti=T[3])

        a = ff(a, b, c, d, mj=item[4], s=SFF[0], ti=T[4])
        d = ff(d, a, b, c, mj=item[5], s=SFF[1], ti=T[5])
        c = ff(c, d, a, b, mj=item[6], s=SFF[2], ti=T[6])
        b = ff(b, c, d, a, mj=item[7], s=SFF[3], ti=T[7])

        a = ff(a, b, c, d, mj=item[8], s=SFF[0], ti=T[8])
        d = ff(d, a, b, c, mj=item[9], s=SFF[1], ti=T[9])
        c = ff(c, d, a, b, mj=item[10], s=SFF[2], ti=T[10])
        b = ff(b, c, d, a, mj=item[11], s=SFF[3], ti=T[11])

        a = ff(a, b, c, d, mj=item[12], s=SFF[0], ti=T[12])
        d = ff(d, a, b, c, mj=item[13], s=SFF[1], ti=T[13])
        c = ff(c, d, a, b, mj=item[14], s=SFF[2], ti=T[14])
        b = ff(b, c, d, a, mj=item[15], s=SFF[3], ti=T[15])

        # Round 2   ---> 5
        a = gg(a, b, c, d, mj=item[1], s=SGG[0], ti=T[0 + 16])
        d = gg(d, a, b, c, mj=item[6], s=SGG[1], ti=T[1 + 16])
        c = gg(c, d, a, b, mj=item[11], s=SGG[2], ti=T[2 + 16])
        b = gg(b, c, d, a, mj=item[0], s=SGG[3], ti=T[3 + 16])

        a = gg(a, b, c, d, mj=item[5], s=SGG[0], ti=T[4 + 16])
        d = gg(d, a, b, c, mj=item[10], s=SGG[1], ti=T[5 + 16])
        c = gg(c, d, a, b, mj=item[15], s=SGG[2], ti=T[6 + 16])
        b = gg(b, c, d, a, mj=item[4], s=SGG[3], ti=T[7 + 16])

        a = gg(a, b, c, d, mj=item[9], s=SGG[0], ti=T[8 + 16])
        d = gg(d, a, b, c, mj=item[14], s=SGG[1], ti=T[9 + 16])
        c = gg(c, d, a, b, mj=item[3], s=SGG[2], ti=T[10 + 16])
        b = gg(b, c, d, a, mj=item[8], s=SGG[3], ti=T[11 + 16])

        a = gg(a, b, c, d, mj=item[13], s=SGG[0], ti=T[12 + 16])
        d = gg(d, a, b, c, mj=item[2], s=SGG[1], ti=T[13 + 16])
        c = gg(c, d, a, b, mj=item[7], s=SGG[2], ti=T[14 + 16])
        b = gg(b, c, d, a, mj=item[12], s=SGG[3], ti=T[15 + 16])

        # Round 3 --->3
        a = hh(a, b, c, d, mj=item[5], s=SHH[0], ti=T[0 + 16 * 2])
        d = hh(d, a, b, c, mj=item[8], s=SHH[1], ti=T[1 + 16 * 2])
        c = hh(c, d, a, b, mj=item[11], s=SHH[2], ti=T[2 + 16 * 2])
        b = hh(b, c, d, a, mj=item[14], s=SHH[3], ti=T[3 + 16 * 2])

        a = hh(a, b, c, d, mj=item[1], s=SHH[0], ti=T[4 + 16 * 2])
        d = hh(d, a, b, c, mj=item[4], s=SHH[1], ti=T[5 + 16 * 2])
        c = hh(c, d, a, b, mj=item[7], s=SHH[2], ti=T[6 + 16 * 2])
        b = hh(b, c, d, a, mj=item[10], s=SHH[3], ti=T[7 + 16 * 2])

        a = hh(a, b, c, d, mj=item[13], s=SHH[0], ti=T[8 + 16 * 2])
        d = hh(d, a, b, c, mj=item[0], s=SHH[1], ti=T[9 + 16 * 2])
        c = hh(c, d, a, b, mj=item[3], s=SHH[2], ti=T[10 + 16 * 2])
        b = hh(b, c, d, a, mj=item[6], s=SHH[3], ti=T[11 + 16 * 2])

        a = hh(a, b, c, d, mj=item[9], s=SHH[0], ti=T[12 + 16 * 2])
        d = hh(d, a, b, c, mj=item[12], s=SHH[1], ti=T[13 + 16 * 2])
        c = hh(c, d, a, b, mj=item[15], s=SHH[2], ti=T[14 + 16 * 2])
        b = hh(b, c, d, a, mj=item[2], s=SHH[3], ti=T[15 + 16 * 2])

        # Round 4 --->7
        a = ii(a, b, c, d, mj=item[0], s=SII[0], ti=T[0 + 16 * 3])
        d = ii(d, a, b, c, mj=item[7], s=SII[1], ti=T[1 + 16 * 3])
        c = ii(c, d, a, b, mj=item[14], s=SII[2], ti=T[2 + 16 * 3])
        b = ii(b, c, d, a, mj=item[5], s=SII[3], ti=T[3 + 16 * 3])

        a = ii(a, b, c, d, mj=item[12], s=SII[0], ti=T[4 + 16 * 3])
        d = ii(d, a, b, c, mj=item[3], s=SII[1], ti=T[5 + 16 * 3])
        c = ii(c, d, a, b, mj=item[10], s=SII[2], ti=T[6 + 16 * 3])
        b = ii(b, c, d, a, mj=item[1], s=SII[3], ti=T[7 + 16 * 3])

        a = ii(a, b, c, d, mj=item[8], s=SII[0], ti=T[8 + 16 * 3])
        d = ii(d, a, b, c, mj=item[15], s=SII[1], ti=T[9 + 16 * 3])
        c = ii(c, d, a, b, mj=item[6], s=SII[2], ti=T[10 + 16 * 3])
        b = ii(b, c, d, a, mj=item[13], s=SII[3], ti=T[11 + 16 * 3])

        a = ii(a, b, c, d, mj=item[4], s=SII[0], ti=T[12 + 16 * 3])
        d = ii(d, a, b, c, mj=item[11], s=SII[1], ti=T[13 + 16 * 3])
        c = ii(c, d, a, b, mj=item[2], s=SII[2], ti=T[14 + 16 * 3])
        b = ii(b, c, d, a, mj=item[9], s=SII[3], ti=T[15 + 16 * 3])

        A = (a + A) & 0xffffffff
        B = (b + B) & 0xffffffff
        C = (c + C) & 0xffffffff
        D = (d + D) & 0xffffffff

    result = reverse_hex(hex(A)) + reverse_hex(hex(B)) + reverse_hex(hex(C)) + reverse_hex(hex(D))
    return result


def md5_encrypt(plain_txt):
    return main_loop(plain_txt)
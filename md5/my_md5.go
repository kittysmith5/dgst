package main

import (
	"fmt"
	"strconv"
)

const Int32Max = 0xffffffff

var T = [64]int{
	0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
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
	0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
}

var SFF = [4]int{7, 12, 17, 22}
var SGG = [4]int{5, 9, 14, 20}
var SHH = [4]int{4, 11, 16, 23}
var SII = [4]int{6, 10, 15, 21}

func f(x, y, z int) int {
	return x&y | ^x&z
}

func g(x, y, z int) int {
	return x&z | y&^z
}

func h(x, y, z int) int {
	return x ^ y ^ z
}

func i(x, y, z int) int {
	return y ^ (x | ^z)
}

func rol(num, count int) int {
	b := (num & Int32Max) << count
	return (b & Int32Max) + (b >> 32)
}

func ff(a, b, c, d, mj, s, ti int) int {
	return b + rol(a+f(b, c, d)+mj+ti, s)
}

func gg(a, b, c, d, mj, s, ti int) int {
	return b + rol(a+g(b, c, d)+mj+ti, s)
}

func hh(a, b, c, d, mj, s, ti int) int {
	return b + rol(a+h(b, c, d)+mj+ti, s)
}

func ii(a, b, c, d, mj, s, ti int) int {
	return b + rol(a+i(b, c, d)+mj+ti, s)
}

func dec2bitStr(dec, bitLen int) string {
	s := ""
	for dec > 0 {
		rem := dec % 2
		dec = dec / 2
		s = strconv.Itoa(rem) + s
	}
	initLen := len(s)
	for i := 0; i < bitLen-initLen; i++ {
		s = "0" + s
	}
	return s
}

func bitStr2dec(bitStr string) int {
	intVal := 0
	for i := 0; i < len(bitStr); i++ {
		if bitStr[len(bitStr)-i-1] == 49 {
			intVal += nonNegIntPow(2, i)
		}
	}
	return intVal
}

func nonNegIntPow(base, power int) int {
	result := 1

	for i := 0; i < power; i++ {
		result *= base
	}
	return result
}
func littleEndian(str string) string {
	if len(str) < 32 {
		count := 32 - len(str)
		for i := 0; i < count; i++ {
			str = "0" + str
		}
	}

	newStr := str[24:32] + str[16:24] + str[8:16] + str[0:8]
	return newStr
}
func plain2bit(plain string) [][]int {
	bitStr := ""
	bitStrSlice := make([]string, 0)
	bitStr32 := make([][]int, 0)

	for _, c := range plain {
		bitStr += dec2bitStr(int(c), 8)
	}
	rmd := len(bitStr) % 512
	if rmd == 448 {
		bitStr += "1"
		for i := 0; i < 511; i++ {
			bitStr += "0"
		}
	} else {
		bitStr += "1"
		for i := 0; i < 448-rmd-1; i++ {
			bitStr += "0"
		}
	}

	lenBitStr := dec2bitStr(len(plain)*8, 64)
	bitStr += lenBitStr

	for i := 0; i < len(bitStr)/512; i++ {
		bitStrSlice = append(bitStrSlice, bitStr[i*512:(i+1)*512])
	}

	bitStr32Item := make([]int, 16)
	for i := 0; i < len(bitStrSlice); i++ {
		for j := 0; j < 16; j++ {
			bitStr32Item[j] = bitStr2dec(littleEndian(bitStrSlice[i][j*32 : (j+1)*32]))
		}
		bitStr32 = append(bitStr32, bitStr32Item)
	}

	bitStr32[len(bitStr32)-1][len(bitStr32[len(bitStr32)-1])-2] = bitStr2dec(lenBitStr[32:64])
	bitStr32[len(bitStr32)-1][len(bitStr32[len(bitStr32)-1])-1] = bitStr2dec(lenBitStr[0:32])

	return bitStr32
}

func md5Loop(plain string) string {
	A := 0x67452301
	B := 0xefcdab89
	C := 0x98badcfe
	D := 0x10325476
	bitStr32Arr := plain2bit(plain)
	for _, item := range bitStr32Arr {
		a := A
		b := B
		c := C
		d := D

		a = ff(a, b, c, d, item[0], SFF[0], T[0])
		d = ff(d, a, b, c, item[1], SFF[1], T[1])
		c = ff(c, d, a, b, item[2], SFF[2], T[2])
		b = ff(b, c, d, a, item[3], SFF[3], T[3])

		a = ff(a, b, c, d, item[4], SFF[0], T[4])
		d = ff(d, a, b, c, item[5], SFF[1], T[5])
		c = ff(c, d, a, b, item[6], SFF[2], T[6])
		b = ff(b, c, d, a, item[7], SFF[3], T[7])

		a = ff(a, b, c, d, item[8], SFF[0], T[8])
		d = ff(d, a, b, c, item[9], SFF[1], T[9])
		c = ff(c, d, a, b, item[10], SFF[2], T[10])
		b = ff(b, c, d, a, item[11], SFF[3], T[11])

		a = ff(a, b, c, d, item[12], SFF[0], T[12])
		d = ff(d, a, b, c, item[13], SFF[1], T[13])
		c = ff(c, d, a, b, item[14], SFF[2], T[14])
		b = ff(b, c, d, a, item[15], SFF[3], T[15])

		a = gg(a, b, c, d, item[1], SGG[0], T[0+16])
		d = gg(d, a, b, c, item[6], SGG[1], T[1+16])
		c = gg(c, d, a, b, item[11], SGG[2], T[2+16])
		b = gg(b, c, d, a, item[0], SGG[3], T[3+16])

		a = gg(a, b, c, d, item[5], SGG[0], T[4+16])
		d = gg(d, a, b, c, item[10], SGG[1], T[5+16])
		c = gg(c, d, a, b, item[15], SGG[2], T[6+16])
		b = gg(b, c, d, a, item[4], SGG[3], T[7+16])

		a = gg(a, b, c, d, item[9], SGG[0], T[8+16])
		d = gg(d, a, b, c, item[14], SGG[1], T[9+16])
		c = gg(c, d, a, b, item[3], SGG[2], T[10+16])
		b = gg(b, c, d, a, item[8], SGG[3], T[11+16])

		a = gg(a, b, c, d, item[13], SGG[0], T[12+16])
		d = gg(d, a, b, c, item[2], SGG[1], T[13+16])
		c = gg(c, d, a, b, item[7], SGG[2], T[14+16])
		b = gg(b, c, d, a, item[12], SGG[3], T[15+16])

		a = hh(a, b, c, d, item[5], SHH[0], T[0+16*2])
		d = hh(d, a, b, c, item[8], SHH[1], T[1+16*2])
		c = hh(c, d, a, b, item[11], SHH[2], T[2+16*2])
		b = hh(b, c, d, a, item[14], SHH[3], T[3+16*2])

		a = hh(a, b, c, d, item[1], SHH[0], T[4+16*2])
		d = hh(d, a, b, c, item[4], SHH[1], T[5+16*2])
		c = hh(c, d, a, b, item[7], SHH[2], T[6+16*2])
		b = hh(b, c, d, a, item[10], SHH[3], T[7+16*2])

		a = hh(a, b, c, d, item[13], SHH[0], T[8+16*2])
		d = hh(d, a, b, c, item[0], SHH[1], T[9+16*2])
		c = hh(c, d, a, b, item[3], SHH[2], T[10+16*2])
		b = hh(b, c, d, a, item[6], SHH[3], T[11+16*2])

		a = hh(a, b, c, d, item[9], SHH[0], T[12+16*2])
		d = hh(d, a, b, c, item[12], SHH[1], T[13+16*2])
		c = hh(c, d, a, b, item[15], SHH[2], T[14+16*2])
		b = hh(b, c, d, a, item[2], SHH[3], T[15+16*2])

		a = ii(a, b, c, d, item[0], SII[0], T[0+16*3])
		d = ii(d, a, b, c, item[7], SII[1], T[1+16*3])
		c = ii(c, d, a, b, item[14], SII[2], T[2+16*3])
		b = ii(b, c, d, a, item[5], SII[3], T[3+16*3])

		a = ii(a, b, c, d, item[12], SII[0], T[4+16*3])
		d = ii(d, a, b, c, item[3], SII[1], T[5+16*3])
		c = ii(c, d, a, b, item[10], SII[2], T[6+16*3])
		b = ii(b, c, d, a, item[1], SII[3], T[7+16*3])

		a = ii(a, b, c, d, item[8], SII[0], T[8+16*3])
		d = ii(d, a, b, c, item[15], SII[1], T[9+16*3])
		c = ii(c, d, a, b, item[6], SII[2], T[10+16*3])
		b = ii(b, c, d, a, item[13], SII[3], T[11+16*3])

		a = ii(a, b, c, d, item[4], SII[0], T[12+16*3])
		d = ii(d, a, b, c, item[11], SII[1], T[13+16*3])
		c = ii(c, d, a, b, item[2], SII[2], T[14+16*3])
		b = ii(b, c, d, a, item[9], SII[3], T[15+16*3])

		A = (a + A) & Int32Max
		B = (b + B) & Int32Max
		C = (c + C) & Int32Max
		D = (d + D) & Int32Max
	}
	aBinStr := littleEndian(dec2bitStr(A, 32))
	bBinStr := littleEndian(dec2bitStr(B, 32))
	cBinStr := littleEndian(dec2bitStr(C, 32))
	dBinStr := littleEndian(dec2bitStr(D, 32))

	md5BinStr := aBinStr + bBinStr + cBinStr + dBinStr
	md5HexStr := strBin2Hex(md5BinStr)

	return md5HexStr
}

func strBin2Hex(str string) string {
	hexStr := ""
	bin2hex := map[string]string{
		"0000": "0", "0001": "1", "0010": "2", "0011": "3",
		"0100": "4", "0101": "5", "0110": "6", "0111": "7",
		"1000": "8", "1001": "9", "1010": "a", "1011": "b",
		"1100": "c", "1101": "d", "1110": "e", "1111": "f",
	}
	for i := 0; i < len(str)/4; i++ {
		hexStr += bin2hex[str[i*4:(i+1)*4]]
	}
	return hexStr
}

func main() {
	str := ""
	fmt.Print("Please input a string to md5 encrypt: ")
	_, err := fmt.Scanln(&str)
	if err != nil {
		return
	}
	res := md5Loop(str)
	fmt.Println(res)
}
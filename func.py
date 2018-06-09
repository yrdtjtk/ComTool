#-*- coding:utf-8 -*-

from PyCRC.CRCCCITT import CRCCCITT

def hexstr2buf(s):
	b = bytearray(len(s)//2)
	for i in range(len(b)):
		s1 = s[i*2:i*2+2]
		i1 = int(s1, 16)
		b[i] = i1
	return bytes(b)

# def hex2asc(h):
# 	if 0<=h and h<=9:
# 		return chr(h+ord('0'))
# 	elif 0x0A<=h and h<=0x0F:
# 		return chr(h+ord('A')-0x0A)
# 	else:
# 		raise Exception('Invalid Argument,must be 0x00~0x0F!')

# def buf2hexstr(b):
# 	sa = []
# 	for b1 in b:
# 		sa.append(hex2asc(b1//16))
# 		sa.append(hex2asc(b1%16))
# 	return ''.join(sa)

def buf2hexstr(b):
	sa = []
	for b1 in b:
		sa.append('%02X' % b1)
	return ''.join(sa)

def crc(data):
	return CRCCCITT().calculate(data)

def bcc(input_data=None, init_val=0):
    try:
        is_string = isinstance(input_data, str)
        is_bytes = isinstance(input_data, bytes)

        if not is_string and not is_bytes:
            raise Exception("Please provide a string or a byte sequence \
                as argument for bcc calculation.")

        bccValue = init_val

        for c in input_data:
            d = ord(c) if is_string else c
            bccValue ^= d
        return bccValue
    except Exception as e:
        print("EXCEPTION(calculate bcc): {}".format(e))

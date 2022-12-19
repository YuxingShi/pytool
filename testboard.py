# coding: utf-8
import zlib
import binascii
import base64


raw_str = 'FJQRJKMC1000000101000000A001O+Y23vJuYLeHjI8G7s7vPchxiuXOZfNFf+RQ3sRG1AxiLi+Hf/nr4DvmpH5kDLcE166674564543464E45948B7817F3A77EC1F1C29B64E37E32BBCA899690988C394037B6D122'

b64_str = 'O+Y23vJuYLeHjI8G7s7vPchxiuXOZfNFf+RQ3sRG1AxiLi+Hf/nr4DvmpH5kDLcE'
b64_str2 = '/bAzQYyqfcSHCIdVpF04pwVQgzMsPiZvTIsQFOXoWqJ3bCPu16xFg8lcNHNIQCDG'
b64_decode = base64.b64decode(b64_str)
b64_decode2 = base64.b64decode(b64_str2)
print('b64_decode', b64_decode)
print('b64_decode2', b64_decode2)
print(binascii.b2a_hqx(b64_decode))
print(binascii.b2a_hqx(b64_decode2))
# print(zlib.decompress(b64_decode))

# if __name__ == '__main__':
#     pass

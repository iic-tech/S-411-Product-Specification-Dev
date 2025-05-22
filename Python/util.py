'''
Created on 21.02.2014
bm12: major changes 2020 now using open source
@author: bm1281,bm12
'''
import binascii
 
    
def calculateCRCCode(path):
    buf = open(path,'rb').read()
    #buf = (binascii.crc_hqx(buf,0) & 0xFFFFFFFF)
    buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    return buf
    #return "%08X" % buf


#!/usr/bin/env python3.5	

import sys, os, zlib
import crcmod, crc16, crc8
#import crc64

# bin source output bak
#
#

#==定义变量==
sourcepath = './source/'
fileend = '.rdb'

outpath = './output/'
outfile = 'dump.rdb'

#定义函数
def ctail(mfile):
	'''
	intercept tail
	'''

	f = open(mfile, 'rb')
	mcom = f.read()[:-9].hex()
	f.close
	return bytes.fromhex(mcom)
	return mcom

def chead(sfile):
	'''
	intercept head
	'''

	s = open(sfile, 'rb')
	scom = s.read()[11:].hex()
	s.close
	return bytes.fromhex(scom)
	return scom

def cksums(nfile, cheads, ctails):

	file_comm = ctails + cheads

	allnew = open(nfile, 'bw')
	allnew.write(file_comm)
	allnew.close

def listfile():


#入口
mcomo = ctail('1506.rdb')
scomo = chead('1706.rdb')

cksums(nfile='new.rdb', ctails=mcomo, cheads=scomo)


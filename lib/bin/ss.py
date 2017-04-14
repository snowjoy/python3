#!/usr/bin/env python3.5	

import sys, os, zlib, shutil
import crcmod, crc16, crc8
import logging
import datetime

#import crc64


#===============定义变量===============#
sourcepath = '../source/'
fileend = '.rdb'

outpath = '../output/'
outfile = outpath + 'dump.rdb'

bakpath = '../bak/'

binpath = '../bin/'

logpath = '../log/'

# 日志目录
log_dir = '../log/redis.log'
# 定义日志格式
logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s|%(name)s|%(levelname)s|%(pathname)s|'
						   '%(lineno)d|%(thread)s|%(process)s|%(message)s',
					filename='../log/redis.log',
					filemode='a', )
# 定义一个Handler打印DEBUG及以上级别的日志到sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# 设置输出格式
formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|'
							  '%(pathname)s|%(lineno)d|%(thread)s|%(process)s|%(message)s')
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)


#===============定义函数===============
def starthello():
	logging.info("#" * 30)
	logging.info('#' + ' ' * 28 + '#')
	#logging.info('#' + ' ' * 28 + '#')
	logging.info('#' + ' ' * 7 + 'start program.' + ' ' * 7 + '#')
	#logging.info('#' + ' ' * 28 + '#')
	logging.info('#' + ' ' * 28 + '#')
	logging.info("#" * 30)

def ctail(ctail_file):
	'''
	intercept tail
	'''

	f = open(ctail_file, 'rb')
	mcom = f.read()[:-9].hex()
	f.close
	return bytes.fromhex(mcom)
	#return mcom

def chead(chead_file):
	'''
	intercept head
	'''

	s = open(chead_file, 'rb')
	scom = s.read()[11:].hex()
	s.close
	return bytes.fromhex(scom)
	#return scom

def cbody(cbody_file):
	'''intercept head and tail'''

	cbd = open(cbody_file, 'rb')
	sbdcom = cbd.read()[11:][:-9].hex()
	cbd.close
	return bytes.fromhex(sbdcom)

def cksums(outfile, result_comm):

	#file_comm = ctails + cheads
	allnew = open(outfile, 'bw')
	allnew.write(result_comm)
	allnew.close

def nowdate():
	'''now time'''
	creat_time = datetime.datetime.now()
	start_time = creat_time.strftime('%Y%m%d_%H%M%S')
	return start_time

def sourcefile(sourcepath):
	'''find file list'''
	if not os.listdir(sourcepath):
		logging.warning('源目录%s中没有文件，请检查' % sourcepath)
		exit()
	file_list = os.listdir(sourcepath)
	logging.info('find %s file .' % int(len(file_list)))
	'''add path'''
	new_file_list = []
	for add_path in file_list:
		new_file = sourcepath + add_path
		new_file_list.append(new_file)
	return new_file_list

def batch_file(outfile, re_file_list):
	'''处理逻辑'''
	#files = sourcefile(sourcepath)
	logging.info('当前文件列表：' + str(re_file_list))
	file_count = len(re_file_list)
	if file_count == 1:
		logging.warning('只有一个文件，不处理。')
		logging.warning('我还没有来得及做一个文件的备份功能')
		exit()
	elif file_count == 2:
		ctail_file = re_file_list[0]
		logging.info('ctail_file：' + str(ctail_file))

		chead_file = re_file_list[1]
		logging.info('chead_file：' + str(chead_file))

		ctail_comm = ctail(ctail_file)
		chead_comm = chead(chead_file)
		result_comm = ctail_comm + chead_comm
		cksums(outfile, result_comm)
	elif file_count > 2:
		file_true = file_count - 1
		cbody_comm = bytes.fromhex('')
		for tmp_count in range(0, file_count):
			if tmp_count == 0:
				ctail_file = re_file_list[0]
				ctail_comm = ctail(ctail_file)

			elif tmp_count == file_true:
				chead_file = re_file_list[file_true]
				chead_comm = chead(chead_file)

			else:
				cbody_file = re_file_list[tmp_count]
				cbody_comms = cbody(cbody_file)
				cbody_comm = cbody_comm + cbody_comms

		result_comm = ctail_comm + cbody_comm + chead_comm
		cksums(outfile, result_comm)
	else:
		logging.warning('文件数量异常为%s，请检查目录或代码' % int(len(file_list)))

def databak(re_file_list, re_sourcedir, re_outputdir, outfile):
	#备份源文件
	for bak_alone in re_file_list:
		shutil.move(bak_alone, re_sourcedir)
		source_file_name = os.path.basename(bak_alone)
		togect_file = re_sourcedir + '/' + source_file_name
		if not os.path.exists(togect_file):
			logging.error('备份源文件%s失败，目标文件%s不存在，请检查...' % (bak_alone,togect_file))
		logging.info('备份源文件%s成功，目标文件%s' % (bak_alone,togect_file))
	#备份结果文件
	if not os.path.exists(outfile):
		logging.error('输出文件%s不存在，请检查...' % (outfile))
		exit()
	shutil.move(outfile, re_outputdir)
	output_file_name = os.path.basename(outfile)
	output_file = re_outputdir + '/' + output_file_name
	if not os.path.exists(output_file):
		logging.error('备份输出文件%s失败，目标文件%s不存在，请检查...' % (outfile, output_file))
	logging.info('备份输出文件%s成功，目标文件%s' % (outfile, output_file))


def creatdir(nowtime, bakpath):
	os.mkdir(bakpath + nowtime)
	bak_dir = bakpath + nowtime
	if not os.path.exists(bak_dir):
		logging.error('创建备份目录：' + bak_dir + '失败，请检查')
		exit()
	logging.info('创建备份目录：' + bak_dir + '完成')

	os.mkdir(bak_dir + '/' + 'source')
	source_bak_dir = bak_dir + '/' + 'source'
	if not os.path.exists(source_bak_dir):
		logging.error('创建源备份目录：' + source_bak_dir + '失败，请检查')
		exit()
	logging.info('创建源备份目录：' + source_bak_dir + '完成')

	os.mkdir(bak_dir + '/' + 'output')
	output_bak_dir = bak_dir + '/' + 'output'
	if not os.path.exists(output_bak_dir):
		logging.error('创建源备份目录：' + output_bak_dir + '失败，请检查')
		exit()
	logging.info('创建源备份目录：' + output_bak_dir + '完成')

	return source_bak_dir, output_bak_dir

def checkdir():
	'''生成工作目录'''
	#heck_log_dir = run_dir + '/' +
	logging.info('我还没有来得及做目录检测，所有目录需要手动创建')


#===============入口===============
#mcomo = ctail('1506.rdb')
#scomo = chead('1706.rdb')

#cksums(nfile='new.rdb', ctails=mcomo, cheads=scomo)

if __name__ == '__main__':
	starthello()

	#确定工作目录
	bin_dir = os.getcwd()
	run_dir = os.path.dirname(bin_dir)
	logging.info('当前工作目录：' + run_dir)

	checkdir()

	#获取当前时间
	nowtime = nowdate()
	logging.info('当前时间为：' + nowtime)

	logging.warning('我还没有来得及做启动时备份之前的输出文件')

	#获取源文件列表
	re_file_list = sourcefile(sourcepath)

	#处理文件
	batch_file(outfile, re_file_list)

	#创建备份目录
	re_sourcedir, re_outputdir = creatdir(nowtime, bakpath)

	#备份文件
	databak(re_file_list, re_sourcedir, re_outputdir, outfile)



#!/usr/bin/env python  
#-*- coding:utf-8 _*-  
"""
@author: HJK 
@file: main.py 
@time: 2019-01-08

"""

import sys
import re
import getopt
import glovar
from core.extractors import kugou
from core.extractors import qq
from core.extractors import netease
from core.extractors import baidu
from utils import echo
from utils.customlog import CustomLog

addons = {
    'qq': qq,
    'kugou': kugou,
    'netease': netease,
    'baidu': baidu,
}

logger = CustomLog(__name__).getLogger()

def indexOrRange(item):
    pattern=r'^(\d*)[-,:](\d*)$'
    m=re.match(pattern,str(item))
    if m:
        index1=int(m.group(1))
        index2=int(m.group(2))
        return 'range' , list(range(index1,index2+1))
    else:
        return 'index' , item

def downloadByIndexList(indexlist,music_list):
    for i in indexlist:
        itemtype,value=indexOrRange(i)
        if itemtype=='range' :
            downloadByIndexList(value,music_list)
            continue
        if int(i) < 0 or int(i) >= len(music_list): raise ValueError
        music = music_list[int(i)]
        addons.get(music['source']).download(music)
    return

def setopts(args):
    '''
    根据命令行输入的参数修改全局变量
    :param args: 命令行参数列表
    :return:
    '''
    try:
        opts, others = getopt.getopt(args, 'vhk:s:c:o:',
                                        ['verbose', 'help', 'keyword=', 'source=', 'count=', 'outdir='])
    except getopt.GetoptError as e:
        logger.error('命令解析失败')
        logger.error(e)
        echo.usage()
        sys.exit(2)

    glovar.init_option()

    for o, a in opts:
        if o in ('-h', '--help'):
            echo.usage()
            sys.exit(2)
        elif o in ('-v', '--verbose'):
            glovar.set_option('verbose', True)
        elif o in ('-k', '--keyword'):
            glovar.set_option('keyword', a)
        elif o in ('-s', '--source'):
            glovar.set_option('source', a)
        elif o in ('-c', '--count'):
            glovar.set_option('count', int(a))
        elif o in ('-o', '--outdir'):
            glovar.set_option('outdir', a)
        else:
            assert False, 'unhandled option'

def main():
    music_list = []

    if not glovar.get_option('keyword'):
        # 如果未设置关键词
        keyword = input('请输入要搜索的歌曲，名称和歌手一起输入可以提高匹配（如 空帆船 朴树）：\n > ')
        glovar.set_option('keyword', keyword)

    for source in glovar.get_option('source').split():
        try:
            music_list += addons.get(source).search(glovar.get_option('keyword'))
        except Exception as e:
            logger.error('Get %s music list failed.' % source.upper())
            logger.error(e)

    echo.menu(music_list)
    choices = input('请输入要下载的歌曲序号，多个序号用空格隔开：')
    downloadByIndexList(choices.split(),music_list)

    # 下载完后继续搜索
    keyword = input('请输入要搜索的歌曲，或Ctrl+C退出：\n > ')
    glovar.set_option('keyword', keyword)
    main()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        setopts(sys.argv[1:])
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)


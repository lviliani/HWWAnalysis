#!/usr/bin/env python

import sys
import glob
import tempfile
import optparse
import hwwinfo
import hwwtools
import shutil
import tarfile
import os

def pack():
    usage = 'usage: %prog -p path'
    parser = optparse.OptionParser(usage)
    parser.add_option('--prefix','-p',dest='prefix',help='prefix',default=None)
    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)

    (opt, args) = parser.parse_args()

    if not opt.prefix:
        parser.error('Prefix not defined: check the usage')
    prefix = opt.prefix if opt.prefix[-1] != '/' else opt.prefix[:-1]
    
    tmppath = tempfile.mkdtemp('_pack_'+prefix)
    shutil.copytree(prefix+'/datacards',tmppath+'/datacards')
    if opt.variable == 'mll':
        os.system('rename _shape _mllShape '+tmppath+'/datacards/*_shape.txt')
    elif opt.variable == 'bdts':
        os.system('rename _shape _bdtShape '+tmppath+'/datacards/*_shape.txt')

    
    tarname = tmppath+'/'+prefix+'.tgz'
    here = os.getcwd()
    os.chdir(tmppath)
    tar = tarfile.open(tarname,mode='w:gz')
    tar.add('datacards')
    tar.close()
    shutil.move(tarname,here)

#     shutil.rmtree(tmppath)
#     print tmppath

if __name__ == '__main__':
    pack()


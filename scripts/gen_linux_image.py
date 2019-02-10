#!/usr/bin/python

import os
import shutil
import subprocess
import argparse
from bench_dict import bench_dict

parser = argparse.ArgumentParser()
parser.add_argument('--outdir', dest = 'out_dir', required = True)
parser.add_argument('--jobs', dest = 'jobs', required = False, default = 1)
args = parser.parse_args()

# riscy dirs
build_linux_script = os.path.join(os.environ['RISCY_HOME'],
                                  'tools', 'build-linux.py')
bbl_path = os.path.join(os.environ['RISCY_TOOLS'], 'build-pk', 'bbl')

# dirs for benchmarks
input_dir = '../benchmark/graphs'
bin_dir = '../build/riscv'

# dir to build linux
out_dir = os.path.abspath(args.out_dir)
test_dir = os.path.join(out_dir, 'test') # build initramfs for this benchmark

for graph, bench_params in bench_dict.iteritems():
    print ''
    print '========================================='
    print 'Generating gapbs graph {} ...'.format(graph)
    print '========================================='
    print ''

    # clean up test dir
    if os.path.isdir(test_dir):
        # to avoid no write permssion, first chmod
        for path, dirs, files in os.walk(test_dir):
            os.chmod(path, int('0777', 8))
            for f in files:
                os.chmod(os.path.join(path, f), int('0777', 8))
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)

    # copy graph
    input_graph = os.path.join(input_dir, graph)
    if not os.path.exists(input_graph):
        print 'Graph {} does not exist, skip'.format(input_graph)
        continue
    shutil.copy(input_graph, test_dir)

    for bench, param in bench_params.iteritems():
        # copy binary
        binary = os.path.join(bin_dir, bench)
        if not os.path.exists(binary):
            print 'Binary {} does not exist, skip'.format(binary)
            continue
        shutil.copy(binary, test_dir)

        # write run.sh
        run_sh = os.path.join(test_dir, bench + '.sh')
        if os.path.isfile(run_sh):
            raise Exception('run.sh already exists!')
        with open(run_sh, 'w') as fp:
            fp.write('#!/bin/ash\n')
            fp.write('if [ $# -ne 1 ]; then\n')
            fp.write('  echo "Usage: ./run.sh THREAD_NUM"\n')
            fp.write('  exit\n')
            fp.write('fi\n')
            fp.write('export OMP_NUM_THREADS=$1\n')
            fp.write('time ./{} -f {} -a -n1 {}\n'.format(bench, graph, param))
        os.chmod(run_sh, int('0777', 8))

    # compile and copy linux (bbl)
    subprocess.check_call([build_linux_script,
                           '--jobs', str(args.jobs),
                           '--testdir', test_dir])
    shutil.copy(bbl_path,
                os.path.join(out_dir,
                             '_'.join(['bbl', 'gapbs', graph])))



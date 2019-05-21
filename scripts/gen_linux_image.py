#!/usr/bin/python

import os
import shutil
import subprocess
import argparse
from bench_dict import arg_dict, run_dict

parser = argparse.ArgumentParser()
parser.add_argument('--outdir', dest = 'out_dir', required = True)
parser.add_argument('--jobs', dest = 'jobs', required = False, default = 1)
parser.add_argument('--depld', dest = 'dep_ld_fence', action = 'store_true')
parser.add_argument('--bindir', dest = 'bin_dir', required = False, default = '../build/riscv')
args = parser.parse_args()

# riscy dirs
build_linux_script = os.path.join(os.environ['RISCY_HOME'],
                                  'tools', 'build-linux.py')
bbl_path = os.path.join(os.environ['RISCY_TOOLS'], 'build-pk', 'bbl')

# dirs for benchmarks
input_dir = '../benchmark/graphs'
bin_dir = args.bin_dir

# dir to build linux
out_dir = os.path.abspath(args.out_dir)
test_dir = os.path.join(out_dir, 'test') # build initramfs for this benchmark

for graph, bench_params in arg_dict.iteritems():
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

        # write run.sh, test and ref
        for size in ['test', 'ref']:
            run_sh = os.path.join(test_dir, bench + '-' + size + '.sh')
            if os.path.isfile(run_sh):
                raise Exception(run_sh + ' already exists!')
            with open(run_sh, 'w') as fp:
                fp.write('#!/bin/ash\n')
                fp.write('if [ $# -ne 1 ]; then\n')
                fp.write('  echo "Usage: $0 ./ THREAD_NUM"\n')
                fp.write('  exit\n')
                fp.write('fi\n')
                fp.write('export OMP_NUM_THREADS=$1\n')
                fp.write('time ./{} -f {} -a -n{} {}\n'.format(
                         bench, graph, run_dict[size][bench], param))
            os.chmod(run_sh, int('0777', 8))

    # compile and copy linux (bbl)
    cmd = [build_linux_script,
           '--jobs', str(args.jobs),
           '--testdir', test_dir]
    if args.dep_ld_fence:
        cmd.append('--depld')
    subprocess.check_call(cmd)
    shutil.copy(bbl_path,
                os.path.join(out_dir,
                             '_'.join(['bbl', 'gapbs', graph])))



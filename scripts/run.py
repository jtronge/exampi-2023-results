#!/usr/bin/env python3
"""Benchmark run script."""
import argparse
import os
import shutil
import subprocess
import sys

# Specific benchmark arguments
benchmarks = {
    'osu_latency': '-i 1000'.split(),
    'osu_mbw_mr': '-i 1000'.split(),
    'osu_bw': '-i 1000'.split(),
}
# Environments for each test version
versions = {
    'sm': {
        'OMPI_MCA_pml': 'ob1',
        'OMPI_MCA_btl': 'sm,self',
        'OMPI_MCA_btl_sm_fbox_max': '0',
    },
    'rsm': {
        'OMPI_MCA_pml': 'ob1',
        'OMPI_MCA_btl': 'rsm,self',
    },
}

def filename(test_name, run, version):
    return f'{test_name}.{run}.{version}'

parser = argparse.ArgumentParser(description='benchmark runner')
parser.add_argument('-o', '--omb-path', required=True,
                    help='path to OMB benchmarks build')
parser.add_argument('-c', '--count', required=True, type=int,
                    help='number of runs to do')
parser.add_argument('-r', '--results-path', required=True,
                    help='path to results dir')
parser.add_argument('-b', '--benchmarks', default=None, help='benchmarks to run')
# It would perhaps be better to have a separate command for flamegraph, but
# this will do for now
parser.add_argument('-f', '--flamegraph', action='store_true',
                    help='generate flamegraph')
parser.add_argument('--rank', default=0, help='rank to run flamegraph test on')
args = parser.parse_args()

if args.benchmarks is None:
    to_run = benchmarks.keys()
else:
    to_run = args.benchmarks.split(',')
    not_found = []
    for bench in to_run:
        if bench not in benchmarks:
            not_found.append(bench)
    if not_found:
        print(f'Benchmarks {",".join(not_found)} were not found', file=sys.stderr)
        sys.exit(1)

omb_path = os.path.join(args.omb_path, 'c/mpi/pt2pt/standard')

for test_name in to_run:
    extra_args = benchmarks[test_name]
    print('Running', test_name)
    for version, env in versions.items():
        print('=> Testing version', version)
        run_env = dict(os.environ)
        run_env.update(env)
        bin_path = os.path.join(omb_path, test_name)
        argv = ['mpirun', '-np', '2']
        if args.flamegraph:
            argv.append('./scripts/flamegraph')
        argv.append(bin_path)
        argv.extend(extra_args)
        print('==> Running', args.count, 'test(s) with args', argv)
        for run in range(args.count):
            fname = filename(test_name, run, version)
            out_file = os.path.join(args.results_path, f'{fname}.out')
            flamegraph_fname = os.path.join(args.results_path, f'{fname}.svg')
            final_env = dict(run_env)
            final_env['FLAMEGRAPH_FNAME'] = str(flamegraph_fname)
            final_env['FLAMEGRAPH_RANK'] = str(args.rank)
            with open(out_file, 'w', encoding='utf-8') as fp:
                print(argv)
                subprocess.run(argv, env=final_env, stdout=fp)

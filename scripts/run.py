"""Benchmark run script."""
import argparse
import os
import shutil
import subprocess
import sys

# Benchmarks with args to pass
benchmarks = {
    'osu_latency': '-m 2:256 -i 16384'.split(),
    'osu_mbw_mr': '-m 2:256 -i 16384'.split(),
    'osu_bw': '-m 2:256 -i 16384'.split(),
}
# Test versions run with the environment
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
    return f'{test_name}.{run}.{version}.out'

parser = argparse.ArgumentParser(description='benchmark runner')
parser.add_argument('-o', '--omb-path', required=True, help='path to OMB benchmarks build')
parser.add_argument('-c', '--count', required=True, type=int, help='number of runs to do')
parser.add_argument('-r', '--results-path', required=True, help='path to results dir')
parser.add_argument('-b', '--benchmarks', default=None, help='benchmarks to run')
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
        argv = ['mpirun', '-np', '2', bin_path]
        argv.extend(extra_args)
        print('==> Running', args.count, 'test(s) with args', argv)
        for run in range(args.count):
            out_file = os.path.join(args.results_path, filename(test_name, run, version))
            with open(out_file, 'w', encoding='utf-8') as fp:
                subprocess.run(argv, env=run_env, stdout=fp)

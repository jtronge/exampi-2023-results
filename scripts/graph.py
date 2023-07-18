"""Plot results from a specific run."""
import matplotlib.pyplot as plt
import argparse
import numpy as np

graph_types = ['box-plot', 'line-graph']
benchmarks = ['osu_mbw_mr', 'osu_latency']
versions = ['sm', 'rsm']
sm_fmt = 'b-'
rsm_fmt = 'r--'

parser = argparse.ArgumentParser(description='generate graphs for results')
parser.add_argument('-r', '--results-path', required=True, help='path to results dir')
parser.add_argument('-c', '--count', required=True, type=int, help='number of runs')
parser.add_argument('-t', '--title', required=True, help='title')
args = parser.parse_args()

def parse_osu_latency_output(fname):
    """Parse latency output."""
    sizes = []
    latencies = []
    with open(fname) as fp:
        for line in fp:
            if line.startswith('#') or not line.strip():
                continue
            size, latency = line.split()
            sizes.append(size)
            latencies.append(float(latency))
    return sizes, latencies

def parse_osu_mbw_mr_output(fname):
    """Parse osu_mbw_mr output."""
    sizes = []
    bandwidth = []
    message_rate = []
    with open(fname) as fp:
        for line in fp:
            if line.startswith('#') or not line.strip():
                continue
            size, bw, mr = line.split()
            sizes.append(size)
            bandwidth.append(float(bw))
            message_rate.append(float(mr))
    return sizes, bandwidth, message_rate

sizes = None
sm_bws = []
sm_mrs = []
rsm_bws = []
rsm_mrs = []
for run in range(args.count):
    sm_size, sm_bw, sm_mr = parse_osu_mbw_mr_output(f'{args.results_path}/osu_mbw_mr.{run}.sm.out')
    rsm_size, rsm_bw, rsm_mr = parse_osu_mbw_mr_output(f'{args.results_path}/osu_mbw_mr.{run}.rsm.out')

    sizes = sm_size
    sm_bws.append(sm_bw)
    sm_mrs.append(sm_mr)
    rsm_bws.append(rsm_bw)
    rsm_mrs.append(rsm_mr)
# Average the results
sm_bw = np.average(np.array(sm_bws), 0)
rsm_bw = np.average(np.array(rsm_bws), 0)
sm_mr = np.average(np.array(sm_mrs), 0)
rsm_mr = np.average(np.array(rsm_mrs), 0)

# Compute overhead
bw_overhead = 100 * ((sm_bw - rsm_bw) / sm_bw)
print('bandwidth overhead:', np.average(bw_overhead, 0))
mr_overhead = 100 * ((sm_mr - rsm_mr) / sm_mr)
print('mr overhead:', np.average(mr_overhead, 0))

fig, (ax0, ax1) = plt.subplots(2)
ax0.plot(sm_size, sm_bw, sm_fmt, label='sm')
ax0.plot(rsm_size, rsm_bw, rsm_fmt, label='rsm')
ax0.legend()
ax0.set_ylabel('Bandwidth (MB/s)')
ax0.set_xlabel('Size (bytes)')
ax0.set_title(f'osu_mbw_mr - {args.title}')

ax1.plot(sm_size, sm_mr, sm_fmt, label='sm')
ax1.plot(rsm_size, rsm_mr, rsm_fmt, label='rsm')
ax1.legend()
ax1.set_ylabel('Messages/s')
ax1.set_xlabel('Size (bytes)')
# ax1.set_ylim(ymin=1.0e6, ymax=4.0e6)
# ax1.set_title(f'osu_mbw_mr - {args.title}')
plt.show()

sizes = None
sm_lats = []
rsm_lats = []
for run in range(args.count):
    sm_size, sm_lat = parse_osu_latency_output(f'{args.results_path}/osu_latency.{run}.sm.out')
    rsm_size, rsm_lat = parse_osu_latency_output(f'{args.results_path}/osu_latency.{run}.rsm.out')

    sizes = sm_size
    sm_lats.append(sm_lat)
    rsm_lats.append(rsm_lat)
sm_lats = np.average(np.array(sm_lats), 0)
rsm_lats = np.average(np.array(rsm_lats), 0)

lat_overhead = 100 * ((rsm_lats - sm_lats) / rsm_lats)
print('latency overhead:', np.average(lat_overhead))

fig, ax = plt.subplots()
ax.plot(sizes, sm_lats, sm_fmt, label='sm')
ax.plot(sizes, rsm_lats, rsm_fmt, label='rsm')
ax.legend()
ax.set_xlabel('Size (bytes)')
ax.set_ylabel('Latency (μs)')
ax.set_title(f'osu_latency - {args.title}')
# ax.set_ylim(ymin=0.0, ymax=1.0)
plt.show()

#!/usr/bin/env python3
"""Plot results from a specific run."""
import matplotlib.pyplot as plt
import argparse
import numpy as np

graph_types = ['box-plot', 'line-graph']
benchmarks = ['osu_mbw_mr', 'osu_latency']
versions = ['sm', 'rsm']
sm_fmt = 'b-'
rsm_fmt = 'r-.'

parser = argparse.ArgumentParser(description='generate graphs for results')
parser.add_argument('-r', '--results-path', required=True, help='path to results dir')
parser.add_argument('-c', '--count', required=True, type=int, help='number of runs')
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
            sizes.append(int(size))
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
            sizes.append(int(size))
            bandwidth.append(float(bw))
            message_rate.append(float(mr))
    return sizes, bandwidth, message_rate

def compute_error(results):
    """Compute the average and error."""
    result = np.average(results, 0)
    max_result = np.amax(results, axis=0)
    min_result = np.amin(results, axis=0)
    error = [result - min_result, max_result - result]
    return result, error

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
sm_bws = np.array(sm_bws)
rsm_bws = np.array(rsm_bws)
sm_mrs = np.array(sm_mrs)
rsm_mrs = np.array(rsm_mrs)

# Average the results
sm_bw = np.average(sm_bws, 0)
rsm_bw = np.average(rsm_bws, 0)
sm_mr = np.average(sm_mrs, 0)
rsm_mr = np.average(rsm_mrs, 0)

# Compute errorbar values
sm_bw, sm_bw_err = compute_error(sm_bws)
rsm_bw, rsm_bw_err = compute_error(rsm_bws)
sm_mr, sm_mr_err = compute_error(sm_mrs)
rsm_mr, rsm_mr_err = compute_error(rsm_mrs)


def min_max_overhead(baseline, result):
    """Compute min and max overhead points."""
    overhead = 100 * ((baseline - result) / baseline)
    # print([int(np.log2(sz)) for sz in sizes])
    # print(overhead)
    avg = np.average(overhead, 0)
    print(f'-- average overhead = {avg:.2f}%')
    mini = np.argmin(overhead)
    power = int(np.log2(sizes[mini]))
    print(f'-- min overhead (2^{power}) =', '{:.2f}%'.format(overhead[mini]))
    maxi = np.argmax(overhead)
    power = int(np.log2(sizes[maxi]))
    print(f'-- max overhead (2^{power}) =', '{:.2f}%'.format(overhead[maxi]))
    return (mini, overhead[mini]), (maxi, overhead[maxi]), avg

# Compute overhead for bandwidth and message rate
print('bandwidth overhead:')
print('================================')
print('message rate overhead:')
min_max_overhead(sm_mr, rsm_mr)
print('================================')

# Set plot style
plt.style.use('./paper.mplstyle')


def compute_and_annotate_overhead(baseline, result, ax, miny, maxy, bestx=None, worstx=None, habest='center', haworst='center', flip=False):
    """Compute and annotate the overhead."""
    (min_overhead_idx, min_overhead), (max_overhead_idx, max_overhead), avg_overhead = min_max_overhead(baseline, result)

    def annotate(text, overhead, xy, xytext, ha):
        ax.annotate(f'{text}: {overhead:.2f}%',
                    xy=xy, xytext=xytext,
                    arrowprops=dict(headwidth=8.0, width=4.0, facecolor='black', shrinkB=0.7),
                    ha=ha, fontweight='bold')

    bestx = sizes[min_overhead_idx] if bestx is None else bestx
    annotate('best', min_overhead,
             xy=(sizes[min_overhead_idx], result[min_overhead_idx] if not flip else baseline[min_overhead_idx]),
             xytext=(bestx, miny(min_overhead_idx)),
             ha=habest)
    worstx = sizes[max_overhead_idx] if worstx is None else worstx
    annotate('worst', max_overhead,
             xy=(sizes[max_overhead_idx], result[max_overhead_idx] if not flip else baseline[max_overhead_idx]),
             xytext=(worstx, maxy(max_overhead_idx)),
             ha=haworst)


# Bandwidth
fig, ax = plt.subplots()
compute_and_annotate_overhead(sm_bw, rsm_bw, ax, miny=lambda i: 3 * rsm_bw[i] / 4, maxy=lambda i: 20 * rsm_bw[i])
# print(sm_size, sm_bw)
ax.errorbar(sizes, sm_bw, yerr=sm_bw_err, fmt=sm_fmt, label='sm')
ax.errorbar(sizes, rsm_bw, yerr=rsm_bw_err, fmt=rsm_fmt, label='rsm')
ax.legend()
ax.set_ylabel('Bandwidth (MB/s)')
ax.set_xlabel('Size (bytes)')
ax.set_title(f'Bandwidth (osu_mbw_mr)')
ax.set_xscale('log', base=2)
ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
plt.show()

# Message rate
fig, ax = plt.subplots()
compute_and_annotate_overhead(sm_mr, rsm_mr, ax, miny=lambda i: 50 * rsm_mr[i], maxy=lambda i: 5 * rsm_mr[i] / 8)
ax.errorbar(sizes, sm_mr, yerr=sm_mr_err, fmt=sm_fmt, label='sm')
ax.errorbar(sizes, rsm_mr, yerr=rsm_mr_err, fmt=rsm_fmt, label='rsm')
ax.legend()
ax.set_title(f'Message Rate (osu_mbw_mr)')
ax.set_ylabel('Messages/s')
ax.set_xlabel('Size (bytes)')
ax.set_xscale('log', base=2)
plt.show()

sizes = None
sm_lats = []
rsm_lats = []
for run in range(args.count):
    sm_size, sm_lat = parse_osu_latency_output(f'{args.results_path}/osu_latency.{run}.sm.out')
    rsm_size, rsm_lat = parse_osu_latency_output(f'{args.results_path}/osu_latency.{run}.rsm.out')

    sizes = sm_size[:16]
    sm_lats.append(sm_lat[:16])
    rsm_lats.append(rsm_lat[:16])
sm_lat, sm_lat_err = compute_error(sm_lats)
rsm_lat, rsm_lat_err = compute_error(rsm_lats)

print('latency overhead:')
min_max_overhead(rsm_lat, sm_lat)
print('================================')

# Latency
fig, ax = plt.subplots()
compute_and_annotate_overhead(rsm_lat, sm_lat, ax, miny=lambda i: sm_lat[i] / 8,
                              maxy=lambda i: 4 * sm_lat[i], habest='right', flip=True)
ax.errorbar(sizes, sm_lat, yerr=sm_lat_err, fmt=sm_fmt, label='sm')
ax.errorbar(sizes, rsm_lat, yerr=rsm_lat_err, fmt=rsm_fmt, label='rsm')
ax.legend()
ax.set_xlabel('Size (bytes)')
ax.set_ylabel('Latency (μs)')
ax.set_title(f'Latency (osu_latency)')
ax.set_xscale('log', base=2)
plt.show()

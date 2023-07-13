import matplotlib.pyplot as plt
import argparse

graph_types = ['box-plot', 'line-graph']
benchmarks = ['osu_mbw_mr', 'osu_latency']

parser = argparse.ArgumentParser(description='generate graphs for results')
parser.add_argument('-r', '--results-path', required=True, help='path to results dir')
parser.add_argument('-b', '--benchmark', required=True, choices=benchmarks, help='benchmark name')
parser.add_argument('-g', '--graph', required=True, choices=graph_types, help='graph type')
args = parser.parse_args()

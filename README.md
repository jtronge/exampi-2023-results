# Running benchmarks

1. Install Open MPI from <https://github.com/jtronge/ompi> with branch `btl-sm-rust`.
2. Install the OSU Micro Benchmarks (OMB)
   <https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.2.tar.gz>
   linked to the above Open MPI.
3. Make sure the right `mpirun` is in your path and run
   `python3 scripts/run.py -o ${path_to_omb} -c 32 -r ${results_dir}`.

#!/bin/bash
# runscipt as ./runme.sh BENCHMARK
set -x
AFS_HOME=/afs/inf.ed.ac.uk/user/s18/s1897969
AFS_PROJ=/afs/inf.ed.ac.uk/group/project/dramrep

# only for parsec and splash we have this array
# lulesh, graph500, comd, xsbench have inline threads
declare -A parsec_bench_threads=( 
["blackscholes"]="17" ["bodytrack"]="18" ["canneal"]="17" 
["dedup"]="51" ["facesim"]="16" ["ferret"]="67" 
["fluidanimate"]="17" ["freqmine"]="16"  ["streamcluster"]="17" 
["vips"]="19" ["x264"]="18" )

declare -A splash_bench_threads=( 
["cholesky"]="16" ["ocean_cp"]="16" ["lu_cb"]="16" 
["fft"]="16" ["radix"]="16" ["raytrace"]="16" 
["barnes"]="16" ["volrend"]="16" ["watern2"]="16" )

function run() {
bench=$1

if [ $bench == "lulesh" ]
then
# lulesh
$AFS_HOME/gem5/build/X86_MESI_Two_Level/gem5.opt -r -e --outdir=$AFS_PROJ/results/meshdir-simple/lulesh --debug-flags=ROI,STIntervalPrintByHour configs/example/synchrotrace_ruby.py \
--event-dir=$AFS_PROJ/traces/16t-lulesh \
--output-dir=$AFS_PROJ/results/meshdir-simple/lulesh \
--ruby \
--network=simple \
--topology=MeshDirCorners_XY \
--mesh-rows=4 \
--cacheline_size=64 \
--l1d_size=32kB --l1d_assoc=8 \
--l1i_size=32kB --l1i_assoc=8 \
--num-dirs=4 --num-l2caches=16 \
--mem-size=16GB \
--l2_size=2048kB --l2_assoc=16 \
--num-cpus=16 --num-threads=16 \
--cpi-iops=1 --cpi-flops=1 --pc-skip \
--warmup-ops=1000000000 --detailed-ops=20000000000 \
--monitor-freq=100 \
--numa-high-bit=12 \
--mem-type=DDR4_2400_4x16 & disown

elif [ $bench == "comd" ]
then
# comd
$AFS_HOME/gem5/build/X86_MESI_Two_Level/gem5.opt -r -e --outdir=$AFS_PROJ/results/meshdir-simple/comd --debug-flags=ROI,STIntervalPrintByHour configs/example/synchrotrace_ruby.py \
--event-dir=$AFS_PROJ/traces/16t-comd \
--output-dir=$AFS_PROJ/results/meshdir-simple/comd \
--ruby \
--network=simple \
--topology=MeshDirCorners_XY \
--mesh-rows=4 \
--cacheline_size=64 \
--l1d_size=32kB --l1d_assoc=8 \
--l1i_size=32kB --l1i_assoc=8 \
--num-dirs=4 --num-l2caches=16 \
--mem-size=16GB \
--l2_size=2048kB --l2_assoc=16 \
--num-cpus=16 --num-threads=16 \
--cpi-iops=1 --cpi-flops=1 --pc-skip \
--warmup-ops=1000000000 --detailed-ops=20000000000 \
--monitor-freq=100 \
--numa-high-bit=12 \
--mem-type=DDR4_2400_4x16 & disown

elif [ $bench == "graph500" ]
then
# graph500 - for now using 16t-graph-s14, revert back to 16t-graph
$AFS_HOME/gem5/build/X86_MESI_Two_Level/gem5.opt -r -e --outdir=$AFS_PROJ/results/meshdir-simple/graph500 --debug-flags=ROI,STIntervalPrintByHour configs/example/synchrotrace_ruby.py \
--event-dir=$AFS_PROJ/traces/16t-graph500-s14 \
--output-dir=$AFS_PROJ/results/meshdir-simple/graph500 \
--ruby \
--network=simple \
--topology=MeshDirCorners_XY \
--mesh-rows=4 \
--cacheline_size=64 \
--l1d_size=32kB --l1d_assoc=8 \
--l1i_size=32kB --l1i_assoc=8 \
--num-dirs=4 --num-l2caches=16 \
--mem-size=16GB \
--l2_size=2048kB --l2_assoc=16 \
--num-cpus=16 --num-threads=16 \
--cpi-iops=1 --cpi-flops=1 --pc-skip \
--warmup-ops=1000000000 --detailed-ops=20000000000 \
--monitor-freq=100\
--numa-high-bit=12 \
--mem-type=DDR4_2400_4x16 & disown

elif [ $bench == "xsbench" ]
then
# xsbench
$AFS_HOME/gem5/build/X86_MESI_Two_Level/gem5.opt -r -e --outdir=$AFS_PROJ/results/meshdir-simple/xsbench --debug-flags=ROI,STIntervalPrintByHour configs/example/synchrotrace_ruby.py \
--event-dir=$AFS_PROJ/traces/16t-small-xsbench \
--output-dir=$AFS_PROJ/results/meshdir-simple/xsbench \
--ruby \
--network=simple \
--topology=MeshDirCorners_XY \
--mesh-rows=4 \
--cacheline_size=64 \
--l1d_size=32kB --l1d_assoc=8 \
--l1i_size=32kB --l1i_assoc=8 \
--num-dirs=4 --num-l2caches=16 \
--mem-size=16GB \
--l2_size=2048kB --l2_assoc=16 \
--num-cpus=16 --num-threads=16 \
--cpi-iops=1 --cpi-flops=1 --pc-skip \
--warmup-ops=1000000000 --detailed-ops=20000000000 \
--monitor-freq=100\
--numa-high-bit=12 \
--mem-type=DDR4_2400_4x16 & disown

elif [[ ${parsec_bench_threads[$bench]} ]]
then
# must be one of the parsec benchmarks
$AFS_HOME/gem5/build/X86_MESI_Two_Level/gem5.opt -r -e --outdir=$AFS_PROJ/results/meshdir-simple/$bench --debug-flags=ROI,STIntervalPrintByHour configs/example/synchrotrace_ruby.py \
--event-dir=$AFS_PROJ/traces/16t-large-roi-parsec/$bench \
--output-dir=$AFS_PROJ/results/meshdir-simple/$bench \
--ruby \
--network=simple \
--topology=MeshDirCorners_XY \
--mesh-rows=4 \
--cacheline_size=64 \
--l1d_size=32kB --l1d_assoc=8 \
--l1i_size=32kB --l1i_assoc=8 \
--num-dirs=4 --num-l2caches=16 \
--mem-size=16GB \
--l2_size=2048kB --l2_assoc=16 \
--num-cpus=16 --num-threads=${parsec_bench_threads[$bench]} \
--cpi-iops=1 --cpi-flops=1 --pc-skip \
--warmup-ops=1000000000 --detailed-ops=20000000000 \
--monitor-freq=100 \
--numa-high-bit=12 \
--mem-type=DDR4_2400_4x16 & disown

elif [[ ${splash_bench_threads[$bench]} ]]
then
# must be one of the splash benchmarks
# for now to run on philly changing splash benchmarks eventdir
# disk local has lu_cb, ocean_cp, radix, raytrace
#       #--event-dir=/disk/scratch/s1897969/traces/16t-large-roi-splash/$bench \
# afs has cholesky, watern2, fft, barnes
#	#--event-dir=$AFS_PROJ/traces/16t-large-roi-splash/$bench \
$AFS_HOME/gem5/build/X86_MESI_Two_Level/gem5.opt -r -e --outdir=$AFS_PROJ/results/meshdir-simple/$bench --debug-flags=ROI,STIntervalPrintByHour configs/example/synchrotrace_ruby.py \
--event-dir=$AFS_PROJ/traces/16t-large-roi-splash/$bench \
--output-dir=$AFS_PROJ/results/meshdir-simple/$bench \
--ruby \
--network=simple \
--topology=MeshDirCorners_XY \
--mesh-rows=4 \
--cacheline_size=64 \
--l1d_size=32kB --l1d_assoc=8 \
--l1i_size=32kB --l1i_assoc=8 \
--num-dirs=4 --num-l2caches=16 \
--mem-size=16GB \
--l2_size=2048kB --l2_assoc=16 \
--num-cpus=16 --num-threads=${splash_bench_threads[$bench]} \
--cpi-iops=1 --cpi-flops=1 --pc-skip \
--warmup-ops=1000000000 --detailed-ops=20000000000 \
--monitor-freq=100 \
--numa-high-bit=12 \
--mem-type=DDR4_2400_4x16 & disown

fi

}

run $1

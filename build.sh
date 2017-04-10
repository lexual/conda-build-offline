#!/bin/bash

#for n in {1..80}
#do
#    python ./code.py ../envs/env.manifest -n$n
#    conda-build-all feedstocks --matrix-conditions "python 2.7.*|3.6.*" "numpy 1.12.*"
#done

conda-build-all forks --matrix-conditions "python 2.7.*" "numpy 1.12.*"
#conda-build-all forks --matrix-conditions "python 3.6.*" "numpy 1.12.*"
#conda-build-all feedstocks --matrix-conditions "python 2.7.*|3.6.*" "numpy 1.12.*"
#time CONDA_PY=27 CONDA_NPY=112 conda-build feedstocks

source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh

setup dunesw v10_13_00d00 -q e26:prof

# path-prepend /exp/dune/app/users/$USER/opt/bin PATH
# path-prepend /exp/dune/app/users/$USER/opt/lib64 LD_LIBRARY_PATH
# path-prepend /exp/dune/app/users/$USER/wct/cfg WIRECELL_PATH

source /nashome/y/yuhw/.bash_profile
export PS1=(app)$PS1

source /exp/dune/app/users/yuhw/wire-cell-python/venv/bin/activate

path-prepend /exp/dune/app/users/$USER/wire-cell-data WIRECELL_PATH
path-prepend /exp/dune/app/users/$USER/wire-cell-cfg WIRECELL_PATH
# path-prepend  /exp/dune/app/users/yuhw/wct/cfg WIRECELL_PATH

path-prepend /exp/dune/app/users/yuhw/dunereco/dunereco/DUNEWireCell/ FHICL_FILE_PATH
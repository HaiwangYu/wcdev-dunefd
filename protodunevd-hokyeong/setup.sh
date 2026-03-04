source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup dunesw v10_05_00d00 -q e26:prof

#############################################################################
# Build Wire-Cell
#############################################################################
local_wirecell_path=/exp/dune/app/users/$USER/opt
path-prepend ${local_wirecell_path}/bin PATH
path-prepend ${local_wirecell_path}/lib64 LD_LIBRARY_PATH

local_wirecell_path=/exp/dune/app/users/$USER/opt
path-prepend ${local_wirecell_path}/bin PATH
path-prepend ${local_wirecell_path}/lib64 LD_LIBRARY_PATH

path-prepend /exp/dune/data/users/hnam/wire-cell-hnam/larwc/wire-cell-cfg WIRECELL_PATH
path-prepend /exp/dune/app/users/yuhw/wcdev-dunefd/protodunevd-hokyeong/cfg WIRECELL_PATH

source /nashome/y/$USER/.bash_profile
export PS1=(app)$PS1

source /exp/dune/app/users/$USER/wire-cell-python/venv/bin/activate

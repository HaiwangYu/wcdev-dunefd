#!/bin/bash

name=$2
base_name="${name%.jsonnet}"


# Split $WIRECELL_PATH on colon into an array of directories
IFS=':' read -ra cfg_dirs <<< "$WIRECELL_PATH"

# Build the -J arguments from the array
J_ARGS=""
for (( idx=${#cfg_dirs[@]}-1; idx>=0; idx-- )); do
    J_ARGS="$J_ARGS -J ${cfg_dirs[$idx]}"
done
# Print the generated J_ARGS for debugging purposes
# echo "J_ARGS: $J_ARGS"

if [[ $1 == "json" || $1 == "all" ]]; then
    jsonnet \
        --ext-str files_fields="dunevd-resp-isoc3views-18d92.json.bz2" \
        --ext-str files_noise="dunevd10kt-1x6x6-3view30deg-noise-spectra-v1.json.bz2" \
        --ext-str files_wires="dunevd10kt_3view_30deg_v3_refactored_1x8x6ref.json.bz2" \
        --ext-code DL=4 \
        --ext-code DT=8.8 \
        --ext-code G4RefTime=0 \
        --ext-code Nbit=14 \
        --ext-code driftSpeed=1.60563 \
        --ext-code elecGain=14 \
        --ext-code lifetime=10 \
        --ext-code ncrm=48 \
        --ext-code nticks=8500 \
        --ext-code response_plane=1.892e1 \
        --ext-code use_dnnroi=false \
        --ext-code use_hydra=true \
        --ext-code save_rawdigits=false \
        $J_ARGS \
        ${base_name}.jsonnet \
        -o ${base_name}.json
fi

if [[ $1 == "pdf" || $1 == "all" ]]; then
    # wirecell-pgraph dotify --jpath -1 --no-services --no-params ${base_name}.json ${base_name}.pdf
    wirecell-pgraph dotify --jpath -1 ${3} ${base_name}.json ${base_name}.pdf
fi

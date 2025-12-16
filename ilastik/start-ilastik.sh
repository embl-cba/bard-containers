#!/bin/bash

ILASTIK_BIN="/opt/conda/envs/ilastik/bin/ilastik"   

if nvidia-smi -L 2>/dev/null |grep -q "GPU"; then
    echo "GPU detected, using VirtualGL"
    unset VOLUMINA_ENABLE_FALLBACK_VIEWPORTS
    exec vglrun "$ILASTIK_BIN" "$@"
else
    echo "No GPU detected, forcing CPU mode"
    export CUDA_VISIBLE_DEVICES=""
    export VOLUMINA_ENABLE_FALLBACK_VIEWPORTS=1
    exec "$ILASTIK_BIN" "$@"
fi

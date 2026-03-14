#!/bin/bash
# Example OpenFOAM simulation runner
# Note: Path to bashrc may vary by OpenFOAM version
if [ -f /opt/openfoam/etc/bashrc ]; then
    source /opt/openfoam/etc/bashrc
fi

cd /workspace/cases/cylinder 2>/dev/null || { echo "Case directory not found"; exit 1; }

blockMesh
decomposePar -force
mpirun -np 4 simpleFoam -parallel
reconstructPar
echo "Simulation complete"

#!/usr/bin/env python3
#SBATCH -J relax_surf_ads
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -p day-long-cpu
#SBATCH -t 1-00:00:00
#SBATCH -e %x.err
#SBATCH -o %x.out

from ase.io import read

from rmgcat_to_sella import adjacency_to_3d, create_relax_jobs

import os

slab     = read('{slabopt}')
slab.pbc = [True, True, False]
repeats  = {repeats}
pytemplate = '{pytemplate}'
adjacency_to_3d('{yamlfile}', slab, repeats, '{facetpath}')
create_relax_jobs('{facetpath}', pytemplate)

bashCommand = os.popen(
    "cd ./{facetpath}/minima/; for i in $(ls | grep py); do sbatch $i; done > ../../submitted_01.txt; cd ../../")
print(bashCommand.read())

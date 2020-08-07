#!/usr/bin/env python3

from rmgcat_to_sella.irc import IRC

slab             = '{slab}'
repeats          = {repeats}
facetpath        = '{facetpath}'
pytemplate_f     = '{pytemplate_f}'
pytemplate_r     = '{pytemplate_r}'
yamlfile         = '{yamlfile}'
ts_dir           = 'TS_estimate'
pseudopotentials = {pseudopotentials}
pseudo_dir       = '{pseudo_dir}'
executable       = {executable}
balsam_exe_settings = {balsam_exe_settings}
calc_keywords    = {calc_keywords}
workflow_name    = yamlfile+facetpath+'04'
dependency_workflow_name    = yamlfile+facetpath+'03'
creation_dir     = '{creation_dir}'

irc = IRC(facetpath, slab, repeats, ts_dir, yamlfile,
          pseudopotentials, pseudo_dir, QE_executable)
irc.set_up_irc(pytemplate_f, pytemplate_r)

from glob import glob
from pathlib import Path

from balsam.launcher.dag import BalsamJob
from balsam.core.models import ApplicationDefinition
myPython, created= ApplicationDefinition.objects.get_or_create(
            name="Python",
            executable="python3")
myPython.save()
cwd=Path.cwd().as_posix()
for py_script in glob('{facetpath}/IRC/*.py'):
    job_dir=Path.cwd().as_posix() + '/' + '/'.join(py_script.strip().split('/')[:-1])
    script_name=py_script.strip().split('/')[-1]
    job_to_add = BalsamJob(
            name=script_name,
            workflow=workflow_name,
            application=myPython.name,
            args=cwd+'/'+py_script,
            input_files='',
            user_workdir=job_dir,
            node_packing_count=64,
            ranks_per_node=1,
            )
    job_to_add.save()
    for job in pending_simulations:
        add_dependency(job, job_to_add) # parent, child


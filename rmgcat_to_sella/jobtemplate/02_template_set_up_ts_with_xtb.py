#!/usr/bin/env python3


import os
from pathlib import Path

from rmgcat_to_sella.ts import TS
from rmgcat_to_sella.io import IO

from balsam.launcher.dag import BalsamJob, add_dependency

slab = '{slab}'
repeats = {repeats}
yamlfile = '{yamlfile}'
facetpath = '{facetpath}'
rotAngle = {rotAngle}
scfactor = {scfactor}
scfactor_surface = {scfactor_surface}
pytemplate_xtb = '{pytemplate_xtb}'
species_list = {species_list}
current_dir = os.path.dirname(os.getcwd())
minima_dir = os.path.join(facetpath, 'minima')
scaled1 = {scaled1}
scaled2 = {scaled2}
ts_dir = 'TS_estimate'
creation_dir = '{creation_dir}'
rxn = {rxn}
rxn_name = '{rxn_name}'
cwd = Path.cwd().as_posix()
path_to_ts_estimate = os.path.join(facetpath, rxn_name, 'TS_estimate')

ts = TS(
    facetpath,
    slab, ts_dir,
    yamlfile,
    repeats,
    creation_dir)

ts.prepare_ts_estimate(
    rxn,
    scfactor,
    scfactor_surface,
    rotAngle,
    pytemplate_xtb,
    species_list,
    scaled1,
    scaled2)

dependancy_dict = IO().depends_on(facetpath, yamlfile)
jobs_to_be_finished = dependancy_dict[rxn_name]

dependency_workflow_name = yamlfile + facetpath + '01' + rxn_name
workflow_name = yamlfile + facetpath + '02' + rxn_name
dependent_workflow_name = yamlfile + facetpath + '03' + rxn_name

pending_simulations_dep = BalsamJob.objects.filter(
    workflow__contains=dependent_workflow_name
).exclude(state="JOB_FINISHED")

# for a given rxn_name, get all BalsamJob objects that it depends on
pending_simulations = []
for dep_job in jobs_to_be_finished:
    pending_simulations.append(BalsamJob.objects.filter(
        name=dep_job).exclude(state="JOB_FINISHED"))

# create BalsamJob objects
for py_script in Path(path_to_ts_estimate).glob('**/*.py'):
    job_dir, script_name = os.path.split(str(py_script))
    job_to_add = BalsamJob(
        name=script_name,
        workflow=workflow_name,
        application='python',
        args=cwd + '/' + str(py_script),
        input_files='',
        ranks_per_node=1,
        node_packing_count=48,
        user_workdir=job_dir,
    )
    job_to_add.save()

    # all job_to_add_ are childs of 01 job, as from jobs_to_be_finished
    # nested for loop becouse BalsamJob.objects.filter(name=dep_job) returns
    # django.query object for a single dep_job, e.g. (H_00_relax.py)
    # no nested loop required if workflow__contains=dependent_workflow_name
    for job in pending_simulations:
        for sub_job in job:
            add_dependency(sub_job, job_to_add)  # parent, child
    # do not run 03 until all 02 for a given reaction are done
    for job in pending_simulations_dep:
        add_dependency(job_to_add, job)  # parent, child

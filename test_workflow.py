"""
test_workflow.py
Mon May 27 10:32:50 CEST 2013
<mittner@uva.nl>

Generate some random data just testing whether the connections work.
"""
import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model generation
import nipype.algorithms.rapidart as ra      # artifact detection

import os, tempfile
import nibabel as nb
import numpy as np

from nipype_connect_str import nipype_connect_str

def gen_fakedata(tmpdir,codes):
    for code in codes:
        filename1 = os.path.join(tmpdir, 'fake%i_func.nii'%code)
        filename2 = os.path.join(tmpdir, 'fake%i_struct.nii'%code)
        nb.Nifti1Image(np.random.rand(10, 10, 10, 200), np.eye(4)).to_filename(filename1)
        nb.Nifti1Image(np.random.rand(10, 10, 10, 200), np.eye(4)).to_filename(filename2)

# fake data
tmpdir = tempfile.mkdtemp()
tmpdir="./tmp"
codes=[1,2]
gen_fakedata(tmpdir, codes)
print ">> tmpdir=", tmpdir

base_outdatadir=os.path.abspath(os.path.join(tmpdir, 'out'))
base_indatadir=os.path.abspath(tmpdir)

plot_graph=True
workflow_basedir=os.path.abspath(os.path.join(tmpdir, 'workflow_folders'))

# ------------------------------------------------------------------------
infosource = pe.Node(interface=util.IdentityInterface(fields=['code']),
                     name="infosource")
infosource.iterables = [('code', codes)]


# data-grabber
datasource = pe.Node(nio.DataGrabber(infields=['code'],
                             outfields=['func','struct']),
                             name = 'datasource')
datasource.inputs.base_directory = base_indatadir
datasource.inputs.template = '*'
datasource.inputs.field_template = dict(func='fake%i_func.nii',
                                struct='fake%i_struct.nii')
datasource.inputs.template_args=dict(func=[['code']], struct=[['code']])

# data-sink
datasink = pe.Node(nio.DataSink(), name='datasink')
datasink.inputs.base_directory = base_outdatadir

# create workflow object
wf = pe.Workflow(name="wf")
wf.base_dir = workflow_basedir

reg_func_struct = pe.Node(interface=fsl.FLIRT(out_matrix_file='func_to_struct.mat', no_resample=True),
                          name='reg_func_struct')


conn=nipype_connect_str("""
infosource(code) -> datasource(code|func) -> datasink(func);

datasource(func,struct)  -> reg_func_struct(in_file,reference | out_matrix_file,out_file)
                         -> datasink(matrix,registered)
""")
print conn
wf.connect(eval(conn))
wf.write_graph()
wf.run()

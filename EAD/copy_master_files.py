from aspace_prep.copy_eads import copy_eads
import os

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

vandura_base_dir = os.path.join(project_dir, 'vandura')
vandura_real_masters_all = os.path.join(vandura_base_dir, 'Real_Masters_all')
aspace_ead_dir = 'eads'

copy_eads(vandura_base_dir, aspace_ead_dir)
copy_eads(vandura_real_masters_all, aspace_ead_dir)
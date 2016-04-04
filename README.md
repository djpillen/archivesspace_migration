## MIGRATION RUNNING ORDER

# EAD
1. run_aspace_cleanup.py
2. Walker's [extent normalization](https://github.com/walkerdb/bentley_code/tree/master/normalization/aspaceify_extents)
3. copy_master_files.py
4. run_aspace_prep.py
5. Walker's [agent mapping](https://github.com/walkerdb/bentley_code/tree/master/mapping/aspace_agent_mapping)
6. run_aspace_preliminary_postings.py
7. Walker's [unitdate_unittitle_fix](https://github.com/walkerdb/bentley_code/tree/master/normalization/unitdates_in_unittitles)
8. run_unitdate_unittitle_post_fix.py
9. run_aspace_verification.py

# ACCESSIONS
1. Walker's donor mapping

# MARC
1. post_agents.py
2. post_subjects.py
3. add_subject_and_agent_uris.py

# EAD
1. run_aspace_ead_migration.py

# ACCESSIONS
1. Walker's accessions mapping
2. Walker's accessions posting

# MARC


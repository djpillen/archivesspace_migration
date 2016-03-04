from unitdate_unittitle_fix_post.capitalize_unittitles import capitalize_unittitles
from unitdate_unittitle_fix_post.deduplicate_dates import remove_duplicate_unitdates
from unitdate_unittitle_fix_post.deduplicate_dates import consolidate_duplicate_data

def run_unitdate_unittitle_fix_post(ead_dir):
	capitalize_unittitles(ead_dir)
	remove_duplicate_unitdates(ead_dir)
	consolidate_duplicate_data(ead_dir)

def main():
	ead_dir = 'eads'
	run_unitdate_unittitle_fix_post(ead_dir)

if __name__ == "__main__":
	main()
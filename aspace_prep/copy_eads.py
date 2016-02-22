import os
from os.path import join
import shutil

def copy_eads(src_dir, dst_dir):
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	for filename in os.listdir(src_dir):
		print "Copying {0} to {1}".format(filename, dst_dir)
		src_file = join(src_dir,filename)
		shutil.copy(src_file,dst_dir)

def main():
	src_dir = 'C:/Users/djpillen/GitHub/vandura/Real_Masters_all'
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	dst_dir = join(project_dir, 'eads')
	copy_eads(src_dir,dst_dir)

if __name__ == "__main__":
	main()
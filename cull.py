import sys, os
import subprocess
import random
import argparse

from os.path import join, isdir, exists, isfile, basename

SIGNALS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", 
"Eight", "Nine", "Ten", "You", "Me", "Ok", "Swim", "Stop", "Up", "Down", 
"Level Off", "Left", "Right", "Line", "Come Here", "Follow", "Look", "Take Picture",
"Take Movie", "Trouble", "All Done", "Together", "Off Hand", "Idle", "Head"]

def label_name(xmlpath):
	return "".join(basename(xmlpath).split(".")[:-1]) + ".txt"

def image_name(xmlpath):
	return "".join(basename(xmlpath).split(".")[:-1]) + ".jpg"

def cull_label(directory, label, limit=2000):
	# Compute paths to images and annotations within dataset directory
	image_dir = join(directory, "images")
	xmls_dir = join(directory, "annotations/xmls")
	labels_dir = join(directory, "labels")
	
	# Find all xml annotations containing the label to be culled
	result = subprocess.run(['grep', '-lr', xmls_dir, '-e', label], stdout=subprocess.PIPE)
	
	# Decode bytearray as string and split line to isolate file path
	files = [f for f in result.stdout.decode('utf-8').split('\n')]
	
	print("There are %s xmls with the label %s" % (len(files), label))
	
	if limit == 0:
		return
	
	print("Randomly removing %s of them" % max(0, len(files) - limit))
	
	# Randomly shuffle file paths 
	random.shuffle(files)
	
	# Remove xml annotation and corresponding image file
	for file in files[:max(0, len(files) - limit)]:
		if file == '':
			print("Empty file")
			continue
		#print("REMOVE: %s" % file)
		#print("REMOVE: %s" % join(image_dir, image_name(file)))
		#print("REMOVE: %s" % join(labels_dir, label_name(file)))
		if not exists(join(image_dir, image_name(file))):
			print("ERROR: %s does not exist " % join(image_dir, image_name(file)))
		if not exists(join(labels_dir, label_name(file))):
			print("ERROR: %s does not exist " % join(labels_dir, label_name(file)))
		os.remove(file)
		os.remove(join(image_dir, image_name(file)))
		os.remove(join(labels_dir, label_name(file)))
		pass
	pass

def main(args):
	directory = args.dataset_dir		# Path to dataset directory to be culled
	limit = args.limit		# Number of labels to be left after cull
	idle_limit = args.idle_limit

	# Check if intended dataset directory exists
	if not exists(directory):
		print("Error: directory %s does not exist" % directory)
		sys.exit(1)
		return
	
	# Cull all labels
	for label in SIGNALS:
		if label == "Off Hand":
			continue
		if label == "Head":
			continue
		if label == "Idle":
			cull_label(directory, label, 0 if limit == 0 else idle_limit)
			continue
		cull_label(directory, label, limit)
		pass
		
	pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('limit', type=int, help="Maximum number of class labels to retain (if Zero dont cull just count)")
	parser.add_argument('--dataset_dir', type=str, default="./", help="Directory where annotations and images folders were created")
	parser.add_argument('--idle_limit', type=int, default=5000, help="Maximum number of idle labels to retain")
	args = parser.parse_args()
	main(args)

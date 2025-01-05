import sys, os
import argparse

from os import listdir, remove
from os.path import isfile, join, isdir, basename

import subprocess

SIGNALS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", 
"Eight", "Nine", "Ten", "You", "Me", "Ok", "Swim", "Stop", "Up", "Down", 
"Level Off", "Left", "Right", "Line", "Come Here", "Follow", "Look", "Take Picture",
"Take Movie", "Trouble", "All Done", "Together", "Off Hand", "Idle", "Head"]

import random
import numpy as np

def image_name(xmlpath):
	result = "".join(basename(xmlpath).split(".")[:-1]) + ".jpg"
	return result

def split_three(lst, ratio=[0.8, 0.1, 0.1]):
	train_r, val_r, test_r = ratio
	assert(np.sum(ratio) == 1.0)  # makes sure the splits make sense
	# note we only need to give the first 2 indices to split, the last one it returns the rest of the list or empty
	indicies_for_splitting = [int(len(lst) * train_r), int(len(lst) * (train_r+val_r))]
	train, val, test = np.split(lst, indicies_for_splitting)
	return train, val, test

def writelist(name, list, pathprefix):
	file = open(name, 'w')
	for line in list:
		print(line)
		file.write(join(pathprefix, line)+"\n")
		pass
	file.close()
	pass

def split_label(label, folder, ratios, seed):
	image_dir = join(folder, "images")
	xmls_dir = join(folder, "annotations/xmls")
	
	modified_label = "<name>%s</name>" % label
	
	# Find all xml annotations containing the label to be split
	result = subprocess.run(['grep', '-lr', xmls_dir, '-e', modified_label], stdout=subprocess.PIPE)
	
	img_files = [join(image_dir, image_name(f)) for f in result.stdout.decode('utf-8').split('\n') if image_name(f) != ".jpg"]
	
	print("Label: %s - %d" % (label, len(img_files)))
	
	random.Random(seed).shuffle(img_files)
	
	return split_three(img_files, ratios)

def main(args):
	seed = 12345
	ratios = [args.train_ratio, args.val_ratio, args.test_ratio]
	folder = args.dataset_dir

	train, val, test = [], [], []

	for label in SIGNALS:
		if label == "Off Hand":
			continue
		if label == "Head":
			continue
		t, v, tst = split_label(label, folder, ratios, seed)
		
		print("%s: %s train - %s val - %s test" % (label, len(t.tolist()), len(v.tolist()), len(tst.tolist()) ))
		train += t.tolist()
		val += v.tolist()
		test += tst.tolist()
		pass
	
	writelist(join(folder, "train.txt"), train, "")
	writelist(join(folder, "validate.txt"), val, "")
	writelist(join(folder, "test.txt"), test, "")
	pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--dataset_dir', type=str, default="./", help="Directory where annotations and images folders were created")
	parser.add_argument('--train_ratio', type=float, default=0.7, help="Percentage of data to use as a training set")
	parser.add_argument('--val_ratio', type=float, default=0.15, help="Percentage of data to use as a validation set")
	parser.add_argument('--test_ratio', type=float, default=0.15, help="Percentage of data to use as a testing set")
	args = parser.parse_args()
	main(args)

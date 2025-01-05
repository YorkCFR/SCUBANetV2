from xml.dom import minidom
import sys
import argparse
import yaml

import os
import os.path

SIGNALS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", 
"Eight", "Nine", "Ten", "You", "Me", "Ok", "Swim", "Stop", "Up", "Down", 
"Level Off", "Left", "Right", "Line", "Come Here", "Follow", "Look", "Take Picture",
"Take Movie", "Trouble", "All Done", "Together", "Off Hand", "Idle", "Head"]

def parseFilename(filename, dict):
	for el in filename:
		if el.nodeName == "#text":
			dict['filename'] = el.nodeValue
		pass
	pass

def parseValue(element, val, dict):
	for el in element.childNodes:
		if el.nodeName == "#text":
			dict[val] = el.nodeValue
		pass
	pass

def parseSize(size, dict):
	for el in size:
		if el.nodeName == "width":
			parseValue(el, "width", dict)
		elif el.nodeName == "height":
			parseValue(el, "height", dict)
		pass
	pass

def parseBndbox(bndbox, dict):
	for el in bndbox.childNodes:
		if el.nodeName == "xmin":
			parseValue(el, "xmin", dict)
		if el.nodeName == "xmax":
			parseValue(el, "xmax", dict)
		if el.nodeName == "ymin":
			parseValue(el, "ymin", dict)
		if el.nodeName == "ymax":
			parseValue(el, "ymax", dict)
		pass
	pass

def parseObject(object, dict):
	tmp = {}
	for el in object:
		if el.nodeName == "bndbox":
			parseBndbox(el, tmp)
		elif el.nodeName == "name":
			parseValue(el, "name", tmp)
		pass
	z = dict['objects']
	z.append(tmp)
	dict['objects'] = z
	pass

def parse(annotation, dict):
	for el in annotation.childNodes:
		if el.nodeName == "object":
			parseObject(el.childNodes, dict)
		elif el.nodeName == "size":
			parseSize(el.childNodes, dict)
		elif el.nodeName == "filename":
			parseFilename(el.childNodes, dict)
		pass
	pass

def parseXML(path, labels_dir, config):
	dat = minidom.parse(path)
	dict = {'objects': []}

	parse(dat.getElementsByTagName('annotation')[0], dict)
	filename = os.path.join(labels_dir, dict['filename'][:-3] + "txt")
	
	dataset_cfg = yaml.safe_load(open(config, "r"))
	
	yolo_id = { key : idx for idx, key in enumerate(dataset_cfg["names"]) }
	
	width = float(dict['width'])
	height = float(dict['height'])

	with open(filename, "w") as fd:
		for o in dict['objects']:
			#print(o['name'])
			xmin = int(o['xmin']) / width
			xmax = int(o['xmax']) / width
			ymin = int(o['ymin']) / height
			ymax = int(o['ymax']) / height
			fd.write(f"{yolo_id[o['name']]} {(xmin+xmax)/2} {(ymin+ymax)/2} {xmax-xmin} {ymax-ymin}\n")
			pass
		pass
	pass

def main(args):
	
	if not os.path.exists(args.dataset_dir):
		print("ERROR: %s does not exists" % args.dataset_dir)
		sys.exit(1)
		pass
	
	annotation_dir = os.path.join(args.dataset_dir, "annotations")
	labels_dir = os.path.join(args.dataset_dir, "labels")
	xmls_dir = os.path.join(annotation_dir, "xmls")
	
	if not os.path.exists(xmls_dir):
		print("ERROR: Cannot find xml annotations directory")
		sys.exit(1)
		pass
	
	if not os.path.exists(labels_dir):
		print(labels_dir)
		os.mkdir(labels_dir)
		pass
	
	for filename in os.listdir(xmls_dir):
		if not filename.endswith("xml"):
			continue
		parseXML(os.path.join(xmls_dir, filename), labels_dir, args.dataset_yaml)
		pass
	pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--dataset_yaml', type=str, default="./scubanetv2.yaml", help="YAML description of YOLO dataset")
	parser.add_argument('--dataset_dir', type=str, default="./", help="Pascal VOC directory (annotations and images folders)")
	args = parser.parse_args()
	main(args)

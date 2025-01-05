import sys, os, json, cv2
from os.path import join, isdir, isfile, exists, basename
from ultralytics import YOLO

import argparse

SIGNALS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", 
"Eight", "Nine", "Ten", "You", "Me", "Ok", "Swim", "Stop", "Up", "Down", 
"Level Off", "Left", "Right", "Line", "Come Here", "Follow", "Look", "Take Picture",
"Take Movie", "Trouble", "All Done", "Together", "Off Hand", "Idle"]

class Rectangle:

	__slots__ = '__x1', '__y1', '__x2', '__y2'
	
	def __init__(self, x1, y1, x2, y2):
		self.__setstate__((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
		pass
	
	def __repr__(self):
		return '{}({})'.format(type(self).__name__, ', '.join(map(repr, self)))
	
	def __eq__(self, other):
		return self.data == other.data
	
	def __ne__(self, other):
		return self.data != other.data
	
	def __hash__(self):
		return hash(self.data)
	
	def __len__(self):
		return 4
	
	def __getitem__(self, key):
		return self.data[key]
	
	def __iter__(self):
		return iter(self.data)

	def __and__(self, other):
		a, b = self, other
		x1 = max(min(a.x1, a.x2), min(b.x1, b.x2))
		y1 = max(min(a.y1, a.y2), min(b.y1, b.y2))
		x2 = min(max(a.x1, a.x2), max(b.x1, b.x2))
		y2 = min(max(a.y1, a.y2), max(b.y1, b.y2))
		if x1<x2 and y1<y2:
			return type(self)(x1, y1, x2, y2)

	def __sub__(self, other):
		intersection = self & other
		if intersection is None:
			yield self
		else:
			x, y = {self.x1, self.x2}, {self.y1, self.y2}
			if self.x1 < other.x1 < self.x2:
				x.add(other.x1)
			if self.y1 < other.y1 < self.y2:
				y.add(other.y1)
			if self.x1 < other.x2 < self.x2:
				x.add(other.x2)
			if self.y1 < other.y2 < self.y2:
				y.add(other.y2)
			for (x1, x2), (y1, y2) in product(pairwise(sorted(x)), pairwise(sorted(y))):
				instance = type(self)(x1, y1, x2, y2)
				if instance != intersection:
					yield instance
				pass
			pass
		pass

	def __getstate__(self):
		return self.x1, self.y1, self.x2, self.y2
	
	def __setstate__(self, state):
		self.__x1, self.__y1, self.__x2, self.__y2 = state
		pass
	
	@property
	def x1(self):
		return self.__x1
	
	@property
	def y1(self):
		return self.__y1
	
	@property
	def x2(self):
		return self.__x2
	
	@property
	def y2(self):
		return self.__y2
	
	@property
	def width(self):
		return self.x2 - self.x1
	
	@property
	def height(self):
		return self.y2 - self.y1
		
	@property
	def area(self):
		return (self.x2 - self.x1) * (self.y2 - self.y1)
	
	intersection = __and__
	
	difference = __sub__
	
	data = property(__getstate__)


def create_label_map(path):
	file = open(join(path, "label_map.pbtxt"), "w")
	for i, sign in enumerate(SIGNALS):
		file.write("item {\n\tid : %i,\n\tname : '%s'\n}\n" % (i+1, sign))
		pass
	file.close()
	pass

def create_directory_tree(name="ScubaNet2"):
	
	#if exists(name):
	#	print("ERROR: %s already exists" % name)
	#	sys.exit(1)
	#	pass

	image_dir = join(name, "images")
	annotation_dir = join(name, "annotations")
	xmls_dir = join(annotation_dir, "xmls")
	
	#os.mkdir(name)
	if not exists(image_dir):
		os.mkdir(image_dir)
	if not exists(annotation_dir):
		os.mkdir(annotation_dir)
	if not exists(xmls_dir):
		os.mkdir(xmls_dir)

	create_label_map(annotation_dir)
	
	return image_dir, annotation_dir, xmls_dir

def json_files(directory):
	files = os.listdir(directory)
	files.sort()
	for file in files:
		if file.endswith(".json"):
			yield join(directory, file)
		pass
	pass

def process_video(json, image_dir):
	cap = cv2.VideoCapture(join(json["directory"], json["file_name"]))
	if cap is None:
		print("ERROR: can't open file %s" % file)
		return
	
	new_images = []
	for i, label in enumerate(json["labels"]):
		ret, frame =  cap.read()
		if frame is None:
			break
		if label["label"] is None:
			continue
		
		image_name = "%s-%i.jpg" % (os.path.splitext(json["file_name"])[0], i)
		image_path = join(image_dir, image_name)
		print("Writing image %s" % image_name)
		
		#frame = cv2.resize(frame, (1024, 576))
		
		new_images.append(image_path)
		cv2.imwrite(image_path, frame)
		pass
	return new_images

def write_annotation(image, objects, labels, xmls_path):
	xml_name = os.path.splitext(image)[0] + ".xml"
	
	file = open(join(xmls_path, xml_name), "w")
	file.write('<?xml version="1.0" ?>\n')
	file.write("<annotation>\n")
	file.write("\t<segmented>0</segmented>\n")
	file.write("\t<folder>less_selected</folder>\n")
	
	file.write("\t<size>\n")
	file.write("\t\t<width>1920</width>\n")
	file.write("\t\t<height>1080</height>\n")
	file.write("\t</size>\n")
	
	for label, (xmin, ymin, xmax, ymax) in zip(labels, objects):
		file.write("\t<object>\n")
		file.write("\t\t<bndbox>\n")
		file.write("\t\t\t<xmin>%i</xmin>>\n" % xmin)
		file.write("\t\t\t<ymin>%i</ymin>>\n" % ymin)
		file.write("\t\t\t<xmax>%i</xmax>>\n" % xmax)
		file.write("\t\t\t<ymax>%i</ymax>>\n" % ymax)
		file.write("\t\t</bndbox>\n")
		file.write("\t\t<difficult>0</difficult>\n")
		file.write("\t\t<pose>Unspecified</pose>\n")
		file.write("\t\t<name>%s</name>\n" % label)
		file.write("\t\t<truncated>0</truncated>\n")
		file.write("\t</object>\n")
		pass
		
	file.write("\t<filename>%s</filename>\n" % image)
	file.write("</annotation>\n")
	file.close()
	pass

def apply_hueristics(label, hands, head):
	
	union = lambda a, b: [min(a[0],b[0]), min(a[1],b[1]), max(a[2],b[2]), max(a[3],b[3])]
	
	expand = lambda b, p: [b[0] - p*(b[2]-b[0]), b[1] - p*(b[3]-b[1]), b[2] + p*(b[2]-b[0]), b[3] + p*(b[3]-b[1])]
	
	expand_dir = lambda b, p, d: [b[0] - (p*(b[2]-b[0]) if d == "LEFT" else 0),
									b[1] - (p*(b[3]-b[1]) if d == "UP" else 0),
									b[2] + (p*(b[2]-b[0]) if d == "RIGHT" else 0),
									b[3] + (p*(b[3]-b[1])if d == "DOWN" else 0)]
	
	#hands = [expand(box, 0.10) for box in hands]
	
	handedness = "RIGHT"
	if len(hands) > 1:
		handedness = "RIGHT" if (hands[0][0]+hands[0][2])/2 <= (hands[1][0]+hands[1][2])/2 else "LEFT"
		pass
	else:
		handedness = "RIGHT" if (hands[0][0]+hands[0][2])/2 <= 512 else "LEFT"
		pass
	
	if label == "Idle":
		return hands + head, len(hands) * ["Idle"] + len(head) * ["Head"]
	
	if label in ["One", "Two", "Three", "Four", "Five"]:
		return [expand_dir(hands[0], 0.15, "UP")] + hands[1:] + head, [label] + len(hands[1:]) * ["Off Hand"] + len(head) * ["Head"]
	
	if label in ["Six", "Seven", "Eight", "Nine", "Ten"]:
		return [expand_dir(hands[0], 0.15, handedness)] + hands[1:] + head, [label] + len(hands[1:]) * ["Off Hand"] + len(head) * ["Head"]
	
	if label in ["Follow", "Together", "Take Movie"]:
		return [union(hands[0], hands[1])] if len(hands) > 1 else [expand(hands[0], 0.1)], [label] + len(head) * ["Head"]
	
	if label == "Look" and len(head) == 1:
		return [union(hands[0], head[0])] + hands[1:] + head , [label] + len(hands[1:]) * ["Off Hand"] + len(head) * ["Head"]
	
	return hands + head, [label] + len(hands[1:]) * ["Off Hand"] + len(head) * ["Head"]

def remove_overlap(hands, head):
	rect_head = Rectangle(head.xyxy[0][0], head.xyxy[0][1], head.xyxy[0][2], head.xyxy[0][3])
	save = []
	for i, hand_one in enumerate(hands):
		rect_one = Rectangle(hand_one.xyxy[0][0], hand_one.xyxy[0][1], hand_one.xyxy[0][2], hand_one.xyxy[0][3])
		sentinel = True
		for hand_two in [hand for j, hand in enumerate(hands) if i != j]:
			rect_two = Rectangle(hand_two.xyxy[0][0], hand_two.xyxy[0][1], hand_two.xyxy[0][2], hand_two.xyxy[0][3])
			intersect = rect_one & rect_two
			if intersect is not None and intersect.area > 25:
				if rect_one.area > rect_two.area or rect_one.area < 0.66*rect_head.area :
					sentinel = False
					pass
				pass
			pass
		pass
		if sentinel:
			save.append(hand_one)
	return save

DIVER_CLS = 1
HEAD_CLS = 0
HAND_CLS = 2
HAND_CONF_THRESHOLD = .85

def process_image(model, image, labels, xmls_dir):
	results = model(image)
	
	# Extract only detected Hands with high confidence
	hands = []
	heads = []
	divers = []
	for result in results:
		print("Found %s objects" % (len(result.boxes)))
		for box in result.boxes:
			if box.cls.item() == DIVER_CLS:
				divers.append(box)
				pass
			if box.cls.item() == HEAD_CLS:
				heads.append(box)
				pass
			elif box.cls.item() == HAND_CLS:
				hands.append(box)
				pass
		pass
	
	if len(divers) > 1:
		print("Image %s has multiple detected divers" % basename(image))
		return False
	
	heads.sort(key=lambda x: x.conf.item(), reverse=True)
	#heads = remove_overlap(heads)

	# Keep max one head
	if len(heads) > 1:
		heads = heads[1:]
		pass
	
	if len(heads) < 1:
		print("Image %s has no detected heads" % basename(image))
		return False
	
	print("Found %s hands" % len(hands))
	
	# Sort Hands by confidence values
	hands.sort(key=lambda x: x.conf.item(), reverse=True)
	hands = remove_overlap(hands, heads[0])
	
	# Keep max two hands
	if len(hands) > 2:
		hands = hands[:2]
		pass
	
	if len(hands) < 1:
		print("Image %s has no detected hands" % basename(image))
		return False
	
	# Sort Hands by height in frame
	hands.sort(key=lambda x: (x.xyxy[0][1] + x.xyxy[0][3])/2, reverse=False)
	
	hand_boxes = []
	for h in hands:
		hand_boxes.append([x.item() for x in h.xyxy[0]])
		pass
	
	head_boxes = []
	for h in heads:
		head_boxes.append([x.item() for x in h.xyxy[0]])
		pass
	
	index = int(basename(image).split('-')[-1].split('.')[0])
	
	gestures, annotations = apply_hueristics(labels[index]["label"], hand_boxes, head_boxes)
	
	if len(gestures) == 0 or len(annotations) == 0:
		return False
	
	write_annotation(basename(image), gestures, annotations, xmls_dir)
	
	return True

#
# Hasn't been tested after rejigging for YOLO
#
#
def main(args):
	dataset_name = args.dataset_name # Name of the directory to store the data
	labels_dir = args.weak_data # Path to the directory where videos and annotations are stored
	model_path = args.model_path # Path to the trained YOLO model 
	
	if not exists(model_path):
		print("ERROR: model %s does not exists")
		sys.exit(1)

	if not isdir(labels_dir):
		print("ERROR: %s is not a directory")
		sys.exit(1)
	
	model = YOLO(model_path)
	
	# Create a PASCAL VOC directory structure
	image_dir, _, xmls_dir = create_directory_tree(dataset_name)
	
	# Process json anotation files sequentially
	for jsonfile in json_files(labels_dir):
		data = None
		with open(jsonfile, "r") as fobj:
			print(jsonfile)
			data = json.load(fobj)
			data['directory'] = labels_dir
			pass
		
		# Extract all labelled images from the video associated with this json file 
		new_images = process_video(data, image_dir)
		
		for image in new_images:
			if not process_image(model, image, data["labels"], xmls_dir):
				print("Removing unlabelled image %s" % image)
				os.remove(image)
				pass
			pass
		pass
	pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('model_path', type=str, help="Path to ScubaNetV1+ YOLO model")
	parser.add_argument('--dataset_name', type=str, default=".", help="Directory to place the new weakly supervised label")
	parser.add_argument('--weak_data', type=str, default="./gestures", help="Directory where the videos and per frame gesture classifications are stored")
	args = parser.parse_args()
	main(args)


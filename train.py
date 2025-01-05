import sys
import os
import os.path
import json
import argparse

from ultralytics import YOLO


def train(args):
	model = YOLO(args.yolo_model)

	kwargs = {
		"data" : os.path.join(os.getcwd(), args.yaml_file),
		"epochs" : 1,
		"batch" : -1 
	}

	if args.cfg_file is not None:
		cfg = json.load(open(args.cfg_file, "r"))
		kwargs.update(cfg)
		pass

	model.train(**kwargs)
	success = model.export(format="onnx")  # export the model to ONNX format
	pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('yaml_file', type=str, help="dataset description file")
	parser.add_argument('--yolo_model', type=str, default="yolov8m.pt", help="YOLO version to train")
	parser.add_argument('--cfg_file', type=str, help="YOLO hyperparameters configuration")
	args = parser.parse_args()
	train(args)

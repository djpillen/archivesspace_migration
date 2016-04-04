from lxml import etree
import os
from os.path import join

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ead_dir = join(project_dir, 'converted_eads')

container_labels = []
container_label_to_type_dict = {"Box":"box", "Folder":"folder", "Box out.":"box", "Vol.":"volume", "Video Box":"box",
								"CD Box":"box", "Sd Rec Box":"box", "Sound Rec":"??", "Vol. out.":"volume",
								"Folder out.":"folder", "Bundle":"bundle", "Print":"print", "DVD Box":"box",
								"P-DVD Box":"box" ,"Tubes":"tube","Framed Art":"art","Film":"film",
								"Phonograph record":"record","Drawer":"map-case","Photo over":"photo",
								"Sculpture":"sculpture", "Realia":"realia","Microfilm":"reel","Microfilm C":"reel",
								"Microfilm B":"reel", "Box P":"box", "Box  P":"box"}
								
container_label_to_label_dict = {"Box out.":"Oversize Box","Vol.":"Volume", "Vol. out.":"Oversize Volume",
								"Folder out.":"Oversize Folder","P-DVD Box":"DVD Box","Box  P":"Box P"}

for filename in os.listdir(ead_dir):
	print "Adding container types to {}".format(filename)
	tree = etree.parse(join(ead_dir, filename))
	containers = tree.xpath("//container")
	for container in containers:
		label = container.attrib["label"]
		if label in container_label_to_type_dict:
			container.attrib["type"] = container_label_to_type_dict[label]
		else:
			container.attrib["type"] = label.lower()
		if label in container_label_to_label_dict:
			container.attrib["label"] = container_label_to_label_dict[label]
		if len(label) == 0:
			container.attrib["label"] = "unknown"
			container.attrib["type"] = "unknown"

	with open(join(ead_dir, filename), 'w') as f:
		f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))

"""
for filename in os.listdir(ead_dir):
	print filename
	tree = etree.parse(join(ead_dir, filename))
	containers = tree.xpath("//container")
	for container in containers:
		container_label = container.attrib["label"]
		if container_label not in container_labels:
			container_labels.append(container_label)

for label in container_labels:
	print label
"""

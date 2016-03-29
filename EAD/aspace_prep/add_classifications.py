from lxml import etree
import os
from os.path import join

def add_classifications(ead_dir):
	classification_base = '/repositories/2/classifications/'
	mhc_classification = classification_base + '1'
	uarp_classification = classification_base + '2'

	for filename in os.listdir(ead_dir):
		print "Adding classifications to {0}".format(filename)
		tree = etree.parse(join(ead_dir,filename))
		eadheader = tree.xpath('//eadheader')[0]
		publisher = tree.xpath('//titlepage/publisher')[0]
		classifications = tree.xpath('//classification')
		classification_id = False
		if 'Michigan Historical Collections' in etree.tostring(publisher):
			classification_id = mhc_classification
		elif 'University Archives' in etree.tostring(publisher):
			classification_id = uarp_classification
		if classification_id and not classifications:
			classification = etree.Element('classification')
			classification.attrib['ref'] = classification_id
			eadheader.append(classification)

		with open(join(ead_dir,filename),'w') as ead_out:
			ead_out.write(etree.tostring(tree,encoding='utf-8',xml_declaration=True,pretty_print=True))

def main():
	project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	aspace_ead_dir = join(project_dir, 'eads')
	add_classifications(aspace_ead_dir)

if __name__ == "__main__":
	main()
from lxml import etree
import os
from os.path import join

converted_eads = "converted_eads"

for filename in os.listdir(converted_eads):
	print filename
	tree = etree.parse(join(converted_eads, filename))
	odds = tree.xpath("//odd")
	for odd in odds:
		p = odd.xpath("./p")
		note_text = p[0].text.strip()
		if "donor" in note_text.lower():
			acqinfo = etree.Element("acqinfo")
			acqinfo.text = note_text
			odd_parent = odd.getparent()
			odd_parent.insert(odd_parent.index(odd)+1, acqinfo)
			odd_parent.remove(odd)
	with open(join(converted_eads, filename), 'w') as f:
		f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))

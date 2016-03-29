from lxml.builder import E
from lxml import etree
import os
from os.path import join

def identify_main_record(marcxml_records):
	# Use some combination of looking for LKR and 580 fields to find the "main record"
	pass

def make_eadheader(marcxml_record):
	pass

def make_filedesc(marcxml_record):
	pass

def make_profiledesc(marcxml_record):
	pass

def make_archdesc(marcxml_record):
	pass

def make_unitid(marcxml_record):
	pass

def make_langmaterial(marcxml_record):
	pass

def make_unitdates(marcxml_record):
	# Return a list of unitdates
	# Parse like "for unitdate in unitdate: unitdate"
	# Look in both 245 and 260 fields
	pass

def make_unitdate(marcxml_record, type):
	pass

def make_unittitle(marcxml_record):
	pass

def make_origination(marcxml_record):
	pass

def make_physdesc(marcxml_record):
	pass

def make_extent(marcxml_record):
	pass

def make_physfacet(marcxml_record):
	pass

def make_dimensions(marcxml_record):
	pass

def make_phystech(marcxml_record):
	pass

def make_descgrp(marcxml_record):
	pass

def make_altformavail(marcxml_record):
	pass

def make_originalsloc(marcxml_record):
	pass

def make_relatedmaterial(marcxml_record):
	pass

def make_custodhist(marcxml_record):
	pass

def make_accessrestrict(marcxml_record):
	pass

def make_userestrict(marcxml_record):
	pass

def make_acqinfo(marcxml_record):
	pass

def make_accruals(marcxml_record):
	pass

def make_bioghist(marcxml_record):
	pass

def make_scopecontent(marcxml_record):
	pass

def make_arrangement(marcxml_record):
	pass

def make_odds(marcxml_record):
	pass

def make_odd(label, text):
	pass

def make_controlaccess(marcxml_records):
	pass

def make_subject(source, tag):
	pass

def make_geogname(source, tag):
	pass

def make_title(source, tag):
	pass

def make_genreform(source, tag):
	pass

def make_persname(source, tag):
	pass

def make_corpname(source, tag):
	pass

def make_famname(source, tag):
	pass

def make_dsc(main_record, other_records):
	pass

def make_series(marcxml_record):
	pass

def make_ead_with_series(marcxml_records):
	main_record = identify_main_record(marcxml_records)
	if main_record:
		other_records = [record for record in marcxml_records if record not main_record]
		ead = E.ead(
			make_eadheader(main_record),
			make_archdesc(main_record),
			make_descgrp(main_record),
			make_controlaccess(main_record),
			make_dsc(main_record, other_records)
			)

		return ead

	else:
		return False

def make_ead_without_series(marcxml_record):
	ead = E.ead(
		make_eadheader(marcxml_record),
		make_archdesc(marcxml_record),
		make_descgrp(marcxml_record),
		make_controlaccess(marcxml_record)
		)

	return ead
	"""
	ead = E.ead(
		E.eadheader(
			E.filedesc(
				E.titlestmt(
					E.titleproper("Finding aid for the --"),
					E.author("Finding aid by --"),
					E.sponsor("Sponsored by --")
					)
				),
			E.profiledesc(
				E.creation("Encoded finding aid created by Dallas Pillen ", E.date("2016")),
				E.langusage("The finding aid is written in ",E.language("English")),
				E.descrules("Finding aid prepared using --")
				)
			),
		E.archdesc("", {"level":"collection"},
			E.did(
				E.origination(
					E.persname("so and so")
					),
				E.unittitle("unittitle"),
				E.unitdate("unitdate"),
				E.physdesc(
					E.extent("extent"),
					E.physfacet("physfacet"),
					E.dimensions("dimensions")
				),
				E.unitid("callnumber"),
				E.langmaterial("The material is in --")
			),
			E.descgrp("", {"type":"admin"})
		)
	)
	"""

def convert_marcxml_to_ead(marcxml_dir, ead_dir):
	for filename in os.listdir(marcxml_dir):
		print "Converting {} to EAD".format(filename)
		tree = etree.parse(join(marcxml_dir,filename))
		ns = {'marc': 'http://www.loc.gov/MARC21/slim'}
		records = tree.xpath('//marc:record', namespaces=ns)
		unconverted = []
		if len(records) > 1:
			# Make an EAD with series
			ead = make_ead_with_series(records)
			if ead:
				# A main record has been identified
				pass
			else:
				# No main record identified
				pass
				"No main record identified for {}".format(filename)
				unconverted.append(filename)
		else:
			# Make only a collection level EAD
			record = records[0]
			ead = make_ead_without_series(record)

		with open(join(ead_dir, filename),'w') as f:
			f.write(etree.tostring(ead,encoding="utf-8",xml_declaration=True,pretty_print=True))

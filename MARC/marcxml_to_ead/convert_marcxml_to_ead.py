from lxml.builder import E
from lxml import etree
import os
from os.path import join
import uuid

ns = {'marc': 'http://www.loc.gov/MARC21/slim'}

def identify_main_record(records):
	# Use some combination of looking for LKR and 580 fields to find the "main record"
	pass

def make_eadheader(record):
	eadheader = E.header(
		make_filedesc(record),
		make_profiledesc(record)
		)

	return eadheader

def make_filedesc(record):
	filedesc = E.filedesc(
		E.titlestmt(
			make_titleproper(record),
			make_sponsor(record)
			)
		)

	return filedesc

def make_titleproper(record):
	titleproper = "Finding aid for the {}".format(extract_collection_title(record))

	return E.titleproper(titleproper)

def make_sponsor(record):
	sponsor = record.xpath("./marc:datafield[@tag='536']/marc:subfield[@code='a']", namespaces=ns)

	if sponsor:
		return E.sponsor(sponsor[0].text.strip().encode("utf-8"))
	else:
		return ""

def make_profiledesc(record):
	profiledesc = E.profiledesc(
		E.creation("Encoded finding aid created from MARC record by Dallas Pillen"),
		E.langusage("The finding aid is written in ", E.language({"langcode":"eng"},"English")),
		make_descrules(record)
		)

	return profiledesc

def make_descrules(record):
	descrules = record.xpath("./marc:datafield[@tag='040']/marc:subfield[@code='e']", namespaces=ns)

	if descrules:
		return E.descrules(descrules[0].text.strip().encode('utf-8'))
	else:
		return ""

def make_archdesc(record):
	archdesc = E.archdesc({"level":"collection"},
		make_collection_did(record),
		make_descgrp(record),
		make_bioghist(record),
		make_arrangement(record),
		make_scopecontent(record),
		make_controlaccess(record)
		)

	return archdesc

def make_collection_did(record):
	did = E.did(
		make_unitid(record),
		make_origination(record),
		make_unittitle(record),
		make_langmaterial(record),
		)

	unitdates = make_unitdates(record)
	for unitdate in unitdates:
		did.append(unitdate)

	physdescs = make_physdescs(record)
	for physdesc in physdescs:
		did.append(physdesc)

	return did


def make_unitid(record):
	call_number = record.xpath("./marc:datafield[@tag='852']/marc:subfield[@code='h']", 
										namespaces=ns)

	mirlyn_record = record.xpath("./marc:controlfield[@tag='001']", namespaces=ns)

	if call_number:
		unitid = E.unitid(call_number[0].text.strip().encode("utf-8"))
	elif mirlyn_record:
		unitid = E.unitid("NO CALL NUMBER -- {}".format(mirlyn_record[0].text.strip()))
	else:
		unitid = E.unitid("NO CALL NUMBER -- {}".format(uuid.uuid4()))

	return unitid

def make_origination(record):

	person_creator = record.xpath("./marc:datafield[@tag='100'][@ind1='1']", namespaces=ns)
	family_creator = record.xpath("./marc:datafield[@tag='100'][@ind1='3']", namespaces=ns)
	corp_creator = record.xpath("./marc:datafield[@tag='110']", namespaces=ns) + record.xpath("./marc:datafield[@tag='111']", namespaces=ns)

	if person_creator:
		return E.origination(make_persname(person_creator[0], "origination"))
	elif family_creator:
		return E.origination(make_famname(family_creator[0], "origination"))
	elif corp_creator:
		return E.origination(make_corpname(corp_creator[0], "origination"))
	else:
		return ""

def make_unittitle(record):
	return E.unittitle(extract_collection_title(record))

def make_langmaterial(record):
	langmaterials = record.xpath("./marc:datafield[@tag='546']", namespaces=ns)

	if langmaterials:
		langmaterial = langmaterials[0]
		language_note = langmaterial.xpath("./marc:subfield[@code='a']", namespaces=ns)[0].text.strip().encode("utf-8")
		materials_specified = langmaterial.xpath("./marc:subfield[@code='3']", namespaces=ns)
		if materials_specified:
			language_note += ": {}".format(materials_specified[0].text.strip().encode("utf-8"))

		return E.langmaterial(language_note)
	else:
		return ""

def make_unitdates(record):
	unitdates = []

	inclusive_dates = record.xpath("./marc:datafield[@tag='245']/marc:subfield[@code='f']", namespaces=ns)
	bulk_dates = record.xpath("./marc:datafield[@tag='245']/marc:subfield[@code='g']", namespaces=ns)
	publication_dates = record.xpath("./marc:datafield[@tag='260']/marc:subfield[@code='c']", namespaces=ns)

	if inclusive_dates or bulk_dates:
		for inclusive_date in inclusive_dates:
			unitdates.append(make_unitdate(inclusive_date, "creation", "inclusive"))
		for bulk_date in bulk_dates:
			unitdates.append(make_unitdate(bulk_date, "creation", "bulk"))
	elif publication_dates:
		for publication_date in publication_dates:
			unitdates.append(make_unitdate(publication_date, "publication", "single"))
	else:
		unitdates.append(E.unitdate("[No date provided]"))

	return unitdates

def make_unitdate(unitdate, date_label, date_type):
	expression = unitdate.text.strip().encode("utf-8")
	
	return E.unitdate({"label":date_label,"type":date_type}, expression)

def extract_collection_title(record):
	title_section = record.xpath("./marc:datafield[@tag='245']",namespaces=ns)[0]

	main_title = title_section.xpath("./marc:subfield[@code='a']", namespaces=ns)
	subtitle = title_section.xpath("./marc:subfield[@code='b']", namespaces=ns)
	responsibility = title_section.xpath("./marc:subfield[@code='c']", namespaces=ns)
	medium = title_section.xpath("./marc:subfield[@code='h']", namespaces=ns)
	number_of_part = title_section.xpath("./marc:subfield[@code='n']", namespaces=ns)
	name_of_part = title_section.xpath("./marc:subfield[@code='p']", namespaces=ns)

	collection_title = main_title[0].text.strip().encode("utf-8")
	collection_title += " {}".format(subtitle[0].text.strip().encode("utf-8")) if subtitle else ""
	collection_title += " {}".format(medium[0].text.strip().encode("utf-8")) if medium else ""
	collection_title += " {}".format(number_of_part[0].text.strip().encode("utf-8")) if number_of_part else ""
	collection_title += " {}".format(name_of_part[0].text.strip().encode("utf-8")) if name_of_part else ""
	collection_title += "/ {}".format(responsibility[0].text.strip().encode("utf-8")) if responsibility else ""

	return collection_title.rstrip(",").decode("utf-8")

def make_physdescs(record):
	physdescs = []
	physdesc_elements = record.xpath("./marc:datafield[@tag='300']", namespaces=ns) + record.xpath("./marc:datafield[@tag='305']", namespaces=ns) + record.xpath("./marc:datafield[@tag='516']", namespaces=ns)

	if physdesc_elements:
		for physdesc in physdesc_elements:
			physdescs.append(make_physdesc(physdesc, record))
	else:
		physdescs.append(E.physdesc(E.extent("1 unknown")))

	return physdescs


def make_physdesc(physdesc, record):
	physdesc = E.physdesc(
		make_extent(physdesc),
		make_physfacet(physdesc),
		make_dimensions(physdesc, record)
		)

	return physdesc

def make_extent(physdesc):
	extents = physdesc.xpath("./marc:subfield[@code='a']", namespaces=ns)

	if extents:
		extent = extents[0]
		return E.extent(extent.text.strip().encode("utf-8"))
	else:
		return ""

def make_physfacet(physdesc):
	physfacets = physdesc.xpath("./marc:subfield[@code='b']", namespaces=ns) + physdesc.xpath("./marc:subfield[@code='e']", namespaces=ns) + physdesc.xpath("./marc:subfield[@code='3']", namespaces=ns)

	if physfacets:
		physfacet_note = ""
		for physfacet in physfacets:
			physfacet_note += "\n{}".format(physfacet.text.strip().encode("utf-8"))
		return E.physfacet(physfacet_note)
	else:
		return ""

def make_dimensions(physdesc, record):
	dimensions = physdesc.xpath("./marc:subfield[@code='c']", namespaces=ns)
	durations = record.xpath("./marc:datafield[@tag='306']/marc:subfield[@code='a']", namespaces=ns)

	if dimensions or durations:
		dimensions_texts = []
		dimensions_texts.extend([dimension.text.strip().encode("utf-8") for dimension in dimensions])
		dimensions_texts.extend([duration.text.strip().encode("utf-8") for duration in durations])
		dimensions_text = "; ".join(dimensions_texts)

		return E.dimensions(dimensions_text)
	else:
		return ""

def make_phystech(record):
	phystechs = record.xpath("./marc:datafield[@tago='538']/marc:subfield[@code='a']", namespaces=ns)

	if phystechs:
		phystech = phystechs[0].text.strip().encode("utf-8")

		return E.phystech(phystech)
	else:
		return ""

def make_descgrp(record):
	descgrp = E.descgrp(
		make_acqinfo(record),
		make_accruals(record),
		make_accessrestrict(record),
		make_userestrict(record),
		make_custodhist(record),
		make_phystech(record),
		make_altformavail(record),
		make_originalsloc(record),
		make_otherfindaid(record),
		make_relatedmaterial(record)
		)

	odds = make_odds(record)
	for odd in odds:
		descgrp.append(odd)

	return descgrp

def make_altformavail(record):
	altformavails = record.xpath("./marc:datafield[@tag='530']", namespaces=ns)

	if altformavails:
		altformavail = altformavails[0]
		altformavail_notes = altformavail.xpath("./marc:subfield[@code='a']", namespaces=ns) + altformavail.xpath("./marc:subfield[@code='3']", namespaces=ns)
		altformavail_texts = [altformavail.text.strip().encode("utf-8") for altformavail in altformavail_notes]
		altformavail_text = " ".join(altformavail_texts)

		return E.altformavail(altformavail_text)
	else:
		return ""

def make_originalsloc(record):
	originalslocs = record.xpath("./marc:datafield[@tag='534']", namespaces=ns) + record.xpath("./marc:datafield[@tag='535']", namespaces=ns)

	if originalslocs:
		originalsloc = originalslocs[0]
		originalsloc_note = ""
		for subfield in originalsloc.xpath("./marc:subfield", namespaces=ns):
			originalsloc_note += "\n{}".format(subfield.text.strip().encode("utf-8"))

		return E.originalsloc(originalsloc_note.strip())
	else:
		return ""

def make_otherfindaid(record):
	otherfindaids = record.xpath("./marc:datafield[@tag='555']/marc:subfield[@code='a']", namespaces=ns)

	if otherfindaids:
		otherfindaid = otherfindaids[0].text.strip().encode("utf-8")
		return E.otherfindaid(otherfindaid)
	else:
		return ""

def make_relatedmaterial(record):
	relatedmaterials = record.xpath("./marc:datafield[@tag='544']", namespaces=ns)

	if relatedmaterials:
		relatedmaterial = relatedmaterials[0]
		relatedmaterial_note = ""
		for subfield in relatedmaterial.xpath("./marc:subfield", namespaces=ns):
			relatedmaterial_note += "\n{}".format(subfield.text.strip().encode("utf-8"))

		return E.relatedmaterial(relatedmaterial_note.strip())
	else:
		return ""

def make_custodhist(record):
	custodhists = record.xpath("./marc:datafield[@tag='546']", namespaces=ns)

	if custodhists:
		custodhist = custodhists[0]
		custodhist_note = custodhist.xpath("./marc:subfield[@code='a']", namespaces=ns)[0].text.strip().encode("utf-8")
		materials_specified = custodhist.xpath("./marc:subfield[@code='3']", namespaces=ns)
		if materials_specified:
			language_note += ": {}".format(materials_specified[0].text.strip().encode("utf-8"))

		return E.custodhist(custodhist_note)
	else:
		return ""

def make_accessrestrict(record):
	accessrestricts = record.xpath("./marc:datafield[@tag='506']", namespaces=ns)

	if accessrestricts:
		accessrestrict = accessrestricts[0]
		accessrestrict_statement = accessrestrict.xpath("./marc:subfield[@code='a']", 
										namespaces=ns)[0].text.strip().encode("utf-8")
		if accessrestrict.xpath("./marc:subfield[@code='2']", namespaces=ns):
			accessrestrict_statement += " {}".format(accessrestrict.xpath("./marc:subfield[@code='2']", 
											namespaces=ns)[0].text.strip().encode("utf-8"))
		return E.accessrestrict(accessrestrict_statement)
	else:
		return ""

def make_userestrict(record):
	userestrict = record.xpath("./marc:datafield[@tag='540']/marc:subfield[@code='a']", namespaces=ns)

	if userestrict:
		return E.userestrict(userestrict[0].text.strip().encode("utf-8"))
	else:
		return ""

def make_acqinfo(record):
	acqinfo = record.xpath("./marc:datafield[@tag='541']/marc:subfield[@code='a']", namespaces=ns)

	if acqinfo:
		return E.acqinfo(acqinfo[0].text.strip().encode("utf-8"))
	else:
		return ""

def make_accruals(record):
	accruals = record.xpath("./marc:datafield[@tag='584']/marc:subfield[@code='a']", namespaces=ns)

	if accruals:
		return E.accruals(accruals[0].text.strip().encode("utf-8"))
	else:
		return ""

def make_bioghist(record):
	bioghists = record.xpath("./marc:datafield[@tag='545']", namespaces=ns)

	if bioghists:
		bioghist = bioghists[0]
		bioghist_statement = ""
		if bioghist.xpath("./marc:subfield[@code='a']", namespaces=ns):
			bioghist_statement += bioghist.xpath("./marc:subfield[@code='a']", 
									namespaces=ns)[0].text.strip().encode("utf-8")
		if bioghist.xpath("./marc:subfield[@code='b']", namespaces=ns):
			bioghist_statement += " " + bioghist.xpath("./marc:subfield[@code='b']", 
															namespaces=ns)[0].text.strip().encode("utf-8")

		return E.bioghist(bioghist_statement.decode("utf-8"))
	else:
		return ""

def make_scopecontent(record):
	scopecontents = record.xpath("./marc:datafield[@tag='520']", namespaces=ns) + record.xpath("./marc:datafield[@tag='510']", namespaces=ns)

	if scopecontents:
		scopecontent = scopecontents[0]
		scopecontent_notes = scopecontent.xpath("./marc:subfield[@code='a']", namespaces=ns) + scopecontent.xpath("./marc:subfield[@code='b']", namespaces=ns)
		scopecontent_texts = [scopecontent.text.strip().encode("utf-8") for scopecontent in scopecontent_notes]
		scopecontent_text = " ".join(scopecontent_texts)

		return E.scopecontent(scopecontent_text.decode("utf-8"))
	else:
		return ""

def make_arrangement(record):
	arrangements = record.xpath("./marc:datafield[@tag='351']", namespaces=ns)

	if arrangements:
		arrangement = arrangements[0]
		arrangement_notes = arrangement.xpath("./marc:subfield[@code='a']", namespaces=ns) + arrangement.xpath("./marc:subfield[@code='b']", namespaces=ns)
		arrangement_texts = [arrangement.text.strip().encode("utf-8") for arrangement in arrangement_notes]
		arrangement_text = " ".join(arrangement_texts)

		return E.arrangement(arrangement_text)
	else:
		return ""

def make_controlaccess(record):
	controlaccess = E.controlaccess()

	subjects = make_subjects(record)
	persnames = make_persnames(record)
	famnames = make_famnames(record)
	corpnames = make_corpnames(record)

	for subject in subjects:
		controlaccess.append(subject)
	for persname in persnames:
		controlaccess.append(persname)
	for famname in famnames:
		controlaccess.append(famname)
	for corpname in corpnames:
		controlaccess.append(corpname)

	return controlaccess

def make_subjects(record):
	subjects_list = []

	tag_mappings = {
	"130":{
		"terms":{"a":"uniform_title", "h":"genre_form"}, 
		"indicator_sources":{},
		"alternate_sources":[]
		},
	"630":{
		"terms":{"a":"uniform_title", "v":"genre_form"}, 
		"indicator_sources":{"0":"lcsh"},
		"alternate_sources":[]
		},
	"650":{
		"terms":{"a":"topical", "b":"topical", "d":"temporal","v":"genre_form","x":"topical","y":"temporal","z":"geographic"}, 
		"indicator_sources":{"0":"lcsh", "2":"mesh", "4":"local"},
		"alternate_sources":["2"]
		},
	"651":{
		"terms":{"a":"geographic","v":"genre_form","x":"topical","y":"temporal","z":"geographic"},
		"indicator_sources":{"0":"lcsh","4":"local"}, 
		"alternate_sources":["2"]
		},
	"655":{
		"terms":{"a":"genre_form","v":"genre_form","y":"temporal","z":"geographic"},
		"indicator_sources":{"0":"lcsh", "4":"local"}, 
		"alternate_sources":["2"]
		},
	# The below is wrong... but it's what we have
	"656":{
		"terms":{"a":"genre_form"},
		"indicator_sources":{}, 
		"alternate_sources":["2"]
		},
	"690":{
		"terms":{"a":"topical","x":"topical","y":"temporal","z":"geographic"},
		"indicator_sources":{}, 
		"alternate_sources":[]
		},
	"691":{
		"terms":{"a":"geographic","x":"topical","y":"temporal"},
		"indicator_sources":{}, 
		"alternate_sources":[]
		},
	"730":{
		"terms":{"a":"uniform_title"}, 
		"indicator_sources":{},
		"alternate_sources":[]
		},
	"740":{
		"terms":{"a":"uniform_title","h":"genre_form"},
		"indicator_sources":{}, 
		"alternate_sources":[]
		},
	"830":{
		"terms":{"a":"uniform_title"}, 
		"indicator_sources":{},
		"alternate_sources":[]
		}
	}

	for tag in tag_mappings:
		subjects = record.xpath("./marc:datafield[@tag={}]".format(tag), namespaces=ns)
		term_types = tag_mappings[tag]["terms"]
		indicator_sources = tag_mappings[tag]["indicator_sources"]
		alternate_sources = tag_mappings[tag]["alternate_sources"]
		for subject in subjects:
			subjects_list.append(make_subject(subject, term_types, indicator_sources, alternate_sources))

	return subjects_list

def make_subject(subject, term_types, indicator_sources, alternate_sources):
	encodinganalog = subject.get("tag","")
	atts = {"encodinganalog":encodinganalog, "source":"local"}
	indicator_source_found = False
	if indicator_sources:
		indicator = subject.get("ind2", "")
		if indicator in indicator_sources:
			source = indicator_sources[indicator]
			atts["source"] = source
			indicator_source_found = True
	elif alternate_sources and not indicator_source_found:
		for code in alternate_sources:
			if subject.xpath("./marc:subfield[@code={}]".format(code), namespaces=ns):
				source = subject.xpath("./marc:subfield[@code={}".format(code))[0].text.strip().encode("utf-8")
				atts["source"] = source

	subject_element = E.subject(atts)

	for subfield in subject.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in term_types:
			term_type = term_types[code]
			term_text = subfield.text.strip().encode("utf-8")
			term = E.term({"type":term_type}, term_text.decode("utf-8"))
			subject_element.append(term)

	return subject_element

def make_persnames(record):
	persnames_list = []
	persnames = record.xpath("./marc:datafield[@tag='600']", namespaces=ns) + record.xpath("./marc:datafield[@tag='700']", namespaces=ns)

	for persname in persnames:
		indicator1 = persname.get("ind1", "")
		if indicator1 != "3":
			persnames_list.append(make_persname(persname, "controlaccess"))

	return persnames_list

def make_persname(persname, context):
	encodinganalog = persname.get("tag","")

	if context == "origination":
		atts = {"encodinganalog":encodinganalog}
	elif context == "controlaccess":
		source_mappings = {"0": "lcnaf", "4":"local"}
		source_indicator = persname.get("ind2", "")
		if source_indicator in source_mappings:
			source = source_mappings[source_indicator]
		else:
			source = "local"

		atts = {"source":source, "encodinganalog":encodinganalog}

	persname_element = E.persname(atts)

	primary_and_rest_of_name = persname.xpath("./marc:subfield[@code='a']", namespaces=ns)[0].text.strip().encode("utf-8").rstrip(",")
	name_parts = primary_and_rest_of_name.split(",")
	if len(name_parts) > 1:
		primary_name = name_parts[0].strip()
		rest_of_name = ",".join(name_parts[1:]).strip()
	else:
		primary_name = name_parts[0].strip()
		rest_of_name = ""
	persname_element.append(E.primary_name(primary_name.decode("utf-8")))
	persname_element.append(E.rest_of_name(rest_of_name.decode("utf-8")))

	persname_mappings = {"b":"number", "c":"title", "d": "dates", "q": "fuller_form"}
	for subfield in persname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in persname_mappings:
			tag = persname_mappings[code]
			element = etree.Element(tag)
			element.text = subfield.text.strip().encode("utf-8")
			persname_element.append(element)

	term_mappings = {"t": "uniform_title", "v":"genre_form", "x": "topical", "y": "temporal", "z": "geographic"}
	for subfield in persname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in term_mappings:
			term_type = term_mappings[code]
			term = E.term({"type":term_type}, subfield.text.strip().encode("utf-8"))
			persname_element.append(term)

	return persname_element

def make_corpnames(record):
	corpnames_list = []
	corpnames = record.xpath("./marc:datafield[@tag='610']", namespaces=ns) + record.xpath("./marc:datafield[@tag='611']", namespaces=ns) + record.xpath("./marc:datafield[@tag='710']", namespaces=ns)

	for corpname in corpnames:
		corpnames_list.append(make_corpname(corpname, "controlaccess"))

	return corpnames_list

def make_corpname(corpname, context):
	encodinganalog = corpname.get("tag","")
	if context == "origination":
		atts = {"encodinganalog":encodinganalog}
	elif context == "controlaccess":
		source_mappings = {"0": "lcnaf", "4":"local"}
		source_indicator = corpname.get("ind2", "")
		if source_indicator in source_mappings:
			source = source_mappings[source_indicator]
		elif corpname.xpath("./marc:subfield[@code='2']", namespaces=ns):
			source = corpname.xpath("./marc:subfield[@code='2']", namespaces=ns)[0].text.strip().encode("utf-8")
		else:
			source = "local"

		atts = {"source":source, "encodinganalog":encodinganalog}

	corpname_element = E.corpname(atts)

	corpname_mappings = {"a":"primary_name","b":"subordinate_name", "n":"number"}
	for subfield in corpname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in corpname_mappings:
			tag = corpname_mappings[code]
			element = etree.Element(tag)
			element.text = subfield.text.strip().encode("utf-8").decode("utf-8")
			corpname_element.append(element)

	term_mappings = {"t": "uniform_title", "v":"genre_form", "x": "topical", "y": "temporal", "z": "geographic"}
	for subfield in corpname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in term_mappings:
			term_type = term_mappings[code]
			term = E.term({"type":term_type}, subfield.text.strip().encode("utf-8"))
			corpname_element.append(term)

	return corpname_element

def make_famnames(record):
	famnames_list = []
	famnames = record.xpath("./marc:datafield[@tag='600'][@ind1='3']", namespaces=ns)

	for famname in famnames:
		famnames_list.append(make_famname(famname, "controlaccess"))

	return famnames_list

def make_famname(famname, context):
	encodinganalog = famname.get("tag","")
	if context == "origination":
		atts = {"encodinganalog":encodinganalog}
	elif context == "controlaccess":
		source_mappings = {"0": "lcnaf", "4":"local"}
		source_indicator = famname.get("ind2", "")
		if source_indicator in source_mappings:
			source = source_mappings[source_indicator]
		else:
			source = "local"

		atts = {"source":source, "encodinganalog":encodinganalog}

	famname_element = E.famname(atts)

	famname_mappings = {"a":"family_name", "d":"dates", "c":"qualifier"}
	for subfield in famname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in famname_mappings:
			tag = famname_mappings[code]
			element = etree.Element(tag)
			element.text = subfield.text.strip().encode("utf-8")
			famname_element.append(element)

	term_mappings = {"t": "uniform_title", "v":"genre_form", "x": "topical", "y": "temporal", "z": "geographic"}
	for subfield in famname.xpath("./marc:subfield", namespaces=ns):
		code = subfield.get("code", "")
		if code in term_mappings:
			term_type = term_mappings[code]
			term = E.term({"type":term_type}, subfield.text.strip().encode("utf-8"))
			famname_element.append(term)

	return famname_element

def make_odds(record):
	tag_mappings = {
	"240":"Uniform Title",
	"246":"Varying Form of Title",
	"250":"Edition Statement",
	"255":"Cartographic Mathematical Data",
	"260":"Publication, Distribution, Etc.",
	"440":"Series Statement",
	"490":"Series Statement",
	"500":"General Note",
	"502":"Dissertation Note",
	"504":"Bibliography",
	"505":"Formatted Contents Note",
	"508":"Creation/Production Credits",
	"511":"Participant or Performer",
	"518":"Date/Time and Place of Event",
	"521":"Target Audience",
	"533":"Reproduction Note",
	"550":"Issuing Body",
	"586":"Awards Note",
	"590":"General Note"
	}

	odds = []
	for tag in tag_mappings:
		odds.extend(record.xpath("./marc:datafield[@tag={}]".format(tag), namespaces=ns))

	odd_elements = []
	for odd in odds:
		odd_elements.append(make_odd(odd, tag_mappings))

	return odd_elements

def make_odd(odd, tag_mappings):
	tag = odd.get("tag", "")
	head_text = tag_mappings[tag]
	note_text = ""
	for subfield in odd.xpath("./marc:subfield", namespaces=ns):
		note_text += "\n{}".format(subfield.text.strip().encode("utf-8"))

	return E.odd(E.head(head_text), E.p(note_text))

def make_dsc(main_record, other_records):
	pass

def make_series(record):
	pass

def make_ead_with_series(records):
	main_record = identify_main_record(records)
	if main_record:
		other_records = [record for record in records if record not in main_record]
		archdesc = make_archdesc(main_record)
		controlaccess = make_controlaccess(other_records)
		dsc = make_dsc(main_record, other_records)
		archdesc.append(controlaccess)
		archdesc.append(dsc)
		ead = E.ead(
			make_eadheader(main_record),
			archdesc
			)

		return ead

	else:
		return False

def make_ead_without_series(record):
	ead = E.ead(
		make_eadheader(record),
		make_archdesc(record)
		)

	return ead

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

if __name__ == "__main__":
	marcxml_dir = "../marcxml_no_ead"
	ead_dir = "../converted_eads"
	convert_marcxml_to_ead(marcxml_dir, ead_dir)

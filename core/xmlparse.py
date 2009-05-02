#
#    Copyright (c) 2007-2009 Corey Goldberg (corey@goldb.org)
#    License: GNU GPLv3
#
#    This file is part of Pylot.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.  See the GNU General Public License 
#    for more details.
#


try:
    import xml.etree.ElementTree as etree
except:
    sys.stderr.write('ERROR: Pylot was unable to find the XML parser.  Make sure you have Python 2.5+ installed.\n')
    sys.exit(1)
from engine import Request



def load_xml_string_cases(tc_xml_blob):
    # parse xml and load request queue with core.engine.Request objects
    # variant to parse from a raw string instead of a filename
    dom = etree.ElementTree(etree.fromstring(tc_xml_blob))
    return load_xml_cases_dom(dom)


def load_xml_cases(tc_xml_filename):
    # parse xml and load request queue with corey.engine.Request objects
    # variant to load the xml from a file (the default shell behavior)
    dom = etree.parse(tc_xml_filename)
    return load_xml_cases_dom(dom)


def load_xml_cases_dom(dom):
    # load cases from an already-parsed XML DOM
    cases = []
    for child in dom.getiterator():
        if child.tag != dom.getroot().tag and child.tag == 'case':
            req = Request()
            repeat = child.attrib.get('repeat')
            if repeat:
                req.repeat = int(repeat)
            else:
                req.repeat = 1
            for element in child:
                if element.tag.lower() == 'url':
                    req.url = element.text
                if element.tag.lower() == 'method': 
                    req.method = element.text
                if element.tag.lower() == 'body': 
                    req.body = element.text
                if element.tag.lower() == 'verify': 
                    req.verify = element.text
                if element.tag.lower() == 'verify_negative': 
                    req.verify_negative = element.text
                if element.tag.lower() == 'timer_group': 
                    req.timer_group = element.text
                if element.tag.lower() == 'add_header':
                    # this protects against headers that contain colons
                    splat = element.text.split(':')
                    x = splat[0].strip()
                    del splat[0]
                    req.add_header(x, ''.join(splat).strip())
            cases.append(req)
    return cases
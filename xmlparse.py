#!/usr/bin/env python
#
#    Copyright (c) 2007-2008 Corey Goldberg (corey@goldb.org)
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


import xml.etree.ElementTree as etree
from pylot_engine import Request


def load_xml_cases():
    # parse xml and load request queue
    dom = etree.parse('testcases.xml')
    cases = []
    for child in dom.getiterator():
        if child.tag != dom.getroot().tag and child.tag == 'case':
            req = Request()
            repeat = child.attrib.get('repeat')
            if repeat:
                req.repeat = int(repeat)
            else:
                repeat = 1
            int(req.repeat)
            #print int()
            for element in child:
                if element.tag == 'url':
                    req.url = element.text
                if element.tag == 'method': 
                    req.method = element.text
                if element.tag == 'body': 
                    req.body = element.text
                if element.tag == 'verify': 
                    req.verify = element.text
                if element.tag == 'verify_negative': 
                    req.verify_negative = element.text
                if element.tag == 'add_header':
                    splat = element.text.split(':')
                    req.add_header(splat[0].strip(), splat[1].strip())
            if 'Content-type' not in req.headers:
                req.add_header('Content-type', 'text/xml')  # default if no type specified
                #req.add_header('Content-type', 'application/x-www-form-urlencoded') 
            cases.append(req)
    return cases
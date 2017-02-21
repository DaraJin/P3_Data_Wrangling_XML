'''
This piece of codes is similar with codes in last Quiz.
'''

# output csv files
import csv	
import codecs
import pprint
import re
import xml.etree.cElementTree as ET


OSM_PATH = "brooklynsp.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
# PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
# Since I think "." is a not a problematic char, so I remove it from the regex formula
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\, \t\r\n]')

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
        
    if element.tag == 'node':
        for k, v in dict.iteritems(element.attrib): # loop throught all attribs
            if k in node_attr_fields: # match and get value
                node_attribs[k] = v
            if k == 'id':  # keep the id for tag use
                id = v
                
        for child in element: # loop through all child tag
            ele = {} # create a dict item for the 'tags' list
            ele['id'] = id
            ele['type'] = default_tag_type
            ele['value'] = child.attrib['v']
            j = child.attrib['k']
            if not re.search(problem_chars, j):
                pos = j.find(":")
                if pos < 0: #as the tag type
                    ele['key'] = j
                else:
                    ele['type'] = j[:pos]
                    ele['key'] = j[pos+1:]                 
            tags.append(ele) # add the item into tags           
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for k, v in dict.iteritems(element.attrib):
            if k in way_attr_fields:
                way_attribs[k] = v
            if k == 'id':
                id = v
        count_nd = 0
        for child in element:
            if child.tag == 'tag':
                ele = {} # creat a dict item for the 'tags' list
                ele['id'] = id
                ele['type'] = default_tag_type
                ele['value'] = child.attrib['v']
                j = child.attrib['k']
                if not re.search(problem_chars, j):
                    pos = j.find(":")
                    if pos < 0: #as the tag type
                        ele['key'] = j
                    else:
                        ele['type'] = j[:pos]
                        ele['key'] = j[pos+1:]
                    
                tags.append(ele) # add the item into tags
            elif child.tag == 'nd':
                for k,v in dict.iteritems(child.attrib):
                    ele = {}
                    ele['node_id'] = v
                    ele['id'] = id
                    ele['position'] = count_nd
                    way_nodes.append(ele)
                count_nd += 1
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()


        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 18:40:53 2023

@author: Flores Bakker

The SVG2RDF script offers a simple way of transforming an SGV-document into a representation of the XML-code in RDF-based triples. Just set your base directory and place there your own SVG-document so that the script can transform this to RDF-format.

"""

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from rdflib import Graph, Namespace, Literal, RDF
import os

from rdflib.namespace import NamespaceManager

# Get the current working directory in which the Playground.py file is located.
current_dir = os.getcwd()

# Set the path to the desired standard directory. 
directory_path = os.path.abspath(os.path.join(current_dir, '..'))

# namespace declaration
rdf   = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs  = Namespace("http://www.w3.org/2000/01/rdf-schema#")
doc   = Namespace("https://example.org/doc/id/")
svg   = Namespace("http://www.w3.org/SVG/model/def/")
xml   = Namespace("http://www.w3.org/XML/model/def/")
xmlns = Namespace("http://www.w3.org/2000/xmlns/model/def/")
xlink = Namespace("https://www.w3.org/1999/xlink/model/def/")

# function to read a graph (as a string) from a file 
def readGraphFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding = 'utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content

def generate_element_id(element):
    # Base case: If there's no parent, return an empty string (root-level element)
    if element.parent is None:
        return "1"

    # Initialize the sibling index for the current element
    sibling_index = 1
    # Count previous siblings (including text and non-element nodes)
    for sibling in element.previous_siblings:
        sibling_index += 1

    # Recursive call: Get the parent's ID
    parent_id = generate_element_id(element.parent)

    # If the parent ID is not empty, append the current element's sibling index
    if parent_id:
        return f"{parent_id}.{sibling_index}"
    else:
        return str(sibling_index)  # This happens at the root level



# loop through any xml files in the input directory
for filename in os.listdir(directory_path+"/OntoSVG/Tools/SVG2RDF/Input"):
    if filename.endswith(".svg"):
        file_path = os.path.join(directory_path+"/OntoSVG/Tools/SVG2RDF/Input", filename)
        
        # Establish the stem of the file name for reuse in newly created files
        filename_stem = os.path.splitext(filename)[0]

        # place the xml code in a string
        xml_doc = readGraphFromFile (file_path)

        # initialize graph
        g = Graph(bind_namespaces="rdflib")
              
        g.bind("rdf", rdf)
        g.bind("rdfs", rdfs)
        g.bind("doc", doc)
        g.bind("svg", svg)
        g.bind("xml", xml)
        g.bind("xmlns", xmlns)
        g.bind("xlink", xlink)

        # fill graph with svg vocabulary
        xml_graph = Graph().parse(directory_path+"/OntoSVG/Specification/svg - core.ttl" , format="ttl")

        # string for query to establish IRI of a 'tag' HTML element
        tagquerystring = '''
            
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix xml: <http://www.w3.org/XML/model/def/>

        select ?element_IRI where {
          ?element_IRI xml:tag ?tag
        }
        '''

        # parse xml document
        soup = BeautifulSoup(xml_doc, features="xml")
        root_element = soup.contents[0]
        root_id = generate_element_id(root_element)
       
        # loop through each node in the XML document
        for element in soup.descendants:
            # check if the element is an XML tag element
            if isinstance(element, Tag):
                # establish unique id for the XML tag element
                element_id = generate_element_id(element)
                
                # establish IRI for the tag class based on the SVG vocabulary
                tag_result = xml_graph.query(tagquerystring, initBindings={"tag" : Literal(element.name)})
                for row in tag_result:
                    tag_IRI = row.element_IRI
                    
                # add the element to the graph with its unique identifier as IRI and its tag as type
                g.add((doc[element_id], RDF.type, tag_IRI))
                
                # add a document node as a container of the XML-tree
                if element.name == 'svg':
                    document_id = '1'
                    g.add((doc[document_id], RDF.type, svg["Document"]))
                    g.add((doc[document_id], rdf["_" + str(document_id)], doc[element_id]))
        
                # establish optional attributes of the element
                for attribute, values in element.attrs.items():
                    # Check if it's the default namespace declaration
                    if attribute == 'xmlns':
                        namespace_uri = xml
                        local_name = 'xmlns'
                    # Split attribute name into namespace and local name
                    elif ':' in attribute:
                        namespace, local_name = attribute.split(':')
                        # Check the namespace of the attribute and add appropriate RDF triple
                        if namespace == 'xml':
                            namespace_uri = xml
                        elif namespace == 'xlink':
                            namespace_uri = xlink
                        elif namespace == 'xmlns':
                            namespace_uri = xmlns
                        elif namespace == 'svg':
                            namespace_uri = svg
                        else:
                            namespace_uri = None  # Unknown namespace prefix
                    else:
                        namespace_uri = svg
                        local_name = attribute 
        
                    # If namespace is found, add RDF triple
                    if namespace_uri:
                        # If the attribute consists of multiple values (as list), join them
                        if isinstance(values, list):
                            attribute_value = ' '.join(values)
                        else:  # If it's a single value, keep it as is
                            attribute_value = values
                        # Add optional attributes of the element to the graph
                        g.add((doc[element_id], namespace_uri[local_name], Literal(attribute_value)))

                # go through the direct children of the element
                member_count = 0 # initialize count
                for child in element.children:
                    member_count = member_count + 1 # count the number of direct children, so that we can establish the sequence of appearance of the children within the parent element, through the 'rdf:_x' property between parent and child.
                    
                    # if the child is an xml tag element get its unique identifier based on sourceline and sourcepos
                    if isinstance(child, Tag):
                      if child.name == None  :
                          childname = ""
                      else:
                          childname = child.name
                      child_id = generate_element_id(child)
                      g.add((doc[element_id], rdf["_" + str(member_count)], doc[child_id]))
                      
                    # if the child is an text node, create a unique identifier based on sourceline and sourcepos of its parent and the sequence position of the child within the parent, as the xml-parser does not have sourceline and sourcepos available as attributes for text nodes.
                    elif isinstance(child, NavigableString):
                      if child.name == None  :
                            childname = "Text"
                      else:
                            childname = child.name
                      child_id = generate_element_id(child)
                      
                      # write to graph that the parent node has a child with a certain sequence position
                      g.add((doc[element_id], rdf["_" + str(member_count)], doc[child_id]))  
                      
                      # write to graph that the child node is of type Text
                      g.add((doc[child_id], RDF.type, svg["Text"]))
                      
                      # empty content (of type None) in xml needs to be converted to empty string
                      if element.string == None: 
                          text_fragment = "" 
                      else:
                          text_fragment = element.string
                      
                      # write string content of the text node to the graph
                      g.add((doc[child_id], svg["fragment"], Literal(text_fragment)))

        # write the resulting graph to file
        g.serialize(destination=directory_path+"/OntoSVG/Tools/SVG2RDF/Output/" + filename_stem + "-parsed.ttl", format="turtle")
        
        print ("SVG file ", filename," is succesfullly transformed to file ", filename_stem + "-parsed.ttl in Turtle format.")
    else: 
        print ('Warning: file in directory "input" is no SVG file and cannot be parsed.')

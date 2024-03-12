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

# Set the path to the desired standard directory. 
directory_path = "C:/Users/Administrator/Documents/Branches/"


# namespace declaration
rdf   = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs  = Namespace("http://www.w3.org/2000/01/rdf-schema#")
doc   = Namespace("https://data.rijksfinancien.nl/svg/doc/id/")
svg   = Namespace("https://data.rijksfinancien.nl/svg/model/def/")
xml   = Namespace("http://www.w3.org/XML/1998/namespace#")
xmlns = Namespace("http://www.w3.org/2000/xmlns/")
xlink = Namespace("http://www.w3.org/1999/xlink#")

# function to read a graph (as a string) from a file 
def readGraphFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding = 'utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content

def generate_element_id(element):
    
    parent_string = ""
    for parent in element.parents:
        parent_sibling_count = 0
        for parent_sibling in parent.previous_siblings:    
            parent_sibling_count = parent_sibling_count + 1
        horizontal_parental_index = parent_sibling_count
        if parent.name:
            parent_string = parent_string + str(horizontal_parental_index)
        else:
            parent_string = parent_string + "0"
        
    
    count_sibling = 0
    for sibling in element.previous_siblings:    
        count_sibling = count_sibling + 1
    horizontal_index = count_sibling
    
    element_id = f"{parent_string}/{horizontal_index}" 
    
    return element_id.replace("[document]/","")




# loop through any xml files in the input directory
for filename in os.listdir(directory_path+"OntoSVG/Tools/SVG2RDF/Input"):
    if filename.endswith(".svg"):
        file_path = os.path.join(directory_path+"OntoSVG/Tools/SVG2RDF/Input", filename)
        
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
        xml_graph = Graph().parse(directory_path+"OntoSVG/Specification/svg - core.ttl" , format="ttl")

        # string for query to establish IRI of a 'tag' HTML element
        tagquerystring = '''
            
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix xml: <http://www.w3.org/XML/1998/namespace#>

        select ?element_IRI where {
          ?element_IRI xml:tag ?tag
        }
        '''

        # parse xml document
        soup = BeautifulSoup(xml_doc, features="xml")
        root_element = soup.contents[0]
        root_id = generate_element_id(root_element)
       
        
       
      
        # loop through each element in the XML document
        for element in soup.descendants:
            # check if the element is an XML tag element
            if isinstance(element, Tag):
                # establish unique id for the XML tag element
                element_id = generate_element_id(element)
                
                # establish IRI for the tag class based on the HTML vocabulary
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
                    
                    # if the child is an html tag element get its unique identifier based on sourceline and sourcepos
                    if isinstance(child, Tag):
                      if child.name == None  :
                          childname = ""
                      else:
                          childname = child.name
                      child_id = generate_element_id(child)
                      g.add((doc[element_id], rdf["_" + str(member_count)], doc[child_id]))
                      
                    # if the child is an text element, create a unique identifier based on sourceline and sourcepos of its parent and the sequence position of the child within the parent, as the html-parser does not have sourceline and sourcepos available as attributes for text elements.
                    elif isinstance(child, NavigableString):
                      if child.name == None  :
                            childname = "TextElement"
                      else:
                            childname = child.name
                      child_id = generate_element_id(child)
                      
                      # write to graph that the parent element has a child with a certain sequence position
                      g.add((doc[element_id], rdf["_" + str(member_count)], doc[child_id]))  
                      
                      # write to graph that the child element is of type TextElement
                      g.add((doc[child_id], RDF.type, svg["TextElement"]))
                      
                      # empty content (of type None) in html needs to be converted to empty string
                      if element.string == None: 
                          text_fragment = "" 
                      else:
                          text_fragment = element.string
                      
                      # write string content of the text element to the graph
                      g.add((doc[child_id], svg["fragment"], Literal(text_fragment)))

        # write the resulting graph to file
        g.serialize(destination=directory_path+"OntoSVG/Tools/SVG2RDF/Output/" + filename_stem + "-parsed.ttl", format="turtle")
        
        print ("SVG file ", filename," is succesfullly transformed to file ", filename_stem + "-parsed.ttl in Turtle format.")
    else: 
        print ('Warning: file in directory "input" is no SVG file and cannot be parsed.')

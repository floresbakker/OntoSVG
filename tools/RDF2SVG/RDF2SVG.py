# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 19:42:53 2023

@author: Flores Bakker

"""
import pyshacl
from rdflib import Graph, Namespace, Literal, RDF, Dataset
import rdflib 
import os

# Get the current working directory in which the RDF2SVG.py file is located.
current_dir = os.getcwd()

# Set the path to the desired standard directory. 
directory_path = os.path.abspath(os.path.join(current_dir))

# Function to read a graph (as a string) from a file 
def readStringFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content

# Function to write a graph to a file
def writeGraph(graph):
    graph.serialize(destination=directory_path+"/tools/RDF2SVG/output/"+filename_stem+"-serialized.trig", format="trig")

# Function to call the PyShacl engine so that a RDF model of a SVG document can be serialized to SVG-code.
def iteratePyShacl(vocabulary, serializable_graph):
        
        # call PyShacl engine and apply the SVG vocabulary to the serializable SVG document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=vocabulary,
        data_graph_format="trig",
        shacl_graph_format="trig",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, # Not using the iterate rules function of PyShacl as it seems to not be working properly. Instead, offer each new resulting state freshly to PyShacl.
        debug=False,
        )
      
        # Query to know if the document has been fully serialised by testing whether the root has a svg:fragment property. If it has, the algorithm has reached the final level of the document.
        resultquery = serializable_graph.query('''
            
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX svg: <http://www.w3.org/SVG/model/def/>
        PREFIX xml: <http://www.w3.org/XML/model/def/> 

        ASK 
        WHERE {
          ?document a svg:Document ;
                  xml:fragment ?fragment.
        }


        ''')   

        # Check whether another iteration is needed. If the svg root of the document contains a svg:fragment statement then the serialisation is considered done.
        for result in resultquery:
            if result == False:
                writeGraph(serializable_graph)
                iteratePyShacl(vocabulary, serializable_graph)
            else: 
                print ("Document is serialised.")
                writeGraph(serializable_graph)
             
# Get all the vocabularies and place them in a string
dom_vocabulary   = readStringFromFile(directory_path   + "/specification/dom - core.trig")
xml_vocabulary   = readStringFromFile(directory_path   + "/specification/xml - core.trig")
xmlns_vocabulary = readStringFromFile(directory_path   + "/specification/xmlns - core.trig")
xlink_vocabulary = readStringFromFile(directory_path   + "/specification/xlink - core.trig")
svg_vocabulary   = readStringFromFile(directory_path   + "/specification/svg - core.trig")

vocabulary = dom_vocabulary + '\n' + xml_vocabulary + '\n' + xmlns_vocabulary + '\n' + xlink_vocabulary + '\n' + svg_vocabulary + '\n'

# loop through any turtle files in the input directory
for filename in os.listdir(directory_path+"/tools/RDF2SVG/input"):
    if filename.endswith(".ttl" or "*.trig"):
        file_path = os.path.join(directory_path+"/tools/RDF2SVG/input", filename)
        
        # Establish the stem of the file name for reuse in newly created files
        filename_stem = os.path.splitext(filename)[0]

        # Get the RDF-model of some SVG document and place it in a string. 
        document_graph = readStringFromFile(file_path)                  

        # Join the SVG vocabulary and the RDF-model of some SVG document into a string
        serializable_graph_string = vocabulary + document_graph

        # Create a graph of the string containing the SVG vocabulary and the RDF-model of some SVG document
        serializable_graph = Dataset(default_union=True)
        serializable_graph.parse(data=serializable_graph_string , format="trig")

        # Inform user
        print ("Serialising the SVG as contained in document '" + filename + "'...")

        # Call the shacl engine with the SVG vocabulary and the document to be serialized
        iteratePyShacl(xml_vocabulary, serializable_graph)

        # Prepare a graph to query the serialized document
        serialized_graph = Dataset(default_union=True)        
        serialized_graph.parse(directory_path+"/tools/RDF2SVG/output/"+filename_stem+"-serialized.trig" , format="trig")

        # Query to get the resulting fragment of the document
        documentQuery = serialized_graph.query('''
            
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
              PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
              PREFIX svg: <http://www.w3.org/SVG/model/def/>
              PREFIX xml: <http://www.w3.org/XML/model/def/> 

              select ?fragment
              WHERE {
                ?svgElement a svg:Document ;
                        xml:fragment ?fragment.
              }

        ''')   

        # Write serialized html to actual html file
        for result in documentQuery:
            with open(directory_path+"/tools/RDF2SVG/output/"+filename_stem+"-serialized.svg", 'w', encoding='utf-8') as file:
               file.write(result.fragment)
               print ("Document is saved to SVG-format as " + filename_stem+"-serialized.svg")

    else:
        print ("No turtle file ('*.ttl') detected")


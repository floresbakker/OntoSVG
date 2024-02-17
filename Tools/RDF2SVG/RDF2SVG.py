# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 19:42:53 2023

@author: Flores Bakker



"""
import pyshacl
import rdflib 
import os

# Set the path to the desired standard directory. 
directory_path = "C:/Users/Administrator/Documents/Branches/"

# Function to read a graph (as a string) from a file 
def readGraphFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content

# Function to write a graph to a file
def writeGraph(graph):
    graph.serialize(destination=directory_path+"/OntoSVG/Tools/RDF2SVG/Output/"+filename_stem+"-serialized.ttl", format="turtle")

# Function to call the PyShacl engine so that a RDF model of a SVG document can be serialized to SVG-code.
def iteratePyShacl(svg_vocabulary, serializable_graph):
        
        # call PyShacl engine and apply the SVG vocabulary to the serializable SVG document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=svg_vocabulary,
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, # Not using the iterate rules function of PyShacl as it seems to not be working properly. Instead, offer each new resulting state freshly to PyShacl.
        debug=False,
        )
      
        # Query to know if the document has been fully serialised by testing whether the root has a svg:fragment property. If it has, the algorithm has reached the final level of the document.
        resultquery = serializable_graph.query('''
            
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX svg: <https://data.rijksfinancien.nl/svg/model/def/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        ASK 
        WHERE {
          ?document a svg:Document ;
                  svg:fragment ?fragment.
        }

        ''')   

        # Check whether another iteration is needed. If the svg root of the document contains a svg:fragment statement then the serialisation is considered done.
        for result in resultquery:
            if result == False:
                writeGraph(serializable_graph)
                iteratePyShacl(svg_vocabulary, serializable_graph)
            else: 
                print ("Document is serialised.")
                writeGraph(serializable_graph)
             

# Get the SVG vocabulary and place it in a string
svg_vocabulary = readGraphFromFile(directory_path + "OntoSVG/Specification/svg - core.ttl")

# loop through any turtle files in the input directory
for filename in os.listdir(directory_path+"OntoSVG/Tools/RDF2SVG/Input"):
    if filename.endswith(".ttl"):
        file_path = os.path.join(directory_path+"OntoSVG/Tools/RDF2SVG/Input", filename)
        
        # Establish the stem of the file name for reuse in newly created files
        filename_stem = os.path.splitext(filename)[0]

        # Get the RDF-model of some SVG document and place it in a string. 
        document_graph = readGraphFromFile(file_path)                  

        # Join the SVG vocabulary and the RDF-model of some SVG document into a string
        serializable_graph_string = svg_vocabulary + document_graph

        # Create a graph of the string containing the SVG vocabulary and the RDF-model of some SVG document
        serializable_graph = rdflib.Graph().parse(data=serializable_graph_string , format="ttl")

        # Inform user
        print ("Serialising the SVG as contained in document '" + filename + "'...")

        # Call the shacl engine with the SVG vocabulary and the document to be serialized
        iteratePyShacl(svg_vocabulary, serializable_graph)

        # Prepare a graph to query the serialized document
        serialized_graph = rdflib.Graph().parse(directory_path+"/OntoSVG/Tools/RDF2SVG/Output/"+filename_stem+"-serialized.ttl" , format="ttl")

        # Query to get the resulting fragment of the document
        documentQuery = serialized_graph.query('''
            
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX svg: <https://data.rijksfinancien.nl/svg/model/def/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        select ?fragment
        WHERE {
          ?document a svg:Document ;
                  svg:fragment ?fragment.
        }

        ''')   

        # Write serialized html to actual html file
        for result in documentQuery:
            with open(directory_path+"/OntoSVG/Tools/RDF2SVG/Output/"+filename_stem+"-serialized.svg", 'w', encoding='utf-8') as file:
               file.write(result.fragment)
               print ("Document is saved to SVG-format as " + filename_stem+"-serialized.svg")

    else:
        print ("No turtle file ('*.ttl') detected")


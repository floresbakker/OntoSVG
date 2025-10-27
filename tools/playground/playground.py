from flask import Flask, request, render_template, url_for
import rdflib
from rdflib import Graph, Namespace, Literal, RDF, Dataset
import pyshacl
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import os

app = Flask(__name__, template_folder='tools/playground/templates', static_folder='tools/playground/static')

# Get the current working directory in which the Playground.py file is located.
current_dir = os.getcwd()

# Set the path to the desired standard directory. 
directory_path = os.path.abspath(os.path.join(current_dir))

# namespace declaration
rdf   = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs  = Namespace("http://www.w3.org/2000/01/rdf-schema#")
doc   = Namespace("https://data.rijksfinancien.nl/svg/doc/id/")
dom   = Namespace("http://www.w3.org/DOM/model/def/") 
svg   = Namespace("http://www.w3.org/SVG/model/def/")
xml   = Namespace("http://www.w3.org/XML/model/def/")
xmlns = Namespace("http://www.w3.org/2000/xmlns/model/def/")
xlink = Namespace("https://www.w3.org/1999/xlink/model/def/")

def writeGraph(graph, name):
    graph.serialize(destination=directory_path + "/tools/playground/" + name + ".trig", format="trig")
    
# Function to read a graph (as a string) from a file 
def readStringFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content


# Get all the vocabularies and place them in a string
dom_vocabulary = readStringFromFile(directory_path   + "/specification/dom - core.trig")
xml_vocabulary = readStringFromFile(directory_path   + "/specification/xml - core.trig")
xmlns_vocabulary = readStringFromFile(directory_path + "/specification/xmlns - core.trig")
xlink_vocabulary = readStringFromFile(directory_path + "/specification/xlink - core.trig")
svg_vocabulary = readStringFromFile(directory_path   + "/specification/svg - core.trig")

vocabulary = dom_vocabulary + '\n' + xml_vocabulary  + '\n' + xmlns_vocabulary + '\n' + xlink_vocabulary + '\n' + svg_vocabulary + '\n'
example_rdf_code = readStringFromFile(directory_path + "/examples/example_rdf_code.trig")
example_svg_code = readStringFromFile(directory_path + "/examples/example_svg_code.svg")


def generate_element_id(element):
    # generate an identifier for an element in the xml
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

def iteratePyShacl(shaclgraph, serializable_graph):
        
        # call PyShacl engine and apply the SVG vocabulary to the serializable SVG document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=shaclgraph,
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
            print ("check if fragment is complete: ", result)
            if result == False:
                return iteratePyShacl(shaclgraph, serializable_graph)
         
            else:
                svgQuery = serializable_graph.query('''
                   
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX svg: <http://www.w3.org/SVG/model/def/>
        PREFIX xml: <http://www.w3.org/XML/model/def/>  

               select ?fragment
               WHERE {
                 ?svgElement a svg:Svg ;
                         xml:fragment ?fragment.
               }

               ''')   

         
                for svg in svgQuery:
                    return svg.fragment


@app.route('/convert2SVG', methods=['POST'])
def convert_to_svg():
    try:
        print("Serializing RDF to SVG code...")  
        text = request.form['rdf']   
        serializable_graph_string = vocabulary + '\n' + text
        serializable_graph = Dataset(default_union=True)
        serializable_graph.parse(data=serializable_graph_string , format="trig")
        svg_fragment = iteratePyShacl(xml_vocabulary, serializable_graph)
        filepath = directory_path+"/tools/playground/static/output.xml"
        src_filepath = url_for('static', filename='output.xml')
        with open(filepath, 'w', encoding='utf-8') as file:
           file.write(svg_fragment)
        writeGraph(serializable_graph, "static/output")
        return render_template('index.html', svgOutput=svg_fragment, svgRawOutput=svg_fragment, rdfInput=text, rdfOutputButton="true")

    except Exception as e:
        print("Error during processing:", e)
        return render_template('index.html', rdfInput=f"Error: {e}")

@app.route('/convert2RDF', methods=['POST'])
def convert_to_rdf():
    try:
        svgInput = request.form['svg']
        # initialize graph
        g = Dataset(default_union=True)
              
        g.bind("rdf", rdf)
        g.bind("rdfs", rdfs)
        g.bind("doc", doc)
        g.bind("svg", svg)
        g.bind("xml", xml)
        g.bind("xmlns", xmlns)
        g.bind("xlink", xlink)

        # fill graph with svg vocabulary
        xml_graph = Dataset(default_union=True)
        xml_graph.parse(directory_path+"/specification/svg - core.trig" , format="trig")

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
        soup = BeautifulSoup(svgInput, features="xml")
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
                    
                    # if the child is an xml tag element get its unique identifier based on sourceline and sourcepos
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
                            childname = "Text"
                      else:
                            childname = child.name
                      child_id = generate_element_id(child)
                      
                      # write to graph that the parent element has a child with a certain sequence position
                      g.add((doc[element_id], rdf["_" + str(member_count)], doc[child_id]))  
                      
                      # write to graph that the child element is of type TextElement
                      g.add((doc[child_id], RDF.type, svg["Text"]))
                      
                      # empty content (of type None) in html needs to be converted to empty string
                      if element.string == None: 
                          text_fragment = "" 
                      else:
                          text_fragment = element.string
                      
                      # write string content of the text element to the graph
                      g.add((doc[child_id], xml["fragment"], Literal(text_fragment)))

        # return the resulting triples
        triples = g.serialize(format="trig").split('\n')
        return render_template('index.html', rdfOutput=triples, svgInput = svgInput, svgRawInput = svgInput, rdfOutputButton="true")
    
    except Exception as e:
        print("Error during processing:", e)
        return render_template('index.html', rdfInput=f"Error: {e}")

@app.route('/')
def index():
    return render_template('index.html', rdfInput=example_rdf_code, svgRawInput=example_svg_code)

if __name__ == '__main__':
    app.run()

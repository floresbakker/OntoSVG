from flask import Flask, request, render_template, jsonify
import rdflib
import pyshacl

app = Flask(__name__)

# Set the path to the desired standard directory. 
directory_path = "C:/Users/Administrator/Documents/Branches/"

# Function to read a graph (as a string) from a file 
def readGraphFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content

# Get the SVG vocabulary and place it in a string
svg_vocabulary = readGraphFromFile(directory_path + "OntoSVG/Specification/svg - core.ttl")
svg_serialisation = readGraphFromFile(directory_path + "OntoSVG/Specification/svg - serialisation.ttl")
xml_vocabulary = readGraphFromFile(directory_path + "OntoSVG/Specification/xml - core.ttl")
xmlns_vocabulary = readGraphFromFile(directory_path + "OntoSVG/Specification/xmlns - core.ttl")
xlink_vocabulary = readGraphFromFile(directory_path + "OntoSVG/Specification/xlink - core.ttl")

vocabulary = svg_vocabulary + svg_serialisation + xml_vocabulary + xmlns_vocabulary + xlink_vocabulary

def iteratePyShacl(shaclgraph, serializable_graph):
        
        # call PyShacl engine and apply the SVG vocabulary to the serializable SVG document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=shaclgraph,
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
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX svg: <https://data.rijksfinancien.nl/svg/model/def/>

        ASK 
        WHERE {
          ?document a svg:Document ;
                  svg:fragment ?fragment.
        }

        ''')   

        # Check whether another iteration is needed. If the svg root of the document contains a svg:fragment statement then the serialisation is considered done.
        for result in resultquery:
            print ("ask result = ", result)
            if result == False:
                return iteratePyShacl(shaclgraph, serializable_graph)
         
            else:
                svgQuery = serializable_graph.query('''
                   
               PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
               PREFIX svg: <https://data.rijksfinancien.nl/svg/model/def/>

               select ?fragment
               WHERE {
                 ?svgElement a svg:Svg ;
                         svg:fragment ?fragment.
               }

               ''')   

         
                for svg in svgQuery:
                    print ("svg.fragment = ", svg.fragment)
                    return svg.fragment


@app.route('/convertSVG', methods=['POST'])
def convert_to_svg():
    text = request.form['text']   
    g = rdflib.Graph().parse(data=text , format="turtle")
    # Zet de RDF-triples om naar een string
    triples = g.serialize(format='turtle')
    serializable_graph_string = vocabulary + triples
    serializable_graph = rdflib.Graph().parse(data=serializable_graph_string , format="turtle")
    svg_fragment = iteratePyShacl(svg_serialisation, serializable_graph)
    print("SVG fragment =", svg_fragment)
    return render_template('index.html', svg=svg_fragment)

if __name__ == '__main__':
    app.run()

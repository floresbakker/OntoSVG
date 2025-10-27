
# Specification 'OntoSVG'

This is the repository for OntoSVG, a RDF-based vocabulary for Scalable Vector Graphics (SVG). You're welcome to contribute! 

OntoSVG offers a toolset comprising of a comprehensive description of the SVG vocabulary - the elements and attributes that constitute SVG documents - and the algorithms with which SVG documents can be generated, as well as tools that make use of this vocabulary to actually parse and generate SVG graphics.

![An example of a SVG-document, modeled and generated using OntoSVG](/examples/SVG_Gallardo.svg)
*An example of a SVG-document, modeled and generated using OntoSVG*

# Status

Unstable, work in progress.

# Background

In today's digital era, Scalable Vector Graphics (SVG) play a vital role in creating interactive and visually appealing web content. SVG provides a powerful framework for defining vector-based graphics using XML syntax, enabling high-quality rendering across various devices and resolutions. Whether it's creating intricate illustrations, interactive data visualizations, or animated icons, SVG empowers designers and developers to unleash their creativity while ensuring optimal performance and accessibility.

At the same time, graphics are not objects without context. It becomes more and more important to be able to model this context of graphics, both the metadata as well as the actual content of such graphics. With this we can generate, annotate, reuse, validate and understand these graphics better, and place them within a wider context of other information. OntoSVG uses semantic web compliant technology to parse, model and generate SVG images in an interoperable and meaningful way, preventing any vendor lock-in. Examples of graphics that can be modeled can be anything, from financial dashboards, architectonic designs up and till car images and the like.


# Introduction

Let us go through the semantic SVG-vocabulary with an example of an ordinary SVG-document.

## Example #1: an ordinary SVG-document with a smiley

```
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
  <svg height="200" width="200" xmlns="http://www.w3.org/2000/svg">
  
  <!-- Circle for the face -->
  <circle cx="100" cy="100" fill="yellow" r="90" stroke="black" stroke-width="2"></circle>
  
   <!-- Eyes -->
  <circle cx="70" cy="70" fill="black" r="10"></circle>
  <circle cx="130" cy="70" fill="black" r="10"></circle>
  
   <!-- Mouth (smile) -->
  <path d="M 60 120 Q 100 150 140 120" fill="none" stroke="black" stroke-width="3"></path></svg>
```

This graphic is rendered in a browser as follows:

![An example of an SVG-document](/examples/SVG_Smiley.svg)

## Expressing the SVG-document in RDF

Now we can represent the very same document in <i>RDF</i> using the SVG-vocabulary. As it is very cumbersome to do so by hand, a <i>SVG2RDF</i> tool is available in this repository that will do exactly that for you. For further information on this tool and other neat tools, scroll down this Readme file.

```
prefix doc: <https://example.org/doc/id> 
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix svg: <http://www.w3.org/SVG/model/def/> 
prefix xml: <http://www.w3.org/XML/model/def/> 

doc:smileyDocument a svg:Document ;
    rdf:_1 doc:docType;
    rdf:_2 doc:smiley .

doc:docType rdf:type xml:DocumentType;
    xml:documentTypeName 'svg'.    

doc:smiley a svg:Svg ;
    rdf:_1 doc:head ;
    rdf:_2 doc:leftEye ;
    rdf:_3 doc:rightEye ;
    rdf:_4 doc:mouth ;
    svg:height "200" ;
    svg:width "200" ;
    xml:xmlns "http://www.w3.org/2000/svg" .

doc:mouth a svg:Path ;
    svg:d "M 60 120 Q 100 150 140 120" ;
    svg:fill "none" ;
    svg:stroke "black" ;
    svg:stroke-width "3" .

doc:head a svg:Circle ;
    svg:cx "100" ;
    svg:cy "100" ;
    svg:fill "yellow" ;
    svg:r "90" ;
    svg:stroke "black" ;
    svg:stroke-width "2" .

doc:leftEye a svg:Circle ;
    svg:cx "70" ;
    svg:cy "70" ;
    svg:fill "black" ;
    svg:r "10" .

doc:rightEye a svg:Circle ;
    svg:cx "130" ;
    svg:cy "70" ;
    svg:fill "black" ;
    svg:r "10" .
```

Make note on how each element in the SVG-document is identified by a unique identifier, the IRI (Internationalized Resource Identifier). Now we can address each element, or combinations of elements, and say something about them. Either we express meaning (RDF, RDFS, OWL and more), or impose constraints (SHACL) or we can query (SPARQL) them to know more about them.

## Example #2: a bar chart with financial figures

```
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg height="350" version="1.1" width="500" xmlns="http://www.w3.org/2000/svg">   <text fill="black" font-size="16" transform="rotate(-90)" x="-180" y="20">Amount (Euro)</text>    <text fill="black" font-size="16" x="200" y="330">Transaction type</text>    <line x1="50" x2="50" y1="50" y2="300" stroke="black" stroke-width="2"></line>    <line x1="50" x2="450" y1="300" y2="300" stroke="black" stroke-width="2"></line>    <rect fill="blue" height="50" width="50" x="80" y="250"></rect>  <text fill="black" font-size="16" x="90" y="210" text-anchor="middle">Budgeted Expenditures</text>  <text fill="black" font-size="14" x="105" y="245" text-anchor="middle">200</text>    <rect fill="red" height="25" width="50" x="180" y="275"></rect>  <text fill="black" font-size="16" x="190" y="230" text-anchor="middle">Realized Expenditures</text>  <text fill="black" font-size="14" x="205" y="270" text-anchor="middle">100</text>    <rect fill="green" height="35" width="50" x="280" y="265"></rect>  <text fill="black" font-size="16" x="290" y="210" text-anchor="middle">Budgeted Receipts</text>  <text fill="black" font-size="14" x="305" y="260" text-anchor="middle">150</text>    <rect fill="orange" height="20" width="50" x="380" y="280"></rect>  <text fill="black" font-size="16" x="390" y="230" text-anchor="middle">Realized Receipts</text>  <text fill="black" font-size="14" x="405" y="275" text-anchor="middle">80</text></svg>
```

This bar chart is rendered in a browser as follows:

![An example of an HTML-document with forms](/examples/SVG_BarChart.svg)

## Again expressing the SVG-document in RDF


```
prefix doc: <https://example.org/doc/id> 
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix svg: <http://www.w3.org/SVG/model/def/> 
prefix xml: <http://www.w3.org/XML/model/def/> 

doc:BarChartDocument a svg:Document ;
    rdf:_1 doc:docType ;
    rdf:_2 doc:barChart .

doc:docType rdf:type xml:DocumentType;
    xml:documentTypeName 'svg'.    

doc:barChart a svg:Svg ;
    xml:xmlns "http://www.w3.org/2000/svg";
    xml:version "1.1";
    svg:height "350" ;
    svg:width "500" ;
    rdf:_1 doc:y-axis-Text ;
    rdf:_2 doc:x-axis-Text ;
    rdf:_3 doc:y-axis-Line ;
    rdf:_4 doc:x-axis-Line ;
    rdf:_5 doc:budgetedExpendituresRectangle ;
    rdf:_6 doc:budgetedExpendituresText ;
    rdf:_7 doc:budgetedExpendituresAmount ;
    rdf:_8 doc:realizedExpendituresRectangle ;
    rdf:_9 doc:realizedExpendituresText ;
    rdf:_10 doc:realizedExpendituresAmount ;
    rdf:_11 doc:budgetedReceiptsRectangle ;
    rdf:_12 doc:budgetedReceiptsText ;
    rdf:_13 doc:budgetedReceiptsAmount ;
    rdf:_14 doc:realizedReceiptsRectangle ;
    rdf:_15 doc:realizedReceiptsText ;
    rdf:_16 doc:realizedReceiptsAmount .

doc:y-axis-Text a svg:Text ;
    rdf:_1 doc:amountText ;
    svg:fill "black" ;
    svg:font-size "16" ;
    svg:transform "rotate(-90)" ;
    svg:x "-180" ;
    svg:y "20" .

doc:y-axis-Line a svg:Line ;
    svg:stroke "black" ;
    svg:stroke-width "2" ;
    svg:x1 "50" ;
    svg:x2 "50" ;
    svg:y1 "50" ;
    svg:y2 "300" .

doc:x-axis-Text a svg:Text ;
    rdf:_1 doc:transactionTypeText ;
    svg:fill "black" ;
    svg:font-size "16" ;
    svg:x "200" ;
    svg:y "330" .

doc:x-axis-Line a svg:Line ;
    svg:stroke "black" ;
    svg:stroke-width "2" ;
    svg:x1 "50" ;
    svg:x2 "450" ;
    svg:y1 "300" ;
    svg:y2 "300" .

doc:budgetedExpendituresRectangle a svg:Rect ;
    svg:fill "blue" ;
    svg:height "50" ;
    svg:width "50" ;
    svg:x "80" ;
    svg:y "250" .

doc:budgetedExpendituresText a svg:Text ;
    rdf:_1 doc:budgetedExpendituresTextString ;
    svg:fill "black" ;
    svg:font-size "16" ;
    svg:text-anchor "middle" ;
    svg:x "90" ;
    svg:y "210" .

doc:budgetedExpendituresAmount a svg:Text ;
    rdf:_1 doc:budgetedExpendituresAmountValue  ;
    svg:fill "black" ;
    svg:font-size "14" ;
    svg:text-anchor "middle" ;
    svg:x "105" ;
    svg:y "245" .

doc:realizedExpendituresRectangle a svg:Rect ;
    svg:fill "red" ;
    svg:height "25" ;
    svg:width "50" ;
    svg:x "180" ;
    svg:y "275" .

doc:realizedExpendituresText a svg:Text ;
    rdf:_1 doc:realizedExpendituresTextString ;
    svg:fill "black" ;
    svg:font-size "16" ;
    svg:text-anchor "middle" ;
    svg:x "190" ;
    svg:y "230" .

doc:realizedExpendituresAmount a svg:Text ;
    rdf:_1 doc:realizedExpendituresAmountValue ;
    svg:fill "black" ;
    svg:font-size "14" ;
    svg:text-anchor "middle" ;
    svg:x "205" ;
    svg:y "270" .

doc:budgetedReceiptsRectangle a svg:Rect ;
    svg:fill "green" ;
    svg:height "35" ;
    svg:width "50" ;
    svg:x "280" ;
    svg:y "265" .

doc:budgetedReceiptsText a svg:Text ;
    rdf:_1 doc:budgetedReceiptsTextString ;
    svg:fill "black" ;
    svg:font-size "16" ;
    svg:text-anchor "middle" ;
    svg:x "290" ;
    svg:y "210" .

doc:budgetedReceiptsAmount a svg:Text ;
    rdf:_1 doc:budgetedReceiptsAmountValue ;
    svg:fill "black" ;
    svg:font-size "14" ;
    svg:text-anchor "middle" ;
    svg:x "305" ;
    svg:y "260" .

doc:realizedReceiptsRectangle a svg:Rect ;
    svg:fill "orange" ;
    svg:height "20" ;
    svg:width "50" ;
    svg:x "380" ;
    svg:y "280" .

doc:realizedReceiptsText a svg:Text ;
    rdf:_1 doc:realizedReceiptsTextString ;
    svg:fill "black" ;
    svg:font-size "16" ;
    svg:text-anchor "middle" ;
    svg:x "390" ;
    svg:y "230" .

doc:realizedReceiptsAmount a svg:Text ;
    rdf:_1 doc:realizedReceiptsAmountValue ;
    svg:fill "black" ;
    svg:font-size "14" ;
    svg:text-anchor "middle" ;
    svg:x "405" ;
    svg:y "275" .

doc:amountText a svg:TextElement ;
    svg:fragment "Amount (Euro)" .

doc:transactionTypeText a svg:TextElement ;
    svg:fragment "Transaction type" .

doc:budgetedExpendituresTextString a svg:TextElement ;
    svg:fragment "Budgeted Expenditures" .

doc:budgetedExpendituresAmountValue a svg:TextElement ;
    svg:fragment "200" .

doc:realizedExpendituresTextString a svg:TextElement ;
    svg:fragment "Realized Expenditures" .

doc:realizedExpendituresAmountValue a svg:TextElement ;
    svg:fragment "100" .

doc:budgetedReceiptsTextString a svg:TextElement ;
    svg:fragment "Budgeted Receipts" .

doc:budgetedReceiptsAmountValue a svg:TextElement ;
    svg:fragment "150" .

doc:realizedReceiptsTextString a svg:TextElement ;
    svg:fragment "Realized Receipts" .

doc:realizedReceiptsAmountValue a svg:TextElement ;
    svg:fragment "80" .

```

# Tools and dependencies

This repository comes with three, fairly primitive, Python-based tools to handle SVG-documents and RDF-representations of SVG. 

1. SVG2RDF 
2. RDF2SVG
3. Playground



## SVG2RDF

The tool SVG2RDF is used to read SVG-documents, parse them and then transform them to RDF-based triples. 

### How to use SVG2RDF

A. Install all necessary libraries:

	1. pip install os 
	2. pip install bs4
	3. pip install rdflib

B. Place one or more SVG-files in the input folder in OntoSVG\tools\SVG2RDF\input. Only ordinary SVG-files can be processed. 

C. Run the script in the command prompt by typing: 

```
python SVG2RDF.py
```

D. Go to the output folder in OntoSVG\tools\SVG2RDF\output and grab your Turtle-file(s) (*.ttl). 


## RDF2SVG

The tool RDF2SVG is used to read a RDF-based representation of an SVG-document into a graph and then serialize and save this to an actual SVG-file. 

### How to use RDF2SVG

A. Install all necessary libraries (in this order):

	1. pip install os 
	2. pip install pyshacl
	3. pip install rdflib

B. Place one or more Turtle-files (*.ttl) in the input folder in OntoSVG\tools\RDF2SVG\input. A Turtle-file should represent a SVG-document using the SVG-vocabulary from this repository.

C. Run the script in the command prompt by typing: 

```
python RDF2SVG.py
```

D. Go to the output folder in OntoSVG\Tools\RDF2SVG\Output and grab your SVG-file(s). Additionally included are Turtle-file(s) (*.ttl) that contain the serialized 'svg:fragment' properties for the very same SVG-document and the SVG-elements it contains. 

## Playground

The tool Playground offers a visual user interface in which a RDF-based representation of an SVG-document can be converted to an actual SVG-image, and an actual SVG-image can be converted to a RDF-based representation of an SVG-document.

![A screenshot of the playground environment](/examples/Playground.JPG)

### How to use Playground

A. Install all necessary libraries (in this order):

	1. pip install os 
	2. pip install pyshacl
	3. pip install rdflib

B. Run the script in the command prompt by typing: 

```
python playground.py
```

C. Navigate to the URL http://localhost:5000/. Then choose one of two options:

   *Option 1*: Place your RDF-triples representing a SVG-document into the corresponding text area and press the button 'convert to SVG'. The playground will convert the triples to an SVG image and display this in your browser. This may take some time.

   *Option 2*: Place the SVG-code of your SVG-image into the corresponding text area and press the button 'convert to RDF'. The playground will convert the SVG image to a RDF-based representation of that image. This should be rather quick.


## Dependencies 

Both tools make extensive use of [RDFlib](https://rdflib.readthedocs.io/en/stable/index.html). Rdflib is a Python library used for working with Resource Description Framework (RDF) data. RDF is a widely used framework for representing and processing information on the web. It is a standard model for data interchange on the web, particularly for representing metadata and data about resources available on the internet.

Rdflib provides a comprehensive set of tools and utilities for working with RDF data, including parsing and serializing RDF in various formats (such as RDF/XML, Turtle, JSON-LD, and more), querying RDF data using SPARQL, creating RDF graphs, and performing various operations on RDF triples.

The RDF2SVG tool additionally makes use of [PyShacl](https://github.com/RDFLib/pySHACL). PySHACL is a complete open-source implementation of the SHACL W3C specification, with broad use in the community as well. 

# Acknowledgements

We would like to thank Iwan Aucamp @RDFlib for his unrelenting support and accomplishments regarding the open source triple store and related services, as well as Ashley Sommer @PyShacl for his work on the important open source implementation of a SHACL engine. 
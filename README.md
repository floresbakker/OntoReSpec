# About

OntoReSpec is a collection of RDF-based vocabularies to generate ReSpec specification documents for ontologies.

# Status

Unstable, no release yet. Work in progress. First working version planned for Q2 2024.

# Background

[ReSpec](https://respec.org/docs/) makes it easier to write technical documents. It was originally designed for writing W3C specifications, but now supports many output formats.

A ReSpec document is a HTML document that brings in the [ReSpec script](https://github.com/w3c/respec), defines a few configuration variables, and follows a few conventions. The ReSpec script is based on a Javascript library. ReSpec is regularly updated and this will allow you to automatically benefit from bug and security fixes and enhancements.

An ontology could be described in a ReSpec specification document. Currently, there are no RDF-based solutions to automate that process.

# OntoReSpec

As ReSpec documents are just HTML documents, they rely on HTML structural elements. With OntoReSpec, any arbitrary ontology or datamodel in RDF can be processed and presented in a ReSpec document, using semantic web technology.

# Example: the HTML vocabulary

Here is an example of a ReSpec-document of the HTML-vocabulary, generated by OntoReSpec. 

![An example of an Respec-document](/Examples/ExampleReSpec-HTMLDocument.JPG)

# Tools and dependencies

This repository comes with two, fairly primitive, Python-based tools to transform an ontology into a ReSpec-document.

1. Playground.py
2. OntoReSpec.py


## Playground.py

![An example of the OntoReSpec playground](/Examples/Playground.JPG)

The tool aims to be a complete environment in which you can generate a ReSpec based specification of your ontology, including textual context, definitions for concepts, classes, object properties, datatype properties, RDF properties, nodeshape and named indivduals, a Mermaid diagram, a link to the serialisation of the ontology, an index of namespaces and more.

A. Install all necessary libraries:

	1. pip install os
	2. pip install pyshacl
	3. pip install rdflib
    4. pip install flask
    5. pip install datetime
    
B. Run the script in the command prompt by typing: 

```
python Playground.py
```

C. Go to localhost:5000 in your browser. 

D. You are now ready to use the application. 


## OntoReSpec.py

The tool OntoReSpec.py is used to read OWL ontologies and generate a presentation of them in a ReSpec-document.

### How to use OntoReSpec.py

A. Install all necessary libraries:

	1. pip install os
	2. pip install pyshacl
    3. pip install rdflib

B. Place one or more OWL-ontologies in the input folder in \OntoReSpec\Tools\Input. 

C. Run the script in the command prompt by typing: 

```
python OntoReSpec.py
```

D. Go to the output folder in \OntoReSpec\Tools\Output and grab your Turtle-file(s) (*.ttl). 

NOTE: If you want to use the OntoReSpec.py script:
1.  First go to https://github.com/floresbakker/manchestersyntax, download the repository and run the manchester syntax script for your ontology. This will enrich your ontology with Manchester Syntax properties. Get the file from the output folder. 
2. Place the output of the manchestersyntax script as input into the OntoReSpec input folder, and run the OntoReSpec script. Get the file from the output folder.
3. Then go to https://github.com/floresbakker/htmlvoc, download the repository.
4. Place the output of the OntoReSpec script into the input folder of the RDF2HTML script (or use the playground application of that repository) and run that script. This will generate the HTML file of your ReSpec-document.

NOTE: This is work in progress. 
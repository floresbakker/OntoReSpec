# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 18:40:53 2023

@author: Flores Bakker


"""
import pyshacl
import rdflib 


# Function to read a graph (as a string) from a file 
def readGraphFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content

# Function to write a graph to a file
def writeGraph(graph):
    graph.serialize(destination="C:/Users/Administrator/Documents/Branches/OntoRespec/Tools/OntoRespec/Output/respecDocument.ttl", format="turtle")

# Function to call the PyShacl engine so that a RDF model of an HTML-based ReSpec-document can be serialized to HTML-code.
def iteratePyShacl(respec_generator, serializable_graph):
        
        # call PyShacl engine and apply the HTML vocabulary to the serializable HTML document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=respec_generator,
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, # Not using the iterate rules function of PyShacl as it seems to not be working properly. Instead, offer each new resulting state freshly to PyShacl.
        debug=False,
        )
       
        writeGraph(serializable_graph)
             

# Get the OntoRespec vocabulary and place it in a string
respec_generator = readGraphFromFile("C:/Users/Administrator/Documents/Branches/ontoRespec/Specification/OntoRespec.ttl")

# Get the RDF-model of some HTML-based ReSpec document and place it in a string. 
ontology_graph = readGraphFromFile("C:/Users/Administrator/Documents/Branches/htmlvocl/Specification/html.ttl")   
template_graph = readGraphFromFile("C:/Users/Administrator/Documents/Branches/ontoRespec/Specification/ReSpecTemplate.ttl")

# Join the HTML vocabulary and the RDF-model of the HTML-based ReSpec-document into a string
serializable_graph_string = ontology_graph + template_graph

# Create a graph of the string containing the HTML vocabulary and the RDF-model of the HTML-based ReSpec-document
serializable_graph = rdflib.Graph().parse(data=serializable_graph_string , format="ttl")

# Inform user
print ('Instantiating ReSpec document...')

# Call the shacl engine with the HTML vocabulary and the document to be serialized
iteratePyShacl(respec_generator, serializable_graph)

print ('ReSpec document instantiated.')

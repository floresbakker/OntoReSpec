# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 18:40:53 2023

@author: Flores Bakker


"""
import os
import pyshacl
import rdflib 

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
    graph.serialize(destination=directory_path + "OntoReSpec/Tools/Output/respecDocument.ttl", format="turtle")

# Function to call the PyShacl engine so that an instantiation of the ReSpec-template can be created.
def iteratePyShacl(respec_html_generator, serializable_graph):
        
        # call PyShacl engine and apply the HTML vocabulary to the serializable HTML document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=respec_html_generator,
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, 
        debug=False,
        )
       
        writeGraph(serializable_graph)
             

# Get the OntoRespec vocabulary and place it in a string
respec_generator = readGraphFromFile(directory_path +"OntoReSpec/Specification/OntoRespec.ttl")
# Get the HTML vocabulary and place it in a string
html_vocabulary = readGraphFromFile(directory_path + "htmlvoc/Specification/html.ttl")

respec_html_generator = respec_generator + html_vocabulary

# loop through any ReSpec RDF files in the input directory
for filename in os.listdir(directory_path+"OntoReSpec/Tools/Input"):
    if filename.endswith(".ttl"):
        file_path = os.path.join(directory_path+"OntoReSpec/Tools/Input", filename)
        
        # Establish the stem of the file name for reuse in newly created files
        filename_stem = os.path.splitext(filename)[0]

# Get any RDF-based ReSpec document and place it in a string. 
ontology_graph = readGraphFromFile(file_path)   
template_graph = readGraphFromFile(directory_path + "OntoReSpec/Specification/ReSpecTemplate.ttl" )

# Join the HTML vocabulary and the RDF-model of the HTML-based ReSpec-document into a string
serializable_graph_string = ontology_graph + template_graph + html_vocabulary

# Create a graph of the string containing the HTML vocabulary and the RDF-model of the HTML-based ReSpec-document
serializable_graph = rdflib.Graph().parse(data=serializable_graph_string , format="ttl")

# Inform user
print ('Instantiating ReSpec document...')

# Call the shacl engine with the HTML vocabulary and the document to be serialized
iteratePyShacl(respec_html_generator, serializable_graph)

print ('ReSpec document instantiated.')

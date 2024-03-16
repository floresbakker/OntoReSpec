from flask import Flask, request, render_template, send_file
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF
import os
import pyshacl
import rdflib 

app = Flask(__name__, template_folder='C:/Users/Administrator/Documents/Branches/Standalone/templates/')

# Define the path to the destination folder
destination_folder = 'C:/Users/Administrator/Documents/Branches/Standalone/Output/'

@app.route('/')
def index():
    return render_template('ontology_form.html')

@app.route('/generate_turtle', methods=['POST'])
def generate_turtle():
    ontology = request.form.get('ontology')
    audience = request.form.get('audience')
    introduction = request.form.get('introduction')
    background = request.form.get('background')
    objective = request.form.get('objective')
    acknowledgements = request.form.get('acknowledgements')

    g = Graph()
    ontology_iri = Namespace(ontology)
    respec = Namespace('https://respec.org/model/def/')

    g.add((URIRef(ontology_iri), respec.audience, Literal(audience)))
    g.add((URIRef(ontology_iri), respec.introduction, Literal(introduction)))
    g.add((URIRef(ontology_iri), respec.background, Literal(background)))
    g.add((URIRef(ontology_iri), respec.objective, Literal(objective)))
    g.add((URIRef(ontology_iri), respec.acknowledgements, Literal(acknowledgements)))

    turtle_data = g.serialize(format='turtle')

# Save the Turtle data to a file in the destination folder
    file_path = f'{destination_folder}respec_metadata.ttl'
    with open(file_path, 'w') as file:
        file.write(turtle_data)

    # Optionally, you can send the file to the user for download
    return send_file(file_path, as_attachment=True)

# Add a new route to trigger the provided Python code
@app.route('/instantiate_respec')
def instantiate_respec():
    # Your Python code here to perform ReSpec instantiation
    # ...

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
    respec_generator = readGraphFromFile(directory_path +"OntoReSpec/Specification/OntoRespec.ttl")

    # loop through any ReSpec RDF files in the input directory
    for filename in os.listdir(directory_path+"OntoReSpec/Tools/Input"):
        if filename.endswith(".ttl"):
            file_path = os.path.join(directory_path+"OntoReSpec/Tools/Input", filename)
            
            # Establish the stem of the file name for reuse in newly created files
            filename_stem = os.path.splitext(filename)[0]

    # Get any RDF-based ReSpec document and place it in a string. 
    ontology_graph = readGraphFromFile(file_path)   
    template_graph = readGraphFromFile(directory_path + "OntoReSpec/Specification/ReSpecTemplate.ttl")

    # Join the HTML vocabulary and the RDF-model of the HTML-based ReSpec-document into a string
    serializable_graph_string = ontology_graph + template_graph

    # Create a graph of the string containing the HTML vocabulary and the RDF-model of the HTML-based ReSpec-document
    serializable_graph = rdflib.Graph().parse(data=serializable_graph_string , format="ttl")

    # Inform user
    print ('Instantiating ReSpec document...')

    # Call the shacl engine with the HTML vocabulary and the document to be serialized
    iteratePyShacl(respec_generator, serializable_graph)

    print ('ReSpec document instantiated.')


    result = "ReSpec document instantiated."  # A message you want to display

    
    return result

if __name__ == '__main__':
    app.run(debug=True, use_reloader = False)

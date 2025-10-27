from flask import Flask, request, render_template, url_for
from rdflib import Graph, Namespace, Literal, RDF, URIRef, XSD, Dataset
import pyshacl
import datetime
import os

app = Flask(__name__, template_folder='tools/playground/templates', static_folder='tools/playground/static')

# Get the current working directory in which the Playground.py file is located.
current_dir = os.getcwd()

# Set the path to the desired standard directory. 
directory_path = os.path.abspath(os.path.join(current_dir))

# namespace declaration
rdf        = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs       = Namespace("http://www.w3.org/2000/01/rdf-schema#")
dct        = Namespace("http://purl.org/dc/terms/")
respec     = Namespace('https://respec.org/ontorespec/model/def/')
template   = Namespace('https://respec.org/ontorespec/id/')
html       = Namespace("https://www.w3.org/html/model/def/")
mermaid    = Namespace("https://mermaid.org/ontomermaid/model/def/")
manchester = Namespace("https://data.rijksfinancien.nl/manchester/model/def/")

# Function to read a graph (as a string) from a file 
def readStringFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content


# Function to write a graph to a file
def writeGraph(graph, name):
    graph.serialize(destination=directory_path + "/tools/playground/static/" + name + ".trig", format="trig")


# Get the ReSpec vocabulary and place it in a string
respec_vocabulary     = readStringFromFile(directory_path + "/specification/ontorespec.trig")
template_graph        = readStringFromFile(directory_path + "/specification/ontorespectemplate.trig" )
html_serialisation    = readStringFromFile(directory_path + "/specification/html - core.trig")
html_vocabulary       = readStringFromFile(directory_path + "/specification/html - core.trig")
dom_vocabulary        = readStringFromFile(directory_path + "/specification/dom - core.trig")
manchester_vocabulary = readStringFromFile(directory_path + "/specification/manchestersyntax.trig")
mermaid_vocabulary    = readStringFromFile(directory_path + "/specification/mermaid.trig")
manchester_query      = readStringFromFile(directory_path + "/tools/playground/static/manchesterQuery.rq")
mermaid_status_query  = readStringFromFile(directory_path + "/tools/playground/static/mermaidStatusQuery.rq")
mermaid_result_query  = readStringFromFile(directory_path + "/tools/playground/static/mermaidResultQuery.rq")
html_status_query     = readStringFromFile(directory_path + "/tools/playground/static/htmlStatusQuery.rq")
html_result_query     = readStringFromFile(directory_path + "/tools/playground/static/htmlResultQuery.rq")
ontology_query        = readStringFromFile(directory_path + "/tools/playground/static/ontologyQuery.rq")


def generateManchester(manchester_generator, serializable_graph):
        
        # call PyShacl engine and apply the HTML vocabulary to the serializable HTML document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=manchester_generator,
        data_graph_format="trig",
        shacl_graph_format="trig",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, #rather than setting this to true, it is better to do the iteration in the script as PyShacl seems to have some buggy behavior around iteration.
        debug=False,
        )
        
        resultquery = serializable_graph.query(manchester_query)   

        # Check whether another iteration is needed. If every OWL and RDFS construct contains a manchester:syntax statement, the processing is considered done.
        for result in resultquery:
            if result == True:
                return generateManchester(manchester_generator, serializable_graph)
            else: 
                 print ('...succes')
                 return serializable_graph


def generateReSpecRDF(shaclgraph, serializable_graph):
        
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
        print ('...succes')
        return serializable_graph


def generateDiagram(mermaid_generator, serializable_graph):
        
        print ('iteration mermaid')
        # call PyShacl engine and apply the HTML vocabulary to the serializable HTML document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=mermaid_generator,
        data_graph_format="trig",
        shacl_graph_format="trig",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, # rather than setting this to true, it is better to do the iteration in the script as PyShacl seems to have some buggy behavior around iteration.
        debug=False,
        )
        
        statusquery = serializable_graph.query(mermaid_status_query)
        resultquery = serializable_graph.query(mermaid_result_query)  

        # Check whether another iteration is needed. If every OWL and RDFS construct contains a mermaid:syntax statement, the processing is considered done.
        for status in statusquery:
            if status == False:
                
                writeGraph(serializable_graph, 'diagram')
                generateDiagram(mermaid_generator, serializable_graph)
            else:     
                 print ('...succes')
                 for result in resultquery:
                    mermaid_diagram = result["mermaid_code"]
                    output_file_path = directory_path+"/tools/playground/static/diagram.html"
                
                    # Write the HTML content to the output file
                    with open(output_file_path, "w", encoding="utf-8") as file:
                        file.write(mermaid_diagram) 

def generateHTML(shaclgraph, serializable_graph):
        
        # call PyShacl engine and apply the html vocabulary to the serializable html document
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
      
        # Query to know if the document has been fully serialised by testing whether the root has a html:fragment property. If it has, the algorithm has reached the final level of the document.
        statusQuery = serializable_graph.query(html_status_query) 

        # Check whether another iteration is needed. If the html root of the document contains a html:fragment statement then the serialisation is considered done.
        for status in statusQuery:
            if status == False:
                writeGraph(serializable_graph, 'html')
                return generateHTML(shaclgraph, serializable_graph)
         
            else:
                writeGraph(serializable_graph, 'html')
                htmlQuery = serializable_graph.query(html_result_query)
                for html in htmlQuery:
                    print ('...succes')
                    return html.fragment



@app.route('/generateReSpec', methods=['POST'])
def generateReSpec():
    print("Starting generation of the ReSpec document...")
    
    #1 Retrieve content from user
    ontology           = request.form['ontology']
    introduction       = request.form['introduction']
    background         = request.form['background']
    audience           = request.form['audience']
    objective          = request.form['objective']
    acknowledgements   = request.form['acknowledgements']
    documentLanguage   = request.form['documentLanguage']
    documentNamespace  = request.form['documentNamespace']

    #2 Retrieve which components of the ontology need to be specified in the document
    conceptSchemes     = request.form.get('conceptSchemes')     == 'true'
    concepts           = request.form.get('concepts')           == 'true'
    classes            = request.form.get('classes')            == 'true'
    objectProperties   = request.form.get('objectProperties')   == 'true'
    datatypeProperties = request.form.get('datatypeProperties') == 'true'
    rdfProperties      = request.form.get('rdfProperties')      == 'true'
    nodeshapes         = request.form.get('nodeshapes')         == 'true'
    namedIndividuals   = request.form.get('namedIndividuals')   == 'true'
    
    # Write ontology to file
    ontology_filepath = directory_path + "/tools/playground/static/ontology.trig"
    with open(ontology_filepath, 'w', encoding='utf-8') as file:
       file.write(str(ontology))

    # Initialize graph
    generation_iri = hash(str(ontology) + str(datetime.datetime.now()))
    generationGraph = Dataset(default_union=True)
    doc = Namespace(documentNamespace)
    generationGraph.bind("html", html)
    generationGraph.bind("respec", respec)    
    generationGraph.bind("mermaid", mermaid)    
    generationGraph.bind("manchester", manchester)      
    generationGraph.bind("template", template)   
    generationGraph.bind("doc", doc)    
    
    # Add triples to be able to kickstart the SHACL engine later.
    
    #1 Add content from user
    generationGraph.add((doc[generation_iri], RDF.type, respec.Generation))
    generationGraph.add((doc[generation_iri], respec.documentLanguage, Literal(documentLanguage)))
    generationGraph.add((doc[generation_iri], respec.documentNamespace, Literal(documentNamespace)))
    if audience != "":
        generationGraph.add((doc[generation_iri], respec.audience, Literal(audience, lang=documentLanguage)))
    if introduction != "":
        generationGraph.add((doc[generation_iri], respec.introduction, Literal(introduction, lang=documentLanguage)))
    if background != "":
        generationGraph.add((doc[generation_iri], respec.background, Literal(background, lang=documentLanguage)))
    if objective != "":
        generationGraph.add((doc[generation_iri], respec.objective, Literal(objective, lang=documentLanguage)))
    if acknowledgements != "":
        generationGraph.add((doc[generation_iri], respec.acknowledgements, Literal(acknowledgements, lang=documentLanguage)))

    #2 Establish which components of the ontology need to be specified in the document
    if conceptSchemes:
        generationGraph.add((doc[generation_iri], respec.include, Literal("conceptschemes")))
    
    if concepts:
        generationGraph.add((doc[generation_iri], respec.include, Literal("concepts")))
    
    if classes:
        generationGraph.add((doc[generation_iri], respec.include, Literal("classes")))
    
    if objectProperties:
        generationGraph.add((doc[generation_iri], respec.include, Literal("objectproperties")))
    
    if datatypeProperties:
        generationGraph.add((doc[generation_iri], respec.include, Literal("datatypeproperties")))
    
    if rdfProperties:
        generationGraph.add((doc[generation_iri], respec.include, Literal("rdfproperties")))
    
    if nodeshapes:
        generationGraph.add((doc[generation_iri], respec.include, Literal("nodeshapes")))
    
    if namedIndividuals:
        generationGraph.add((doc[generation_iri], respec.include, Literal("namedindividuals")))

    #2 Establish which components of the ontology need to be visualised in the document as a Mermaid diagram
    if conceptSchemes:
        generationGraph.add((doc[generation_iri], mermaid.include, Literal("CONCEPTSCHEME")))
    
    if concepts and not conceptSchemes:
        generationGraph.add((doc[generation_iri], mermaid.include, Literal("CONCEPT")))
    
    if classes:
        generationGraph.add((doc[generation_iri], mermaid.include, Literal("CLASS")))
    
    if objectProperties:
        generationGraph.add((doc[generation_iri], mermaid.include, Literal("OBJECTPROPERTY")))
    
    if datatypeProperties:
        generationGraph.add((doc[generation_iri], mermaid.include, Literal("DATATYPEPROPERTY")))
    
    if rdfProperties:
        generationGraph.add((doc[generation_iri], mermaid.include, Literal("RDF_PROPERTY")))
    
    if nodeshapes:
        generationGraph.add((doc[generation_iri], mermaid.include, Literal("NODESHAPE")))
    
    if namedIndividuals:
        generationGraph.add((doc[generation_iri], mermaid.include, Literal("NAMEDINDIVIDUAL")))

    # Let us establish which ontology needs to be documented in ReSpec
    try:
       generationGraph.parse(data=ontology , format="trig")
    except Exception as e:
        error_message = str(e)
        return render_template('index.html', 
                               ontology           = ontology, 
                               introduction       = introduction,
                               background         = background,
                               audience           = audience,
                               objective          = objective,
                               acknowledgements   = acknowledgements,
                               conceptSchemes     = conceptSchemes,
                               concepts           = concepts,
                               classes            = classes,
                               objectProperties   = objectProperties,
                               datatypeProperties = datatypeProperties,
                               rdfProperties      = rdfProperties,
                               nodeshapes         = nodeshapes,
                               namedIndividuals   = namedIndividuals,
                               status='Error: Unable to parse the ontology {}'.format(error_message))
    
    ontologyQuery = generationGraph.query(ontology_query) 

    for result in ontologyQuery:
        generationGraph.add((doc[generation_iri], dct.subject, URIRef(result.ontology)))
    
    # Generating Mermaid diagram 
    print("Step #1. Creating Mermaid diagram...")
    generateDiagram(mermaid_vocabulary, generationGraph)
    writeGraph(generationGraph, 'diagram')
    
    # Enriching the ontology with manchester metadata
    print("Step #2. Creating Manchester Syntax labels...")
   
    generationGraph = generateManchester(manchester_vocabulary, generationGraph)
    writeGraph(generationGraph, 'manchestersyntax')
    
    # Build the ReSpec structure of the document in RDF
    print("Step #3. Creating ReSpec document structure...")

    generationGraph.parse(data=html_vocabulary, format="trig")
    generationGraph.parse(data=dom_vocabulary,  format="trig")
    generationGraph.parse(data=template_graph,  format="trig")
    generationGraph = generateReSpecRDF(respec_vocabulary, generationGraph)
    writeGraph(generationGraph, 'respec')
    
    # Serialize the document to HTML
    print("Step #4. Creating HTML code...")

    html_fragment = generateHTML(html_vocabulary, generationGraph)
    print("...Done")
    filepath = directory_path+"/tools/playground/static/output.html"
    src_filepath = url_for('static', filename='output.html')
    with open(filepath, 'w', encoding='utf-8') as file:
       file.write(html_fragment)
    return render_template('index.html', htmlOutput='<iframe src='+ src_filepath + ' width="100%" height="600"></iframe>',
                           ontology=ontology, 
                           introduction=introduction,
                           background=background,
                           audience=audience,
                           objective=objective,
                           acknowledgements=acknowledgements,
                           conceptSchemes = conceptSchemes,
                           concepts = concepts,
                           classes = classes,
                           objectProperties = objectProperties,
                           datatypeProperties = datatypeProperties,
                           rdfProperties = rdfProperties,
                           nodeshapes = nodeshapes,
                           namedIndividuals = namedIndividuals,
                           status ='Ready'
                           )

@app.route('/')
def index():
    return render_template('index.html', 
                           ontology          = 'Place your ontology in trig format here', 
                           introduction      = 'Write here an introduction to your ontology.',
                           background        = 'Write here some background context for your ontology.',
                           audience          = 'Write here about the indended audience to your ontology.',
                           objective         = 'Write here about the objective of your ontology.',
                           acknowledgements  = 'Write here your acknowledgements in relation to your ontology.',
                           conceptSchemes    = True,
                           concepts          = True,
                           classes           = True,
                           objectProperties  = True,
                           datatypeProperties= True,
                           rdfProperties     = True,
                           nodeshapes        = True,
                           namedIndividuals  = True,
                           status='Ready'
                           )

if __name__ == '__main__':
    app.run()

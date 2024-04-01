from flask import Flask, request, render_template, url_for
import rdflib
from rdflib import Graph, Namespace, Literal, RDF, URIRef
import pyshacl
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import datetime

app = Flask(__name__)

# Set the path to the desired standard directory. 
directory_path = "C:/Users/Administrator/Documents/Branches/"

# namespace declaration
rdf    = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs   = Namespace("http://www.w3.org/2000/01/rdf-schema#")
dct    = Namespace("http://purl.org/dc/terms/")
respec = Namespace('https://respec.org/model/def/')
html   = Namespace("https://data.rijksfinancien.nl/html/model/def/")


# Function to read a graph (as a string) from a file 
def readStringFromFile(file_path):
    # Open each file in read mode
    with open(file_path, 'r', encoding='utf-8') as file:
            # Read the content of the file and append it to the existing string
            file_content = file.read()
    return file_content

# Function to write a graph to a file
def writeGraph(graph):
    graph.serialize(destination=directory_path + "OntoReSpec/Tools/Playground/Output/respecDocument.ttl", format="turtle")

# Get the SVG vocabulary and place it in a string
respec_vocabulary     = readStringFromFile(directory_path + "OntoReSpec/Specification/OntoRespec.ttl")
template_graph        = readStringFromFile(directory_path + "OntoReSpec/Specification/ReSpecTemplate.ttl" )
html_serialisation    = readStringFromFile(directory_path + "htmlvoc/Specification/html - core.ttl")
html_vocabulary       = readStringFromFile(directory_path + "htmlvoc/Specification/html - core.ttl")
manchester_vocabulary = readStringFromFile(directory_path+"OntoManchester/Specification/manchestersyntax.ttl")
mermaid_vocabulary    = readStringFromFile(directory_path+"OntoMermaid/Specification/mermaid.ttl")

def generateManchester(manchester_generator, serializable_graph):
        
        # call PyShacl engine and apply the HTML vocabulary to the serializable HTML document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=manchester_generator,
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, #rather than setting this to true, it is better to do the iteration in the script as PyShacl seems to have some buggy behavior around iteration.
        debug=False,
        )
        
        resultquery = serializable_graph.query('''
            
prefix manchester: <https://data.rijksfinancien.nl/manchester/model/def/>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sh: <http://www.w3.org/ns/shacl#>
ASK
WHERE {
  # Any OWL or RDFS entity that is not yet described in terms of the manchester syntax
  {
    $this a owl:Class.
  }  
  UNION
  {
    $this a rdfs:Class.
  }
  UNION
  {
    $this rdfs:subClassOf []
  }
  UNION
  {
    $this owl:equivalentClass []
  }
  UNION
  {
    $this owl:unionOf []
  }
  UNION
  {
    $this owl:intersectionOf []
  }
  UNION
  {
    $this owl:complementOf []
  }
  UNION
  {
    $this owl:oneOf []
  }
  UNION
  {
    $this owl:allValuesFrom []
  }
  UNION
  {
    $this owl:someValuesFrom []
  }
  UNION
  {
    $this owl:hasValue []
  }
  UNION
  {
    $this owl:cardinality []
  }
  UNION
  {
    $this owl:maxCardinality []
  }
  UNION
  {
    $this owl:minCardinality []
  }  
  UNION
  {
    $this rdf:type owl:DatatypeProperty.
  }
  UNION
  {
    $this rdf:type owl:ObjectProperty.
  }
  UNION
  {
    $this rdfs:subPropertyOf [].
  }
  UNION
  {
    $this owl:equivalentProperty [].
  }
  filter not exists {
    $this manchester:syntax 'CLASS'.
  }
  filter not exists {
    $this manchester:syntax 'CLASS'.
  }
  filter not exists {
    $this manchester:syntax 'SUBCLASSOF'.
  }
  filter not exists {
    $this manchester:syntax 'EQUIVALENTTO'.
  }
  filter not exists {
    $this manchester:syntax 'OR'.
  }
  filter not exists {
    $this manchester:syntax 'AND'.
  }
  filter not exists {
    $this manchester:syntax 'NOT'.
  }
  filter not exists {
    $this manchester:syntax '{}'.
  }
  filter not exists {
    $this manchester:syntax 'ONLY'.
  }
  filter not exists {
    $this manchester:syntax 'SOME'.
  }
  filter not exists {
    $this manchester:syntax 'VALUE'.
  }
  filter not exists {
    $this manchester:syntax 'EXACTLY'.
  }
  filter not exists {
    $this manchester:syntax 'MAX'.
  }
  filter not exists {
    $this manchester:syntax 'MIN'.
  }
  filter not exists {
    $this manchester:syntax 'DATATYPEPROPERTY'.
  }
  filter not exists {
    $this manchester:syntax 'OBJECTPROPERTY'.
  }
  filter not exists {
    $this manchester:syntax 'SUBPROPERTYOF'.
  }
  filter not exists {
    $this manchester:syntax 'EQUIVALENTPROPERTY'.
  }
}
        ''')   

        # Check whether another iteration is needed. If every OWL and RDFS construct contains a manchester:syntax statement, the processing is considered done.
        for result in resultquery:
            if result == True:
                return generateManchester(manchester_generator, serializable_graph)
            else: 
                 return serializable_graph


def generateReSpecRDF(shaclgraph, serializable_graph):
        
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
      
        return serializable_graph


def generateDiagram(mermaid_generator, serializable_graph):
        
        # call PyShacl engine and apply the HTML vocabulary to the serializable HTML document
        pyshacl.validate(
        data_graph=serializable_graph,
        shacl_graph=mermaid_generator,
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        advanced=True,
        inplace=True,
        inference=None,
        iterate_rules=False, #rather than setting this to true, it is better to do the iteration in the script as PyShacl seems to have some buggy behavior around iteration.
        debug=False,
        )
        
       
        statusquery = serializable_graph.query('''
            
prefix mermaid: <https://data.rijksfinancien.nl/mermaid/model/def/>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sh: <http://www.w3.org/ns/shacl#>
ASK
WHERE {
  # Any OWL or RDFS entity that is not yet described in terms of the manchester syntax
  {
    $this a owl:Class.
  }  
  UNION
  {
    $this a rdfs:Class.
  }
  UNION
  {
    $this rdfs:subClassOf []
  }
  UNION
  {
    $this owl:equivalentClass []
  }
  UNION
  {
    $this owl:unionOf []
  }
  UNION
  {
    $this owl:intersectionOf []
  }
  UNION
  {
    $this owl:complementOf []
  }
  UNION
  {
    $this owl:oneOf []
  }
  UNION
  {
    $this owl:allValuesFrom []
  }
  UNION
  {
    $this owl:someValuesFrom []
  }
  UNION
  {
    $this owl:hasValue []
  }
  UNION
  {
    $this owl:cardinality []
  }
  UNION
  {
    $this owl:maxCardinality []
  }
  UNION
  {
    $this owl:minCardinality []
  }  
  UNION
  {
   $this rdf:type rdf:Property
  }
  UNION
  {
    $this rdf:type owl:DatatypeProperty.
  }
  UNION
  {
    $this rdf:type owl:ObjectProperty.
  }
  UNION
  {
    $this rdfs:subPropertyOf []
    FILTER NOT EXISTS {$this rdf:type owl:AnnotationProperty}.
    FILTER NOT EXISTS {$this rdf:type owl:InverseFunctionalProperty}
    FILTER NOT EXISTS {$this rdf:type owl:FunctionalProperty}
  }
  UNION
  {
    $this owl:equivalentProperty [].
  }
  filter not exists {
    $this mermaid:syntax 'CLASS'.
  }
  filter not exists {
    $this mermaid:syntax 'CLASS'.
  }
  filter not exists {
    $this mermaid:syntax 'SUBCLASSOF'.
  }
  filter not exists {
    $this mermaid:syntax 'EQUIVALENTTO'.
  }
  filter not exists {
    $this mermaid:syntax 'OR'.
  }
  filter not exists {
    $this mermaid:syntax 'AND'.
  }
  filter not exists {
    $this mermaid:syntax 'NOT'.
  }
  filter not exists {
    $this mermaid:syntax '{}'.
  }
  filter not exists {
    $this mermaid:syntax 'ONLY'.
  }
  filter not exists {
    $this mermaid:syntax 'SOME'.
  }
  filter not exists {
    $this mermaid:syntax 'VALUE'.
  }
  filter not exists {
    $this mermaid:syntax 'EXACTLY'.
  }
  filter not exists {
    $this mermaid:syntax 'MAX'.
  }
  filter not exists {
    $this mermaid:syntax 'MIN'.
  }
  filter not exists {
    $this mermaid:syntax 'RDF_PROPERTY'.
  }
  filter not exists {
    $this mermaid:syntax 'DATATYPEPROPERTY'.
  }
  filter not exists {
    $this mermaid:syntax 'OBJECTPROPERTY'.
  }
  filter not exists {
    $this mermaid:syntax 'SUBPROPERTYOF'.
  }
  filter not exists {
    $this mermaid:syntax 'EQUIVALENTPROPERTY'.
  }
  filter not exists {
    $this mermaid:syntax 'OR-DATATYPE'.
  }
  filter not exists {
    $this mermaid:syntax 'AND-DATATYPE'.
  }
  filter not exists {
    $this mermaid:syntax 'NOT-DATATYPE'.
  }
  filter not exists {
    $this mermaid:syntax '{}-DATATYPE'.
  }
  filter not exists {
    $this mermaid:syntax 'EXACTLYQUALIFIED'.
  }
  filter not exists {
    $this mermaid:syntax 'MAXQUALIFIED'.
  }
  filter not exists {
    $this mermaid:syntax 'MINQUALIFIED'.
  }
}
        ''')   

        resultquery = serializable_graph.query('''
            
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sh: <http://www.w3.org/ns/shacl#>
prefix : <https://data.rijksfinancien.nl/mermaid/model/def/>

SELECT (GROUP_CONCAT(?label; separator="\\n") AS ?mermaid_code)
WHERE {
  ?element :label ?label.
  
  minus {
      ?this owl:annotatedTarget ?target.
      ?target (:|!:)* ?element.
      ?element :label ?label
      FILTER isBlank(?target)
      FILTER isBlank(?element)}
  
}
ORDER BY ?mermaid_code
        ''')   

        # Check whether another iteration is needed. If every OWL and RDFS construct contains a mermaid:syntax statement, the processing is considered done.
        for status in statusquery:
            if status == True:
                generateDiagram(mermaid_generator, serializable_graph)
            else:     
                 for result in resultquery:
                    mermaid_code = result["mermaid_code"]
                    output_file_path = directory_path+"OntoReSpec/Tools/Playground/static/diagram.html"
                    # Create the HTML content with the Mermaid code
                    html_start =  '''
                    <!DOCTYPE html>
                    <html>
                    <head>
                    </head>
                    <body>
                    <div><pre class="mermaid">
                    %%{
                    init: {
                    "flowchart":{
                    "useMaxWidth": 0
                    }
                    }
                    }%%
                    graph TB
                    classDef Datatype fill:#9c6,stroke:#9c6;
                    
                    
                    '''
                    
                    html_graph = f'''
                  
                    {mermaid_code}
                    
                    ''' 
                    
                    html_end = '''
                    </pre>
                    <script type="module">
                      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                      mermaid.initialize({ startOnLoad: true });
                    </script>
                    </div>
                    </body>
                    </html>
                    '''
                    
                    html_content = html_start + html_graph + html_end
                    
                    # Write the HTML content to the output file
                    with open(output_file_path, "w", encoding="utf-8") as file:
                        file.write(html_content) 

def generateHTML(shaclgraph, serializable_graph):
        
        # call PyShacl engine and apply the html vocabulary to the serializable html document
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
      
        # Query to know if the document has been fully serialised by testing whether the root has a html:fragment property. If it has, the algorithm has reached the final level of the document.
        resultquery = serializable_graph.query('''
            
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
       PREFIX html: <https://data.rijksfinancien.nl/html/model/def/>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

       ASK 
       WHERE {
         ?document a html:Document ;
                 html:fragment ?fragment.
       }
        ''')   

        # Check whether another iteration is needed. If the html root of the document contains a html:fragment statement then the serialisation is considered done.
        for result in resultquery:
            print ("ask result = ", result)
            if result == False:
                writeGraph(serializable_graph)
                return generateHTML(shaclgraph, serializable_graph)
         
            else:
                htmlQuery = serializable_graph.query('''
                   
               PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               PREFIX html: <https://data.rijksfinancien.nl/html/model/def/>
               PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

               select ?fragment
               WHERE {
                 ?document a html:Document ;
                         html:fragment ?fragment.
               }

               ''')   

         
                for html in htmlQuery:
                    print ("html.fragment = ", html.fragment)
                    return html.fragment


@app.route('/generateReSpec', methods=['POST'])
def generateReSpec():
    ontology = request.form['ontology']
    introduction = request.form['introduction']
    background = request.form['background']
    audience = request.form['audience']
    objective = request.form['objective']
    acknowledgements = request.form['acknowledgements']
    documentLanguage = request.form['documentLanguage']
    documentNamespace = request.form['documentNamespace']
    
    generation_iri = hash(ontology + str(datetime.datetime.now()))

    generationGraph = Graph()
    generationGraph.bind("html", html)
    generationGraph.bind("respec", respec)    
    doc = Namespace(documentNamespace)
    generationGraph.bind("doc", doc)    
    
    # Add triples to be able to kickstart the SHACL engine later.
    generationGraph.add((doc[generation_iri], RDF.type, respec.Generation))
    generationGraph.add((doc[generation_iri], respec.documentLanguage, Literal(documentLanguage)))
    generationGraph.add((doc[generation_iri], respec.documentNamespace, Literal(documentNamespace)))
    generationGraph.add((doc[generation_iri], respec.audience, Literal(audience, lang=documentLanguage)))
    generationGraph.add((doc[generation_iri], respec.introduction, Literal(introduction, lang=documentLanguage)))
    generationGraph.add((doc[generation_iri], respec.background, Literal(background, lang=documentLanguage)))
    generationGraph.add((doc[generation_iri], respec.objective, Literal(objective, lang=documentLanguage)))
    generationGraph.add((doc[generation_iri], respec.acknowledgements, Literal(acknowledgements, lang=documentLanguage)))
    
    # Let us establish which ontology needs to be documented in ReSpec
    generationGraph.parse(data=ontology , format="turtle")
    
    ontologyQuery = generationGraph.query('''
       
   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
   PREFIX html: <https://data.rijksfinancien.nl/html/model/def/>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

   select ?ontology
   WHERE {
     ?ontology a owl:Ontology .
   }

   ''')   


    for result in ontologyQuery:
        generationGraph.add((doc[generation_iri], dct.subject, URIRef(result.ontology)))
    
    # Generating diagram 
    generateDiagram(mermaid_vocabulary, generationGraph)
    
    # Enriching the ontology with manchester metadata
    generationGraph = generateManchester(manchester_vocabulary, generationGraph)
    
    # Build the ReSpec structure of the document in RDF
    generationGraph.parse(data=html_vocabulary, format="turtle")
    generationGraph.parse(data=template_graph, format="turtle")
    generationGraph = generateReSpecRDF(respec_vocabulary, generationGraph)
    writeGraph(generationGraph)
    
    # Serialize the document to HTML
    html_fragment = generateHTML(html_vocabulary, generationGraph)
    print("HTML fragment =", html_fragment)
    filepath = directory_path+"OntoRespec/Tools/Playground/static/output.html"
    src_filepath = url_for('static', filename='output.html')
    with open(filepath, 'w', encoding='utf-8') as file:
       file.write(html_fragment)
    return render_template('index.html', htmlOutput='<iframe src='+ src_filepath + ' width="100%" height="600"></iframe>')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

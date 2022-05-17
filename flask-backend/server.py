import json

from flask import Flask, jsonify
from flask_cors import CORS

from data_processing.clean import (clean_data, 
                                   fetch_data_csv)

from data_processing.network import (create_citing_edges, 
                                     create_coauthor_edges, 
                                     create_nodes_from_influential_authors, 
                                     get_coauthors_groups)


app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    df = fetch_data_csv("./data/output4.csv")
    df = clean_data(df)
    nodes = create_nodes_from_influential_authors(df, NUMBER_OF_NODES=150)
    coauthors_edges = create_coauthor_edges(df, nodes)
    citing_edges = create_citing_edges(df, nodes)
    groups = get_coauthors_groups(nodes, coauthors_edges)
    nodes['group'] = groups
    
    return {
        "nodes": json.loads(nodes.to_json(orient = "records")),
        "coauthors_edges": json.loads(coauthors_edges.to_json(orient = "records")),
        "citing_edges": json.loads(citing_edges.to_json(orient = "records"))
    }

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
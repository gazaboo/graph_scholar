const coauthors_edge_color = 'orange';
const citing_edge_color = '#696969';

var nodes = new vis.DataSet([]);
var edges = new vis.DataSet([]);

axios.get('http://127.0.0.1:5000/')
  .then(function (response) {
    add_nodes(response);
    add_coauthor_edges(response);
    add_citing_edges(response);
  })
  .catch(function (error) {
    console.log(error);
  })
  .then(function () {
  });


function add_nodes(response) {
  response.data.nodes.forEach(element => {
    nodes.add([
      { 
        id: element.id, 
        label: element.author,
        value: element.num_times_cited,
        group:element.group,
        title: element.titles
      },
    ]);
  });
}

function add_coauthor_edges(response) {
  response.data.coauthors_edges.forEach(element => {
    edges.add([
      { 
        from: element.id_author1, 
        to: element.id_author2,
        color: coauthors_edge_color, 
        width: element.number
      },
    ]);
  });
}

function add_citing_edges(response) {
  response.data.citing_edges.forEach(element => {
    edges.add([
      { 
        from: element.id_author1, 
        to: element.id_author2,
        color: citing_edge_color,
        dashes:true,
        physics:false 	
      },
    ]);
  });
}

// Slider event
var sliderValue = 500;
document.getElementById('slider').value = sliderValue;
document.getElementById('sliderValueDisplay').innerHTML = sliderValue;
var nodesView = new vis.DataView(nodes, {
  filter: function (node) {
    return (node.value >= sliderValue);
  }
});

document.getElementById('slider').oninput = function() {
  sliderValue = this.value;
  nodesView.refresh();
}



// Checkbox event
var coauthor_edge_input = document.getElementById('coauthor');
var citing_edge_input = document.getElementById('citing');

coauthor_edge_input.addEventListener('click', () => edgesView.refresh());
citing_edge_input.addEventListener('click', () => edgesView.refresh());

var edgesView = new vis.DataView(edges, {
  filter: function (edge) {
    allowed_colors = [];
    if (coauthor_edge_input.checked){ 
      allowed_colors.push(coauthors_edge_color);
    }
    if (citing_edge_input.checked){ 
      allowed_colors.push(citing_edge_color);
    }    
    return allowed_colors.includes(edge.color); 
  }
});


// Create Network
var container = document.getElementById("mynetwork");
var data = {
  nodes: nodesView,
  edges:edgesView
};



var options = {
  "nodes": {
      "shape": "circle",
      "scaling": {
        "min": 5,
        "max": 50
      },
      "font": "12px arial white"
   }
}




var network = new vis.Network(container, data, options);



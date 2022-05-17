import itertools
import pandas as pd
import community as community_louvain
import networkx as nx

def create_nodes_from_influential_authors(df, NUMBER_OF_NODES=100):
    total_num_citation_per_author = (df.loc[:, ["title", "authors", "cited"] ]
                                       .drop_duplicates(subset="title")
                                       .explode("authors")
                                       .groupby("authors")
                                       .sum()
                                       .loc[:, 'cited']
                                       .sort_values(ascending=False)
                                       .iloc[:NUMBER_OF_NODES]
                                    )
    
    titles = (df.reset_index()
              .loc[:, ["title", "authors"]]
              .drop_duplicates(subset="title")
              .explode("authors")
           )
    titles = titles.groupby("authors")["title"].apply('\n'.join)
    titles = titles[total_num_citation_per_author.index]
    
    return pd.DataFrame(data = {
            "id": range(NUMBER_OF_NODES),
            "author": total_num_citation_per_author.index,
            "num_times_cited": total_num_citation_per_author.values, 
            "titles": titles.values
    })

def get_working_relation_between_authors(df):
    coauthors = df.authors.apply(lambda team: list(itertools.combinations(team, r=2)))
    mask = coauthors.apply(len) > 0
    coauthors = coauthors[mask]
    coauthors = coauthors.explode()
    coauthorship = coauthors.map(lambda t: tuple(sorted(t)))
    edges = coauthorship.value_counts()
    return pd.DataFrame( data = {
            'author1': edges.index.map(lambda t: t[0]),
            'author2': edges.index.map(lambda t: t[1]),
            'number': edges.values 
    })
    
def get_coauthors_groups(nodes, coauthors_edges): 
    G = nx.from_pandas_edgelist(coauthors_edges, source="id_author1", target="id_author2")
    partition = community_louvain.best_partition(G, weight='number')
    groups = nodes['id'].map(partition).fillna(-1)
    return groups

def names_to_nodes_ids(coauthors_edges, nodes):
    nodes_ids = coauthors_edges[ ["author1", "author2"] ].applymap(lambda name: nodes[nodes.author==name].id.values[0]).reset_index(drop=True)
    return pd.DataFrame( data = { 
            "id_author1": nodes_ids.author1,
            "id_author2": nodes_ids.author2,
            "number": coauthors_edges["number"].values
    })


def get_citing_relation_between_authors(df):
    edges = df.explode('authors').explode("authors_of_parent_article")[["authors", "authors_of_parent_article"]]
    edges = edges.dropna(axis="index")
    edges = edges.reset_index().groupby(["authors", "authors_of_parent_article"]).count()
    edges = edges.reset_index()
    edges.columns = ["author1", "author2", "number"]
    return edges

def select_subset_edges(edges, subset_authors):
    coauthors_to_keep = edges.query('author1 in @subset_authors and author2 in @subset_authors')
    return coauthors_to_keep


def create_coauthor_edges(df, nodes):
    return (df.pipe(lambda df: df.copy(deep=True))
              .pipe(get_working_relation_between_authors)
              .pipe(select_subset_edges, subset_authors=nodes.author.values)
              .pipe(names_to_nodes_ids, nodes=nodes)
    )

def create_citing_edges(df, nodes):
    return (df.pipe(lambda df: df.copy(deep=True))
              .pipe(get_citing_relation_between_authors)
              .pipe(select_subset_edges, subset_authors=nodes.author.values)
              .pipe(names_to_nodes_ids, nodes=nodes)
    )
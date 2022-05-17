import pandas as pd

def copy_df(input_df):
    return input_df.copy(deep=True)

def format_numeric_types(df):
    df.cited = df.cited.fillna(0)
    df = df.astype({"parent_id":"int32", "cited":"int32"})
    return df
    
def format_str_types(df):
    df.publication_data = df.publication_data.str.replace(u"\xa0", " ").str.replace('\u2026', '') # remove ellipsis and non-breaking space
    df[ ["authors", "journal_date"] ] = df.publication_data.str.split(" - ", n=1, expand=True)
    df = df.drop(columns='publication_data')
    df["title"] = df["title"].str.title()
    df["authors"] = df["authors"].str.title()
    df["authors"] = df["authors"].str.split(", ")
    return df
    
def identify_same_articles_under_different_ids(df):
    df = df.reset_index()
    df["id"] = df.groupby('title')["id"].transform(lambda x: min(x)) # donner le même id pour les articles ayant le même nom
    df = df.set_index("id")
    return df

def add_parents_data(df):
    df["authors_of_parent_article"] = df.parent_id.apply(lambda parent_id: df.loc[parent_id, "authors"] if parent_id != -1 else [])
    df["title_of_parent_article"] = df.parent_id.apply(lambda parent_id: df.loc[parent_id, "title"] if parent_id != -1 else [])
    return df

def fetch_data_csv(path): 
    cols = ["id", "parent_id", "title", "cited", "publication_data", "snippet"]
    df = pd.read_csv(path, usecols=cols)
    df = df.set_index("id")
    return df

def clean_data(df):
    return (
        df.pipe(copy_df)
          .pipe(format_str_types)
          .pipe(format_numeric_types)
          .pipe(add_parents_data)
          .pipe(identify_same_articles_under_different_ids)
    )
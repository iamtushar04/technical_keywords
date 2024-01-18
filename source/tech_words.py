import logging

import pandas as pd
from database.keywords import ENGINE, TechKeywords
from sqlalchemy.dialects.mysql import insert
from sqlite3 import IntegrityError

KEYWORDS_TABLE = "keywords"
COLUMNS = ['keyword', 'tech_words']
UPDATE_MODE = 'replace'


def upload_data(file: str):
    df = pd.read_excel(file)
    df = df[['Keywords', 'Synonmns']].rename(columns={'Keywords': 'keyword', 'Synonmns': 'tech_words'})
    df['keyword'] = df['keyword'].str.lower()
    df['tech_words'] = df['tech_words'].str.lower()
    df['keyword'] = df['keyword'].str.strip()
    df = df.groupby('keyword')['tech_words'].agg(
        lambda x: ', '.join(str(word).strip() for word in x if pd.notna(word))).reset_index()
    msg, status = df_insert(table=KEYWORDS_TABLE, df=df)
    if status == 200:
        return msg, status
    else:
        msg, status = upsert(table=KEYWORDS_TABLE, df=df)
        return msg, status


def df_insert(table: str, df: pd.DataFrame):
    try:
        df.to_sql(table, if_exists="append", con=ENGINE, index=False)
        return "Successfully Inserted the data", 200
    except Exception as e:
        print(f"Failed due to {e}")
        return f"Failed to Upload. Check the logs.", 400


def insert_on_duplicate(table, conn, keys, data_iter):
    insert_stmt = insert(table.table).values(list(data_iter))
    on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
    conn.execute(on_duplicate_key_stmt)


def df_upsert(table: str, df: pd.DataFrame):
    try:
        # import pdb;pdb.set_trace()
        # df.to_sql(table, if_exists="append", con=ENGINE, index=False, chunksize=4096, method=insert_on_duplicate)
        dbase = TechKeywords()
        data = df[['keyword', 'tech_words']].to_dict(orient='records')
        # import pdb;pdb.set_trace()
        for i, each in enumerate(data):
            print(i)
            # words_ = each['tech_words'].split(',')
            # words_ = ', '.join(set([word.strip() for word in words_]))
            try:
                dbase.update(keyword_=each['keyword'], tech_words=each['tech_words'])
                # dbase.add_keyword(keyword_=each['keyword'], tech_words=each['tech_words'])
            # except IntegrityError as e:
            #     dbase.update(keyword_=each['keyword'], tech_words=each['tech_words'])
            except Exception as e:
                print(f"{e}")
        return "Successfully Inserted the data", 200
    except Exception as e:
        print(f"Failed due to {e}")
        return f"Failed to Upload. Check the logs.", 400


def upsert(table: str, df: pd.DataFrame):
    dbase = TechKeywords()
    existing_data = pd.DataFrame(dbase.get_existing_keywords(df['keyword'].tolist()))
    df1 = pd.merge(df, existing_data, on='keyword', how='inner')
    df_new = df.merge(existing_data, on='keyword', how='left', indicator=True).query("_merge == 'left_only'").drop(
        '_merge', axis=1).rename(columns={'tech_words_x': 'tech_words'})

    df1['tech_words_x'] = df1['tech_words_x'].fillna('')
    df1['tech_words_y'] = df1['tech_words_y'].fillna('')
    df1['tech_words'] = df1.apply(
        lambda row: ', '.join(set(row['tech_words_x'].split(', ') + row['tech_words_y'].split(', '))),
        axis=1)
    df1.drop(['tech_words_x', 'tech_words_y'], axis=1, inplace=True)
    try:
        df_insert(table=KEYWORDS_TABLE, df=df_new[COLUMNS])
        msg, status = df_upsert(table=table, df=df1)
        return msg, status
    except Exception as e:
        print(f"Failed due to {e}")
        return f"Failed to Upload. Check the logs", 400








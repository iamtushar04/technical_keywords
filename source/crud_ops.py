from database.keywords import TechKeywords, ENGINE, Keywords


def add_update_synonyms(keyword: str, tech_words: list):
    """
    :title: Function to add synonyms either keyword exists or not.
    :param keyword: keyword
    :param tech_words: synonyms or tech_word of the keyword.
    :return:
    """

    dbase = TechKeywords()
    try:
        record = dbase.find(keyword_=keyword)
        if record:
            existing_words = record[0]['tech_words'].split(',')
            existing_words += tech_words
            existing_words = [x.strip() for x in existing_words if x != '']
            dbase.update(keyword_=record[0]['keyword'], tech_words=', '.join(set(existing_words)))
            return f"Successfully Updated the keyword {keyword}", 200
        else:
            dbase.add_keyword(keyword_=keyword, tech_words=', '.join(tech_words))
            return f"Successfully Added the keyword {keyword}", 201

    except Exception as e:
        return f"Failed to add/update due to database error", 400

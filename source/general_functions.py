def read_file(file_name: str) -> str:
    """
    :Title: Funtion to read a file
    :param file_name: File from where data has to be read
    :return: file_content
    """
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()


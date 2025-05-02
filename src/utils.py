import os

def load_tender_files(folder_path):
    tender_texts = []
    for filename in os.listdir(folder_path):
        with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
            tender_texts.append((filename, file.read()))
    return tender_texts
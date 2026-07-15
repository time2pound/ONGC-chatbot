from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("docs/ONGC manual.pdf")

docs = loader.load()

print("Total Pages:", len(docs))

print("\nFIRST PAGE\n")

print(docs[0].page_content)
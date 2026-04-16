import sys
import traceback
try:
    import chromadb
    print("OK:", chromadb.__version__)
    c = chromadb.PersistentClient(path="./test_chroma")
    print("Client OK")
except Exception as e:
    print("ERROR:", type(e).__name__)
    traceback.print_exc()
    sys.exit(1)

# api2/search_test.py

from search_engine import search

if __name__ == "__main__":
    query = "pc portable"
    results = search(query)

    for prod, score in results:
        print(f"{prod['title']}  →  score={score:.3f}")

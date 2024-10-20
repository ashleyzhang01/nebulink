from sqlalchemy.orm import Session
from app.db.session import get_db  # Assuming this is your DB session setup
from app.chromadb.internal_api import get_chroma_collection  # ChromaDB functions
from app.utils.enums import ChromaCollections
from app.db.repository_functions import get_all_repositories, get_readme_by_path  # Reuse your repository functions

# Set up the database session and get ChromaDB collection for GitHub Repositories
def update_chroma_with_repositories(db: Session):
    # Fetch all repositories from the SQLite database
    repositories = get_all_repositories(db)
    
    # Get the ChromaDB collection for GitHub repositories
    github_collection = get_chroma_collection(ChromaCollections.GITHUB_REPOSITORY)

    # Iterate over each repository and insert/update in ChromaDB
    for repository in repositories:
        # Fetch the README content for each repository
        readme_string = get_readme_by_path(path=repository.path, token=None)

        if readme_string:
            # Insert or update the repository data in ChromaDB
            github_collection.upsert(
                documents=[readme_string],
                ids=[repository.path],
            )
            print(f"Updated ChromaDB with repository: {repository.path}")
        else:
            print(f"No README found for repository: {repository.path}")

# Run the update function
if __name__ == "__main__":
    # Use session management provided by FastAPI or SQLAlchemy
    db: Session = get_db()  # Get the database session
    try:
        update_chroma_with_repositories(db)
    finally:
        db.close()

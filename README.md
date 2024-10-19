# calhacks

## Setup

### Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

If you add new packages, run `pip freeze > requirements.txt` to update the requirements.txt file.

### Frontend
cd frontend
npm install
npm run dev
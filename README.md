# nebulink

<img width="1691" alt="Screenshot 2024-10-20 at 9 23 55 AM" src="https://github.com/user-attachments/assets/7c5c44d7-b526-45ec-b6bd-82bfe4319ab3">

## Inspiration
Have you ever spent hours trying to find the right person—whether it’s a hire, a mentor, or a collaborator—only to feel like the process was inefficient and hit-or-miss? It’s not just about finding talent; it’s about finding people who align with your goals, bring positive value, and fit into your long-term vision.


The problem? This process is time-consuming and often reliant on referrals or alumni networks, making it hard to discover the best-fit individuals. That’s why we built this platform: **to automate parts of the process while increasing its human-centered essence.** We don’t just help users search for people or talent—we enable them to **understand their network, foster genuine connections, and make strategic decisions** with visibility into how people and companies relate to one another.

## What it does
Our platform combines **real-time graph visualization** with **LLM-powered search and message generation** to streamline relationship-building. Users connect their social platforms (e.g., LinkedIn, GitHub) to view an interactive graph of people, companies, and connections, grouped by organizations and structured by degrees of separation. The graph provides insights into the **strength of connections**, letting users navigate between platforms to explore how individuals and organizations are linked.

With **semantic search**, users can input queries like:
- “Find a cybersecurity mentor at a startup.”
- “Who in my network has experience with AI and fundraising?”
Behind the scenes, a **multi-agent system** classifies each query and triggers specialized agents to search through GitHub, LinkedIn, or other sources. Results are stored as **vector embeddings in ChromaDB**, ensuring quick and relevant retrieval. Users receive not just matches, but insights into who the right person is based on shared values, skills, and experiences.

To facilitate outreach, the platform offers **tailored message generation** based on the context of the platform and the common points between them. If they don’t have a direct connection, they can request introductions through mutual contacts.

Finally, **data-scraping agents** pull and refresh data from platforms like GitHub and LinkedIn to keep the graph updated. The agents work on a schedule or on-demand by proxy, ensuring users always have access to the latest information.

## How we built it
Our platform combines a multi-agent system, interactive graph visualization, and intelligent search and outreach capabilities to help users discover and build meaningful connections. Here’s a breakdown of the core technologies and how they work together:

1. Multi-Agent System:
 - Classification agents analyze user queries to determine if they target people or companies.
 - Search agents first figure out how best identify key individuals or companies that fit user criteria. They then optimize queries with the **Hyperbolic** API, based on how many searches they need to get to the goal, and where they want to search.
 - Scraping agents from **Fetch.ai** pull data from platforms like GitHub and LinkedIn, extracting relevant content (e.g., GitHub projects, LinkedIn profiles) to enrich the graph or store as vector embeddings in **ChromaDB** for more optimized search. Agents also retrieve contact information, ensuring a way to reach out to people even if the platform doesn’t offer direct messaging (e.g., finding GitHub usernames from email addresses).
 - Message-generation agents create personalized outreach content, incorporating **Hyperbolic inference APIs** to ensure contextual relevance and prevent hallucinations.
2. Interactive Graph Visualization and Retrieval:
 - Built using **Three.js** for smooth rendering, with a SQL database for relational data and **ChromaDB** for vector-based search
 - Each node represents a person, company, or organization, with node size reflecting the strength of the connection.
 - Users can navigate their connections across platforms, grouped by organizations, and seamlessly click between contexts (e.g., viewing a person’s LinkedIn profile and their GitHub activity).
 - If not logged in, the graph displays public companies without revealing sensitive data, preserving privacy.

## What's next for nebulink
- Twitter scraping
- Groups of users, to see all your connections/networks together
- Filters for graph visualization
- More optimal algorithms
- Sentiment analysis and more user info, for message drafting to really personalize the user
- Searching with you.com or perplexity for additional context for message drafting


## Setup

### Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

If you add new packages, run `pip freeze > requirements.txt` to update the requirements.txt file.
To lint, run `chmod +x lint.sh` to make it executable for the first time, and then run `./lint.sh`.

To run the Fetch AI agent, run `python -m app.agents.scraper_agents`. They will be hosted on port 8001!

### Frontend
cd frontend
npm install
npm run dev

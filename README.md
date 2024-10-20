# nebulink

## Inspiration
Have you ever spent hours trying to find the right person—whether it’s a hire, a mentor, or a collaborator—only to feel like the process was inefficient and hit-or-miss? It’s not just about finding talent; it’s about finding people who align with your goals, bring positive value, and fit into your long-term vision. From our experience as founders and students, we’ve seen that the best connections come from meaningful relationships. Successful hiring, mentorship, or collaboration is about **building relationships over time, identifying mutual values, and offering the right opportunity at the right moment**.

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

## Challenges we ran into
- Designing a Complex System and Maintaining Consistency: Building a platform with multiple interconnected agents, data sources, and visual components required meticulous planning. Dividing tasks across our team while maintaining a consistent structure and flow was challenging, especially when coordinating agents’ tasks (e.g., search, scraping, message generation) and datatypes to work together seamlessly. Smooth communication between components was essential to avoid duplication, misalignment, or performance bottlenecks.
- Scraping Without Accessible APIs: Platforms like LinkedIn don’t provide public APIs for many key data points, making scraping particularly challenging. We had to develop creative solutions to reliably access and extract the data while staying compliant with privacy policies. For users who don’t want to provide account credentials, we implemented proxy-based scraping techniques that work within platform limitations, providing functionality without compromising security or usability.
- Graph Search Optimization: Traversing large networks in real-time is computationally demanding. With thousands of nodes and connections, we focused on minimizing query complexity using advanced search techniques, such as graph pruning and embeddings-based lookups, to ensure fast and responsive performance.
- Data Consistency and Scraping: Pulling data from multiple sources with different structures required intelligent fetch and refresh cycles. Agents handle scheduled updates and on-demand queries to keep data current without overwhelming APIs.
- Accurate, Context-Aware Messaging: Balancing automation with personalization was challenging. The Hyperbolic API ensures that messages align with the search context, preventing irrelevant or incorrect messaging.
- Cross-Platform Integration: Creating smooth transitions between platforms like GitHub and LinkedIn required careful planning to synchronize different data structures and privacy constraints.
- The wifi at the venue was very slow and made scraping and LLM calls very inefficient.

## Accomplishments that we're proud of
- For all of us, this was our first multi-agent system relying on heavy inter-agent communication. We're of our robust multi-agent system capable of handling classification, search, scraping, and personalized outreach seamlessly.
- Using graph traversal and theory we learned in our classes in a real application!
- Developed a real-time, interactive graph that visualizes thousands of nodes, connections, and degrees of separation efficiently. Very pleasing to scroll and click around on too.
- Successfully integrated ChromaDB embeddings to enable fast, semantic search across diverse datasets and 2 types of dbs.
- Created a platform that not only identifies the right connections but also facilitates genuine relationship-building over time. While building this, we definitely gained even more insight on the benefits a tool like this can bring.

## What we learned
- Real-time graph traversal at scale is challenging: Managing thousands of nodes efficiently (and our computers continuously crashing) required us to rethink our query optimization strategies, ultimately leading to embeddings-based lookups and graph pruning techniques.
- Consistent data management and communication about it is key: Keeping scraped data current across multiple platforms was more complex than anticipated, especially when we divided up tasks without clear communication about it and had to make changes on that later. Intelligent agents allowed us to balance data freshness with API usage constraints.
- The strongest models aren't always necessary. We experimented a lot and ended up going with lighter models to balance performance and latency.
- graph animations! (physics and math there too)

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

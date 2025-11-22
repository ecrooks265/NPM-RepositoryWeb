🕸️ NPM Dependency Intelligence Web

A local-first interactive tool to analyze, visualize, and understand your JavaScript project's dependencies — showing who maintains them and what security vulnerabilities exist.

🚀 Overview

This tool builds a live dependency graph from your project’s data, either by:

Uploading/pasting a local package-lock.json or similar dependency file, or

Searching an npm package name directly.

The graph then enriches that information using public APIs:

🧑‍💻 Maintainer Data — from the npm registry

🔒 Vulnerability Data — via the OSV.dev
 database (and easily extendable to the Snyk API)

This helps developers quantify package trust, see who controls their supply chain, and spot risky dependencies before they impact production.

🏗️ Architecture
npm-dep-web/
├── backend/
│   ├── app.py              # FastAPI app with enrichment endpoints
│   ├── deps_fetcher.py     # Parses dependency JSON structure
│   ├── npm_client.py       # Maintainer & version metadata
│   ├── osv_client.py       # Vulnerability data via OSV.dev API
│   └── requirements.txt
│
├── frontend/
│   ├── vite.config.mjs     # React + Vite configuration
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── DependencyInput.jsx  # Upload/paste area for JSON
│       │   └── GraphView.jsx        # Cytoscape-based dependency graph
│       └── styles.css
│
└── README.md

⚙️ Setup Instructions
1️⃣ Backend
cd backend
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app:app --reload


Runs on http://localhost:8000

2️⃣ Frontend
cd frontend
npm install
npm run dev


Runs on http://localhost:5173

Github setup:
first configure gh CLI with WSL or whatever distro you run the backend on (HTTPS or SSH doesn't matter as long as you're logged in)
Then set the environment variable so python os.env can find it
gh auth login to login to the gh CLI. Go to https://docs.github.com/en/rest/quickstart?apiVersion=2022-11-28 for more information
export GITHUB_TOKEN=$(gh auth token)
echo $GITHUB_TOKEN - to test it


🧰 Features
Feature	Description
📁 File upload/paste	Drop or paste your package-lock.json to visualize dependencies
🔍 Search npm packages	Explore a single npm package interactively
🧑‍💻 Maintainer insights	See how many people maintain each dependency
🔒 Security awareness	Highlights known vulnerabilities from OSV.dev
🎨 Visual graph	Interactive Cytoscape graph: size = maintainers, color = security status
📊 Local-first	No login or external data persistence; works offline for uploads
🧬 Visual Legend
Node color	Meaning
🔵 Blue	No known vulnerabilities
🔴 Red	One or more known vulnerabilities
Node size	Meaning
Larger	More maintainers
Smaller	Fewer maintainers
🛠️ Planned Features

 Integrate Snyk API for richer CVE data

 Add tooltips with maintainer names and CVE summaries

 Allow filtering by maintainer count or risk score

 Add report export (CSV / PDF)

 Support multi-package dependency overlay

🧑‍💻 Example Use Case

A developer uploads a project’s package-lock.json.
The app builds a network graph showing how deeply each dependency is nested.
Clicking a node displays:

Maintainers (who)

Version (what)

CVEs (how risky)

They can then make decisions such as:

“We depend on 43 packages maintained by 8 unique people.
2 packages have known CVEs (1 critical). Let’s pin safer versions.”

🤝 Contributing

Pull requests are welcome!
If you’d like to help extend the vulnerability sources (e.g. integrating Snyk or npm audit), start a discussion in the issues section.

⚖️ License

MIT License — free to use, modify, and distribute.

🐚 Quick Commands Summary
Action	Command
Run backend	uvicorn app:app --reload
Run frontend	npm run dev
Install backend deps	pip install -r requirements.txt
Install frontend deps	npm install
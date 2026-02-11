# Apps — Narralytica Powered Products

This directory contains **end-user applications** built on top of the Narralytica platform.

Narralytica itself is an infrastructure layer.  
The apps in this folder are **interfaces, tools, and products** that leverage its APIs and intelligence.

---

## 🧠 Relationship with Narralytica Core

All apps:

- Consume the **Narralytica API**
- Do **not** implement ingestion or AI pipelines themselves
- Focus on **UX, workflows, and domain-specific features**
- Share the same underlying data model (segments, speakers, topics, trends)

Think of Narralytica as the **brain**, and these apps as **specialized interfaces**.

---

## 📦 Applications in This Folder

| App | Purpose |
|-----|---------|
| **videoresearch-pro** | Searchable, verifiable video citations for journalists and researchers |
| **linguatube-studio** | Language learning platform using real-world video content |
| **insightmonitor** | Strategic monitoring of public discourse in video |
| **creator-intelligence** | Analytics and clip discovery for video creators |
| **speakerdna** | Analytical speaker profiles built from their speech history |
| **clipquote** | Tool for extracting publishable video quotes with context |
| **lecturefinder** | Find the best video explanations of a concept |
| **debatemap** | Mapping arguments and positions across video discourse |
| **trendpulse** | Detection of emerging ideas and trends in global video speech |
| **admin-console** | Internal operations dashboard (jobs, reindexing, cost monitoring) |

---

## 🧱 Architectural Principle

Apps must follow these rules:

- ❌ No direct access to the database  
- ❌ No direct access to raw object storage  
- ✅ All data access goes through the **Narralytica API**
- ✅ Apps remain stateless and loosely coupled

This ensures the platform remains scalable and consistent.

---

## 🛠 Tech Independence

Each app may:

- Use its own frontend stack
- Have its own deployment cycle
- Maintain its own UI/UX decisions

But must respect:

- API contracts (`/packages/contracts`)
- Authentication and rate limits
- Platform data model

---

## 🚀 Deployment

Apps can be deployed independently of the core platform.

See platform deployment docs in: ```docs/runbooks/deploy.md```

---

## 📌 Note

This folder may be empty during early infrastructure phases.  
Apps are expected to grow as the core Narralytica platform stabilizes.
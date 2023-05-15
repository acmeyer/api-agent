# API Agent

This is an experimental project to create an agent that can build an integration for you based on your query. 

## How it works

There are two main parts to how it works:
1. A service that ingests OpenAPI specs from urls and stores them in a vectorstore (in this case, Pinecone).
2. A suite of agents (project manager, coder, and researcher) that can use the ingested specs to understand available APIs and their endpoints and write code for the integration.

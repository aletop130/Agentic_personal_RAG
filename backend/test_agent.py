"""
Test script per l'agente RAG.

Usa questo script per testare l'agente senza il frontend.
"""

import asyncio
from app.agents import create_rag_agent
from langchain_core.messages import HumanMessage


async def test_agent():
    print("Testing Agentic RAG...\n")
    
    # Create agent
    agent = create_rag_agent()
    print("✓ Agent created successfully\n")
    
    # Test query
    query = "Cosa sai sui documenti caricati?"
    print(f"Query: {query}\n")
    
    result = agent.invoke({
        "messages": [HumanMessage(content=query)],
        "retrieved_context": "",
        "sources": []
    })
    
    print("Response:")
    print("-" * 80)
    for msg in result["messages"]:
        if hasattr(msg, 'content'):
            print(msg.content)
    print("-" * 80)
    
    print(f"\nSources: {result['sources']}")
    print(f"\nRetrieved context length: {len(result['retrieved_context'])}")


if __name__ == "__main__":
    asyncio.run(test_agent())

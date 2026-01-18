import asyncio
import sys
sys.path.append('.')

from app.services.rag_service import rag_service
from app.core.document_store import document_store

async def test_query_scenarios():
    test_cases = [
        ("ciao", "CONVERSATIONAL", "Should respond directly without RAG"),
        ("grazie", "CONVERSATIONAL", "Should respond directly without RAG"),
        ("parlami dei documenti", "META-DOCUMENT", "Should give helpful response about documents"),
        ("cosa ci sta scritto", "META-DOCUMENT", "Should give helpful response about documents"),
        ("summary of documents", "META-DOCUMENT", "Should give helpful response about documents"),
        ("tell me about the documents", "META-DOCUMENT", "Should give helpful response about documents"),
    ]
    
    print("Testing Query Scenarios")
    print("=" * 80)
    
    for query, expected_type, description in test_cases:
        print(f"\nQuery: '{query}'")
        print(f"Expected: {expected_type}")
        print(f"Description: {description}")
        
        # Check classification
        is_info = rag_service._is_informational_query(query)
        is_meta = rag_service._is_meta_document_query(query)
        
        print(f"  Informational: {is_info}")
        print(f"  Meta-document: {is_meta}")
        
        # Determine actual type
        if is_meta:
            actual_type = "META-DOCUMENT"
            doc_count = document_store.get_document_count()
            response = rag_service._get_meta_document_response(doc_count)
            print(f"  Response: {response}")
        elif not is_info:
            actual_type = "CONVERSATIONAL"
            print(f"  Response: Would be direct LLM response")
        else:
            actual_type = "INFORMATIONAL"
            print(f"  Response: Would trigger RAG search")
        
        # Verify match
        if actual_type == expected_type:
            print(f"  [PASS]")
        else:
            print(f"  [FAIL] - Got: {actual_type}")
    
    print("\n" + "=" * 80)
    print("Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_query_scenarios())

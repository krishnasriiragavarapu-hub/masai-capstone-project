# Support Assistant Module('/support_assistant')

## Architecture
-**Vector DB**: CHromaDB with 'all-MiniLm-L6-v2' embeddings.
-**Routing**: Uses keyword heuristic intent classifier ('policy_question' vs 'general_question').
-**Mock Mode**: Returns '"Based on the retrieved context: .."' for policy queries and restricted fallback for general queries.

## Output Examples
-**Plicy Question**: Query: "What is return policy? -> Answer: "Based on the retrieved context: Perishable grocery items..."
-**Genral Question**: Query: "hi" -> Answer: "I can only answer questions about Zepto policies right now."

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

#OllamaLLM: A class from langchain that interfaces with Ollama's local LLM models.
#ChatPromptTemplate: A template system for creating structured prompts for the LLM.

template = (
    "You are tasked with extracting specific information from the following text"
    "content: {dom_content}."
"Please follow these instructions carefully: \n\n"
"1. **Extract Information:** Only extract the information that directly"
"matches the provided description: {parse_description}. "
"2. **No Extra Content:** Do not include any additional text, comments, or"
"explanations in your response. "
"3. **Empty Response:** If no information matches the description, return"
"an empty string ('')."
"4. **Direct Data Only:** Your output should contain only the data that is"
"explicitly requested, with no other text."
)

#Template has two placeholders:
  #{dom_content}: The actual webpage content to analyze
  #{parse_description}: user's description of what to extract



#instruction for the LLM:

# 1.Extract only relevant information
# 2.keep response clean without extra text
# 3.return empty string if no match found
# 4.focus on direct data only



#Model initialization
model = OllamaLLM(model="llama3.1")

#Creates Creates an instance of OllamaLLM
#Uses "llama3" as the base model
# This is a local LLM that runs on the user's machine



#Main parsing function
def parse_with_ollama(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []
    for i, chunk in enumerate(dom_chunks, start=1):
      response = chain.invoke(
    {"dom_content": chunk, "parse_description": parse_description}
    )
    print(f"Parsed batch: {i} of {len(dom_chunks)}")
    parsed_results.append(response)
    return "\n".join(parsed_results)


#Creates a chat prompt from the template
#Creates a processing chain that connects prompt to model
#The | operator creates a pipeline of operations

#process each chunk of text seperately
#uses emuneration to track progress
#starts counting from 1 for user-frndly display
#invokes the LLM chain for each chunk
#provides both the content and parsing instruction
#gets structured response from the model
#shows progress through chucks 
#helps user track long operations
#collects all parsed result
#joins them with newlines
#returns complete parsed content



#Complete Data Flow:
  # User provides parse description and content chunks
  #Each chunk goes through:
  #Template formatting
  #LLM processing
  #Result collection
  # All results are combined into final output

from llama_cpp import Llama

def predict(inp):
	_input = str(inp)

	llm = Llama.from_pretrained(
		repo_id="QuantFactory/Phi-3-mini-128k-instruct-GGUF",
		filename="Phi-3-mini-128k-instruct.Q4_K_M.gguf"
	)

	output = llm.create_chat_completion(
		messages=[
			{
				"role": "user",
				"content": _input
			}
		]
	)
	return output["choices"][0]["message"]["content"]



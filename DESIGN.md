# System Design Walkthrough

1. LLM: OpenAI ChatGPT 4.0
2. TTS and STT: ElevenLabs

TODO:
Prompt engineering:
- Make llm responses match sentiment
- Make llm focus on scheduling, insurance verification, and faqs
- Make llm end call with a polite close
- Make llm not give medical advice and only stick to scheduling, insurance, faqs
- Provide the llm with scheduling and insurance data
- Keep conversation memory stored
- Have the llm greet the caller
- Have the llm look up scheduling data and insurance data if needed

Edge cases:
- If stt confidence is low or LLM respones is confusing/off-topic, output "Sorry didnt catch that"
- Different languages?
- Handle certain questions from user, like asking for medical advice or wanting to talk to a human
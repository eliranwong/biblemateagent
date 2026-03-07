# Tested Request

The same request used for testing the Bible Agent:

```
Prepare a comprehensive Youth Bible course (age-range: secondary school students; context: UK) about the fruits of the Holy Spirit. A total of 9 lessons, with each containing:

* ice-breakers

* detailed bible teaching with quoted bible verses

* illustrations, devotions and applications

* guidance for youth team helpers

* group discussion questions
```

# Tested with:

```
cat tested_request.md | bibleagent -p -md -docx -b ollamacloud -tk high -m gemini-3-flash-preview -cw 1048576 -mt 65536 -o ollama_gemini-3-flash-preview

cat tested_request.md | bibleagent -p -md -docx -b ollamacloud -tk high -m kimi-k2.5 -cw 256000 -mt 32000 -o ollama_kimi-k2.5

cat tested_request.md | bibleagent -p -md -docx -b ollamacloud -tk high -m mistral-large-3:675b -cw 256000 -mt 65536 -o ollama_mistral-large-3

cat tested_request.md | bibleagent -p -md -docx -b ollamacloud -tk high -m gpt-oss:120b -cw 131072 -mt 8192 -o ollama_gpt-oss:120b

cat tested_request.md | bibleagent -p -md -docx -b ollamacloud -tk high -m deepseek-v3.2 -cw 128000 -mt 8000 -o ollama_deepseek-v3.2

cat tested_request.md | bibleagent -p -md -docx -b ollamacloud -tk high -m qwen3.5:397b -cw 262144 -mt 65536 -o ollama_qwen3.5

cat tested_request.md | bibleagent -p -md -docx -b ollamacloud -tk high -m minimax-m2.5 -cw 200000 -mt 65536 -o ollama_minimax-m2.5

cat tested_request.md | bibleagent -p -md -docx -b ollamacloud -tk high -m glm-5 -cw 200000 -mt 65536 -o ollama_glm-5
```
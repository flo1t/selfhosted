FROM lscr.io/linuxserver/code-server:latest

# install npm
RUN apt-get update && apt-get install -y nodejs npm

# install claude code
RUN npm install -g @anthropic-ai/claude-code@latest

# install codex
RUN npm install -g @openai/codex@latest
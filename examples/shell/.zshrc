# Basic .zshrc
export PATH="$HOME/bin:$PATH"

# Enable Oh My Zsh
if [ -d "$HOME/.oh-my-zsh" ]; then
  export ZSH="$HOME/.oh-my-zsh"
  ZSH_THEME="robbyrussell"  # Use powerlevel10k if available
  plugins=(git docker docker-compose python)
  source $ZSH/oh-my-zsh.sh
fi

# Aliases
alias ll="ls -la"
alias gs="git status"
alias gd="git diff"

# Python virtual environment
alias venv="source ./.venv/bin/activate"
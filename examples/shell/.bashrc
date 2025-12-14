# Basic .bashrc
export PATH="$HOME/bin:$PATH"

# Git prompt (if available)
if [ -f /usr/share/git/completion/git-prompt.sh ]; then
  source /usr/share/git/completion/git-prompt.sh
  export GIT_PS1_SHOWDIRTYSTATE=1
  export PS1='\u@\h:\w$(__git_ps1 " (%s)") \$ '
fi

# Aliases
alias ll="ls -la"
alias gs="git status"
alias gd="git diff"
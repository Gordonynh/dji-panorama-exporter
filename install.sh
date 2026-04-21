#!/bin/zsh
set -euo pipefail
ROOT="${0:A:h}"
SRC="$ROOT/bin"
DEST="$HOME/.local/bin"
mkdir -p "$DEST"
for f in "$SRC"/dji-*; do
  name="$(basename "$f")"
  ln -sfn "$f" "$DEST/$name"
  echo "linked $DEST/$name -> $f"
done
cat <<'EOF'

If ~/.local/bin is not already on PATH, add this to ~/.zshrc:

export PATH="$HOME/.local/bin:$PATH"

Then reload shell:

source ~/.zshrc
EOF

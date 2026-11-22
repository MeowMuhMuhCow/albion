#!/bin/bash
# python_pakete.sh - sorgt dafuer, dass python3 die Pakete unicorn und capstone hat (ohne sudo)
python3 -c "import unicorn, capstone" 2>/dev/null && exit 0
echo "[pakete] unicorn/capstone fehlen - installiere fuer diesen Benutzer ..."
if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "[pakete] pip fehlt - hole get-pip.py"
  curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py || { echo "[pakete] Download fehlgeschlagen"; exit 1; }
  python3 /tmp/get-pip.py --user --break-system-packages -q 2>/dev/null || python3 /tmp/get-pip.py --user -q || exit 1
fi
python3 -m pip install --user --break-system-packages -q unicorn capstone 2>/dev/null \
  || python3 -m pip install --user -q unicorn capstone || exit 1
python3 -c "import unicorn, capstone; print('[pakete] ok: unicorn', unicorn.__version__, 'capstone', capstone.__version__)"

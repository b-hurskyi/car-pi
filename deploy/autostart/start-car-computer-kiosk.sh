#!/bin/sh

set -eu

app_url="http://127.0.0.1:8000"
health_url="${app_url}/health"
python_command="/home/bohdan/car-computer/backend/.venv/bin/python"
profile_directory="/home/bohdan/.local/share/car-computer/chromium-profile"

PATH="/usr/local/bin:/usr/bin:/bin"
export PATH

if [ ! -x "${python_command}" ]; then
    echo "Python virtual environment not found: ${python_command}" >&2
    exit 1
fi

if command -v chromium >/dev/null 2>&1; then
    chromium_command="chromium"
elif command -v chromium-browser >/dev/null 2>&1; then
    chromium_command="chromium-browser"
else
    echo "Chromium executable not found" >&2
    exit 1
fi

mkdir -p "${profile_directory}"

until "${python_command}" -c \
    "import urllib.request; urllib.request.urlopen('${health_url}', timeout=1).close()" \
    >/dev/null 2>&1
do
    sleep 1
done

exec "${chromium_command}" \
    --kiosk \
    --no-first-run \
    --user-data-dir="${profile_directory}" \
    --password-store=basic \
    "${app_url}"

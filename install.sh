#!/usr/bin/env bash

# Install python requirements first
if ! which pip &> /dev/null; then
    echo '[ERROR] pip command missing, setup python + pip and try again'
    exit 1
fi

pip install --user -r ./requirements.txt 2> /dev/null
pip_code=$?
if [[ ${pip_code} -ne 0 ]]; then
    echo -e "\n[FATAL] Failed to install python requirements via pip"
    exit ${pip_code}
fi

install_path='/usr/local/bin/diary'

echo "Copying to '${install_path}'"
cp ./diary.py ${install_path}

cp_code=$?
if [[ ${cp_code} -ne 0 ]]; then
    echo -e "\n[FATAL] Error copying file, ensure you have rights, or try running as root"
    exit ${cp_code}
fi

echo -e "\nInstallation complete\n"

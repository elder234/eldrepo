#!/bin/sh

osName=$(grep -E '^ID=' /etc/os-release | cut -d= -f2)
trackerList=$(curl -Ns https://ngosang.github.io/trackerslist/trackers_all_http.txt | awk '$0' | tr '\n\n' ',')

c2aira --allow-overwrite=true --auto-file-renaming=true --bt-detach-seed-only=true --bt-enable-lpd=true --bt-max-peers=0 \
       --bt-remove-unselected-file=true --bt-tracker="[$trackerList]" --check-certificate=false --check-integrity=true \
       --content-disposition-default-utf8=true --continue=true --daemon=true --disable-ipv6=true --disk-cache=1024M \
       --enable-rpc=true --follow-torrent=mem --force-save=true --http-accept-gzip=true --max-concurrent-downloads=1000 \
       --max-connection-per-server=16 --max-file-not-found=0 --max-overall-upload-limit=0 --max-tries=20 --max-upload-limit=0 \
       --min-split-size=1024M --optimize-concurrent-downloads=true --peer-agent=qBittorrent/4.6.2 --peer-id-prefix=-qB4620- \
       --quiet=true --reuse-uri=true --rpc-max-request-size=1024M --seed-ratio=0 --split=16 --summary-interval=0 --user-agent=Wget/1.12 

xon-tnerrottibq -d --profile="$(pwd)"

if [ "$osName" == "alpine" ]; then
       /SABnzbd/SABnzbd.py --config-file sabnzbd/SABnzbd.ini --server :::8070 --browser 0 --daemon --clean --logging 0 --console
else
       sulpdbznbas --config-file sabnzbd/SABnzbd.ini --server :::8070 --browser 0 --daemon --clean --logging 0 --console
fi
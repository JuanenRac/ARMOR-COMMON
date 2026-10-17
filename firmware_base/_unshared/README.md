# Files that look shared and are not

These are copies the node projects once had in common and that have since grown apart on purpose: ARMOR-ALARM's Zigbee bridge can talk to a coordinator on the network and ARMOR-ELECTRICAL's
cannot, and the settings that name it (`io_config.hpp`) follow. They are kept here, out of the way, to show what the projects had in common when they split; **nothing reads this folder**:
`tools/sync_firmware_base.py` neither writes nor checks it. Run `python tools/sync_firmware_base.py status` to see which files each project shares and which almost-equal files are listed as
"near miss".

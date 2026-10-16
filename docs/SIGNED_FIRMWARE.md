# Signed firmware: how a node decides what it installs from GitHub

A node that updates itself from GitHub (the *Look for updates* and *Install the latest* buttons of its panel) trusts three things, in this order:

1. **Where it looks:** the releases of its own repository (`JuanenRac/ARMOR-<NODE>`), over HTTPS.
2. **The hash:** the image it downloads must hash (SHA-256) to the value in the `<image>.sha256` file of the release. This catches a truncated or mixed-up download.
3. **The signature:** the file `<image>.sig` holds the Ed25519 signature (64 bytes as 128 hexadecimal digits) of those 32 bytes of hash. The node verifies it with the public key of the releases, which is part of its firmware (`firmware_base/core/fw_trust.hpp`). A release without a signature, or with one that does not verify, is refused and the node changes nothing.

Without the third step, whoever could change what a release holds on GitHub (a stolen account, a malicious maintainer of a dependency of the release tooling) could publish a firmware and its matching hash. With it, they would also need the private key, which is never on GitHub.

## What is not covered

- The upload of a firmware file by an administrator in the panel is **not** checked: it is the administrator's own act, and it is the way out when something has to change (a lost key, a board with no Internet route).
- A node that is running a firmware from before this check does not verify anything the first time: the first signed release is installed by trust in the hash alone. From then on the node enforces the signature.
- The key protects the releases, not the boards: somebody with a cable and physical access can flash anything.

## The key

- The private key is `~/.armor/firmware_ed25519.pem` on the maintainer's computer (PKCS #8, mode 0600). **It must be backed up** somewhere safe and offline: if it is lost, no new release can be installed by the nodes' GitHub updater until a firmware that holds a new public key has been installed by the manual upload or by cable.
- It is never copied into a repository, a CI secret or a release. `release.py` refuses to publish if the key it holds is not the one the firmware trusts.
- The public key is in `firmware_base/core/fw_trust.hpp` (and so in the five projects' copies, kept identical by `tools/sync_firmware_base.py check`).

## Publishing a release

`python release.py KIND VERSION` (the maintainer's tool) builds the assets of every board and, for each application image, writes `<image>.sha256` and `<image>.sig` (`node ~/.armor/sign.mjs --digest <sha256>`). Nothing else signs; the CI never has the key.

## Changing the key

1. Make a new pair, put the new public key in `fw_trust.hpp`, build and release a firmware **signed with the old key**: the nodes install it, and from then on trust the new key.
2. Sign the following releases with the new key.
3. A node that missed step 1 (it is still on the old key) needs the manual upload or a cable.

## How the check is tested

`firmware_base/tests/test_base.cpp` runs SHA-512 and Ed25519 on a computer against signatures and hashes made by Node's own implementations (several keys, messages of several sizes), with the message, each part of the signature and the key altered one at a time, and verifies a hash signed with the real key of the releases. `tests/test_release.cpp` checks that the signature file picked is the one next to the image of this board.

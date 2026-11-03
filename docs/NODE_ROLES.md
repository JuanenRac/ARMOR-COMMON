# The access of each kind of broker identity

`src/armor_common/node_roles.json` is the one table of what each kind of identity may do on the broker: the user name pattern and the access lines, with `{name}` for the name of the node. `armor_common.node_roles` reads it (`user_for`, `acl_lines`, `acl_block`).

The rules it keeps, checked by `tests/test_node_roles.py`: a node writes only under its own name, no node can write an order topic (only the identity of the server publishes orders), and a name outside `^[a-z0-9][a-z0-9_-]{0,63}$` is refused.

ARMOR-DEVOPS `scripts/mqtt_identity.sh` writes the blocks and its test compares what it writes for every role with this table, so the script and the table cannot drift apart. The lines of the server itself are in ARMOR-DEVOPS `scripts/armor_server.acl`, and the lines that are written only on purpose (commands) stay with the commands of `mqtt_identity.sh` that switch them on.

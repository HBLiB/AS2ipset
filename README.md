# AS2ipset
create ipset nethash for a specifc AS announced Prefixes

Just run it like the following:

python3 AS2ipset.py 'AS49981'

This will create an ipset with the name AS49981 and all the latest announced prefixes by this AS in a nethash.
Which you can utlize in iptables.

Maybe new features later, if needed in real live situations...

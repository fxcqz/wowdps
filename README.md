# wow dps table

Make a table of the top wow dps specs for each class.

Run main.py to obtain the data (writes to data.json) then run parse.py to print
the results.

## limitations

* If a spec does not appear in the top 100 for that class, it will not appear in
the final results table.

* Hardcoded ilvl ranges for each spec (update this as ilvl gets higher, or make
it dynamic).

## results

```
Spec             DPS
-----------  -------
Havoc        13058.1
Outlaw       12680.2
Subtlety     12664.6
Retribution  12160.7
Windwalker   12061.2
Affliction   11990.3
Arcane       11958.7
Fury         11883.1
Arms         11772.6
Frost        11512.1
Enhancement  11377.3
Elemental    11275.4
Unholy       10997.5
Shadow       10554.7
```

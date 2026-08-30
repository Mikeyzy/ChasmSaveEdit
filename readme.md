### Chasm Save Editor

A simple save editor for Chasm written in Python

It can edit item attributes(quantity, etc.) and equipment attributes(rarity, etc.) with console interface

minimun python version: 3.10 (type annotations support)

pywin32 module is optional for better file dialog support

If it fails to load some items, you may report it in issue page with error message attached

This is usually caused by extra data associated with the item

You can also try to fix it by add the item to `_SPECIAL_ITEM_EXTRA_DATA_SIZE` in `_common.py`



### Chasm[2018] Save Editor

A simple save editor for Chasm[2018] written in Python

[Chasm](https://store.steampowered.com/app/312200/Chasm/)

It can edit item attributes(quantity, etc.) and equipment attributes(rarity, etc.) with console interface

*Always remember to backup your save before editing, this may corrupt your save*

minimun python version: 3.10 (type annotations support)

pywin32 module is optional for better file dialog support

If it fails to load some items, you may report it in issue page with error message attached

This is usually caused by extra data associated with the item

You can also try to fix it by add the item to `_SPECIAL_ITEM_EXTRA_DATA_SIZE` in `_common.py`



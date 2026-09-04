import os, sys, time

import _common

_WIN32API_AVAILABLE = False
HOMEPATH = os.environ.get('USERPROFILE', os.environ.get('HOME', ''))
CHASM_SAVE_DIR = os.path.join(HOMEPATH, 'Documents', 'Chasm')
_LAST_OPENED_DIR = ''
_VERSION = '1.02'

try:
	import win32ui, win32con
	_WIN32API_AVAILABLE = True
except ImportError:
	pass

try:
	import json5 as json
except ImportError:
	import json


MENU_INIT = [
	'1.Load File',
	'2.Save File',
	'3.Edit Items',
	'4.Export items to JSON',
	'5.Import items from JSON',
	'6.Import items from JSON (Override)',
	'x.Exit',
]

MENU_SELECT_ITEM_CATEGORY = [
	'1.Weapon',
	'2.Spell',
	'3.Helmet',
	'4.Armor',
	'5.Accessory',
	'6.Item',
	'b.Back',
]

MENU_ACTION = [
	'1.Edit Selected Item',
	'2.Duplicate Selected Item',
	'3.Remove Selected Item',
	'4.Move Selected Item',
	'b.Back',
]

MENU_EDIT_ITEM_ATTRIBUTE = [
	'1.Id',
	'2.Quantity',
	'3.Reserved1',
	'4.Reserved2',
	'5.Extra Data',
	'b.Back',
]

MENU_EDIT_EQUIPMENT_ATTRIBUTE = [
	' 1.Id',
	' 2.Rarity/Quality',
	' 3.CON [Constitution]',
	' 4.HP  [Health]',
	' 5.INT [Intelligence]',
	' 6.LCK [Luck]',
	' 7.MP  [Mana]',
	' 8.STR [Strength]',
	' 9.Reserved',
	'10.Extra Data',
	'b.Back',
]

def clearTerminal():
	# print("\033[H\033[J", end="", flush=True)
	print("\033[H\033[2J\033[3J", end="", flush=True)
	print(f'#### Chasm Save Editor V{_VERSION} @MikesLab ####')

def selectMenuOptions(menu: list, title: str = '') -> str:
	if len(title):
		print(f'{title:=^32}')
	for line in menu:
		print(line)
	return input('Option Selected: ')

def getOpenSaveFileName(bOpen=False, sTitle: str = '', sDefaultName: str = '', sDefaultExt: str = '', sInitDir: str = '', sFilter: str = 'All Files (*.*)|*.*||') -> str:
	sIn = ''
	if _WIN32API_AVAILABLE:
		if bOpen:
			flags = win32con.OFN_FILEMUSTEXIST | win32con.OFN_PATHMUSTEXIST
			if len(sTitle) == 0:
				sTitle = 'Open File'
		else:
			flags = win32con.OFN_OVERWRITEPROMPT
			if len(sTitle) == 0:
				sTitle = 'Save File'
		dialog = win32ui.CreateFileDialog(
			bOpen,
			sDefaultExt,
			sDefaultName,
			flags,
			sFilter,
		)
		if len(sInitDir):
			dialog.SetOFNInitialDir(sInitDir)
		dialog.SetOFNTitle(sTitle)
		if dialog.DoModal() == win32con.IDOK:
			sIn = dialog.GetPathName()
	else:
		if bOpen:
			prompt = '>>> Open file path: '
		else:
			prompt = '>>> Save file path: '
		sIn = input(prompt)
	return sIn

if __name__ == '__main__':
	print(f"\033]0;Chasm Save Editor\007", end="", flush=True)
	save = _common.SaveData()
	selectedItem = -1
	while 1:
		# menu base
		clearTerminal()
		if len(save._pathCurrentFile):
			print(f'Current File: {save._pathCurrentFile}')
		else:
			print(f'No File Loaded')
		sIn = selectMenuOptions(MENU_INIT)
		if sIn == 'x':
			break
		elif sIn == '1':
			# load file
			sIn = getOpenSaveFileName(True, 'Open Chasm Save File', '*.sav', '.sav', CHASM_SAVE_DIR, 'Chasm Save File (*.sav)|*.sav|All Files (*.*)|*.*||')
			# if _WIN32API_AVAILABLE:
			# 	dialog = win32ui.CreateFileDialog(
			# 		1,
			# 		'.sav',
			# 		'*.sav',
			# 		win32con.OFN_FILEMUSTEXIST | win32con.OFN_PATHMUSTEXIST,
			# 		"Chasm Save File (*.sav)|*.sav|All Files (*.*)|*.*||",
			# 	)
			# 	if os.path.isdir(CHASM_SAVE_DIR):
			# 		dialog.SetOFNInitialDir(_LAST_OPENED_DIR or CHASM_SAVE_DIR)
			# 	dialog.SetOFNTitle('Open Chasm Save File')
			# 	if dialog.DoModal() == win32con.IDOK:
			# 		sIn = dialog.GetPathName()
			# 		_LAST_OPENED_DIR = os.path.dirname(sIn)
			# 	else:
			# 		continue
			# else:
			# 	sIn = input('Load File Path: ')
			try:
				print(f'Load File: {sIn}')
				_common.ERROR_STATUS = 0
				if save.loadFile(sIn):
					print(f'Error occurred when loading file')
					input('Press Enter to continue...')
				if _common.ERROR_STATUS:
					print(f'Error occurred when loading file')
					input('Press Enter to continue...')
			except Exception as e:
				# raise
				print(f'Error occurred when loading file')
				input('Press Enter to continue...')
		elif len(save._pathCurrentFile):
			if sIn == '2':
				# save file
				newFileName = os.path.basename(save._pathCurrentFile)
				if '.sav' in newFileName.lower():
					newFileName = newFileName[:newFileName.index('.sav')] + '_edited.sav'
				getOpenSaveFileName(False, 'Save Chasm Save File', newFileName, '.sav', _LAST_OPENED_DIR, 'Chasm Save File (*.sav)|*.sav|All Files (*.*)|*.*||')
				# if _WIN32API_AVAILABLE:
				# 	dialog = win32ui.CreateFileDialog(
				# 		0,
				# 		'.sav',
				# 		newFileName,
				# 		win32con.OFN_OVERWRITEPROMPT,
				# 		"Chasm Save File (*.sav)|*.sav|All Files (*.*)|*.*||",
				# 	)
				# 	if _LAST_OPENED_DIR:
				# 		dialog.SetOFNInitialDir(_LAST_OPENED_DIR)
				# 	dialog.SetOFNTitle('Save Chasm Save File')
				# 	if dialog.DoModal() == win32con.IDOK:
				# 		sIn = dialog.GetPathName()
				# 	else:
				# 		continue
				# else:
				# 	sIn = input('>>> Save file path: ')
				try:
					save.saveFile(sIn)
				except Exception as e:
					print(f'Error occurred when saving file')
			elif sIn == '3':
				# edit items
				while 1:
					# menu select item category
					clearTerminal()
					print('=> Select Item Category')
					sIn = selectMenuOptions(MENU_SELECT_ITEM_CATEGORY)
					itemTypeToEdit = ''
					lItemToEdit:list[_common.Item|_common.Equipment] = []
					if sIn == 'b':
						break
					elif sIn == '1':
						# edit weapon
						lItemToEdit = save.lWeapon
						itemTypeToEdit = 'Weapon'
					elif sIn == '2':
						# edit spell
						lItemToEdit = save.lSpell
						itemTypeToEdit = 'Spell'
					elif sIn == '3':
						# edit helmet
						lItemToEdit = save.lHelmet
						itemTypeToEdit = 'Helmet'
					elif sIn == '4':
						# edit armor
						lItemToEdit = save.lArmor
						itemTypeToEdit = 'Armor'
					elif sIn == '5':
						# edit accessory
						lItemToEdit = save.lAccessory
						itemTypeToEdit = 'Accessory'
					elif sIn == '6':
						# edit item
						lItemToEdit = save.lItem
						itemTypeToEdit = 'Item'
					if len(lItemToEdit):
						clearTerminal()
						while 1:
							# list items
							print(f'==> Editing {itemTypeToEdit}, total: {len(lItemToEdit)}')
							print(f'Index: Item Id')
							for i in range(len(lItemToEdit)):
								if isinstance(lItemToEdit[i], _common.Equipment):
									print(f'{i:>2}: {lItemToEdit[i].sId} Rarity:{lItemToEdit[i].iRarity}')
								else:
									print(f'{i:>2}: {lItemToEdit[i].sId} x{lItemToEdit[i].iQuantity}')
							print('s: Sort by Item Id')
							print('b: Back')
							sIn = input('>>> Select item index to edit: ')
							if sIn == 'b':
								break
							elif sIn.lower() == 's':
								# sort item
								lItemToEdit.sort(key=lambda x: (x.sId, x.iQuantity, 0 if isinstance(x, _common.Item) else x.iRarity))
								continue
							try:
								iSelected = int(sIn)
							except Exception as e:
								print('Invalid input')
								continue
							if iSelected < 0 or iSelected >= len(lItemToEdit):
								print('Invalid input')
								continue
							selectedItem = lItemToEdit[iSelected]
							# menu action
							sIn = selectMenuOptions(MENU_ACTION)
							if sIn == 'b':
								break
							elif sIn == '1':
								# edit item
								while 1:
									# menu edit item attribute
									clearTerminal()
									print(f'==> Editing [{iSelected}]{selectedItem.sId}')
									if isinstance(selectedItem, _common.Item):
										# display item attributes
										print(f'->Item Id: {selectedItem.sId}')
										print(f'->Quantity: {selectedItem.iQuantity}')
										print(f'->Reserved1: {selectedItem.iReserved1}')
										print(f'->Reserved2: {selectedItem.iReserved2}')
										print(f'->Extra Data: {_common.bytesToHexString(selectedItem.bExtraData)}')
										sIn = selectMenuOptions(MENU_EDIT_ITEM_ATTRIBUTE)
										if sIn == 'b':
											break
										elif sIn == '1':
											# edit item id
											sIn = input('>>> New Item Id: ')
											if len(sIn) > 0:
												selectedItem.sId = sIn
											else:
												print('Invalid input')
										elif sIn == '2':
											# edit quantity
											sIn = input('>>> New Quantity: ')
											if sIn.isdigit():
												selectedItem.iQuantity = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '3':
											# edit reserved1
											sIn = input('>>> New Reserved1: ')
											if sIn.isdigit():
												selectedItem.iReserved1 = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '4':
											# edit reserved2
											sIn = input('>>> New Reserved2: ')
											if sIn.isdigit():
												selectedItem.iReserved2 = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '5':
											# edit extra data
											sIn = input('>>> New Extra Data: ')
											if len(sIn) > 0:
												data = _common.hexStringToBytes(sIn)
												if data is not None:
													selectedItem.bExtraData = data
												else:
													print('Invalid input')
											else:
												print('Invalid input')
									elif isinstance(selectedItem, _common.Equipment):
										# display equipment attributes
										print(f'->Item Id: {selectedItem.sId}')
										print(f'->Rarity: {selectedItem.iRarity}')
										print(f'->CON[Constitution]: {selectedItem.iConstitution}')
										print(f'->HP [Health]: {selectedItem.iHealth}')
										print(f'->INT[Intelligence]: {selectedItem.iIntelligence}')
										print(f'->LCK[Luck]: {selectedItem.iLuck}')
										print(f'->MP [Mana]: {selectedItem.iMana}')
										print(f'->STR[Strength]: {selectedItem.iStrength}')
										print(f'->Reserved: {selectedItem.iReserved}')
										print(f'->Extra Data: {_common.bytesToHexString(selectedItem.bExtraData)}')
										sIn = selectMenuOptions(MENU_EDIT_EQUIPMENT_ATTRIBUTE)
										if sIn == 'b':
											break
										elif sIn == '1':
											# edit item id
											sIn = input('>>> New Item Id: ')
											if len(sIn) > 0:
												selectedItem.sId = sIn
											else:
												print('Invalid input')
										elif sIn == '2':
											# edit rarity
											sIn = input('>>> New Rarity: ')
											if sIn.isdigit():
												selectedItem.iRarity = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '3':
											# edit constitution
											sIn = input('>>> New Constitution: ')
											if sIn.isdigit():
												selectedItem.iConstitution = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '4':
											# edit health
											sIn = input('>>> New Health: ')
											if sIn.isdigit():
												selectedItem.iHealth = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '5':
											# edit intelligence
											sIn = input('>>> New Intelligence: ')
											if sIn.isdigit():
												selectedItem.iIntelligence = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '6':
											# edit luck
											sIn = input('>>> New Luck: ')
											if sIn.isdigit():
												selectedItem.iLuck = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '7':
											# edit mana
											sIn = input('>>> New Mana: ')
											if sIn.isdigit():
												selectedItem.iMana = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '8':
											# edit strength
											sIn = input('>>> New Strength: ')
											if sIn.isdigit():
												selectedItem.iStrength = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '9':
											# edit reserved
											sIn = input('>>> New Reserved: ')
											if sIn.isdigit():
												selectedItem.iReserved = int(sIn)
											else:
												print('Invalid input')
										elif sIn == '10':
											# edit extra data
											sIn = input('>>> New Extra Data: ')
											if len(sIn) > 0:
												data = _common.hexStringToBytes(sIn)
												if data is not None:
													selectedItem.bExtraData = data
												else:
													print('Invalid input')
											else:
												print('Invalid input')
								clearTerminal()
							elif sIn == '2':
								# duplicate item
								lItemToEdit.append(selectedItem.copy())
								print(f'Duplicated item {selectedItem}')
							elif sIn == '3':
								# remove item
								sIn = input('>>> Are you sure? (Y/n):')
								if sIn.lower() == 'y':
									lItemToEdit.pop(iSelected)
									print(f'Removed item {selectedItem}')
								else:
									print('Canceled')
							elif sIn == '4':
								# move item
								sIn = input('>>> New Index: ')
								if sIn.isdigit():
									iNew = int(sIn)
									if 0 <= iNew < len(lItemToEdit) and iNew != iSelected:
										# valid index
										item = lItemToEdit.pop(iSelected)
										lItemToEdit.insert(iNew, item)
								else:
									print('Invalid input')
			elif sIn == '4':
				# export json file
				pathFile = getOpenSaveFileName(bOpen=False, sTitle='Save JSON File', sDefaultExt='.json', sFilter='JSON Files (*.json)|*.json|All Files (*.*)|*.*||')
				if len(pathFile) > 0:
					os.makedirs(os.path.dirname(pathFile), exist_ok=True)
					with open(pathFile, 'w', encoding='utf-8') as file:
						file.write(json.dumps(save.toJson(), indent='\t'))
						print('Save data exported to JSON')
			elif sIn in ('5', '6'):
				# import json file
				override = (sIn == '6')
				if override:
					if input('>>> WARNING: This will override items in current save file. Continue? (Y/n):').lower() != 'y':
						continue
				pathFile = getOpenSaveFileName(bOpen=True, sTitle='Open JSON File', sDefaultExt='.json', sFilter='JSON Files (*.json)|*.json|All Files (*.*)|*.*||')
				if os.path.isfile(pathFile):
					with open(pathFile, 'r', encoding='utf-8') as file:
						dItems = json.load(file)
						itemLoaded = save.loadJson(dItems, override)
						print(f'Loaded {itemLoaded} items')
		else:
			print('No file loaded')
			time.sleep(1)
	print('Exiting...')

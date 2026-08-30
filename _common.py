import os, struct, warnings

BYTES_NULL_ITEM = b'\x04null'
ERROR_STATUS = 0

# Item Attributes
# sz   itemId                          iQuantity     iReserved1    iReserved2
# [0A] [66 6F 6F 64 5F 61 70 70 6C 65] [11 00 00 00] [00 00 00 00] [00 00 00 00]
# Spell Attributes
# sz   itemId                                iQuantity     iReserved1    iReserved2
# [0C] [73 70 65 6C 6C 5F 42 6C 61 64 65 73] [01 00 00 00] [00 00 00 00] [F4 01 00 00]
StructItemAttributes = struct.Struct('<3I')

# Equipment Attributes
# sz   itemId                                                     iQuantity     iRarity       iConstitution iHealth       iIntelligence iLuck         iMana         iStrength     iReserved
# [13] [61 63 63 65 73 73 6F 72 79 5F 68 65 61 72 74 72 69 6E 67] [01 00 00 00] [02 00 00 00] [00 00 00 00] [0F 00 00 00] [02 00 00 00] [00 00 00 00] [06 00 00 00] [00 00 00 00] [00 00 00 00]
StructEquipmentAttributes = struct.Struct('<9I')

_SPECIAL_ITEM_EXTRA_DATA_SIZE = {
	'sword_assassins': 8,
	'head_birdhat': 20,
	'head_swordhat': 20,
}

def bytesToHexString(data: bytes):
	return ' '.join(f'{b:02x}' for b in data)

def hexStringToBytes(data: str):
	try:
		return bytes.fromhex(data)
	except:
		return None

class Item:
	sId: str
	iQuantity: int
	iReserved1: int
	iReserved2: int
	bExtraData: bytes

	def __init__(self, sId: str, iQuantity: int, iReserved1: int, iReserved2: int, bExtraData: bytes):
		self.sId = sId
		self.iQuantity = iQuantity
		self.iReserved1 = iReserved1
		self.iReserved2 = iReserved2
		self.bExtraData = bExtraData

	@classmethod
	def fromBytes(cls, data: bytes):
		sz = data[0]
		i = 1
		# sz = int.from_bytes(data[:4], 'little')
		# i = 4
		sId = data[i:sz+i].decode('utf-8')
		i += sz
		if sz > 64 or sz == 0:
			global ERROR_STATUS
			warnings.warn(f'Item id longer than 64 bytes, sz={sz}, {sId}\nData misalignment might occured in last item?')
			ERROR_STATUS = 1
		if sId == 'null':
			return cls.null()
		iQuantity, iReserved1, iReserved2 = StructItemAttributes.unpack(data[i:i+StructItemAttributes.size])
		i += StructItemAttributes.size
		sz = _SPECIAL_ITEM_EXTRA_DATA_SIZE.get(sId, 0)
		if sz > 0:
			bExtraData = data[i:i+sz]
		else:
			bExtraData = b''
		return cls(sId, iQuantity, iReserved1, iReserved2, bExtraData)
	
	@classmethod
	def null(cls):
		return cls('null', 0, 0, 0, b'')

	def toBytes(self):
		if self.sId == 'null':
			return BYTES_NULL_ITEM
		bName = self.sId.encode('utf-8')
		bData = len(bName).to_bytes(1, 'little')
		bData += bName
		bData += StructItemAttributes.pack(self.iQuantity, self.iReserved1, self.iReserved2)
		if len(self.bExtraData):
			bData += self.bExtraData
		return bData

	def copy(self):
		return Item(self.sId, self.iQuantity, self.iReserved1, self.iReserved2, self.bExtraData)

	def __repr__(self):
		return f'Item(sId={repr(self.sId)}, iQuantity={repr(self.iQuantity)}, iReserved1={repr(self.iReserved1)}, iReserved2={repr(self.iReserved2)}, bExtraData={repr(self.bExtraData)})'

	def __str__(self):
		return f'Item[{self.sId}] x{self.iQuantity}, {self.iReserved1}, {self.iReserved2}, {self.bExtraData}'

	@staticmethod
	def currentBlockSize(data):
		i = 1
		sz = data[0]
		sId = data[i:sz+i].decode('utf-8')
		i += sz
		if sId == 'null':
			return i
		i += StructItemAttributes.size
		sz = _SPECIAL_ITEM_EXTRA_DATA_SIZE.get(sId, 0)
		if sz > 0:
			i += sz
		return i

	@staticmethod
	def maxBlockSize():
		'Aproximate max block size, assume all id are 24 bytes long'
		return 1 + StructItemAttributes.size + 24

class Equipment:
	sId: str
	iRarity: int
	iConstitution: int
	iHealth: int
	iIntelligence: int
	iLuck: int
	iMana: int
	iStrength: int
	iReserved: int
	bExtraData: bytes

	def __init__(self, sId: str, iRarity: int, iConstitution: int, iHealth: int, iIntelligence: int, iLuck: int, iMana: int, iStrength: int, iReserved: int, bExtraData: bytes):
		self.sId = sId
		self.iQuantity = 1
		self.iRarity = iRarity
		self.iConstitution = iConstitution
		self.iHealth = iHealth
		self.iIntelligence = iIntelligence
		self.iLuck = iLuck
		self.iMana = iMana
		self.iStrength = iStrength
		self.iReserved = iReserved
		self.bExtraData = bExtraData

	@classmethod
	def fromBytes(cls, data: bytes):
		sz = data[0]
		i = 1
		# sz = int.from_bytes(data[:4], 'big')
		# i = 4
		sId = data[i:sz+i].decode('utf-8')
		i += sz
		if sz > 64 or sz == 0:
			global ERROR_STATUS
			warnings.warn(f'Item id longer than 64 bytes, sz={sz}, {sId}\nData misalignment might occured in last item?')
			ERROR_STATUS = 1
		if sId == 'null':
			return cls.null()
		# first decode with Item attributes
		_, iRarity, iReserved = StructItemAttributes.unpack(data[i:i+StructItemAttributes.size])
		if iRarity > 0:
			# decode again with Equipment attributes
			_, iRarity, iConstitution, iHealth, iIntelligence, iLuck, iMana, iStrength, iReserved = StructEquipmentAttributes.unpack(data[i:i+StructEquipmentAttributes.size])
			i += StructEquipmentAttributes.size
		else:
			iConstitution = 0
			iHealth = 0
			iIntelligence = 0
			iLuck = 0
			iMana = 0
			iStrength = 0
			i += StructItemAttributes.size
		sz = _SPECIAL_ITEM_EXTRA_DATA_SIZE.get(sId, 0)
		if sz > 0:
			bExtraData = data[i:i+sz]
			i += sz
		else:
			bExtraData = b''
		return cls(sId, iRarity, iConstitution, iHealth, iIntelligence, iLuck, iMana, iStrength, iReserved, bExtraData)
	
	@classmethod
	def null(cls):
		return Item.null()
	
	def toBytes(self):
		if self.sId == 'null':
			return BYTES_NULL_ITEM
		bName = self.sId.encode('utf-8')
		bData = len(bName).to_bytes(1, 'big')
		bData += bName
		if self.iRarity > 0:
			bData += StructEquipmentAttributes.pack(1, self.iRarity, self.iConstitution, self.iHealth, self.iIntelligence, self.iLuck, self.iMana, self.iStrength, self.iReserved)
		else:
			bData += StructItemAttributes.pack(1, self.iRarity, self.iReserved)
		if len(self.bExtraData):
			bData += self.bExtraData
		return bData

	def copy(self):
		return Equipment(self.sId, self.iRarity, self.iConstitution, self.iHealth, self.iIntelligence, self.iLuck, self.iMana, self.iStrength, self.iReserved, self.bExtraData)

	def __repr__(self):
		return f'Equipment(sId={repr(self.sId)}, iRarity={self.iRarity}, iConstitution={self.iConstitution}, iHealth={self.iHealth}, iIntelligence={self.iIntelligence}, iLuck={self.iLuck}, iMana={self.iMana}, iStrength={self.iStrength}, iReserved={self.iReserved}, bExtraData={repr(self.bExtraData)})'
	
	def __str__(self):
		return f'Equipment[{self.sId}] Rarity {self.iRarity}, CON {self.iConstitution}, HP {self.iHealth}, INT {self.iIntelligence}, LCK {self.iLuck}, MP {self.iMana} STR {self.iStrength}, {self.iReserved}, {self.bExtraData}'

	@staticmethod
	def currentBlockSize(data: bytes):
		i = 1
		sz = data[0]
		sId = data[i:sz+i].decode('utf-8')
		i += sz
		if sId == 'null':
			return i
		qty, rar, res = StructItemAttributes.unpack(data[i:i+StructItemAttributes.size])
		if rar > 0:
			i += StructEquipmentAttributes.size
		else:
			i += StructItemAttributes.size
		sz = _SPECIAL_ITEM_EXTRA_DATA_SIZE.get(sId, 0)
		if sz > 0:
			i += sz
		return i
	
	@staticmethod
	def maxBlockSize():
		'Aproximate max block size, assume all id are 24 bytes long'
		return 1 + StructEquipmentAttributes.size + 24

class SaveData:
	bHead: bytes
	lWeapon: list[Equipment|Item]
	# bSpell: bytes
	lSpell: list[Item]
	lHelmet: list[Equipment|Item]
	lArmor: list[Equipment|Item]
	lAccessory: list[Equipment|Item]
	lItem: list[Item]
	bTail: bytes
	_pathCurrentFile = ''

	def __init__(self):
		self.bHead = b''
		self.lWeapon = []
		# self.bSpell = b''
		self.lSpell = []
		self.lHelmet = []
		self.lArmor = []
		self.lAccessory = []
		self.lItem = []
		self.bTail = b''
	
	def loadFile(self, path: str):
		if os.path.isfile(path):
			with open(path, 'rb') as file:
				bSaveFile: bytes = file.read()
			# check header
			sz = bSaveFile[0]
			fVersion = float(bSaveFile[1:sz].decode('utf-8'))
			if fVersion < 1:
				print(f'Unsupported save file version: {fVersion}')
				return 1
			self._pathCurrentFile = path
			self.bHead = b''
			self.lWeapon.clear()
			self.lSpell.clear()
			self.lHelmet.clear()
			self.lArmor.clear()
			self.lAccessory.clear()
			self.lItem.clear()
			self.bTail = b''
			iWeapon = bSaveFile.index(BYTES_NULL_ITEM)
			iWeaponCount = int.from_bytes(bSaveFile[iWeapon-4:iWeapon], 'little')
			self.bHead = bSaveFile[:iWeapon-4]
			print(f'Weapon data start: {iWeapon}, count: {iWeaponCount}')
			bWeaponData = bSaveFile[iWeapon:iWeapon+Equipment.maxBlockSize()*iWeaponCount]
			i = 0
			for _ in range(iWeaponCount):
				sz = Equipment.currentBlockSize(bWeaponData[i:])
				bData = bWeaponData[i:i+sz]
				i += sz
				eq = Equipment.fromBytes(bData)
				if eq.sId == 'null': # skip null items
					continue
				print(f'Parsed: {eq}')
				self.lWeapon.append(eq)
			print(f'Weapon block end index: {iWeapon}')
			iSpellCount = int.from_bytes(bSaveFile[iWeapon+i:iWeapon+i+4], 'little')
			iSpell = iWeapon+i+4
			print(f'Spell data start: {iSpell}, count: {iSpellCount}')
			bSpellData = bSaveFile[iSpell:iSpell+Item.maxBlockSize()*iSpellCount]
			i = 0
			for _ in range(iSpellCount):
				sz = Item.currentBlockSize(bSpellData[i:])
				bData = bSpellData[i:i+sz]
				i += sz
				it = Item.fromBytes(bData)
				if it.sId == 'null': # skip null items
					continue
				print(f'Parsed: {it}')
				self.lSpell.append(it)
			print(f'Spell block end index: {iSpell+i}')
			iHelmetCount = int.from_bytes(bSaveFile[iSpell+i:iSpell+i+4], 'little')
			iHelmet = iSpell+i+4
			print(f'Helmet data start: {iHelmet}, count: {iHelmetCount}')
			bHelmetData = bSaveFile[iHelmet:iHelmet+Equipment.maxBlockSize()*iHelmetCount]
			i = 0
			for _ in range(iHelmetCount):
				sz = Equipment.currentBlockSize(bHelmetData[i:])
				bData = bHelmetData[i:i+sz]
				i += sz
				eq = Equipment.fromBytes(bData)
				if eq.sId == 'null': # skip null items
					continue
				print(f'Parsed: {eq}')
				self.lHelmet.append(eq)
			print(f'Helmet block end index: {iHelmet+i}')
			iArmorCount = int.from_bytes(bSaveFile[iHelmet+i:iHelmet+i+4], 'little')
			iArmor = iHelmet+i+4
			print(f'Armor data start: {iArmor}, count: {iArmorCount}')
			bArmorData = bSaveFile[iArmor:iArmor+Equipment.maxBlockSize()*iArmorCount]
			i = 0
			for _ in range(iArmorCount):
				sz = Equipment.currentBlockSize(bArmorData[i:])
				bData = bArmorData[i:i+sz]
				i += sz
				eq = Equipment.fromBytes(bData)
				if eq.sId == 'null': # skip null items
					continue
				print(f'Parsed: {eq}')
				self.lArmor.append(eq)
			print(f'Armor block end index: {iArmor+i}')
			iAccessoryCount = int.from_bytes(bSaveFile[iArmor+i:iArmor+i+4], 'little')
			iAccessory = iArmor+i+4
			print(f'Accessory data start: {iAccessory}, count: {iAccessoryCount}')
			bAccessoryData = bSaveFile[iAccessory:iAccessory+Equipment.maxBlockSize()*iAccessoryCount]
			i = 0
			for _ in range(iAccessoryCount):
				sz = Equipment.currentBlockSize(bAccessoryData[i:])
				bData = bAccessoryData[i:i+sz]
				i += sz
				eq = Equipment.fromBytes(bData)
				if eq.sId == 'null': # skip null items
					continue
				print(f'Parsed: {eq}')
				self.lAccessory.append(eq)
			print(f'Accessory block end index: {iAccessory+i}')
			iItemCount = int.from_bytes(bSaveFile[iAccessory+i:iAccessory+i+4], 'little')
			iItem = iAccessory+i+4
			print(f'Item data start: {iItem}, count: {iItemCount}')
			bItemData = bSaveFile[iItem:iItem+Item.maxBlockSize()*iItemCount]
			i = 0
			for _ in range(iItemCount):
				sz = Item.currentBlockSize(bItemData[i:])
				bData = bItemData[i:i+sz]
				i += sz
				it = Item.fromBytes(bData)
				print(f'Parsed: {it}')
				self.lItem.append(it)
			print(f'Item block end index: {iItem+i}')
			self.bTail = bSaveFile[iItem+i:]
			print(f'Tail data start: {iItem+i}, length: {len(self.bTail)}')
			print(f'Done')
			return 0
		return 1

	def saveFile(self, path:str):
		if not os.path.isdir(os.path.dirname(path)):
			os.makedirs(os.path.dirname(path))
		print(f'Saving to file: {path}')
		with open(path, 'wb') as file:
			file.write(self.bHead)
			file.flush()
			# Weapon
			print(f'Writing {len(self.lWeapon)} weapons')
			wpCount = len(self.lWeapon) + 1 # first item is null item
			file.write(wpCount.to_bytes(4, 'little'))
			file.write(Item.null().toBytes())
			for item in self.lWeapon:
				print(f'Writing: {item}')
				file.write(item.toBytes())
			file.flush()
			# Spell
			print(f'Writing {len(self.lSpell)} spells')
			spCount = len(self.lSpell) + 1 # first item is null item
			file.write(spCount.to_bytes(4, 'little'))
			file.write(Item.null().toBytes())
			for item in self.lSpell:
				print(f'Writing: {item}')
				file.write(item.toBytes())
			file.flush()
			# Helmet
			print(f'Writing {len(self.lHelmet)} helmets')
			helmetCount = len(self.lHelmet) + 1 # first item is null item
			file.write(helmetCount.to_bytes(4, 'little'))
			file.write(Item.null().toBytes())
			for item in self.lHelmet:
				print(f'Writing: {item}')
				file.write(item.toBytes())
			file.flush()
			# Armor
			print(f'Writing {len(self.lArmor)} armors')
			armorCount = len(self.lArmor) + 1 # first item is null item
			file.write(armorCount.to_bytes(4, 'little'))
			file.write(Item.null().toBytes())
			for item in self.lArmor:
				print(f'Writing: {item}')
				file.write(item.toBytes())
			file.flush()
			# Accessory
			print(f'Writing {len(self.lAccessory)} accessories')
			accessoryCount = len(self.lAccessory) + 1 # first item is null item
			file.write(accessoryCount.to_bytes(4, 'little'))
			file.write(Item.null().toBytes())
			for item in self.lAccessory:
				print(f'Writing: {item}')
				file.write(item.toBytes())
			file.flush()
			# Item
			print(f'Writing {len(self.lItem)} items')
			itemCount = len(self.lItem)
			file.write(itemCount.to_bytes(4, 'little'))
			for item in self.lItem:
				print(f'Writing: {item}')
				file.write(item.toBytes())
			file.flush()
			file.write(self.bTail)
			file.flush()
		print(f'Done')

__all__ = ['BYTES_NULL_ITEM', 'bytesToHexString', 'hexStringToBytes', 'Item', 'Equipment', 'SaveData']

import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QSpinBox
from Cryptodome.Hash import SHA1
from Cryptodome.Cipher import AES

# Constants
SALT = "jjo+Ffqil5bdpo5VG82kLj8Ng1sK7L/rCqFTa39Zkom2/baqf5j9HMmsuCr0ipjYsPrsaNIOESWy7bDDGYWx1eA=="
BLOCK_SIZE = 16
CRC32_SIZE = 4


# CRC32 Class
class CRC32:
    def __init__(self):
        self.__table = self.__make_table()

    def compute(self, data):
        num = 0xD6EAF23C
        for idx in range(len(data)):
            num = num >> 8 ^ self.__table[data[idx] ^ num & 0xFF]
        return num

    @staticmethod
    def __make_table():
        table = []
        for idx1 in range(256):
            num = idx1
            for idx2 in range(8):
                num = num >> 1 if (num & 1) != 1 else num ^ 0x58E6D9AF
            table.append(num)
        return table


# Helper Functions
def password_derive_bytes(pstring, salt, iterations, keylen):
    lasthash = pstring + salt
    for i in range(iterations - 1):
        lasthash = SHA1.new(lasthash).digest()
    bytes = SHA1.new(lasthash).digest()
    ctrl = 1
    while len(bytes) < keylen:
        bytes += SHA1.new(str(ctrl).encode() + lasthash).digest()
        ctrl += 1
    return bytes[:keylen]


def pkcs5_unpad(data):
    return data[0:-data[-1]]


def pkcs5_pad(data):
    length = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([length] * length)


def verify_crc32(data):
    data_crc32 = CRC32().compute(data[0:len(data) - CRC32_SIZE])
    real_crc32 = int.from_bytes(data[len(data) - CRC32_SIZE:], byteorder='little')
    return data_crc32 == real_crc32


# Encryption and Decryption Logic
def decrypt_oc2(save_file_path, dest_file_path, steam_id):
    with open(save_file_path, 'rb') as file_d:
        data = file_d.read()
    if len(data) <= BLOCK_SIZE + CRC32_SIZE:
        raise RuntimeError("Cannot decrypt save because source save is too small")
    if not verify_crc32(data):
        print("WARNING: The save file seems corrupted (CRC32 mismatch)")
    aes_iv = data[:BLOCK_SIZE]
    data = data[BLOCK_SIZE:len(data) - CRC32_SIZE]
    key = password_derive_bytes(steam_id.encode(), SALT.encode(), 2, 32)
    cipher = AES.new(key, AES.MODE_CBC, iv=aes_iv)
    decrypted_file = pkcs5_unpad(cipher.decrypt(data))
    try:
        json.loads(decrypted_file)
    except json.JSONDecodeError:
        raise RuntimeError("Decryption failed, either the savegame is not valid or the wrong SteamID64 has been used.")
    with open(dest_file_path, "wb+") as file_d:
        file_d.write(decrypted_file)


def encrypt_oc2(save_file_path, dest_file_path, steam_id):
    with open(save_file_path, 'rb') as file_d:
        data = file_d.read()
    try:
        json.loads(data)
    except json.JSONDecodeError:
        raise RuntimeError("Cannot encrypt save because source save is not a valid JSON")
    key = password_derive_bytes(steam_id.encode(), SALT.encode(), 2, 32)
    cipher = AES.new(key, AES.MODE_CBC)
    aes_iv = cipher.iv
    with open(dest_file_path, "wb+") as file_d:
        crypted_data_with_iv = aes_iv + cipher.encrypt(pkcs5_pad(data))
        data_crc32 = CRC32().compute(crypted_data_with_iv)
        file_d.write(crypted_data_with_iv)
        file_d.write(data_crc32.to_bytes(4, byteorder='little'))


# GUI Application
class SaveFileConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.owner_id_label = QLabel('Owner Game ID:')
        self.owner_id_input = QLineEdit()
        layout.addWidget(self.owner_id_label)
        layout.addWidget(self.owner_id_input)

        self.friend_id_label = QLabel('Friend Game ID:')
        self.friend_id_input = QLineEdit()
        layout.addWidget(self.friend_id_label)
        layout.addWidget(self.friend_id_input)

        self.source_save_label = QLabel('Source Save File:')
        self.source_save_input = QLineEdit()
        self.source_save_button = QPushButton('Browse')
        self.source_save_button.clicked.connect(self.browse_source_save)
        layout.addWidget(self.source_save_label)
        layout.addWidget(self.source_save_input)
        layout.addWidget(self.source_save_button)

        self.slot_number_label = QLabel('Save Slot Number (1-3):')
        self.slot_number_input = QSpinBox()
        self.slot_number_input.setRange(1, 3)  # Allowing slot numbers only from 1 to 3
        layout.addWidget(self.slot_number_label)
        layout.addWidget(self.slot_number_input)

        self.destination_save_label = QLabel('Destination Folder:')
        self.destination_save_input = QLineEdit()
        self.destination_save_button = QPushButton('Browse')
        self.destination_save_button.clicked.connect(self.browse_destination_save)
        layout.addWidget(self.destination_save_label)
        layout.addWidget(self.destination_save_input)
        layout.addWidget(self.destination_save_button)

        self.convert_button = QPushButton('Convert Save File')
        self.convert_button.clicked.connect(self.convert_save_file)
        layout.addWidget(self.convert_button)

        self.setLayout(layout)
        self.setWindowTitle('Save File Converter')
        self.show()

    def browse_source_save(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Source Save File", "", "All Files (*)", options=options)
        if file_name:
            self.source_save_input.setText(file_name)

    def browse_destination_save(self):
        options = QFileDialog.Options()
        folder_name = QFileDialog.getExistingDirectory(self, "Select Destination Folder", options=options)
        if folder_name:
            self.destination_save_input.setText(folder_name)

    def convert_save_file(self):
        owner_id = self.owner_id_input.text()
        friend_id = self.friend_id_input.text()
        source_save = self.source_save_input.text()
        destination_save = self.destination_save_input.text()
        slot_number = self.slot_number_input.value()

        if not owner_id or not friend_id or not source_save or not destination_save:
            QMessageBox.warning(self, 'Input Error', 'All fields are required.')
            return

        try:
            # Adjust the save file name based on the slot number (1-based input converted to 0-based save file format)
            base_name = os.path.basename(source_save)
            new_slot_name = base_name.replace("_0.save", f"_{slot_number - 1}.save")
            temp_decrypted_path = os.path.join(destination_save, new_slot_name)

            # Perform decryption and re-encryption
            decrypt_oc2(source_save, temp_decrypted_path, owner_id)
            final_save_path = os.path.join(destination_save, new_slot_name)
            encrypt_oc2(temp_decrypted_path, final_save_path, friend_id)

            QMessageBox.information(self, 'Success', f'Save file converted successfully: {final_save_path}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SaveFileConverter()
    sys.exit(app.exec_())

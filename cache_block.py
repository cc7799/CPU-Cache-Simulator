class CacheBlock:
    """
    Stores and controls a single block of the cache
    """
    def __init__(self, memory: bytearray, block_size: int):
        """
        Creates an empty block
        :param memory: The byte array containing the simulation's memory
        :param block_size: The size of each block in bits
        """
        self.memory = memory
        self.block_size = block_size
        self.occupied = False  # Whether the block is storing memory or not
        self.dirty = False  # Whether the data in the block has been changed
        self.tag = -1

        bytes_per_block = int(self.block_size / 8)

        self.word = bytearray(bytes_per_block)

    def read_from_memory(self, address: int, tag: int):
        """
        Reads a value from an address in memory
        :param address: The address of the value
        :param tag: The tag of the address
        """
        self.occupied = True
        self.tag = tag

        for i in range(0, 4):
            self.word[i] = self.memory[address + i]

    def read_from_cache(self, tag: int):
        """
        Reads a value from a memory address that is currently in the cache
        :param tag: The tag of the address of the value to read
        """
        self.tag = tag
        self.occupied = True

    def write_to_memory(self, address: int):
        """
        Writes a value to an address in memory
        :param address: The address to write to
        """
        for i in range(0, 4):
            self.memory[address + i] = self.word[i]

    def write_to_cache(self, word):
        """
        Reads a value to a memory address that is currently in the cache
        :param word: The word to write to the cache
        """
        self.word = word

    def clear_block(self):
        """
        Clears a block of any data
        """
        self.occupied = False
        self.dirty = False
        self.tag = -1
        self.word = bytearray(4)

    def get_word_hex(self):
        """
        Returns the word stored in the block in hexadecimal form
        :return: The hexadecimal form of the word stored in the block
        """
        return self.word.hex()

    def get_word_dec(self):
        """
        Returns the word stored in the block in decimal form
        :return: The decimal form of the word stored in the block
        """
        return self.word[0] + 256 * (self.word[1] + 256 * (self.word[2] + 256 * (self.word[3])))


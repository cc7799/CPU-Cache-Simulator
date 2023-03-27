import math
from typing import Dict

from cache import Cache


def int_to_bytearray(num: int) -> bytearray:
    """
    Converts an integer to a byte array
    :param num: The integer to convert
    :return: The given integer as a bytearray
    """
    word_int = num
    word_bytes = bytearray(4)
    bytes_to_load = [0, 0, 0, 0]
    num_bits_to_remove = int(math.pow(2, 8))

    for j in range(0, 4):
        bytes_to_load[j] = word_int % num_bits_to_remove
        word_int = word_int // num_bits_to_remove

    for p in range(0, 4):
        word_bytes[p] = bytes_to_load[p]

    return word_bytes


def operation_details_to_string(operation_details: Dict):
    """
    Creates an output string in the following format

    "<read or write> <hit or miss> <'+replace' if cache block replaced>
    [addr = <address>, offset = <address offset>, set index = <index of set accessed>, tag = <address tag>,
    word = <word read or written> (<range of block accessed>)]"

    If a cache block was replaced
        "[evict tag <tag of evicted block>, in block index <index of evicted block>]"

    If the simulator is in write-back mode and data was written back to memory
        "[write back (<range of block accessed>)]"

    "<tag queue>"
    :param operation_details: The details of the operation
    :return: The string representation of the operation
    """
    basic_details = ""
    evict_details = None
    write_back_details = None

    op_result = operation_details["op_result"]

    if operation_details["op_type"] == "read":
        basic_details += "read " + str(op_result["hit_or_miss"]) + " "

        # If a block in the cache was replaced
        if op_result["replace_details"] is not None:
            replace_details = op_result["replace_details"]
            basic_details += "+ replace "
            evict_details = "[evict tag " + str(replace_details["evict_tag"]) \
                            + ", in block index " + str(replace_details["evict_index"]) + "]"

    elif operation_details["op_type"] == "write":
        basic_details += "write " + str(op_result["hit_or_miss"]) + " "

        if op_result["write_back"] is True:
            write_back_details = "[write back (" + op_result["block_range"]["min"] \
                                 + " - " + op_result["block_range"]["max"] + ")]"

    basic_details += "[addr = " + str(op_result["address"]) + ", offset = " + str(op_result["offset"]) + \
                     ", set index = " + str(op_result["set_index"]) + ", tag = " + str(op_result["tag"]) + \
                     ", word = " + str(op_result["word"]) + \
                     " (" + op_result["block_range"]["min"] + " - " + op_result["block_range"]["max"] + ")]"

    output = basic_details + "\n"

    if evict_details is not None:
        output += evict_details + "\n"
    if write_back_details is not None:
        output += (write_back_details + "\n")

    output += str(op_result["tag_queue"]) + "\n"

    return output


class CacheSim:
    """
    Creates and simulates a cache with the given parameters
    """
    def __init__(self, address_size: int, cache_size: int, block_size: int, associativity: int, write_back: bool):
        """
        Creates a new cache simulator and initialized the memory bytearray
        :param address_size: The size of the memory addresses in bits
        :param cache_size: The size of the cache in bits
        :param block_size: The size of each block in bits
        :param associativity: The associativity of the cache
        :param write_back: Whether the cache should be run in write-back mode
        """

        self.address_size = address_size
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.write_back = write_back

        self.memory_size = int(math.pow(2, address_size))

        # Initialize memory
        self.memory = bytearray(self.memory_size)
        for i in range(0, self.memory_size, 4):
            word = i
            bytes_to_load = []
            num_bits_to_remove = int(math.pow(2, 8))

            for j in range(0, 4):
                bytes_to_load.append(word % num_bits_to_remove)
                word = word // num_bits_to_remove

            for p in range(0, 4):
                self.memory[i + p] = bytes_to_load[p]

        self.cache = Cache(self.memory, self.address_size, self.cache_size, self.block_size,
                           self.associativity, self.write_back)

    def read(self, address: int):
        """
        Get the value from a given memory address
        :param address: The address to access; Must be four bytes
        :return: The value at the memory address
        """
        operation_details: Dict = {}
        assert(address % 4 == 0)
        assert(0 <= address <= self.memory_size)

        operation_details["op_type"] = "read"
        operation_details["op_result"] = self.cache.read(address)
        print(operation_details_to_string(operation_details))

    def write(self, address: int, word: int):
        """
        Writes a value to a given memory address
        :param address: The address to write to; Must be four bytes
        :param word: The data to write to the memory; Must be a four byte word
        :return:
        """
        operation_details: Dict = {}
        assert(address % 4 == 0)
        assert(0 <= address <= self.memory_size)

        byte_word = int_to_bytearray(word)

        operation_details["op_type"] = "write"
        operation_details["op_result"] = self.cache.write(address, byte_word)

        print(operation_details_to_string(operation_details))

    def print_memory(self):
        """
        Print the contents of the memory
        """
        for i in range(0, self.memory_size, 4):
            print("Word " + str(i) + ": ", end="")
            print(self.memory[i:i+4])

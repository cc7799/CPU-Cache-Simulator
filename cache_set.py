import math
from typing import Dict, Tuple

from cache_block import CacheBlock
from tag_queue import TagQueue


def find_range(address: int, block_size: int) -> Tuple:
    """
    Takes an address and finds the lowest and highest addresses in the given address' memory block
    :param address: An address in memory
    :param block_size: The size of the memory blocks in bits
    :return: A tuple in the form [<lower_limit>, <upper_limit>]
    """
    lower_limit = block_size * math.floor(address / block_size)
    upper_limit = lower_limit + (block_size - 1)

    return lower_limit, upper_limit


class CacheSet:
    def __init__(self, memory: bytearray, write_back: bool,
                 num_blocks: int, block_size: int, set_index: int):
        """
        Creates an empty set
        :param memory: The byte array containing the simulation's memory
        :param write_back: Whether the cache is in write-back mode
        :param num_blocks: The number of blocks in the set
        :param block_size: The size of each block in bits
        :param set_index: The index of the set in the cache
        """
        self.memory = memory
        self.write_back = write_back
        self.tag_queue = TagQueue(num_blocks)
        self.blocks = []
        self.num_blocks = num_blocks
        self.block_size = block_size
        self.set_index = set_index

        # Keeps track of the tag and block index of the most recently evicted block,
        #   will be -1 if no tags have been evicted or the last tag was not evicted
        self.evicted_tag = -1
        self.evicted_block_index = -1

        self.last_write_address = -1

        for i in range(0, self.num_blocks):
            self.blocks.append(CacheBlock(self.memory, self.block_size))

    def find_free_block(self):
        """
        Finds the first free (empty) block in the cache
        :return: The first free block if there is any free block; None otherwise
        """
        for block in self.blocks:
            if not block.occupied:
                return block

        return None

    def read_from_memory(self, address: int, tag: int, offset: int) -> Dict:
        """
        Reads a value from a memory address into the cache.
        If there is no free blocks in the cache, clears and reads into the least recently accessed block.
        :param address: The memory address to read from
        :param tag: The tag of the address
        :param offset: The offset of the address
        :return: A dictionary containing information about the results of the operation
        """
        operation_details: Dict = {}

        self.last_write_address = -1

        free_block = self.find_free_block()

        if free_block:
            free_block.read_from_memory(address, tag)
            block_accessed = free_block

            self.evicted_tag = -1
            self.evicted_block_index = -1
            operation_details["replace_details"] = None
        else:
            block_accessed = self.replace_cache_block(address, tag, operation_details)

        self.tag_queue.update_queue(tag)

        operation_details["word"] = block_accessed.get_word_dec()
        operation_details = self.add_basic_operation_details(operation_details, address, offset, tag)

        return operation_details

    def replace_cache_block(self, address: int, tag: int, operation_details: Dict) -> CacheBlock:
        """
        Replaces the least recently used cache block with the block from memory containing a given address
        :param address: The memory address to read from
        :param tag: The tag of the address
        :param operation_details: A dictionary containing information about the results of the operation
        :return: The new block that was added to the cache
        """
        least_recently_used_tag = self.tag_queue.get_least_recently_used()
        least_recently_used_block_index = self.find_block_index(least_recently_used_tag)
        least_recently_used_block = self.blocks[least_recently_used_block_index]

        # If write-back cache and block has been changed, write the data in the block to memory
        if self.write_back and least_recently_used_block.dirty:
            least_recently_used_block.write_to_memory(address)
            self.last_write_address = address
            operation_details["write_back"] = {"lower_limit": find_range(address, self.block_size)[0],
                                               "upper_limit": find_range(address, self.block_size)[1]}
        else:
            operation_details["write_back"] = None

        least_recently_used_block.clear_block()
        self.blocks[least_recently_used_block_index].read_from_memory(address, tag)
        block_accessed = self.blocks[least_recently_used_block_index]

        operation_details["replace_details"] = {"evict_tag": least_recently_used_tag,
                                                "evict_index": least_recently_used_block_index}

        return block_accessed

    def read_from_cache(self, address: int, tag: int, block_index: int, offset: int) -> Dict:
        """
        Reads a value from the cache
        :param address: The memory address to read from
        :param tag: The tag of the address
        :param block_index: The list index of the block in the cache where the memory address current resides
        :param offset: The offset of the address
        :return: A dictionary containing information about the results of the operation
        """
        operation_details = {}

        block_accessed = self.blocks[block_index]

        block_accessed.read_from_cache(tag)

        self.tag_queue.update_queue(tag)

        operation_details["word"] = block_accessed.get_word_dec()
        operation_details["replace_details"] = None
        operation_details = self.add_basic_operation_details(operation_details, address, offset, tag)

        return operation_details

    def write_to_cache(self, address: int, tag: int, block_index: int, offset: int, word, write_back: bool) -> Dict:
        """
        Writes a four byte word to the cache
        :param address: The memory address to read to
        :param tag: The tag of the memory address
        :param block_index: The index of the block in the set's block list
        :param offset: The address' offset
        :param word: The four-byte word to write to the cache
        :param write_back: Whether the cache is in write-back mode
        :return: A dictionary containing information about the results of the operation
        """
        operation_details = self.add_basic_operation_details({}, address, offset, tag)

        if write_back:
            return operation_details | self.write_to_cache_wb(block_index, word)
        else:
            return operation_details | self.write_to_cache_wt(address, block_index, word)

    def write_to_cache_wb(self, block_index: int, word: int) -> Dict:
        """
        Writes a word to the cache in write-back mode
        :param block_index: The index of the block in the set's block list
        :param word: The four-byte word to write to the cache
        :return: A dictionary containing information about the results of the operation
        """
        operation_details = {}
        block_accessed = self.blocks[block_index]

        block_accessed.write_to_cache(word)
        block_accessed.dirty = True

        operation_details["word"] = block_accessed.get_word_dec()
        operation_details["write_back"] = True

        return operation_details

    def write_to_cache_wt(self, address: int, block_index: int, word: int) -> Dict:
        """
        Writes a word to the cache in write-through mode
        :param address: The memory address to write to
        :param block_index: The index of the cache block
        :param word: The word to be written
        :return: A dictionary containing information about the results of the operation
        """
        operation_details = {}
        block_accessed = self.blocks[block_index]

        block_accessed.write_to_cache(word)
        block_accessed.write_to_memory(address)

        operation_details["word"] = block_accessed.get_word_dec()
        operation_details["write_back"] = False

        return operation_details

    def find_block_index(self, tag: int) -> int:
        """
        Finds the index of the block containing the memory address with the given tag, if it exists
        :param tag: The tag of the memory address to search for
        :return: The index of the block if it exists; -1 otherwise
        """
        for i in range(0, len(self.blocks)):
            if self.blocks[i].tag == tag and self.blocks[i].occupied:
                return i

        return -1

    def add_basic_operation_details(self, operation_details: Dict, address: int, offset: int, tag: int) -> Dict:
        """
        Adds operation details that are present in every type of operation to the dictionary
        :param operation_details: The dictionary to add to
        :param address: The address of the memory access
        :param offset: The offset of the address
        :param tag: The tag of the address
        :return: The parameter `operation_details` combined with a dictionary containing the basic details
        """
        block_range = find_range(address, self.block_size)

        details_to_add = {
            "address": address,
            "offset": offset,
            "set_index": self.set_index,
            "tag": tag,
            "block_range": {"min": str(block_range[0]),
                            "max": str(block_range[1])},
            "tag_queue": self.tag_queue.queue
        }

        return operation_details | details_to_add

    def to_string_blocks(self) -> str:
        """
        Creates a string representation of the blocks in the set with the following format for each block:
            "Block: <index>, Tag: <tag>, Occupied <occupied>, Dirty <dirty>"
        :return: A string representing the blocks in the set
        """
        for i in range(0, len(self.blocks)):
            block = self.blocks[i]
            return "Block: " + str(i) + ", Tag: " + str(block.tag) + ", Occupied: " + str(block.occupied) \
                   + ", Dirty: " + str(block.dirty)

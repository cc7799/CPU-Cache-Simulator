import math
from typing import Dict, List

from cache_set import CacheSet


class Cache:
    def __init__(self, memory: bytearray,
                 address_size: int, cache_size: int, block_size: int,
                 associativity: int, write_back: bool):
        """
        Creates a new cache
        :param memory: The byte array containing the simulation's memory
        :param address_size: The size of the memory addresses in bits
        :param cache_size: The size of the cache in bits
        :param block_size: The size of each block in bits
        :param associativity: The associativity of the cache
        :param write_back: Whether the cache should be run in write-back mode
        """

        self.memory = memory
        self.address_size = address_size
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.write_back = write_back

        self.num_blocks = int(self.cache_size / self.block_size)
        self.num_sets = int(self.num_blocks / self.associativity)
        self.num_blocks_per_set = int(self.num_blocks / self.num_sets)

        self.index_size = int(math.log(self.num_sets, 2))
        self.block_offset_size = int(math.log(self.block_size, 2))
        self.tag_size = int(self.address_size - (self.index_size + self.block_offset_size))

        # Initialize sets
        self.sets = []
        for i in range(0, self.num_sets):
            self.sets.append(CacheSet(self.memory, self.write_back, self.num_blocks_per_set, self.block_size, i))

    def read(self, address: int) -> Dict:
        """
        Returns the value from a given memory address.
        If the data is in the cache, reads from the cache. If not, reads from memory and moves the data into the cache.
        :param address: The memory address to access
        :return: A dictionary containing information about the results of the operation
        """
        operation_details = {}

        block_offset, index, tag = self.split_address(address)

        target_set = self.sets[index]
        block_index = target_set.find_block_index(tag)

        # If the block is not in the set; Cache miss
        if block_index == -1:
            operation_details["hit_or_miss"] = "miss"
            operation_details = operation_details | target_set.read_from_memory(address, tag, block_offset)
            return operation_details

        # If the block is in the set; Cache hit
        else:
            operation_details["hit_or_miss"] = "hit"
            operation_details = operation_details | target_set.read_from_cache(address, tag, block_index, block_offset)
            return operation_details

    def write(self, address: int, word: bytearray) -> Dict:
        """
        Writes a given word to a given memory address
        :param address: The memory address to write to
        :param word: The word to write to memory
        :return: A dictionary containing information about the results of the operation
        """
        operation_details: Dict = {}

        block_offset, index, tag = self.split_address(address)

        target_set = self.sets[index]
        block_index = target_set.find_block_index(tag)

        # If the block is not in the set; Cache miss
        if block_index == -1:
            # Reads missing block from memory into cache
            target_set.read_from_memory(address, tag, block_offset)
            operation_details["hit_or_miss"] = "miss"

        # If block is in the set; Cache hit
        else:
            operation_details["hit_or_miss"] = "hit"

        operation_details = operation_details | \
            target_set.write_to_cache(address, tag, block_index, block_offset, word, self.write_back)

        return operation_details

    def split_address(self, address: int) -> List:
        """
        Splits a memory address into it's block offset, index, and tag
        :param address: The address to split
        :return: A tuple containing the address' block offset, index, and tag
        """
        address_split = address

        block_offset = int(address_split % (math.pow(2, self.block_offset_size)))
        address_split = address_split // math.pow(2, self.block_offset_size)

        index = int(address_split % (math.pow(2, self.index_size)))
        address_split = int(address_split // math.pow(2, self.index_size))

        tag = address_split

        return block_offset, index, tag

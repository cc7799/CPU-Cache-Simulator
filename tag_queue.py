class TagQueue:
    """
    A queue for storing the tags present in a cache set. The least recently accessed tags will be in the front and
    tags will be moved to the back when accessed.
    """
    def __init__(self, size: int):
        """
        Initializes the queue with a list of size `size` filled with the invalid tag `-1`
        :param size:
        """
        self.queue = []
        self.size = size

        # Fill the queue with invalid tags
        for i in range(0, size):
            self.queue.append(-1)

    def update_queue(self, tag: int) -> bool:
        """
        Updates the tag queue to account for the given tag being accessed
        :param tag: The tag to add to the queue or to be moved to the front
        :return: True if the tag was already present in the queue; False otherwise
        """
        # If tag is already in queue, move it to the end
        for i in range(0, self.size):
            if self.queue[i] == tag:
                self.queue.pop(i)
                self.queue.append(tag)
                return True

        # If tag is not in queue, remove the least recently used tag and add the new one to the end
        self.queue.pop(0)
        self.queue.append(tag)
        return False

    def get_least_recently_used(self) -> int:
        """
        Gets the least recently used tag in the queue
        :return: The first item in the queue's list
        """
        return self.queue[0]

    def to_string(self) -> str:
        """
        Returns the queue in string form
        :return: A string form of the queue
        """
        return str(self.queue)

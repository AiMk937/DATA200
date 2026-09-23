"""DATA 200 classwork: custom doubly linked list + LRU feature cache.

Run: python student_starter.py
No OrderedDict, deque, functools cache, or third-party linked-list class.
A dictionary is used only for key -> Node lookup. Python lists below are
snapshots for display/testing; they never store or implement cache order.
"""


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
        self.owner = None  # Prevent double insertion and removal from wrong list.


class DoublyLinkedList:
    """Head = least recently used; tail = most recently used."""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, node):
        """Attach a detached node at tail in O(1)."""
        if node.owner is not None:
            raise ValueError('node already belongs to a list')
        node.prev = self.tail
        node.next = None
        if self.tail is None:
            self.head = node  # First node is both endpoints.
        else:
            self.tail.next = node
        self.tail = node
        node.owner = self
        self.size += 1

    def remove(self, node):
        """Unlink a known member in O(1); return that detached node."""
        if node.owner is not self:
            raise ValueError('node does not belong to this list')
        # Reconnect each side; a missing neighbour means this node was an endpoint.
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev
        node.prev = None
        node.next = None
        node.owner = None
        self.size -= 1
        return node

    def move_to_end(self, node):
        """Promote a known node to most recently used in O(1)."""
        if node.owner is not self:
            raise ValueError('node does not belong to this list')
        if node is self.tail:
            return  # Already most recently used; unlinking it would be wasted work.
        # Reuse the same object so the dictionary keeps pointing at a live node.
        self.remove(node)
        self.append(node)

    def pop_first(self):
        """Remove least recently used node; raise IndexError if empty."""
        if self.head is None:
            raise IndexError('empty linked list')
        return self.remove(self.head)

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node
            node = node.next

    def validate(self):
        """O(n) teaching/debug check, NOT part of production cache updates."""
        if self.size == 0:
            assert self.head is None and self.tail is None
            return
        assert self.head.prev is None and self.tail.next is None
        count = 0
        previous = None
        current = self.head
        while current is not None:
            assert count < self.size, 'cycle or incorrect size'
            assert current.prev is previous
            assert current.owner is self
            previous, current = current, current.next
            count += 1
        assert previous is self.tail and count == self.size
        count = 0
        following = None
        current = self.tail
        while current is not None:
            assert count < self.size
            assert current.next is following
            following, current = current, current.prev
            count += 1
        assert following is self.head and count == self.size


class LRUCache:
    """Keys must be hashable. get/put are expected O(1), excluding payload work."""
    def __init__(self, capacity):
        # type(...) is int also rejects True, because bool is a subclass of int.
        if type(capacity) is not int or capacity <= 0:
            raise ValueError('capacity must be a positive integer')
        self.capacity = capacity
        self.nodes = {}
        self.order = DoublyLinkedList()

    def __len__(self):
        return len(self.nodes)

    def get(self, key):
        """Return value and promote node. A miss raises KeyError without change."""
        # Subscripting raises KeyError before anything is promoted or mutated.
        node = self.nodes[key]
        self.order.move_to_end(node)
        return node.value

    def put(self, key, value):
        """Insert/update and promote. Return evicted (key, value), or None."""
        # Dictionary lookup also checks hashability before list mutation.
        if key in self.nodes:
            node = self.nodes[key]
            node.value = value
            self.order.move_to_end(node)
            return None
        node = Node(key, value)
        self.nodes[key] = node
        self.order.append(node)
        if len(self.nodes) > self.capacity:
            old = self.order.pop_first()
            del self.nodes[old.key]
            return old.key, old.value
        return None

    def keys_lru_to_mru(self):
        """O(n) snapshot used only for demonstrations."""
        return [node.key for node in self.order]

    def validate(self):
        """O(n) invariant checks for classroom demonstrations."""
        self.order.validate()
        assert self.order.size == len(self.nodes) <= self.capacity
        for node in self.order:
            assert self.nodes[node.key] is node


def show(label, cache, expected):
    cache.validate()
    actual = cache.keys_lru_to_mru()
    assert actual == expected, (actual, expected)
    print(f'  {label}: {actual}  (LRU -> MRU)')


def expect_error(error_type, operation):
    try:
        operation()
    except error_type:
        print(f'  Expected {error_type.__name__}: passed')
    else:
        raise AssertionError(f'Expected {error_type.__name__}')


def demo_01_empty_cache():
    """Edge: get on empty cache and pop on empty linked list."""
    print('\n01. Empty cache and empty linked list')
    cache = LRUCache(3)
    expect_error(KeyError, lambda: cache.get('A'))
    expect_error(IndexError, cache.order.pop_first)
    show('Both failures leave the cache empty', cache, [])


def demo_02_first_insertion():
    """Edge: a singleton is both head and tail, with null links."""
    print('\n02. First insertion creates both endpoints')
    cache = LRUCache(3)
    assert cache.put('A', 100) is None
    assert cache.order.head is cache.order.tail
    assert cache.order.head.prev is None and cache.order.tail.next is None
    show('Insert A', cache, ['A'])


def demo_03_fill_to_capacity():
    """Edge: reaching capacity must not evict an entry."""
    print('\n03. Fill exactly to capacity')
    cache = LRUCache(3)
    for key in ('A', 'B', 'C'):
        assert cache.put(key, key.lower()) is None
    assert len(cache) == 3
    show('Exactly full; no eviction', cache, ['A', 'B', 'C'])


def demo_04_hit_moves_middle():
    """Edge: remove a middle node and reconnect BOTH neighboring links."""
    print('\n04. A hit moves the middle node to MRU')
    cache = LRUCache(3)
    for key in ('A', 'B', 'C'):
        cache.put(key, key.lower())
    original = cache.nodes['B']
    assert cache.get('B') == 'b'
    assert cache.order.tail is original  # Reuse node; do not make a duplicate.
    show('Read B', cache, ['A', 'C', 'B'])


def demo_05_head_and_tail_hits():
    """Edges: promote head, then repeatedly access the existing tail."""
    print('\n05. Hits at the two endpoints')
    cache = LRUCache(3)
    for key in ('A', 'B', 'C'):
        cache.put(key, key)
    cache.get('A')
    show('Read old head A', cache, ['B', 'C', 'A'])
    tail = cache.order.tail
    cache.get('A'); cache.get('A')
    assert cache.order.tail is tail
    show('Read existing tail A twice', cache, ['B', 'C', 'A'])


def demo_06_eviction_after_hit():
    """Edge: evict by access order, not original insertion order."""
    print('\n06. Eviction honors recent accesses')
    cache = LRUCache(3)
    for key in ('A', 'B', 'C'):
        cache.put(key, key.lower())
    cache.get('A')
    old = cache.nodes['B']
    assert cache.put('D', 'd') == ('B', 'b')
    assert old.prev is None and old.next is None and old.owner is None
    expect_error(KeyError, lambda: cache.get('B'))
    show('Insert D; B is evicted and detached', cache, ['C', 'A', 'D'])


def demo_07_update_existing_key():
    """Edge: update at full capacity without duplicate nodes or eviction."""
    print('\n07. Update an existing key at full capacity')
    cache = LRUCache(2)
    cache.put('A', 10); cache.put('B', 20)
    node = cache.nodes['A']
    assert cache.put('A', 99) is None
    assert cache.nodes['A'] is node and len(cache) == 2
    assert cache.get('A') == 99
    show('Update A to 99', cache, ['B', 'A'])


def demo_08_capacity_one():
    """Edges: singleton hit/update, replacement, and endpoint reset."""
    print('\n08. Capacity-one cache and singleton removal')
    cache = LRUCache(1)
    cache.put('A', 1)
    assert cache.get('A') == 1
    assert cache.put('A', 2) is None
    assert cache.put('B', 3) == ('A', 2)
    assert cache.order.head is cache.order.tail
    show('Replace A with B', cache, ['B'])
    # Exercise singleton removal on a separate list; do not bypass cache bookkeeping.
    linked = DoublyLinkedList()
    linked.append(Node('X', 4))
    removed = linked.pop_first()
    assert removed.key == 'X' and removed.owner is None
    linked.validate()
    assert linked.head is None and linked.tail is None and linked.size == 0
    print('  Removing the only list node resets both endpoints: passed')


def demo_09_invalid_inputs_and_none():
    """Edges: invalid capacities, unhashable key, None value, foreign node."""
    print('\n09. Invalid inputs and valid None values')
    for capacity in (0, -1, True, 2.5):
        expect_error(ValueError, lambda c=capacity: LRUCache(c))
    cache = LRUCache(2)
    cache.put('A', None)
    assert cache.get('A') is None  # A stored None is not a cache miss.
    expect_error(KeyError, lambda: cache.get('missing'))
    expect_error(TypeError, lambda: cache.put([], 9))
    expect_error(ValueError, lambda: cache.order.remove(Node('Z', 0)))
    expect_error(ValueError, lambda: cache.order.append(cache.nodes['A']))
    show('Rejected operations preserve valid state', cache, ['A'])


def demo_10_data_science_feature_cache():
    """Application: reuse image features; an evicted image needs recomputation."""
    print('\n10. Image-feature cache for a data science pipeline')
    cache = LRUCache(2)
    calls = {'count': 0}

    def extract_features(image_id):
        # Deterministic stand-in for expensive image processing; no files needed.
        calls['count'] += 1
        length = len(image_id)
        return (length, length * length)

    def features(image_id):
        try:
            return cache.get(image_id), 'HIT'
        except KeyError:
            value = extract_features(image_id)
            cache.put(image_id, value)
            return value, 'MISS'

    requests = ('img_A', 'img_B', 'img_A', 'img_C', 'img_B')
    expected_status = ('MISS', 'MISS', 'HIT', 'MISS', 'MISS')
    expected_orders = (['img_A'], ['img_A', 'img_B'], ['img_B', 'img_A'],
                       ['img_A', 'img_C'], ['img_C', 'img_B'])
    for image_id, status, order in zip(requests, expected_status, expected_orders):
        result, actual_status = features(image_id)
        assert actual_status == status and result == (5, 25)
        show(f'{image_id}: {actual_status}, features={result}', cache, order)
    assert calls['count'] == 4
    print('  5 requests, 4 computations, 1 cache hit: passed')


def main():
    demos = (demo_01_empty_cache, demo_02_first_insertion,
             demo_03_fill_to_capacity, demo_04_hit_moves_middle,
             demo_05_head_and_tail_hits, demo_06_eviction_after_hit,
             demo_07_update_existing_key, demo_08_capacity_one,
             demo_09_invalid_inputs_and_none, demo_10_data_science_feature_cache)
    for demo in demos:
        demo()
    print('\nAll 10 demos passed.')


if __name__ == '__main__':
    main()

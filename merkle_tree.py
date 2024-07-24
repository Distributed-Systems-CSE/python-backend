import hashlib

import utils


class MerkelTree:

	def __init__(self, byte_stream):
		"""
		:param byte_stream: Byte stream of file uploaded

		1. Added padding to the byte_stream to make it possible to split the file into 2^n chunks of 16KB
			(fixed size determined).
			Here, n= number of the levels in the merkel tree.

		2. Build merkel tree s.t.
			- Root will have the hash of the complete file.
			- left child will have the hash of the first half of the file and right child will have the hash of the
				last half of the file.
			- So, on the hashes will be computed for each level till the chunk size is set to be 16KB
		"""
		self.chunk_size = 16 * 1024  # 16KB
		self.padding = utils.padding_size(byte_stream)
		self.byte_stream = byte_stream + b'\0' * self.padding
		self.root = self.build_tree(self.byte_stream)

	def build_tree(self, byte_stream):
		"""
		:param byte_stream: byte_stream with padding added
		:return: root MerkelTreeNode
		"""
		if len(byte_stream) == self.chunk_size:
			return MerkelTreeNode(hashlib.sha256(byte_stream).hexdigest(), None, None)
		else:
			mid = len(byte_stream) // 2
			left_child = self.build_tree(byte_stream[:mid])
			right_child = self.build_tree(byte_stream[mid:])
			root_hash = hashlib.sha256(byte_stream).hexdigest()
			return MerkelTreeNode(root_hash, left_child, right_child)


class MerkelTreeNode:
	def __init__(self, root_hash, left_child, right_child):
		"""
		:param root_hash: hash of the content of the root
		:param left_child: Merkel tree or None
		:param right_child: Merkel tree or None
		"""
		self.root_hash = root_hash
		self.left_child = left_child
		self.right_child = right_child

	def get_json(self):
		"""
		:return: json in format
			{
				root: Hash,
				left_child: {
						root: Hash,
						left_child: { ... },
						right_child: { ... }
							},
				right_child: {
						root: Hash,
						left_child: { ... },
						right_child: { ... }
							},
			}
		"""
		return {
			'root': self.root_hash,
			'left_child': self.left_child.get_json() if self.left_child else None,
			'right_child': self.right_child.get_json() if self.right_child else None
		}

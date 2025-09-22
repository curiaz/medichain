"""
Blockchain ledger integration for medical record integrity verification
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the SHA-256 hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4):
        """Mine the block with proof of work"""
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    """Simple blockchain for medical record integrity verification"""
    
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []
    
    def create_genesis_block(self) -> Block:
        """Create the first block in the chain"""
        return Block(
            index=0,
            timestamp=str(datetime.now()),
            data={'message': 'Genesis Block'},
            previous_hash='0'
        )
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_block(self, data: Dict) -> Block:
        """Add a new block to the chain"""
        new_block = Block(
            index=len(self.chain),
            timestamp=str(datetime.now()),
            data=data,
            previous_hash=self.get_latest_block().hash
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        return new_block
    
    def add_medical_record_hash(self, record_id: str, encrypted_hash: str) -> Block:
        """Add a medical record hash to the blockchain"""
        data = {
            'type': 'medical_record',
            'record_id': record_id,
            'encrypted_hash': encrypted_hash,
            'timestamp': str(datetime.now())
        }
        return self.add_block(data)
    
    def verify_chain(self) -> bool:
        """Verify the integrity of the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify link to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_record_transactions(self, record_id: str) -> List[Dict]:
        """Get all blockchain transactions for a specific medical record"""
        transactions = []
        for block in self.chain:
            if block.data.get('type') == 'medical_record' and block.data.get('record_id') == record_id:
                transactions.append({
                    'block_index': block.index,
                    'hash': block.hash,
                    'timestamp': block.timestamp,
                    'data': block.data
                })
        return transactions
    
    def to_dict(self) -> Dict:
        """Convert blockchain to dictionary format"""
        return {
            'chain': [
                {
                    'index': block.index,
                    'timestamp': block.timestamp,
                    'data': block.data,
                    'previous_hash': block.previous_hash,
                    'hash': block.hash,
                    'nonce': block.nonce
                }
                for block in self.chain
            ],
            'length': len(self.chain)
        }

# Global blockchain instance
medical_blockchain = Blockchain()

def add_medical_record_to_blockchain(record_id: str, encrypted_hash: str) -> Dict:
    """Add a medical record to the blockchain and return transaction details"""
    block = medical_blockchain.add_medical_record_hash(record_id, encrypted_hash)
    return {
        'block_index': block.index,
        'hash': block.hash,
        'timestamp': block.timestamp
    }

def verify_medical_record_integrity(record_id: str, expected_hash: str) -> bool:
    """Verify if a medical record's hash matches the blockchain"""
    transactions = medical_blockchain.get_record_transactions(record_id)
    if not transactions:
        return False
    
    # Check if the expected hash matches any blockchain transaction
    for transaction in transactions:
        if transaction['data']['encrypted_hash'] == expected_hash:
            return True
    
    return False

def get_blockchain_status() -> Dict:
    """Get current blockchain status"""
    return {
        'length': len(medical_blockchain.chain),
        'is_valid': medical_blockchain.verify_chain(),
        'latest_block': {
            'index': medical_blockchain.get_latest_block().index,
            'hash': medical_blockchain.get_latest_block().hash,
            'timestamp': medical_blockchain.get_latest_block().timestamp
        }
    }

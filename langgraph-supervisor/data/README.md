# Data Module

This module contains data models and mock data storage.

## Files

- `models.py` - Pydantic data models
- `mock_store.py` - In-memory mock data storage
- `__init__.py` - Module initialization

## Models

### Account
Represents account information with:
- Basic details (ID, name, status)
- Address information
- Facility associations
- Balance and pricing information
- Loyalty and rewards data
- Evolux level

### Facility
Represents facility information with:
- Basic details (ID, name, status)
- Medical license information
- Agreement status
- Shipping address
- Account associations

### Note
Represents a saved note with:
- Note ID
- User ID
- Content
- Timestamps (created_at, updated_at)

### Session
Represents a conversation session with:
- Session ID
- User ID
- Messages list
- Timestamps

### Message
Represents a chat message with:
- Role (user/assistant)
- Content
- Timestamp

## Mock Store

The `MockDataStore` class provides in-memory storage:
- `accounts` - Dictionary of Account objects
- `facilities` - Dictionary of Facility objects
- `notes` - Dictionary of user_id -> List[Note]

### Methods
- `get_account(account_id)` - Get account by ID
- `get_all_accounts()` - Get all accounts
- `get_facility(facility_id)` - Get facility by ID
- `get_all_facilities()` - Get all facilities
- `save_note(user_id, content)` - Save a note
- `get_notes(user_id, date, last_n, order)` - Get notes with filters and ordering
  - `order`: "asc" for first N (oldest first), "desc" for last N (newest first, default)

## Sample Data

The store includes sample data:
- Account: A-011977763 (Dimod Account) - Complete with rewards, facilities, and all fields
- Facilities: F-013203268 (TEST Delete Facility, INACTIVE), F-015766066 (Diamond Facility, ACTIVE)
- Notes: Pre-seeded for demo users (sumer.choudhary@bitcot.com, kaushal.sethia.c@evolus.com)

## Usage

```python
from data import mock_store

account = mock_store.get_account("A-011977763")
facility = mock_store.get_facility("F-015766066")
note = mock_store.save_note("user1", "Meeting notes...")
```

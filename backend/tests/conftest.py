import pytest
import sys
from unittest.mock import MagicMock

# Create a mock for the whisper module so tests can run without installing it
mock_whisper = MagicMock()
sys.modules['whisper'] = mock_whisper

# Mock litellm to avoid making real API calls during tests
mock_litellm = MagicMock()
sys.modules['litellm'] = mock_litellm

# Mock yt_dlp
mock_ydl = MagicMock()
sys.modules['yt_dlp'] = mock_ydl

import pytest
import os
from unittest.mock import patch, MagicMock
from app.synthesis.advanced_media import advanced_stitch_with_crossfade

def test_advanced_stitch_single_file():
    """Test stitching logic when only one file is provided (no crossfade)."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        result = advanced_stitch_with_crossfade(["only_file.mp3"], "data/out.mp3")
        assert result is True
        
        args = mock_run.call_args[0][0]
        assert "ffmpeg" in args
        assert "-c" in args
        assert "copy" in args
        assert "-filter_complex" not in args

def test_advanced_stitch_multiple_files():
    """Verify the FFmpeg complex filter command generation for crossfading multiple files."""
    audio_files = ["intro.mp3", "clip1.mp3", "clip2.mp3"]
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        result = advanced_stitch_with_crossfade(audio_files, "data/out.mp3")
        assert result is True
        
        args = mock_run.call_args[0][0]
        assert args[0] == "ffmpeg"
        assert "-filter_complex" in args
        
        # Check that the correct crossfade strings were generated
        filter_str = args[args.index("-filter_complex") + 1]
        
        # Should have 2 acrossfade nodes for 3 files
        assert filter_str.count("acrossfade") == 2
        assert "[0:a]" in filter_str
        assert "c1=tri:c2=tri" in filter_str

import pytest
import sys
from unittest.mock import MagicMock, patch
from cli.game.audio_service import AudioService
from cli.sral_wrapper import SRALEngines


class TestSRALIntegration:
    """Tests for SRAL integration in the audio service"""

    def test_sral_initialization_success(self):
        """Test successful SRAL initialization"""
        with patch('sral.Sral') as mock_sral:
            # Setup mock
            mock_sral_instance = MagicMock()
            mock_sral.return_value = mock_sral_instance
            
            # Create audio service
            audio = AudioService()
            
            # Verify SRAL was initialized correctly
            mock_sral.assert_called_once_with(engines_exclude=0)
            assert audio.sral is not None
            
    def test_sral_initialization_failure(self):
        """Test fallback behavior when SRAL initialization fails"""
        with patch('sral.Sral', side_effect=Exception("SRAL initialization failed")):
            # Create audio service - should not raise exception
            audio = AudioService()
            
            # Verify SRAL is None
            assert audio.sral is None
    
    def test_play_narration_with_sral(self):
        """Test play_narration using SRAL"""
        with patch('sral.Sral') as mock_sral:
            # Setup mock
            mock_sral_instance = MagicMock()
            mock_sral.return_value = mock_sral_instance
            
            # Create audio service
            audio = AudioService()
            
            # Test play_narration
            test_text = "Test narration"
            audio.play_narration(test_text)
            
            # Verify SRAL.speak was called
            mock_sral_instance.speak.assert_called_once_with(test_text)
    
    def test_play_narration_without_sral(self):
        """Test play_narration fallback when SRAL is not available"""
        with patch('sral.Sral', side_effect=Exception("SRAL initialization failed")):
            # Create audio service
            audio = AudioService()
            
            # Test play_narration (should not raise exception)
            audio.play_narration("Test narration")
            # No assertion needed - we're just verifying it doesn't crash
    
    def test_play_narration_with_sral_exception(self):
        """Test play_narration fallback when SRAL.speak raises exception"""
        with patch('sral.Sral') as mock_sral:
            # Setup mock
            mock_sral_instance = MagicMock()
            mock_sral_instance.speak.side_effect = Exception("SRAL speak failed")
            mock_sral.return_value = mock_sral_instance
            
            # Create audio service
            audio = AudioService()
            
            # Test play_narration (should not raise exception)
            audio.play_narration("Test narration")
            # No assertion needed - we're just verifying it doesn't crash
    
    def test_speech_rate_with_sral(self):
        """Test setting speech rate with SRAL"""
        with patch('sral.Sral') as mock_sral:
            # Setup mock
            mock_sral_instance = MagicMock()
            mock_sral.return_value = mock_sral_instance
            
            # Create audio service
            audio = AudioService()
            
            # Test setting speech rate
            test_rate = 75
            audio.set_speech_rate(test_rate)
            
            # Verify SRAL.set_rate was called
            mock_sral_instance.set_rate.assert_called_once_with(test_rate)
    
    def test_speech_rate_with_sral_exception(self):
        """Test setting speech rate when SRAL.set_rate raises exception"""
        with patch('sral.Sral') as mock_sral:
            # Setup mock
            mock_sral_instance = MagicMock()
            mock_sral_instance.set_rate.side_effect = Exception("SRAL set_rate failed")
            mock_sral.return_value = mock_sral_instance
            
            # Create audio service
            audio = AudioService()
            
            # Test setting speech rate (should not raise exception)
            audio.set_speech_rate(75)
            # No assertion needed - we're just verifying it doesn't crash
    
    def test_toggle_running_screen_reader(self):
        """Test toggling between running screen reader and SAPI"""
        with patch('sral.Sral') as mock_sral, \
             patch('cli.game.pygame_interface.PygameAudioService.play_narration'):
            # Import here to avoid circular import
            from cli.game.pygame_interface import PygameAudioService
            
            # Setup mock
            mock_sral_instance = MagicMock()
            mock_sral.return_value = mock_sral_instance
            
            # Create audio service
            audio = PygameAudioService()
            
            # Reset mock to clear initialization call
            mock_sral.reset_mock()
            
            # Test toggling to SAPI
            audio.toggle_running_screen_reader(False)
            
            # Verify SRAL was initialized with correct parameters for SAPI
            mock_sral.assert_called_with(engines_exclude=(
                SRALEngines.NVDA | SRALEngines.JAWS | SRALEngines.SPEECH_DISPATCHER | 
                SRALEngines.UIA | SRALEngines.AV_SPEECH | SRALEngines.NARRATOR
            ))
            
            # Reset mock
            mock_sral.reset_mock()
            
            # Test toggling back to running screen reader
            audio.toggle_running_screen_reader(True)
            
            # Verify SRAL was initialized with correct parameters for running screen reader
            mock_sral.assert_called_with(engines_exclude=0)
    
    def test_toggle_running_screen_reader_exception(self):
        """Test exception handling when toggling screen reader mode fails"""
        with patch('sral.Sral', side_effect=Exception("SRAL initialization failed")), \
             patch('cli.game.pygame_interface.PygameAudioService.play_narration') as mock_play_narration:
            # Import here to avoid circular import
            from cli.game.pygame_interface import PygameAudioService
            
            # Create audio service
            audio = PygameAudioService()
            
            # Test toggling (should not raise exception)
            audio.toggle_running_screen_reader(False)
            
            # Verify error message was narrated
            mock_play_narration.assert_called_with("Failed to change screen reader mode")
